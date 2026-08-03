from __future__ import annotations

from pathlib import Path
import sys
import time

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from benchmark_queries import BENCHMARK_QUERIES  # noqa: E402
from demo.retrieval_service import (  # noqa: E402
    DATA_DIR,
    DEFAULT_MODEL,
    build_index,
    grounded_extractive_answer,
    load_embedding_model,
    records_for_document,
    retrieve,
)
from demo.strategy_registry import STRATEGIES, get_strategy  # noqa: E402


st.set_page_config(
    page_title="RAG Strategy Lab",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root { --ink:#172226; --muted:#617074; --lime:#d9f99d; --orange:#ff8a4c; }
    .stApp { background: #f5f3ed; color: var(--ink); }
    [data-testid="stSidebar"] { background: #182225; }
    [data-testid="stSidebar"] * { color: #f6f2e8; }
    .hero { padding: 1.6rem 0 .8rem; border-bottom: 1px solid #c9cec8; margin-bottom: 1.2rem; }
    .eyebrow { font-size:.76rem; letter-spacing:.16em; text-transform:uppercase; color:#65736f; font-weight:700; }
    .hero h1 { font-size: clamp(2.3rem, 5vw, 5rem); line-height:.94; margin:.35rem 0 .65rem; letter-spacing:-.055em; }
    .hero p { max-width:760px; color:#576561; font-size:1.05rem; }
    .strategy-card { background:#fffdf8; border:1px solid #d8dbd3; border-radius:16px; padding:18px; min-height:176px; }
    .strategy-card.active { box-shadow: inset 5px 0 0 #ff8a4c; }
    .strategy-card h3 { margin:.25rem 0 .5rem; }
    .method-pill { display:inline-block; padding:4px 9px; border-radius:999px; background:#e4f7b9; font-size:.78rem; font-weight:700; }
    .answer { background:#172226; color:#f7f5ef; border-radius:18px; padding:22px; font-size:1.04rem; line-height:1.65; }
    .meta { color:#66716f; font-size:.86rem; }
    .score { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; color:#b64a20; font-weight:700; }
    div[data-testid="stMetric"] { background:#fffdf8; border:1px solid #d8dbd3; padding:14px; border-radius:14px; }
    .stButton > button { border-radius:999px; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def cached_model(model_name: str):
    return load_embedding_model(model_name)


@st.cache_resource(show_spinner=False)
def cached_index(strategy_key: str, model_name: str):
    model = cached_model(model_name)
    return build_index(strategy_key, model, model_name)


def source_link(metadata: dict) -> str:
    url = metadata.get("source_url")
    source = metadata.get("source", "không rõ nguồn")
    return f"[{source}]({url})" if url else str(source)


st.markdown(
    """
    <section class="hero">
      <div class="eyebrow">Lab 07 · Retrieval Observatory</div>
      <h1>Một câu hỏi.<br>Bốn cách chia.</h1>
      <p>Quan sát trực tiếp cách ranh giới chunk thay đổi kết quả retrieval và câu trả lời có căn cứ trên cùng corpus thương mại điện tử.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Thiết lập thử nghiệm")
    strategy_key = st.selectbox(
        "Phương pháp chunking",
        options=list(STRATEGIES),
        format_func=lambda key: STRATEGIES[key].label,
    )
    query_labels = [f"{q['id']} · {q['question_vi']}" for q in BENCHMARK_QUERIES]
    selected_query = st.selectbox("Câu hỏi benchmark", ["Tự nhập"] + query_labels)
    default_question = "" if selected_query == "Tự nhập" else BENCHMARK_QUERIES[query_labels.index(selected_query)]["question_vi"]
    question = st.text_area("Câu hỏi", value=default_question, height=120, placeholder="Nhập câu hỏi về chính sách TMĐT…")
    top_k = st.slider("Số chunk retrieval", 1, 8, 3)
    role_label = st.selectbox("Metadata filter · customer_role", ["Không lọc", "buyer", "seller", "both"])
    role_filter = None if role_label == "Không lọc" else role_label
    run = st.button("Chạy retrieval", type="primary", use_container_width=True)
    st.caption("Embedding thật · chạy cục bộ · không dùng mock")

active = get_strategy(strategy_key)
cols = st.columns(4)
for column, spec in zip(cols, STRATEGIES.values()):
    active_class = " active" if spec.key == strategy_key else ""
    column.markdown(
        f"""
        <div class="strategy-card{active_class}">
          <span class="method-pill">{spec.method}</span>
          <h3>{spec.owner.split(' · ')[0]}</h3>
          <div class="meta">{spec.parameters}</div>
          <p>{spec.description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.spinner("Đang nạp model embedding thật và lập chỉ mục…"):
    model = cached_model(DEFAULT_MODEL)
    index = cached_index(strategy_key, DEFAULT_MODEL)

metric_cols = st.columns(4)
metric_cols[0].metric("Strategy đang chọn", active.method)
metric_cols[1].metric("Tổng chunks", index.chunk_count)
metric_cols[2].metric("Tài liệu", len({r.metadata.get('doc_id') for r in index.records}))
metric_cols[3].metric("Thời gian lập chỉ mục", f"{index.build_seconds:.2f}s")

if run:
    st.session_state["question"] = question
    st.session_state["strategy_key"] = strategy_key
    st.session_state["top_k"] = top_k
    st.session_state["role_filter"] = role_filter

current_question = st.session_state.get("question", question)
should_search = bool(current_question.strip())
results = (
    retrieve(
        index,
        model,
        current_question,
        st.session_state.get("top_k", top_k),
        st.session_state.get("role_filter", role_filter),
    )
    if should_search
    else []
)

answer_tab, retrieval_tab, chunks_tab, compare_tab = st.tabs(
    ["Câu trả lời", "Retrieval chunks", "Chunk explorer", "So sánh 4 phương pháp"]
)

with answer_tab:
    st.subheader(f"Trả lời bằng {active.label}")
    if not should_search:
        st.info("Chọn câu benchmark hoặc nhập câu hỏi, sau đó bấm **Chạy retrieval**.")
    elif not results:
        st.warning("Không tìm thấy chunk phù hợp với bộ lọc hiện tại.")
    else:
        answer = grounded_extractive_answer(model, current_question, results)
        st.markdown(f'<div class="answer">{answer}</div>', unsafe_allow_html=True)
        st.caption("Số trong ngoặc vuông trỏ tới thứ hạng chunk ở tab Retrieval chunks. Câu trả lời offline chỉ trích xuất từ context, không tự bổ sung kiến thức ngoài corpus.")

with retrieval_tab:
    st.subheader("Những gì model thực sự nhìn thấy")
    if not results:
        st.info("Chưa có kết quả retrieval.")
    for result in results:
        metadata = result["metadata"]
        title = (
            f"#{result['rank']} · {result['id']} · score {result['score']:.4f}"
        )
        with st.expander(title, expanded=result["rank"] == 1):
            left, right = st.columns([3, 1])
            left.markdown(result["content"])
            right.markdown(f"**doc_id**  \n`{metadata.get('doc_id')}`")
            right.markdown(f"**role**  \n`{metadata.get('customer_role', 'n/a')}`")
            right.markdown(f"**độ dài**  \n`{len(result['content'])} ký tự`")
            right.markdown(f"**nguồn**  \n{source_link(metadata)}")

with chunks_tab:
    st.subheader(f"Toàn bộ chunk · {active.label}")
    doc_ids = sorted({record.metadata.get("doc_id", "") for record in index.records})
    selected_doc = st.selectbox("Chọn tài liệu", doc_ids)
    document_chunks = records_for_document(index, selected_doc)
    lengths = [len(record.content) for record in document_chunks]
    a, b, c = st.columns(3)
    a.metric("Số chunks", len(document_chunks))
    b.metric("Độ dài trung bình", f"{sum(lengths) / len(lengths):.0f}" if lengths else "0")
    c.metric("Chunk dài nhất", max(lengths) if lengths else 0)
    for record in document_chunks:
        with st.expander(f"{record.id} · {len(record.content)} ký tự"):
            st.markdown(record.content)

with compare_tab:
    st.subheader("Cùng câu hỏi, cùng model, chỉ đổi chunker")
    if not should_search:
        st.info("Hãy nhập một câu hỏi trước khi so sánh.")
    else:
        comparison_columns = st.columns(4)
        for column, (key, spec) in zip(comparison_columns, STRATEGIES.items()):
            started = time.perf_counter()
            with st.spinner(f"Đang chạy {spec.method}…"):
                compared_index = cached_index(key, DEFAULT_MODEL)
                compared_results = retrieve(
                    compared_index,
                    model,
                    current_question,
                    st.session_state.get("top_k", top_k),
                    st.session_state.get("role_filter", role_filter),
                )
            elapsed = time.perf_counter() - started
            with column:
                st.markdown(f"### {spec.label}")
                st.caption(f"{compared_index.chunk_count} chunks · query {elapsed:.2f}s")
                for item in compared_results:
                    st.markdown(
                        f"**#{item['rank']} · `{item['score']:.4f}`**  \n"
                        f"`{item['id']}`  \n"
                        f"{item['content'][:220].replace(chr(10), ' ')}…"
                    )

st.divider()
st.caption(f"Corpus: {DATA_DIR.relative_to(PROJECT_ROOT)} · Model: {DEFAULT_MODEL} · Vector cosine trên embedding đã chuẩn hóa")
