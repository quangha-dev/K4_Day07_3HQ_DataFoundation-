"""Registry that adapts the four personal chunking strategies used by the group.

The demo deliberately imports the original classes from each student's package.
No chunking implementation is copied into this directory, so changes in a
student package are reflected automatically after Streamlit's cache is cleared.
"""
from __future__ import annotations

from dataclasses import dataclass
import importlib
from typing import Callable, Protocol


class Chunker(Protocol):
    def chunk(self, text: str) -> list[str]: ...


@dataclass(frozen=True)
class StrategySpec:
    key: str
    label: str
    owner: str
    method: str
    parameters: str
    description: str
    factory: Callable[[], Chunker]


def _class_factory(module_name: str, class_name: str, **kwargs) -> Callable[[], Chunker]:
    def create() -> Chunker:
        module = importlib.import_module(module_name)
        chunker_class = getattr(module, class_name)
        return chunker_class(**kwargs)

    return create


STRATEGIES: dict[str, StrategySpec] = {
    "paragraph_ha": StrategySpec(
        key="paragraph_ha",
        label="Theo đoạn · Hà",
        owner="Nguyễn Quang Hà · 2A202601424",
        method="ParagraphChunker",
        parameters="max_chunk_size=700 · min_chunk_size=450 · keep_heading=True",
        description=(
            "Tách tại dòng trống, gộp các đoạn quá ngắn và gắn lại tiêu đề Điều. "
            "Phù hợp văn bản pháp luật có cấu trúc đoạn rõ ràng."
        ),
        factory=_class_factory(
            "src.2A202601424-NguyenQuangHa.chunking",
            "ParagraphChunker",
            max_chunk_size=700,
            min_chunk_size=450,
            keep_heading=True,
        ),
    ),
    "sentence_hai": StrategySpec(
        key="sentence_hai",
        label="Theo câu · Hải",
        owner="Trương Ngọc Hải · 2A202601092",
        method="SentenceChunker",
        parameters="max_sentences_per_chunk=3",
        description=(
            "Gom tối đa ba câu mỗi chunk; bảo vệ chữ viết tắt như TS., Dr. và "
            "số thập phân để tránh tách sai ranh giới câu."
        ),
        factory=_class_factory(
            "src.2A202601092_TruongNgocHai.chunking",
            "SentenceChunker",
            max_sentences_per_chunk=3,
        ),
    ),
    "recursive_huy": StrategySpec(
        key="recursive_huy",
        label="Đệ quy · Huy",
        owner="Vũ Văn Huy · 2A202601342",
        method="RecursiveChunker",
        parameters="chunk_size=500 · separators=đoạn → dòng → câu → từ → ký tự",
        description=(
            "Ưu tiên ranh giới tự nhiên theo thứ tự; nếu một phần vẫn quá dài thì "
            "hạ xuống separator nhỏ hơn và cuối cùng mới cắt cứng."
        ),
        factory=_class_factory(
            "src.K4_2A202601342_VuVanHuy.chunking",
            "RecursiveChunker",
            chunk_size=500,
        ),
    ),
    "fixed_quang": StrategySpec(
        key="fixed_quang",
        label="Kích thước cố định · Quang",
        owner="Nguyễn Nhật Quang · 01452",
        method="FixedSizeChunker",
        parameters="chunk_size=500 · overlap=50",
        description=(
            "Cắt mỗi 500 ký tự và lặp lại 50 ký tự ở hai chunk liên tiếp. "
            "Đơn giản, ổn định và giữ một phần ngữ cảnh tại ranh giới cắt."
        ),
        factory=_class_factory(
            "src.K4_01452_NguyenNhatQuang.chunking",
            "FixedSizeChunker",
            chunk_size=500,
            overlap=50,
        ),
    ),
}


def get_strategy(key: str) -> StrategySpec:
    try:
        return STRATEGIES[key]
    except KeyError as error:
        raise ValueError(f"Unknown strategy: {key}") from error


def validate_strategies() -> dict[str, int]:
    """Small adapter check used by the smoke test and the UI diagnostics."""
    sample = (
        "## Điều 1. Quy định chung\n\n"
        "Người bán phải công bố thông tin trước khi giao dịch.\n\n"
        "## Điều 2. Trách nhiệm\n\n"
        "Khách hàng được quyền kiểm tra chính sách hoàn trả."
    )
    counts: dict[str, int] = {}
    for key, spec in STRATEGIES.items():
        chunks = spec.factory().chunk(sample)
        if not isinstance(chunks, list) or not all(isinstance(item, str) for item in chunks):
            raise TypeError(f"{spec.method} must return list[str]")
        if not chunks:
            raise ValueError(f"{spec.method} returned no chunks for non-empty text")
        counts[key] = len(chunks)
    return counts
