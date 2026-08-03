"""
export_ket_qua.py — Xuat ket qua benchmark CUA RIENG TOI ra file Markdown.

Vi sao can file nay ngoai `bench.py`
------------------------------------
`bench.py` in ra terminal, dinh kem ca 6 strategy, doc trong report thi roi.
File nay chi chay DUNG strategy ca nhan (`MY_STRATEGY` trong bench.py) va sinh
mot bao cao Markdown sach se, dan thang vao report duoc.

Chay:
    $env:EMBEDDING_PROVIDER="lexical"; python export_ket_qua.py

Ket qua ghi ra:
    report/KET_QUA_PARAGRAPH.md

Moi thanh vien chay chinh file nay trong repo cua minh; ten file dau ra tu doi
theo ten strategy nen khong de len nhau.
"""
from __future__ import annotations

from pathlib import Path

from bench import (
    BENCHMARK_QUERIES,
    DATA_DIR,
    MY_STRATEGY,
    STRATEGIES,
    TOP_K,
    _norm,
    demo_llm,
    score_results,
    select_embedder,
)
from ingest import build_knowledge_base
from solution import KnowledgeBaseAgent

OUT_DIR = Path("report")


def doc_level_points(results: list[dict], query: dict) -> int:
    """Cham theo kieu CU: chi kiem gold doc_id co trong top-3 khong."""
    ranks = [
        rank
        for rank, result in enumerate(results, start=1)
        if result["metadata"].get("doc_id") == query["gold_doc_id"]
    ]
    if not ranks:
        return 0
    return 2 if ranks[0] == 1 else 1


def preview(text: str, limit: int = 150) -> str:
    """Rut gon noi dung chunk ve mot dong, escape ky tu pha bang Markdown."""
    flat = " ".join(text.split())
    if len(flat) > limit:
        flat = flat[:limit] + "…"
    return flat.replace("|", "\\|")


def render_results(lines: list[str], results: list[dict], label: str) -> None:
    lines.append(f"**{label}**\n")
    if not results:
        lines.append("_(khong co ket qua)_\n")
        return
    lines.append("| # | score | doc_id | chunk | role | Trich noi dung |")
    lines.append("|---|-------|--------|-------|------|----------------|")
    for rank, result in enumerate(results, start=1):
        metadata = result["metadata"]
        lines.append(
            f"| {rank} | {result['score']:+.4f} | `{metadata.get('doc_id')}` | "
            f"{metadata.get('chunk_index')} | {metadata.get('customer_role')} | "
            f"{preview(result['content'])} |"
        )
    lines.append("")


def main() -> int:
    embedder = select_embedder()
    backend = getattr(embedder, "_backend_name", embedder.__class__.__name__)

    chunker = STRATEGIES[MY_STRATEGY]()
    params = chunker.params() if hasattr(chunker, "params") else repr(vars(chunker))
    store = build_knowledge_base(DATA_DIR, embedder, chunker=chunker)
    agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)

    lines: list[str] = []
    add = lines.append

    add(f"# Ket qua benchmark — strategy `{MY_STRATEGY}`")
    add("")
    add("**Nguyen Quang Ha · 2A202601424 · Lab 07 (K4)**")
    add("")
    add("| Muc | Gia tri |")
    add("|---|---|")
    add(f"| Strategy | `{MY_STRATEGY}` (`ParagraphChunker`) |")
    add(f"| Tham so | `{params}` |")
    add(f"| Corpus | `{DATA_DIR}` |")
    add(f"| So chunk da nap | **{store.get_collection_size()}** |")
    add(f"| Embedding backend | `{backend}` |")
    add(f"| top_k | {TOP_K} |")
    add("")
    if backend == "mock embeddings fallback":
        add(
            "> ⚠️ Dang chay **MockEmbedder** (hash MD5). Score khong mang ngu nghia, "
            "khong dung ket qua nay de ket luan chat luong. Chay lai voi "
            "`EMBEDDING_PROVIDER=lexical`."
        )
        add("")
    add("Sinh tu dong boi `export_ket_qua.py`. Khong sua tay file nay.")
    add("")
    add("---")
    add("")

    total_chunk, total_doc = 0, 0
    summary_rows: list[str] = []

    for query in BENCHMARK_QUERIES:
        add(f"## {query['id']} — {query['kind']}")
        add("")
        add(f"**Cau hoi:** {query['question_vi']}")
        add("")
        add(f"**Gold answer:** {query['gold_answer']}")
        add("")
        add(f"**Tai lieu ky vong:** `{query['gold_doc_id']}`")
        add("")
        add(f"**Anchor (chuoi phai xuat hien trong chunk):** `{query['anchors'][0]}`")
        add("")

        no_filter = store.search(query["question_vi"], top_k=TOP_K)
        render_results(lines, no_filter, "Khong filter")

        scored_results = no_filter
        if query["metadata_filter"]:
            with_filter = store.search_with_filter(
                query["question_vi"],
                top_k=TOP_K,
                metadata_filter=query["metadata_filter"],
            )
            render_results(
                lines, with_filter, f"Co filter `{query['metadata_filter']}`"
            )
            same = [r["id"] for r in no_filter] == [r["id"] for r in with_filter]
            add(
                f"**A/B filter:** ket qua **{'GIONG HET' if same else 'KHAC NHAU'}**"
                f"{' — filter khong loai duoc gi, can xem lai query hoac corpus.' if same else ''}"
            )
            add("")
            scored_results = with_filter

        chunk_points, note = score_results(scored_results, query)
        doc_points = doc_level_points(scored_results, query)
        total_chunk += chunk_points
        total_doc += doc_points

        answer = (
            agent.llm_fn(agent.build_prompt(query["question_vi"], scored_results))
            if scored_results
            else agent.NO_CONTEXT_MESSAGE
        )

        add(f"**Cham chunk-level:** {note}")
        add("")
        add(f"**Cham doc-level (de doi chieu):** {doc_points}/2")
        add("")
        add("**Cau tra loi cua agent:**")
        add("")
        add("```")
        add(answer[:600])
        add("```")
        add("")
        add("---")
        add("")

        summary_rows.append(
            f"| {query['id']} | {query['kind']} | {doc_points} | {chunk_points} | "
            f"{note.split('—')[-1].strip()} |"
        )

    add("## Tong ket")
    add("")
    add("| Query | Loai | Doc-level | Chunk-level | Ghi chu |")
    add("|-------|------|-----------|-------------|---------|")
    lines.extend(summary_rows)
    add(f"| **TONG** | | **{total_doc}/10** | **{total_chunk}/10** | |")
    add("")
    add(
        f"Chenh lech **{total_doc} vs {total_chunk}**: cham theo `doc_id` cho diem "
        "cao hon vi chi can lay dung TAI LIEU la duoc, du chunk lay ve khong chua "
        "cau tra loi. Day la ly do bo query phai co `anchors`."
    )
    add("")

    OUT_DIR.mkdir(exist_ok=True)
    out_path = OUT_DIR / f"KET_QUA_{MY_STRATEGY.upper()}.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Da ghi: {out_path}")
    print(f"Chunk-level: {total_chunk}/10   |   Doc-level: {total_doc}/10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
