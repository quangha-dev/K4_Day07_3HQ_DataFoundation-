from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """

    NO_CONTEXT_MESSAGE = (
        "Khong tim thay tai lieu nao trong knowledge base de tra loi cau hoi nay."
    )
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            return self.NO_CONTEXT_MESSAGE

        return self.llm_fn(self.build_prompt(question, results))

    def format_context(self, results: list[dict]) -> str:
        context = []
        for index, result in enumerate(results, start=1):
            metadata = result.get("metadata", {}) or {}
            doc_id = metadata.get("doc_id", "unknown")
            chunk_index = metadata.get("chunk_index")
            label = doc_id if chunk_index is None else f"{doc_id}::chunk_{chunk_index}"
            source = metadata.get("source_url") or metadata.get("source") or "n/a"
            context.append(
                f"[{index}] (nguon: {label} | url: {source})\n{result.get('content', '')}"
            )
        return "\n\n".join(context)

    def build_prompt(self, question: str, results: list[dict]) -> str:
        context = self.format_context(results)
        return (
            "Instruction: Chi dung thong tin trong Context de tra loi. "
            "Neu Context khong du, hay noi ro khong du thong tin.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\nAnswer:"
        )
