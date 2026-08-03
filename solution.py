"""
solution.py — Tro toan bo repo ve DUNG goi code ca nhan cua tung thanh vien.

Van de can giai
---------------
Deliverable #1 la "Mỗi người": ca 4 nguoi deu phai TU viet lai `src/`. Neu bon
nguoi cung ghi de len `src/*.py` thi khong the lam viec chung tren mot repo.
Giai phap: moi nguoi mot thu muc rieng trong `src/`, dat theo MSSV-HoTen:

    src/
      chunking.py, store.py, agent.py, ...   <- ban goc cua de bai, GIU NGUYEN
      2A202601424-NguyenQuangHa/             <- Nguyen Quang Ha
      <MSSV>-<HoTen>/                        <- Thanh vien 2
      <MSSV>-<HoTen>/                        <- Thanh vien 3
      <MSSV>-<HoTen>/                        <- Thanh vien 4

File nay tu tim thu muc do va re-export cac ten can dung, nen `ingest.py`,
`bench.py`, `chunkers/`, `main.py` khong can biet thu muc cua ai.

Cach chon goi
-------------
1. Bien moi truong `LAB_SOLUTION_PACKAGE` neu duoc dat (uu tien cao nhat).
   Day cung la bien ma `tests/test_solution.py` dung, nen chay test va chay
   benchmark luon khop nhau:

       # PowerShell
       $env:LAB_SOLUTION_PACKAGE="src.2A202601424-NguyenQuangHa"
       python -m pytest tests -v
       python bench.py

2. Neu khong dat: tu do tim thu muc con duy nhat trong `src/` co `__init__.py`.
   Trong repo ca nhan (chi co mot thu muc) thi khong phai cau hinh gi ca.

3. Neu `src/` khong co thu muc con nao: quay ve dung `src` truc tiep (huu ich
   cho ai lam theo cach mac dinh cua de bai).
"""
from __future__ import annotations

import importlib
import os
from pathlib import Path

_ROOT = Path(__file__).parent
_SRC = _ROOT / "src"
_ENV_VAR = "LAB_SOLUTION_PACKAGE"


def _discover_package() -> str:
    """Tra ve ten goi (dang chuoi import) chua bai lam ca nhan."""
    override = os.getenv(_ENV_VAR, "").strip()
    if override:
        return override

    if _SRC.is_dir():
        candidates = sorted(
            path.name
            for path in _SRC.iterdir()
            if path.is_dir()
            and not path.name.startswith((".", "__"))
            and (path / "__init__.py").exists()
        )
        if len(candidates) == 1:
            return f"src.{candidates[0]}"
        if len(candidates) > 1:
            raise RuntimeError(
                f"Tim thay {len(candidates)} thu muc bai lam trong src/: {candidates}. "
                f"Hay dat bien moi truong {_ENV_VAR} de chon ro mot cai, vi du:\n"
                f'  $env:{_ENV_VAR}="src.{candidates[0]}"'
            )

    return "src"


PACKAGE_NAME = _discover_package()
_pkg = importlib.import_module(PACKAGE_NAME)

# --- Re-export -------------------------------------------------------------
Document = _pkg.Document

FixedSizeChunker = _pkg.FixedSizeChunker
SentenceChunker = _pkg.SentenceChunker
RecursiveChunker = _pkg.RecursiveChunker
ChunkingStrategyComparator = _pkg.ChunkingStrategyComparator
compute_similarity = _pkg.compute_similarity

EmbeddingStore = _pkg.EmbeddingStore
KnowledgeBaseAgent = _pkg.KnowledgeBaseAgent

MockEmbedder = _pkg.MockEmbedder
LocalEmbedder = _pkg.LocalEmbedder
OpenAIEmbedder = _pkg.OpenAIEmbedder
_mock_embed = _pkg._mock_embed
LOCAL_EMBEDDING_MODEL = _pkg.LOCAL_EMBEDDING_MODEL
OPENAI_EMBEDDING_MODEL = _pkg.OPENAI_EMBEDDING_MODEL
EMBEDDING_PROVIDER_ENV = _pkg.EMBEDDING_PROVIDER_ENV

__all__ = [
    "PACKAGE_NAME",
    "Document",
    "FixedSizeChunker",
    "SentenceChunker",
    "RecursiveChunker",
    "ChunkingStrategyComparator",
    "compute_similarity",
    "EmbeddingStore",
    "KnowledgeBaseAgent",
    "MockEmbedder",
    "LocalEmbedder",
    "OpenAIEmbedder",
    "_mock_embed",
    "LOCAL_EMBEDDING_MODEL",
    "OPENAI_EMBEDDING_MODEL",
    "EMBEDDING_PROVIDER_ENV",
]


if __name__ == "__main__":
    print(f"Dang dung goi bai lam: {PACKAGE_NAME}")
    try:
        SentenceChunker(max_sentences_per_chunk=2).chunk("A. B. C.")
        print("Trang thai: da implement, chay duoc.")
    except NotImplementedError:
        print("Trang thai: CHUA implement (con NotImplementedError).")
