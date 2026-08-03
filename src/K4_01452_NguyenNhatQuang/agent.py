from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.

    Ghi chu trien khai (Nguyen Nhat Quang - K4_01452)
    ------------------------------------------------
    Agent KHONG tu tinh embedding. Toan bo viec do da nam trong `EmbeddingStore`
    o Task 4/5; agent chi noi ket qua retrieve vao prompt. Neu agent tu embed
    lai thi se co hai duong code tinh diem va rat de lech nhau.
    """

    #: Store rong -> tra thong bao ro rang thay vi goi LLM vo ich (va ton tien).
    NO_CONTEXT_MESSAGE = (
        "Khong co tai lieu nao trong knowledge base nen chua du thong tin de tra loi."
    )

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            return self.NO_CONTEXT_MESSAGE

        return self.llm_fn(self.build_prompt(question, results))

    # ------------------------------------------------------------------
    # Hai helper duoi day khong nam trong contract cua 42 test, nhung `bench.py`
    # goi lai duoc de in ra dung prompt ma agent da dung — khong phai copy code.
    # ------------------------------------------------------------------
    def format_context(self, results: list[dict]) -> str:
        """Danh so [1], [2]... kem `doc_id` va `chunk_index`.

        Day la phan dang dau tu nhat cua Task 6: nho no ma khi cau tra loi sai,
        ta truy nguoc duoc ngay agent da duoc cho an chunk nao cua file nao.
        Do chinh la tieu chi grounding trong `docs/EVALUATION.md`.
        """
        blocks = []
        for index, result in enumerate(results, start=1):
            metadata = result.get("metadata") or {}
            doc_id = metadata.get("doc_id", "unknown")
            chunk_index = metadata.get("chunk_index")
            source = metadata.get("source_url") or metadata.get("source") or "n/a"
            label = doc_id if chunk_index is None else f"{doc_id}::chunk_{chunk_index}"
            blocks.append(
                f"[{index}] (nguon: {label} | url: {source})\n{result.get('content', '')}"
            )
        return "\n\n".join(blocks)

    def build_prompt(self, question: str, results: list[dict]) -> str:
        """Prompt gom 4 phan: instruction -> context da danh so -> question -> 'Answer:'."""
        return (
            "Instruction: Ban la tro ly tra loi dua tren tai lieu. CHI dung thong tin "
            "trong phan Context ben duoi, khong suy dien them. Moi y phai trich dan so "
            "hieu nguon dang [1], [2]. Neu Context khong du de tra loi, hay noi ro la "
            "khong du thong tin thay vi doan.\n\n"
            f"Context:\n{self.format_context(results)}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )
