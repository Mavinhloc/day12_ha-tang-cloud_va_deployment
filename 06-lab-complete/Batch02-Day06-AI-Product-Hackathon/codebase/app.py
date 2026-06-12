import streamlit as st
from src.tutor import (
    extract_text, stream_chat, summarize,
    generate_quiz, generate_flashcards, generate_objectives, generate_study_plan,
)

st.set_page_config(page_title="AI Tutor — AI Thực Chiến", layout="wide")

SUGGESTIONS = [
    "LangChain là gì?",
    "Agent khác Chain thế nào?",
    "RAG hoạt động ra sao?",
]


# ── Parsers ──────────────────────────────────────────────────────────────────

def parse_quiz(raw: str) -> list[dict]:
    questions = []
    for block in [b.strip() for b in raw.split("**Câu ") if b.strip()]:
        try:
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            q_text = lines[0].split(":**", 1)[-1].strip() if ":**" in lines[0] else lines[0]
            options, answer, explanation = {}, "", ""
            for line in lines[1:]:
                if line.startswith(("A.", "B.", "C.", "D.")):
                    options[line[0]] = line[2:].strip()
                elif "✅" in line or "Đáp án" in line:
                    part = (line.replace("✅", "")
                               .replace("**Đáp án:**", "")
                               .replace("**Đáp án**:", "").strip())
                    if "—" in part:
                        a, e = part.split("—", 1)
                        answer, explanation = a.strip(), e.strip()
                    elif part:
                        answer = part[0]
            if q_text and len(options) >= 2:
                questions.append({"text": q_text, "options": options,
                                   "answer": answer, "explanation": explanation})
        except Exception:
            continue
    return questions


def parse_flashcards(raw: str) -> list[dict]:
    cards = []
    for line in raw.split("\n"):
        if line.startswith("CARD|||"):
            parts = line.split("|||")
            if len(parts) == 3:
                cards.append({"front": parts[1].strip(), "back": parts[2].strip()})
    return cards


def parse_objectives(raw: str) -> list[str]:
    return [l.replace("OBJ|||", "").strip()
            for l in raw.split("\n") if l.startswith("OBJ|||") and l.replace("OBJ|||", "").strip()]


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("📚 Tài liệu buổi học")
    st.caption("Upload để AI đọc, tóm tắt và tạo nội dung học tự động.")

    uploaded = st.file_uploader("PDF / DOCX / TXT", type=["pdf", "docx", "txt"],
                                label_visibility="collapsed")

    if uploaded and uploaded.name != st.session_state.get("doc_name"):
        try:
            with st.spinner("Đang đọc tài liệu..."):
                doc_text = extract_text(uploaded)
            st.session_state.update({
                "doc_context": doc_text,
                "doc_name": uploaded.name,
                "chat_history": [],
                "quiz": None, "flashcards": None,
                "objectives": None, "study_plan": None,
                "quiz_version": 0, "fc_version": 0,
                "obj_version": 0, "suggestions_used": False,
            })
            if len(doc_text) >= 50_000:
                st.info("File lớn — chỉ đọc được 50,000 ký tự đầu.")
            with st.spinner("Đang tóm tắt..."):
                st.session_state["doc_summary"] = summarize(doc_text)
        except ValueError as e:
            st.error(str(e))

    if "doc_name" in st.session_state:
        st.success(f"✅ {st.session_state['doc_name']}")
        st.caption(f"{len(st.session_state.get('doc_context', ''))} ký tự đã đọc")

        if st.session_state.get("doc_summary"):
            with st.expander("📋 Tóm tắt nội dung", expanded=True):
                st.markdown(st.session_state["doc_summary"])

        st.divider()
        st.caption("Tạo nội dung học:")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🧪 Quiz", use_container_width=True):
                with st.spinner("Đang tạo quiz..."):
                    st.session_state["quiz"] = generate_quiz(st.session_state["doc_context"])
                    st.session_state["quiz_version"] += 1
            if st.button("🎯 Objectives", use_container_width=True):
                with st.spinner("Đang tạo..."):
                    st.session_state["objectives"] = generate_objectives(st.session_state["doc_context"])
                    st.session_state["obj_version"] = st.session_state.get("obj_version", 0) + 1
        with col2:
            if st.button("🃏 Flashcards", use_container_width=True):
                with st.spinner("Đang tạo flashcards..."):
                    st.session_state["flashcards"] = generate_flashcards(st.session_state["doc_context"])
                    st.session_state["fc_version"] = st.session_state.get("fc_version", 0) + 1
            if st.button("📅 Study Plan", use_container_width=True):
                with st.spinner("Đang tạo..."):
                    st.session_state["study_plan"] = generate_study_plan(st.session_state["doc_context"])
    else:
        st.info("Chưa có tài liệu — bạn vẫn có thể hỏi bất kỳ điều gì.")

# ── Main area ─────────────────────────────────────────────────────────────────

st.title("💬 AI Tutor")
st.caption("Hỏi bất kỳ điều gì — giải thích có cấu trúc, ví dụ code, kiểm tra hiểu.")

# ── Learning Objectives ───────────────────────────────────────────────────────
if st.session_state.get("objectives"):
    with st.expander("🎯 Learning Objectives", expanded=True):
        objectives = parse_objectives(st.session_state["objectives"])
        ver = st.session_state.get("obj_version", 0)
        if objectives:
            checked = sum(
                st.session_state.get(f"obj_{i}_v{ver}", False)
                for i in range(len(objectives))
            )
            st.progress(checked / len(objectives))
            st.caption(f"{checked}/{len(objectives)} mục tiêu đã hoàn thành")
            for i, obj in enumerate(objectives):
                st.checkbox(obj, key=f"obj_{i}_v{ver}")
        else:
            st.markdown(st.session_state["objectives"])
    if st.button("✕ Đóng", key="close_obj"):
        st.session_state["objectives"] = None
        st.rerun()

# ── Study Plan ────────────────────────────────────────────────────────────────
if st.session_state.get("study_plan"):
    with st.expander("📅 Study Plan — Lịch học 1 ngày", expanded=True):
        st.markdown(st.session_state["study_plan"])
    if st.button("✕ Đóng", key="close_sp"):
        st.session_state["study_plan"] = None
        st.rerun()

# ── Flashcards ────────────────────────────────────────────────────────────────
if st.session_state.get("flashcards"):
    with st.expander("🃏 Flashcards", expanded=True):
        cards = parse_flashcards(st.session_state["flashcards"])
        ver = st.session_state.get("fc_version", 0)
        if cards:
            cols_per_row = 3
            for row in range(0, len(cards), cols_per_row):
                cols = st.columns(min(cols_per_row, len(cards) - row))
                for col, idx in zip(cols, range(row, min(row + cols_per_row, len(cards)))):
                    card = cards[idx]
                    flip_key = f"flip_{idx}_v{ver}"
                    is_flipped = st.session_state.get(flip_key, False)
                    with col:
                        if not is_flipped:
                            st.info(f"**{card['front']}**")
                            if st.button("🔄 Lật thẻ", key=f"flip_btn_{idx}_v{ver}",
                                         use_container_width=True):
                                st.session_state[flip_key] = True
                                st.rerun()
                        else:
                            st.success(card["back"])
                            if st.button("↩️ Lật lại", key=f"flip_btn_{idx}_v{ver}",
                                         use_container_width=True):
                                st.session_state[flip_key] = False
                                st.rerun()
        else:
            st.markdown(st.session_state["flashcards"])
    if st.button("✕ Đóng", key="close_fc"):
        st.session_state["flashcards"] = None
        st.rerun()

# ── Quiz ──────────────────────────────────────────────────────────────────────
if st.session_state.get("quiz"):
    with st.expander("🧪 Quiz — kiểm tra hiểu bài", expanded=True):
        questions = parse_quiz(st.session_state["quiz"])
        ver = st.session_state.get("quiz_version", 0)
        if questions:
            for i, q in enumerate(questions):
                st.markdown(f"**Câu {i + 1}:** {q['text']}")
                opts = [f"{k}. {v}" for k, v in sorted(q["options"].items())]
                selected = st.radio(f"q{i}", opts, key=f"quiz_q{i}_v{ver}",
                                    label_visibility="collapsed", index=None)
                if selected:
                    if selected[0] == q["answer"]:
                        st.success(f"✅ Đúng rồi! {q['explanation']}")
                    else:
                        st.error(f"❌ Chưa đúng. Đáp án: **{q['answer']}** — {q['explanation']}")
                st.markdown("---")
        else:
            st.markdown(st.session_state["quiz"])
    if st.button("✕ Đóng quiz", key="close_quiz"):
        st.session_state["quiz"] = None
        st.rerun()

# ── Chat ──────────────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("used_doc"):
            st.caption(f"📄 Dùng context từ {msg['used_doc']}")

question = st.chat_input("Bạn đang stuck ở đâu?")

if (not st.session_state.get("suggestions_used")
        and not st.session_state.get("chat_history")
        and not question):
    st.caption("Thử hỏi:")
    cols = st.columns(len(SUGGESTIONS))
    for col, q in zip(cols, SUGGESTIONS):
        if col.button(q, use_container_width=True):
            question = q
            st.session_state["suggestions_used"] = True

if question:
    st.session_state["chat_history"].append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    doc_context = st.session_state.get("doc_context", "")
    doc_name = st.session_state.get("doc_name")

    with st.chat_message("assistant"):
        try:
            answer = st.write_stream(
                stream_chat(doc_context, st.session_state["chat_history"][:-1], question)
            )
        except Exception as e:
            answer = f"⚠️ Lỗi khi gọi AI: {e}"
            st.markdown(answer)
        if doc_name and doc_context:
            st.caption(f"📄 Dùng context từ {doc_name}")

    st.session_state["chat_history"].append({
        "role": "assistant", "content": answer,
        "used_doc": doc_name if doc_context else None,
    })
