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
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        # Lab cho phep chon in-memory hoac ChromaDB, test khong yeu cau ben nao.
        # Chon in-memory: deterministic, khong phu thuoc I/O, va quan trong nhat
        # la MOI method deu di qua dung mot duong code (_store). Neu de
        # _use_chroma = True ma nhanh Chroma chua hoan thien thi test store se
        # fail du logic trong khong sai (xem Phu luc A cua de bai).
        self._use_chroma = False
        self._collection = None

    # ------------------------------------------------------------------
    # Hai helper viet TRUOC, bon method cong khai ben duoi chi goi lai.
    # Lam nguoc lai se phai lap cung mot logic bon lan.
    # ------------------------------------------------------------------
    def _make_record(self, doc: Document) -> dict[str, Any]:
        """Chuan hoa mot Document thanh mot record luu trong store."""
        # (1) COPY metadata thay vi dung thang object cua nguoi goi, de khong
        #     sua nham du lieu ben ngoai.
        metadata = dict(doc.metadata or {})

        # (2) metadata PHAI co doc_id — delete_document() dua vao chinh no.
        #     Test tao Document voi metadata rong {} nen phai setdefault.
        metadata.setdefault("doc_id", doc.id)

        return {
            # (3) Ghep doc.id voi _next_index de id khong trung khi them nhieu
            #     document (vd. cung mot file duoc nap hai lan).
            "id": f"{doc.id}#{self._next_index}",
            "doc_id": metadata["doc_id"],
            "content": doc.content,
            "metadata": metadata,
            "embedding": self._embedding_fn(doc.content),
        }

    def _search_records(
        self, query: str, records: list[dict[str, Any]], top_k: int
    ) -> list[dict[str, Any]]:
        """Xep hang mot tap record bat ky theo do tuong dong voi query."""
        if not records or top_k <= 0:
            return []

        # Embed query MOT lan, khong goi lai trong vong lap.
        query_vector = self._embedding_fn(query)

        scored = [
            {
                "id": record["id"],
                "content": record["content"],
                "metadata": record["metadata"],
                "score": _dot(query_vector, record["embedding"]),
            }
            for record in records
        ]
        # Sap xep giam dan roi cat top_k.
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
        # docs rong -> return binh thuong, khong raise.
        if not docs:
            return
        for doc in docs:
            record = self._make_record(doc)
            self._next_index += 1
            self._store.append(record)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        # Khong co filter -> hanh vi phai TRUNG KHOP voi search() cung top_k.
        # Vi ca hai deu goi _search_records nen khong the lech nhau.
        if not metadata_filter:
            return self._search_records(query, self._store, top_k)

        # FILTER TRUOC, RANK SAU.
        # Lam nguoc lai (lay top-k roi loai cai khong khop) co the tra ve 0 ket
        # qua du store van con tai lieu hop le — vd. 3 chunk 'seller' chiem het
        # top-3, loc 'buyer' xong con rong.
        candidates = [
            record
            for record in self._store
            if all(
                record["metadata"].get(key) == value
                for key, value in metadata_filter.items()
            )
        ]
        return self._search_records(query, candidates, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        remaining = [
            record for record in self._store if record["metadata"].get("doc_id") != doc_id
        ]
        removed = len(self._store) - len(remaining)
        self._store = remaining
        return removed > 0
