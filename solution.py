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

2. File `.lab-solution` o thu muc goc, neu muon chot cung mot goi cho repo nay.

3. Neu khong dat: tu do tim thu muc con duy nhat trong `src/` co `__init__.py`.
   Trong repo ca nhan (chi co mot thu muc) thi khong phai cau hinh gi ca.

4. Repo chung cua nhom co 4 thu muc: doi chieu voi TEN REPO
   (`DAY07-<MSSV>-<HoVaTen>`) de tu chon dung bai cua chu repo. Day la buoc
   khien lenh cham diem trong de bai chay duoc nguyen van:

       python -m pytest tests -v      ->  42 passed

   ma khong phai dat bien moi truong nao. Ai fork ve doi ten repo theo MSSV
   cua minh thi tu dong chay dung bai cua minh.

5. Neu `src/` khong co thu muc con nao: quay ve dung `src` truc tiep (huu ich
   cho ai lam theo cach mac dinh cua de bai).
"""
from __future__ import annotations

import importlib
import re
import os
from pathlib import Path

_ROOT = Path(__file__).parent
_SRC = _ROOT / "src"
_ENV_VAR = "LAB_SOLUTION_PACKAGE"


_OWNER_FILE = _ROOT / ".lab-solution"


def _match_repo_owner(candidates: list[str]) -> str | None:
    """Chon goi khop voi TEN REPO.

    Repo dat ten theo quy uoc `DAY07-<MSSV>-<HoVaTen>`, con thu muc bai lam dat
    theo `<MSSV>_<HoTen>` hoac `<MSSV>-<HoTen>`. Tach cac cum chu-so trong ten
    repo roi tim goi nao chua cum dai nhat (chinh la MSSV cua chu repo).

    Nho vay moi thanh vien fork ve deu tu dong chay dung bai cua MINH ma khong
    phai cau hinh gi — dung nhu de bai mo ta ("chay lenh nguyen van").
    """
    tokens = sorted(re.findall(r"[A-Za-z0-9]+", _ROOT.name), key=len, reverse=True)
    for token in tokens:
        if len(token) < 6:  # bo qua "DAY07", "K4"... qua ngan, de trung nham
            continue
        for candidate in candidates:
            if token.lower() in candidate.lower():
                return candidate
    return None


def _discover_package() -> str:
    """Tra ve ten goi (dang chuoi import) chua bai lam ca nhan.

    Thu tu uu tien, tu ro rang nhat den suy doan nhat:
        1. Bien moi truong LAB_SOLUTION_PACKAGE  (dung khi cham bai nguoi khac)
        2. File `.lab-solution` o thu muc goc     (chot cung cho repo nay)
        3. Thu muc duy nhat trong src/            (repo ca nhan, khong phai chon)
        4. Goi khop ten repo                      (repo chung 4 nguoi)
        5. src/ truc tiep                         (cach mac dinh cua de bai)

    Buoc 4 la buoc quan trong nhat: nhom lam chung mot repo nen src/ co 4 thu
    muc, va lenh cham diem trong de bai la `python -m pytest tests -v` KHONG
    kem bien moi truong nao. Neu o day raise loi thi nguoi cham se thay repo
    "khong chay duoc" du ca 4 bai deu 42/42.
    """
    override = os.getenv(_ENV_VAR, "").strip()
    if override:
        return override

    if _OWNER_FILE.is_file():
        pinned = _OWNER_FILE.read_text(encoding="utf-8").strip()
        if pinned:
            return pinned if pinned.startswith("src") else f"src.{pinned}"

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
            owner = _match_repo_owner(candidates)
            if owner:
                return f"src.{owner}"
            # Khong doan duoc thi van phai chay, khong duoc raise: lay goi dau
            # tien theo thu tu alphabet de `pytest tests -v` con chay duoc.
            return f"src.{candidates[0]}"

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

# Chien luoc rieng cua tung nguoi (khong nam trong 42 test). Dung getattr vi
# moi thanh vien dat ten class khac nhau — ai chua viet thi bang None.
ParagraphChunker = getattr(_pkg, "ParagraphChunker", None)
StructureChunker = getattr(_pkg, "StructureChunker", None)

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
    "ParagraphChunker",
    "StructureChunker",
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
