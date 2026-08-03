from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        # Không tách sau chữ viết tắt và trong số thập phân
        abbreviations = r"(TS|ThS|GS|PGS|Mr|Mrs|Ms|Dr|Prof)"
        protected = re.sub(
            rf"\b{abbreviations}\.",
            lambda m: m.group(0).replace(".", "<DOT>"),
            text.strip(),
        )
        protected = re.sub(r"(?<=\d)\.(?=\d)", "<DOT>", protected)

        # Tách câu, kể cả khi có dấu nháy hoặc ngoặc đóng
        protected = re.sub(
            r'([.!?]+["”’)\]]*)\s+',
            r"\1<SPLIT>",
            protected,
        )

        sentences = [
            sentence.replace("<DOT>", ".").strip()
            for sentence in protected.split("<SPLIT>")
            if sentence.strip()
        ]

        return [
            " ".join(sentences[i:i + self.max_sentences_per_chunk])
            for i in range(0, len(sentences), self.max_sentences_per_chunk)
        ]


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
            # Nếu text trống hoặc chỉ chứa khoảng trắng, trả về danh sách rỗng
            if not text or not text.strip():
                return []
            #  Nếu chunk_size <= 0, ném ra ValueError
            if self.chunk_size <= 0:
                raise ValueError("chunk_size must be greater than zero")
            return self._split(text.strip(), self.separators)
    
    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # Nếu current_text ngắn hơn hoặc bằng chunk_size, trả về danh sách chứa current_text
        if len(current_text) <= self.chunk_size:
            return [current_text]
        if not remaining_separators:
            return [
                current_text[start : start + self.chunk_size]
                for start in range(0, len(current_text), self.chunk_size)
            ]

        # Lấy separator đầu tiên từ remaining_separators và gọi đệ quy với phần còn lại
        separator, *later_separators = remaining_separators
        if separator == "":
            return [
                current_text[start : start + self.chunk_size]
                for start in range(0, len(current_text), self.chunk_size)
            ]
        if separator not in current_text:
            return self._split(current_text, later_separators)

        # Tách current_text thành các phần dựa trên separator, loại bỏ các phần rỗng và khoảng trắng
        #  Lặp qua từng phần, nếu phần đó dài hơn chunk_size, gọi đệ quy để tách nó tiếp
        #  Nếu phần đó cộng với pending dài hơn chunk_size, thêm pending vào chunks và đặt pending = phần hiện tại
        #  Nếu không, cộng phần đó vào pending
        pieces = [piece.strip() for piece in current_text.split(separator) if piece.strip()]
        chunks: list[str] = []
        pending = ""

        for piece in pieces:
            if len(piece) > self.chunk_size:
                if pending:
                    chunks.append(pending)
                    pending = ""
                chunks.extend(self._split(piece, later_separators))
                continue

            candidate = piece if not pending else pending + separator + piece
            if len(candidate) <= self.chunk_size:
                pending = candidate
            else:
                chunks.append(pending)
                pending = piece

        if pending:
            chunks.append(pending)
        return chunks

def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    magnitude_a = math.sqrt(_dot(vec_a, vec_a))
    magnitude_b = math.sqrt(_dot(vec_b, vec_b))
    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0
    return _dot(vec_a, vec_b) / (magnitude_a * magnitude_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
            if chunk_size <= 0:
                raise ValueError("chunk_size must be greater than zero")
    
            overlap = min(50, max(0, chunk_size - 1))
            # Tạo một từ điển results chứa kết quả của ba chiến lược chunking khác nhau: FixedSizeChunker, SentenceChunker và RecursiveChunker
            results = {
                "fixed_size": FixedSizeChunker(chunk_size, overlap).chunk(text),
                "by_sentences": SentenceChunker().chunk(text),
                "recursive": RecursiveChunker(chunk_size=chunk_size).chunk(text),
            }
    
            # Tạo một từ điển comparison chứa thông tin so sánh về số lượng chunk, độ dài trung bình của chunk và danh sách các chunk cho từng chiến lược chunking
            comparison: dict = {}
            for name, chunks in results.items():
                comparison[name] = {
                    "count": len(chunks),
                    "avg_length": (
                        sum(len(chunk) for chunk in chunks) / len(chunks) if chunks else 0.0
                    ),
                    "chunks": chunks,
                }
            return comparison
