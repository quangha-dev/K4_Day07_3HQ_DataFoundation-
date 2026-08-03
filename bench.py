"""
bench.py — Benchmark retrieval cho Lab 07 (K4 · corpus phap luat TMDT Viet Nam).

Cach chay:
    python bench.py                    # strategy ca nhan cua toi (paragraph)
    python bench.py recursive          # mot strategy khac de doi chieu
    python bench.py --all              # chay het, in bang so sanh cuoi cung
    python bench.py --all > report/bench_output_lexical.txt

    # Windows PowerShell — dung embedder co nghia (khuyen dung):
    $env:EMBEDDING_PROVIDER="lexical"; python bench.py --all

Ba buoc theo dung mo ta cua de bai:
    1. Chon chunker cua rieng minh  -> bien MY_STRATEGY + registry STRATEGIES
    2. Nap corpus                   -> ingest.build_knowledge_base(...)
    3. Chay 5 query, in top-3       -> run_strategy(...)

DONG DUY NHAT khac giua cac thanh vien la dong chon chunker. Corpus, 5 query,
embedder, cach cham diem deu chung — co vay bang so sanh moi cong bang.
"""
from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

from benchmark_queries import BENCHMARK_QUERIES
from ingest import build_knowledge_base
from solution import (
    EMBEDDING_PROVIDER_ENV,
    LOCAL_EMBEDDING_MODEL,
    OPENAI_EMBEDDING_MODEL,
    FixedSizeChunker,
    KnowledgeBaseAgent,
    LocalEmbedder,
    OpenAIEmbedder,
    ParagraphChunker,
    RecursiveChunker,
    SentenceChunker,
    _mock_embed,
)

DATA_DIR = os.getenv("LAB_DATA_DIR", "data/k4_ecommerce")
TOP_K = 3

# ---------------------------------------------------------------------------
# BUOC 1 — CHON CHUNKER.
# Day la phan DUY NHAT khac giua cac thanh vien trong nhom.
#
# `paragraph` la chien luoc tu viet cua toi, nam trong
# `src/2A202601424-NguyenQuangHa/chunking.py`. Ba dong con lai la baseline co
# san trong starter code, giu de doi chieu.
# ---------------------------------------------------------------------------
STRATEGIES = {
    # <<< STRATEGY CA NHAN CUA TOI (Nguyen Quang Ha - 2A202601424) >>>
    "paragraph": lambda: ParagraphChunker(max_chunk_size=700, min_chunk_size=450),
    # Ablation 1: tat buoc gan tieu de -> do xem buoc do dong gop bao nhieu.
    "paragraph_noheading": lambda: ParagraphChunker(
        max_chunk_size=700, min_chunk_size=450, keep_heading=False
    ),
    # Ablation 2: khong gop doan ngan -> moi doan la mot chunk, dung nguyen ban.
    "paragraph_nomerge": lambda: ParagraphChunker(
        max_chunk_size=700, min_chunk_size=0
    ),
    # Baseline co san trong src/, khong phai cua ai ca.
    "fixed": lambda: FixedSizeChunker(chunk_size=500, overlap=50),
    "recursive": lambda: RecursiveChunker(chunk_size=400),
    "sentence": lambda: SentenceChunker(max_sentences_per_chunk=3),
}

MY_STRATEGY = "paragraph"


# ---------------------------------------------------------------------------
def _make_llm_fn():
    """Tra ve ham LLM that neu co OPENAI_API_KEY, khong thi tra None (-> fallback)."""
    load_dotenv(override=False)
    if not os.getenv("OPENAI_API_KEY"):
        return None
    try:
        from openai import OpenAI

        client = OpenAI()
        model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

        def _call(prompt: str) -> str:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            return response.choices[0].message.content or ""

        return _call
    except Exception:
        return None


