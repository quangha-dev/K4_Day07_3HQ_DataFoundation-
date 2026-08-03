"""Real-embedding retrieval service used by the isolated Streamlit demo."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import time
from typing import Any, Iterable

import numpy as np

from demo.strategy_registry import get_strategy


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "k4_ecommerce"
DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
TEXT_EXTENSIONS = {".md", ".txt"}


@dataclass(frozen=True)
class SourceDocument:
    doc_id: str
    content: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class ChunkRecord:
    id: str
    content: str
    metadata: dict[str, Any]


@dataclass
class RetrievalIndex:
    strategy_key: str
    model_name: str
    records: list[ChunkRecord]
    embeddings: np.ndarray
    build_seconds: float

    @property
    def chunk_count(self) -> int:
        return len(self.records)


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    closing = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if closing is None:
        return {}, text
    metadata: dict[str, str] = {}
    for raw in lines[1:closing]:
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        metadata[key.strip()] = value.split(" #", 1)[0].strip().strip('"').strip("'")
    return metadata, "\n".join(lines[closing + 1 :]).lstrip("\n")


def load_corpus(data_dir: Path = DATA_DIR) -> list[SourceDocument]:
    documents: list[SourceDocument] = []
    for path in sorted(data_dir.iterdir()):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        metadata, body = parse_front_matter(path.read_text(encoding="utf-8"))
        doc_id = metadata.get("doc_id", path.stem)
        metadata.setdefault("doc_id", doc_id)
        metadata.setdefault("source", str(path.relative_to(PROJECT_ROOT)))
        documents.append(SourceDocument(doc_id=doc_id, content=body, metadata=metadata))
    return documents


def chunk_corpus(strategy_key: str, documents: Iterable[SourceDocument]) -> list[ChunkRecord]:
    chunker = get_strategy(strategy_key).factory()
    records: list[ChunkRecord] = []
    for document in documents:
        for index, piece in enumerate(chunker.chunk(document.content)):
            content = piece.strip()
            if not content:
                continue
            metadata = dict(document.metadata)
            metadata["chunk_index"] = index
            records.append(
                ChunkRecord(
                    id=f"{document.doc_id}::chunk_{index}",
                    content=content,
                    metadata=metadata,
                )
            )
    return records


def load_embedding_model(model_name: str = DEFAULT_MODEL):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def build_index(strategy_key: str, model, model_name: str = DEFAULT_MODEL) -> RetrievalIndex:
    started = time.perf_counter()
    records = chunk_corpus(strategy_key, load_corpus())
    vectors = model.encode(
        [record.content for record in records],
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True,
    )
    return RetrievalIndex(
        strategy_key=strategy_key,
        model_name=model_name,
        records=records,
        embeddings=np.asarray(vectors, dtype=np.float32),
        build_seconds=time.perf_counter() - started,
    )


def retrieve(
    index: RetrievalIndex,
    model,
    question: str,
    top_k: int = 3,
    customer_role: str | None = None,
) -> list[dict[str, Any]]:
    if not question.strip() or top_k <= 0 or not index.records:
        return []
    candidate_indices = [
        i
        for i, record in enumerate(index.records)
        if customer_role is None or record.metadata.get("customer_role") == customer_role
    ]
    if not candidate_indices:
        return []
    query = model.encode(
        [question], normalize_embeddings=True, show_progress_bar=False, convert_to_numpy=True
    )[0]
    scores = index.embeddings[candidate_indices] @ query
    order = np.argsort(scores)[::-1][:top_k]
    results: list[dict[str, Any]] = []
    for rank, offset in enumerate(order, start=1):
        record_index = candidate_indices[int(offset)]
        record = index.records[record_index]
        results.append(
            {
                "rank": rank,
                "id": record.id,
                "content": record.content,
                "metadata": record.metadata,
                "score": float(scores[int(offset)]),
            }
        )
    return results


_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


def grounded_extractive_answer(model, question: str, results: list[dict[str, Any]]) -> str:
    """Create a concise offline answer from retrieved text, with citations.

    This is intentionally extractive: it cannot invent an answer that is absent
    from retrieval, making it suitable for a classroom grounding demo.
    """
    candidates: list[tuple[str, int]] = []
    for result in results:
        for sentence in _SENTENCE_SPLIT.split(result["content"]):
            clean = sentence.strip(" -\t")
            if len(clean) >= 30:
                candidates.append((clean, int(result["rank"])))
    if not candidates:
        return "Không đủ ngữ cảnh được truy xuất để tạo câu trả lời."
    sentence_vectors = model.encode(
        [item[0] for item in candidates],
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True,
    )
    query_vector = model.encode(
        [question], normalize_embeddings=True, show_progress_bar=False, convert_to_numpy=True
    )[0]
    order = np.argsort(sentence_vectors @ query_vector)[::-1]
    selected: list[str] = []
    seen: set[str] = set()
    for index in order:
        sentence, rank = candidates[int(index)]
        signature = sentence.lower()
        if signature in seen:
            continue
        selected.append(f"{sentence} [{rank}]")
        seen.add(signature)
        if len(selected) == 3:
            break
    return " ".join(selected)


def records_for_document(index: RetrievalIndex, doc_id: str) -> list[ChunkRecord]:
    return [record for record in index.records if record.metadata.get("doc_id") == doc_id]

