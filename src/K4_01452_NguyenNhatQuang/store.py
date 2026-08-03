from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.

    Ghi chu trien khai (Nguyen Nhat Quang - K4_01452)
    ------------------------------------------------
    Chon nhanh IN-MEMORY (`_use_chroma = False`). De bai cho phep chon, va Phu
    luc A canh bao dung loi nay: neu dat `_use_chroma = True` khi nhanh Chroma
    chua hoan thien thi 14 test store se do du logic trong khong sai. In-memory
    con mot uu diem quan trong hon: MOI method deu di qua dung mot duong code
    (`self._store`), nen `search` va `search_with_filter` khong the lech nhau.

    Thu tu viet: hai helper truoc (`_make_record`, `_search_records`), bon
    method cong khai sau chi goi lai helper. Neu lam nguoc lai se phai lap cung
    mot doan logic tinh diem bon lan.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        # Khong bat ChromaDB. Xem docstring ben tren.
        self._use_chroma = False

    # ------------------------------------------------------------------
    # Helper 1 — chuan hoa Document thanh record luu trong store
    # ------------------------------------------------------------------
    def _make_record(self, doc: Document) -> dict[str, Any]:
        """Tra ve mot dict nhat quan cho mot Document.

        Ba dieu bat buoc theo de bai (muc 4.1):

        1. COPY `metadata` chu khong dung thang object cua nguoi goi. Neu dung
           thang, `ingest.py` sua dict metadata sau khi add se lam hong du lieu
           da nam trong store.
        2. `metadata` PHAI co `doc_id`, vi `delete_document()` xoa theo chinh
           `metadata['doc_id']`. Test tao `Document(..., metadata={})` nen phai
           `setdefault` bang `doc.id`.
        3. Ghep `doc.id` voi `self._next_index` de id khong trung khi cung mot
           file duoc nap hai lan.
        """
        metadata = dict(doc.metadata) if doc.metadata else {}
        metadata.setdefault("doc_id", doc.id)

        return {
            "id": f"{doc.id}#{self._next_index}",
            "content": doc.content,
            "metadata": metadata,
            "embedding": self._embedding_fn(doc.content),
        }

    # ------------------------------------------------------------------
    # Helper 2 — xep hang MOT TAP RECORD BAT KY (khong nhat thiet la ca store)
    # ------------------------------------------------------------------
    def _search_records(
        self, query: str, records: list[dict[str, Any]], top_k: int
    ) -> list[dict[str, Any]]:
        """Tinh diem, sort giam dan, cat top_k.

        Nho tham so `records` ma `search_with_filter` tai su dung duoc nguyen
        ham nay sau khi da loc — khong phai viet lai vong lap tinh diem.
        """
        if not records or top_k <= 0:
            return []

        # Embed query DUNG MOT LAN, o ngoai vong lap.
        query_vector = self._embedding_fn(query)

        scored: list[dict[str, Any]] = []
        for record in records:
            scored.append(
                {
                    "id": record["id"],
                    "content": record["content"],
                    "metadata": record["metadata"],
                    "score": _dot(query_vector, record["embedding"]),
                }
            )

        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]

    # ------------------------------------------------------------------
    # API cong khai
    # ------------------------------------------------------------------
    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        if not docs:
            # docs rong -> return binh thuong, KHONG raise.
            return

        for doc in docs:
            self._store.append(self._make_record(doc))
            self._next_index += 1

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        return len(self._store)

    def search_with_filter(
        self, query: str, top_k: int = 3, metadata_filter: dict = None
    ) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.

        FILTER TRUOC, RANK SAU — day la diem chinh cua Task 5.
        Lam nguoc lai (lay top-k roi bo cai khong khop) co the tra ve 0 ket qua
        du store van con tai lieu hop le: vi du 3 chunk `customer_role=seller`
        chiem het top-3, loc `buyer` xong thi con list rong.
        """
        if not metadata_filter:
            # Khong co filter -> hanh vi phai TRUNG KHOP `search()` cung top_k.
            # Ca hai deu di qua `_search_records` nen khong the lech nhau.
            return self._search_records(query, self._store, top_k)

        candidates = [
            record for record in self._store if self._matches(record, metadata_filter)
        ]
        return self._search_records(query, candidates, top_k)

    @staticmethod
    def _matches(record: dict[str, Any], metadata_filter: dict) -> bool:
        """Record chi di tiep khi MOI cap key/value duoc yeu cau deu khop.

        So sanh BANG NHAU tuyet doi, khong phai tim keyword. `{"customer_role":
        "buyer"}` chi giu document co metadata dung bang gia tri do; embedding
        moi la thu quyet dinh thu tu trong nhom con lai.
        """
        metadata = record.get("metadata") or {}
        return all(metadata.get(key) == value for key, value in metadata_filter.items())

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        before = len(self._store)
        self._store = [
            record
            for record in self._store
            if (record.get("metadata") or {}).get("doc_id") != doc_id
        ]
        return len(self._store) < before