def select_embedder():
    """mock (mac dinh) | lexical | local | openai.

    `lexical` la backend TF-IDF tu viet (lexical_embedding.py): khong can
    PyTorch, khong can API key, nhung score co y nghia hon mock rat nhieu.
    Dat EMBEDDING_PROVIDER=lexical trong .env hoac bien moi truong.
    """
    load_dotenv(override=False)
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "mock").strip().lower()
    if provider == "lexical":
        from lexical_embedding import LexicalEmbedder

        return LexicalEmbedder(DATA_DIR)
    if provider == "local":
        try:
            return LocalEmbedder(model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL))
        except Exception:
            print("[!] Local embedder khong san sang; dung mock.")
    elif provider == "openai":
        try:
            return OpenAIEmbedder(model_name=os.getenv("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL))
        except Exception:
            print("[!] OpenAI embedder khong san sang; dung mock.")
    return _mock_embed


def demo_llm(prompt: str) -> str:
    """LLM gia: tra lai chinh context da retrieve, de kiem tra grounding.

    Khong co API key nen khong sinh chu moi. Tra ve dong dau cua tung chunk
    de nhin thay agent thuc su duoc cho an nhung gi.
    """
    context = prompt.split("Context:", 1)[-1].split("Question:", 1)[0].strip()
    heads = [line.strip() for line in context.splitlines() if line.strip()][:6]
    return "[MOCK LLM] Tra loi dua tren context: " + " | ".join(heads)


# ---------------------------------------------------------------------------
# Cham diem o MUC CHUNK (rubric docs/EVALUATION.md)
#   2 = anchor nam trong top-3 VA o vi tri top-1
#   1 = anchor nam trong top-3 nhung khong phai top-1
#   0 = khong co bang chung dap an trong top-3
# ---------------------------------------------------------------------------
def _norm(text: str) -> str:
    return " ".join(text.lower().split())


def score_results(results: list[dict], query: dict) -> tuple[int, str]:
    anchors = [_norm(a) for a in query["anchors"]]
    hit_ranks = [
        rank
        for rank, result in enumerate(results, start=1)
        if any(anchor in _norm(result["content"]) for anchor in anchors)
    ]
    doc_hit = any(r["metadata"].get("doc_id") == query["gold_doc_id"] for r in results)

    if not hit_ranks:
        note = (
            "0 — khong chunk nao chua anchor"
            + (" (DUNG doc_id nhung SAI section)" if doc_hit else "")
        )
        return 0, note
    if hit_ranks[0] == 1:
        return 2, "2 — anchor nam o chunk top-1"
    return 1, f"1 — anchor nam o top-{hit_ranks[0]}, khong phai top-1"


def run_query(store, agent, query: dict, use_filter: bool) -> dict:
    metadata_filter = query["metadata_filter"] if use_filter else None
    if metadata_filter:
        results = store.search_with_filter(
            query["question_vi"], top_k=TOP_K, metadata_filter=metadata_filter
        )
    else:
        results = store.search(query["question_vi"], top_k=TOP_K)

    points, note = score_results(results, query)
    answer = (
        agent.llm_fn(agent.build_prompt(query["question_vi"], results))
        if results
        else agent.NO_CONTEXT_MESSAGE
    )
    return {"results": results, "points": points, "note": note, "answer": answer}


def print_run(query: dict, run: dict, label: str) -> None:
    print(f"  --- {label} ---")
    if not run["results"]:
        print("    (khong co ket qua)")
    for rank, result in enumerate(run["results"], start=1):
        metadata = result["metadata"]
        preview = " ".join(result["content"].split())[:110]
        print(
            f"    {rank}. score={result['score']:+.4f}  "
            f"doc_id={metadata.get('doc_id')}  "
            f"chunk={metadata.get('chunk_index')}  "
            f"role={metadata.get('customer_role')}"
        )
        print(f"       {preview}...")
    print(f"    -> diem chunk-level: {run['note']}")
    print(f"    -> agent: {run['answer'][:220]}")


def run_strategy(name: str, embedder) -> dict:
    """BUOC 2 + BUOC 3: nap corpus bang chunker da chon, roi chay 5 query."""
    chunker = STRATEGIES[name]()
    params = chunker.params() if hasattr(chunker, "params") else repr(vars(chunker))

    print("=" * 78)
    print(f"STRATEGY: {name}{'   <- CUA TOI' if name == MY_STRATEGY else ''}")
    print(f"PARAMS  : {params}")

    # BUOC 2 — ingest.py lo het: parse front matter -> chunk -> gan metadata
    # -> nap vao EmbeddingStore. Khong viet lai phan nay.
    store = build_knowledge_base(DATA_DIR, embedder, chunker=chunker)

    agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)
    total_chunks = store.get_collection_size()
    print(f"CHUNKS  : {total_chunks} chunk tu {DATA_DIR}")
    print("-" * 78)

    per_query = {}
    total_points = 0
    for query in BENCHMARK_QUERIES:
        print(f"\n[{query['id']}] ({query['kind']}) {query['question_vi']}")
        print(f"  gold doc : {query['gold_doc_id']}   anchor: {query['anchors']}")

        run_nofilter = run_query(store, agent, query, use_filter=False)
        print_run(query, run_nofilter, "KHONG FILTER")

        entry = {"no_filter": run_nofilter}
        if query["metadata_filter"]:
            run_filter = run_query(store, agent, query, use_filter=True)
            print_run(query, run_filter, f"CO FILTER {query['metadata_filter']}")
            same = [r["id"] for r in run_nofilter["results"]] == [
                r["id"] for r in run_filter["results"]
            ]
            print(f"    -> A/B: ket qua {'GIONG HET' if same else 'KHAC NHAU'}")
            entry["filter"] = run_filter
            entry["ab_identical"] = same
            scored = run_filter["points"]
        else:
            scored = run_nofilter["points"]

        entry["points"] = scored
        total_points += scored
        per_query[query["id"]] = entry

    print("-" * 78)
    print(f"TONG DIEM {name}: {total_points}/10  (chunks={total_chunks})")
    return {
        "name": name,
        "params": params,
        "chunks": total_chunks,
        "total_points": total_points,
        "per_query": per_query,
    }


def print_summary(summaries: list[dict]) -> None:
    print("\n" + "=" * 78)
    print("BANG SO SANH STRATEGY (diem chunk-level, toi da 10)")
    print("=" * 78)
    header = (
        f"{'strategy':22} {'chunks':>7} "
        + " ".join(f"{q['id']:>4}" for q in BENCHMARK_QUERIES)
        + f" {'TONG':>6}"
    )
    print(header)
    print("-" * len(header))
    for summary in summaries:
        cells = " ".join(
            f"{summary['per_query'][q['id']]['points']:>4}" for q in BENCHMARK_QUERIES
        )
        mark = " <- CUA TOI" if summary["name"] == MY_STRATEGY else ""
        print(
            f"{summary['name']:22} {summary['chunks']:>7} {cells} "
            f"{summary['total_points']:>6}{mark}"
        )
    print("-" * len(header))
    print("Q4 duoc cham theo lan CO metadata_filter (customer_role=buyer).")
    print(
        "Cac thanh vien khac chay bench.py trong repo cua ho roi dan ket qua vao\n"
        "bang so sanh trong REPORT_NHOM.md muc 2."
    )


def main() -> int:
    args = [a for a in sys.argv[1:] if a.strip()]
    embedder = select_embedder()
    backend = getattr(embedder, "_backend_name", embedder.__class__.__name__)
    print(f"Embedding backend: {backend}")
    if backend == "mock embeddings fallback":
        print(
            "[!] Dang dung MockEmbedder: score chi phan anh hash, KHONG phan anh ngu "
            "nghia. Ket qua duoi day dung de kiem luong ky thuat + so sanh so chunk / "
            "coherence / provenance, khong dung de ket luan strategy nao 'hieu' hon."
        )
    print()

    if args and args[0] == "--all":
        summaries = [run_strategy(name, embedder) for name in STRATEGIES]
        print_summary(summaries)
        return 0

    name = args[0] if args else MY_STRATEGY
    if name not in STRATEGIES:
        print(f"Strategy khong hop le: {name}.")
        print(f"Chon mot trong: {sorted(STRATEGIES)}")
        return 1
    run_strategy(name, embedder)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
