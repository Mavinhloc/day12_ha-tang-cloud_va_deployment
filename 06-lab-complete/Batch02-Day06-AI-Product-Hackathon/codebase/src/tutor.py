import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pypdf import PdfReader
from docx import Document
from dotenv import load_dotenv

load_dotenv()

MAX_DOC_CHARS = 50_000

SYSTEM_PROMPT = (
    "Bạn là AI Tutor hỗ trợ học tập.\n"
    "Khi giải thích, luôn theo cấu trúc:\n"
    "1. Giải thích ngắn gọn\n"
    "2. Ví dụ code cụ thể (nếu áp dụng)\n"
    "3. Câu hỏi kiểm tra hiểu: \"Bạn có thể giải thích lại... không?\"\n"
    "Nếu câu hỏi mơ hồ → hỏi lại: \"Bạn đang bị stuck ở điểm nào cụ thể?\" trước khi giải thích.\n"
    "Trả lời bằng tiếng Việt. Dùng code block khi có code. /no_think"
)


def extract_text(file) -> str:
    name = file.name.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(file)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif name.endswith(".docx"):
        doc = Document(file)
        text = "\n".join(p.text for p in doc.paragraphs)
    elif name.endswith(".txt"):
        text = file.read().decode("utf-8", errors="replace")
    else:
        raise ValueError(f"Unsupported file type: {file.name}")
    return text[:MAX_DOC_CHARS]


def build_prompt(doc_context: str, history: list, question: str) -> tuple:
    system = SYSTEM_PROMPT
    if doc_context:
        system += f"\n\nTài liệu buổi học:\n{doc_context}"

    lines = []
    for msg in history:
        role = "Học viên" if msg["role"] == "user" else "AI Tutor"
        lines.append(f"{role}: {msg['content']}")
    lines.append(f"Học viên: {question}")

    return system, "\n".join(lines)


def _get_llm():
    return ChatOpenAI(
        model=os.getenv("CUSTOM_LLM_MODEL", "deepseek-v4-flash"),
        openai_api_key=os.getenv("CUSTOM_LLM_KEY"),
        openai_api_base=os.getenv("CUSTOM_LLM_URL"),
        temperature=0.3,
    )


def _call_llm(system_prompt: str, user_prompt: str) -> str:
    llm = _get_llm()
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    return llm.invoke(messages).content


def chat(doc_context: str, history: list, question: str) -> str:
    system, user_prompt = build_prompt(doc_context, history, question)
    return _call_llm(system, user_prompt)


def stream_chat(doc_context: str, history: list, question: str):
    system, user_prompt = build_prompt(doc_context, history, question)
    llm = _get_llm()
    messages = [SystemMessage(content=system), HumanMessage(content=user_prompt)]
    for chunk in llm.stream(messages):
        yield chunk.content


def summarize(doc_context: str) -> str:
    system = (
        "Bạn là AI Tutor hỗ trợ học tập. /no_think\n"
        "Tóm tắt tài liệu học tập ngắn gọn bằng tiếng Việt."
    )
    user = (
        "Tóm tắt tài liệu sau thành 4-6 gạch đầu dòng (bullet •), mỗi gạch 1-2 câu. "
        "Chỉ dùng bullet points, không dùng headers hay số thứ tự.\n\n"
        f"{doc_context[:8000]}"
    )
    return _call_llm(system, user)


def generate_quiz(doc_context: str) -> str:
    system = (
        "Bạn là AI Tutor hỗ trợ học tập. /no_think\n"
        "Tạo câu hỏi trắc nghiệm kiểm tra hiểu bài bằng tiếng Việt."
    )
    user = (
        "Tạo 5 câu hỏi trắc nghiệm từ tài liệu sau.\n"
        "Dùng CHÍNH XÁC format này cho mỗi câu (không thêm bớt):\n\n"
        "**Câu N:** [câu hỏi]\n"
        "A. [lựa chọn]\n"
        "B. [lựa chọn]\n"
        "C. [lựa chọn]\n"
        "D. [lựa chọn]\n"
        "✅ **Đáp án:** [A/B/C/D] — [giải thích ngắn 1 câu]\n\n"
        f"Tài liệu:\n{doc_context[:8000]}"
    )
    return _call_llm(system, user)


def generate_flashcards(doc_context: str) -> str:
    system = "Bạn là AI Tutor hỗ trợ học tập. /no_think"
    user = (
        "Tạo 5 flashcard từ tài liệu sau. Mỗi card gồm THUẬT NGỮ và GIẢI THÍCH.\n"
        "Dùng CHÍNH XÁC format này, mỗi card 1 dòng:\n"
        "CARD|||[thuật ngữ hoặc khái niệm ngắn]|||[giải thích 1-2 câu dễ hiểu]\n\n"
        f"Tài liệu:\n{doc_context[:8000]}"
    )
    return _call_llm(system, user)


def generate_objectives(doc_context: str) -> str:
    system = "Bạn là AI Tutor hỗ trợ học tập. /no_think"
    user = (
        "Dựa trên tài liệu sau, tạo 5 mục tiêu học tập cụ thể, có thể đo lường được (bằng tiếng Việt).\n"
        "Mỗi mục tiêu bắt đầu bằng động từ hành động: Giải thích / Áp dụng / Phân biệt / Xây dựng / Mô tả...\n"
        "Dùng CHÍNH XÁC format này, mỗi mục tiêu 1 dòng:\n"
        "OBJ|||[mục tiêu]\n\n"
        f"Tài liệu:\n{doc_context[:8000]}"
    )
    return _call_llm(system, user)


def generate_study_plan(doc_context: str) -> str:
    system = "Bạn là AI Tutor hỗ trợ học tập. /no_think"
    user = (
        "Dựa trên tài liệu sau, tạo lịch học 1 ngày bằng tiếng Việt.\n"
        "Tạo 4-5 khung giờ từ sáng đến tối, mỗi khung có 2-3 hoạt động cụ thể.\n"
        "Format CHÍNH XÁC:\n"
        "## ⏰ [Khung giờ] — [Tên buổi]\n"
        "- [hoạt động cụ thể]\n"
        "- [hoạt động cụ thể]\n\n"
        f"Tài liệu:\n{doc_context[:8000]}"
    )
    return _call_llm(system, user)
