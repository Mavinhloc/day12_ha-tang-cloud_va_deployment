import io
import pytest
from unittest.mock import MagicMock, patch
from src.tutor import extract_text, build_prompt, MAX_DOC_CHARS


class MockFile:
    """Mimics a Streamlit UploadedFile object."""
    def __init__(self, name: str, content: bytes):
        self.name = name
        self._buf = io.BytesIO(content)

    def read(self):
        return self._buf.read()

    def seek(self, pos):
        self._buf.seek(pos)

    def tell(self):
        return self._buf.tell()


# --- extract_text ---

def test_extract_text_txt():
    f = MockFile("notes.txt", "Hello world\nSecond line".encode("utf-8"))
    assert extract_text(f) == "Hello world\nSecond line"


def test_extract_text_txt_unicode():
    f = MockFile("notes.txt", "Xin chào thế giới".encode("utf-8"))
    assert extract_text(f) == "Xin chào thế giới"


def test_extract_text_pdf():
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "PDF page content"
    with patch("src.tutor.PdfReader") as MockPdfReader:
        MockPdfReader.return_value.pages = [mock_page]
        f = MockFile("slides.pdf", b"")
        result = extract_text(f)
    assert result == "PDF page content"


def test_extract_text_pdf_multiple_pages():
    pages = [MagicMock(), MagicMock()]
    pages[0].extract_text.return_value = "Page 1"
    pages[1].extract_text.return_value = "Page 2"
    with patch("src.tutor.PdfReader") as MockPdfReader:
        MockPdfReader.return_value.pages = pages
        f = MockFile("slides.pdf", b"")
        result = extract_text(f)
    assert "Page 1" in result
    assert "Page 2" in result


def test_extract_text_pdf_none_page():
    page = MagicMock()
    page.extract_text.return_value = None
    with patch("src.tutor.PdfReader") as MockPdfReader:
        MockPdfReader.return_value.pages = [page]
        assert extract_text(MockFile("doc.pdf", b"")) == ""


def test_extract_text_docx():
    mock_para = MagicMock()
    mock_para.text = "DOCX paragraph content"
    with patch("src.tutor.Document") as MockDocument:
        MockDocument.return_value.paragraphs = [mock_para]
        f = MockFile("notes.docx", b"")
        result = extract_text(f)
    assert result == "DOCX paragraph content"


def test_extract_text_unknown_format_raises():
    f = MockFile("slides.pptx", b"some content")
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text(f)


def test_extract_text_truncates_long_file():
    long_text = "x" * (MAX_DOC_CHARS + 1000)
    f = MockFile("notes.txt", long_text.encode("utf-8"))
    result = extract_text(f)
    assert len(result) == MAX_DOC_CHARS


# --- build_prompt ---

def test_build_prompt_includes_question():
    _, user = build_prompt("", [], "Giải thích LangChain")
    assert "Giải thích LangChain" in user


def test_build_prompt_includes_doc_context_in_system():
    system, _ = build_prompt("Đây là tài liệu buổi học", [], "hỏi gì đó")
    assert "Đây là tài liệu buổi học" in system


def test_build_prompt_no_doc_context_excludes_section():
    system, _ = build_prompt("", [], "hỏi gì đó")
    assert "Tài liệu buổi học" not in system


def test_build_prompt_includes_history():
    history = [
        {"role": "user", "content": "Agents là gì?"},
        {"role": "assistant", "content": "Agents là các thực thể tự trị..."},
    ]
    _, user = build_prompt("", history, "Câu tiếp theo")
    assert "Agents là gì?" in user
    assert "Agents là các thực thể tự trị" in user
    assert "Câu tiếp theo" in user


def test_build_prompt_returns_tuple_of_two_strings():
    result = build_prompt("", [], "câu hỏi")
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert all(isinstance(s, str) for s in result)
