"""Non-UI verification for all four adapters and the real embedding pipeline."""
from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from demo.retrieval_service import (  # noqa: E402
    DEFAULT_MODEL,
    build_index,
    load_embedding_model,
    retrieve,
)
from demo.strategy_registry import STRATEGIES, validate_strategies  # noqa: E402


def main() -> int:
    print("Adapters:", validate_strategies())
    model = load_embedding_model(DEFAULT_MODEL)
    question = "Chính sách kiểm hàng có bắt buộc phải công bố không?"
    for key in STRATEGIES:
        index = build_index(key, model, DEFAULT_MODEL)
        results = retrieve(index, model, question, top_k=3, customer_role="buyer")
        assert index.chunk_count > 0
        assert len(results) == 3
        assert all("content" in result and "score" in result for result in results)
        print(key, index.chunk_count, results[0]["id"], f"{results[0]['score']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
