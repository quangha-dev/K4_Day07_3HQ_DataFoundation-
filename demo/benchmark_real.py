"""Benchmark all four inherited strategies with the real multilingual embedder."""
from __future__ import annotations

import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from benchmark_queries import BENCHMARK_QUERIES  # noqa: E402
from demo.retrieval_service import (  # noqa: E402
    DEFAULT_MODEL,
    build_index,
    load_embedding_model,
    retrieve,
)
from demo.strategy_registry import STRATEGIES  # noqa: E402


OUTPUT_DIR = PROJECT_ROOT / "demo" / "outputs"


def anchor_rank(results: list[dict], anchors: list[str]) -> int | None:
    lowered = [anchor.casefold() for anchor in anchors]
    for result in results:
        content = result["content"].casefold()
        if any(anchor in content for anchor in lowered):
            return int(result["rank"])
    return None


def points_for_rank(rank: int | None) -> int:
    if rank == 1:
        return 2
    if rank in {2, 3}:
        return 1
    return 0


def run() -> dict:
    model = load_embedding_model(DEFAULT_MODEL)
    payload = {"model": DEFAULT_MODEL, "strategies": []}
    for key, spec in STRATEGIES.items():
        index = build_index(key, model, DEFAULT_MODEL)
        query_rows = []
        total = 0
        for query in BENCHMARK_QUERIES:
            metadata_filter = query.get("metadata_filter") or {}
            role = metadata_filter.get("customer_role")
            results = retrieve(index, model, query["question_vi"], top_k=3, customer_role=role)
            hit_rank = anchor_rank(results, query["anchors"])
            points = points_for_rank(hit_rank)
            total += points
            query_rows.append(
                {
                    "id": query["id"],
                    "kind": query["kind"],
                    "question": query["question_vi"],
                    "gold_doc_id": query["gold_doc_id"],
                    "anchors": query["anchors"],
                    "filter": metadata_filter or None,
                    "hit_rank": hit_rank,
                    "points": points,
                    "results": [
                        {
                            "rank": item["rank"],
                            "id": item["id"],
                            "score": round(item["score"], 6),
                            "customer_role": item["metadata"].get("customer_role"),
                            "preview": item["content"][:260].replace("\n", " "),
                        }
                        for item in results
                    ],
                }
            )
        payload["strategies"].append(
            {
                "key": key,
                "label": spec.label,
                "owner": spec.owner,
                "method": spec.method,
                "parameters": spec.parameters,
                "chunks": index.chunk_count,
                "build_seconds": round(index.build_seconds, 4),
                "total_points": total,
                "queries": query_rows,
            }
        )
    return payload


def render_markdown(payload: dict) -> str:
    lines = [
        "# Benchmark bốn phương pháp — embedding thật",
        "",
        f"Model: `{payload['model']}`",
        "",
        "Cách chấm ở mức chunk: anchor ở top-1 = 2 điểm; top-2/3 = 1 điểm; không có trong top-3 = 0 điểm.",
        "",
        "| Thành viên | Phương pháp | Chunks | Q1 | Q2 | Q3 | Q4 | Q5 | Tổng /10 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for strategy in payload["strategies"]:
        points = [str(query["points"]) for query in strategy["queries"]]
        lines.append(
            f"| {strategy['owner']} | `{strategy['method']}` | {strategy['chunks']} | "
            + " | ".join(points)
            + f" | **{strategy['total_points']}** |"
        )
    lines.extend(["", "## Bằng chứng top-3 và failure case", ""])
    for strategy in payload["strategies"]:
        lines.extend(
            [
                f"### {strategy['label']} — {strategy['total_points']}/10",
                "",
                f"Tham số: `{strategy['parameters']}`",
                "",
            ]
        )
        for query in strategy["queries"]:
            status = f"anchor ở top-{query['hit_rank']}" if query["hit_rank"] else "không có anchor trong top-3"
            lines.append(f"- **{query['id']} · {query['points']}/2:** {status}.")
            for item in query["results"]:
                lines.append(f"  - #{item['rank']} `{item['id']}` · score `{item['score']:.4f}`")
        failures = [query for query in strategy["queries"] if query["points"] < 2]
        if failures:
            ids = ", ".join(query["id"] for query in failures)
            lines.append(f"- **Failure cases cần phân tích:** {ids}.")
        else:
            lines.append("- Không có failure case theo rubric top-1 trên bộ 5 query này.")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    payload = run()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "benchmark_real.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report = render_markdown(payload)
    (OUTPUT_DIR / "BENCHMARK_REAL.md").write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
