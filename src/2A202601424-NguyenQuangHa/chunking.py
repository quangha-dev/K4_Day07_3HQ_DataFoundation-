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

    # Cat tai khoang trang DUNG SAU dau ket cau.
    # Lookbehind (?<=[.!?]) chi "nhin lai" de xac nhan co dau cau, KHONG nuot no,
    # nen dau cham van nam lai o cuoi cau truoc. Neu viet [.!?]\s+ thi dau cau bi
    # an mat va cac cau ghep lai se dinh vao nhau.
    _SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        # Buoc 1: text rong -> tra list rong (khong phai [""]).
        if not text:
            return []

        # Buoc 2 + 3: tach cau, strip tung cau, bo phan rong.
        sentences = [
            sentence.strip()
            for sentence in self._SENTENCE_BOUNDARY.split(text)
            if sentence.strip()
        ]
        if not sentences:
            return []

        # Buoc 4 + 5: gom tung nhom `limit` cau, ghep bang mot dau cach.
        limit = self.max_sentences_per_chunk
        return [
            " ".join(sentences[index : index + limit])
            for index in range(0, len(sentences), limit)
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
        """Vo ngoai: xu ly text rong, goi de quy, roi don dep ket qua."""
        if not text:
            return []
        pieces = self._split(text, list(self.separators))
        return [piece.strip() for piece in pieces if piece and piece.strip()]

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        """Phan de quy. Moi lan goi lai PHAI hoac bot separator hoac thu nho text."""
        # Base case 1: da du ngan -> tra ve nguyen.
        if len(current_text) <= self.chunk_size:
            return [current_text]

        # Base case 2: het separator -> cat cung theo chunk_size.
        if not remaining_separators:
            return self._hard_split(current_text)

        separator = remaining_separators[0]
        rest = remaining_separators[1:]

        # Separator rong "" cung la tin hieu cat cung (muc uu tien thap nhat).
        if separator == "":
            return self._hard_split(current_text)

        # Separator khong xuat hien trong text -> ha xuong muc uu tien thap hon.
        if separator not in current_text:
            return self._split(current_text, rest)

        # Cat duoc: gom cac phan lien nhau cho toi truoc khi vuot chunk_size.
        # Bo buoc gom nay la loi pho bien nhat -> sinh ra hang loat chunk vun.
        chunks: list[str] = []
        buffer = ""
        for part in current_text.split(separator):
            candidate = part if not buffer else buffer + separator + part
            if len(candidate) <= self.chunk_size:
                buffer = candidate
                continue

            if buffer:
                chunks.append(buffer)
                buffer = ""

            if len(part) > self.chunk_size:
                # Mot manh don le van qua dai -> xu ly bang separator uu tien thap hon.
                chunks.extend(self._split(part, rest))
            else:
                buffer = part

        if buffer:
            chunks.append(buffer)
        return chunks

    def _hard_split(self, text: str) -> list[str]:
        """Cat co dinh theo chunk_size, khong quan tam ranh gioi ngu nghia."""
        size = max(1, self.chunk_size)
        return [text[index : index + size] for index in range(0, len(text), size)]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    # norm(v) = sqrt(dot(v, v)) — dung lai _dot co san.
    norm_a = math.sqrt(_dot(vec_a, vec_a))
    norm_b = math.sqrt(_dot(vec_b, vec_b))

    # Chan chia cho 0 TRUOC khi chia.
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    # Giong het -> 1 | vuong goc -> 0 | nguoc huong -> -1
    return _dot(vec_a, vec_b) / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        # Ba key PHAI dung ten nay, test so tung ky tu.
        runs = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=0).chunk(text),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3).chunk(text),
            "recursive": RecursiveChunker(chunk_size=chunk_size).chunk(text),
        }

        comparison: dict = {}
        for name, chunks in runs.items():
            count = len(chunks)
            total_length = sum(len(chunk) for chunk in chunks)
            comparison[name] = {
                "count": count,
                # Text rong -> count = 0 -> phai chan truoc khi chia.
                "avg_length": (total_length / count) if count else 0.0,
                "chunks": chunks,
            }
        return comparison
