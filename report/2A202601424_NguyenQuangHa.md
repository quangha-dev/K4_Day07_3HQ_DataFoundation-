# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Quang Hà\
**MSSV:** 2A202601424\
**Nhóm:** 3HQ\
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

**Gói bài làm của tôi:** `src/2A202601424-NguyenQuangHa/` · **Chiến lược cá nhân:** `ParagraphChunker` (chia theo **đoạn**, ranh giới là dòng trống).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector chỉ về cùng một hướng trong không gian embedding, tức là mô hình cho rằng hai đoạn text có phân bố ngữ nghĩa gần nhau. Nó nói về *hướng*, không nói về *độ dài*, nên một câu ngắn và một đoạn dài cùng chủ đề vẫn có thể đạt cosine cao.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Người bán phải công bố chính sách hoàn trả trên website."
- Câu B: "Website thương mại điện tử phải nêu rõ quy định đổi trả hàng."
- Tại sao tương đồng: cùng nói về nghĩa vụ công bố chính sách đổi/trả, chỉ khác cách diễn đạt.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Thời hạn trả lời đề nghị giao kết hợp đồng là 12 giờ."
- Câu B: "Sàn phải thông báo trước ít nhất 5 ngày khi đổi quy chế hoạt động."
- Tại sao khác: cùng là con số thời gian nhưng khác chủ thể, khác nghĩa vụ, khác Điều luật.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Vì độ dài vector của text embedding phần lớn phản ánh **độ dài / tần suất từ** của đoạn text chứ không phản ánh nội dung. Euclid phạt sự chênh lệch độ dài đó, còn cosine chuẩn hoá nó đi và chỉ so hướng — nên "một câu" và "một đoạn 5 câu" cùng chủ đề vẫn được coi là gần nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Công thức: `ceil((length - overlap) / (chunk_size - overlap))`
> = `ceil((10000 - 50) / (500 - 50))` = `ceil(9950 / 450)` = `ceil(22.11)`

> *Đáp án:* **23 chunk**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> `ceil((10000 - 100) / (500 - 100)) = ceil(24.75) = 25` chunk → **số chunk TĂNG**.
>
> Muốn overlap nhiều hơn vì mỗi thông tin có nhiều "cơ hội" lọt top-k hơn và ít bị cắt đôi giữa một câu điều kiện. Đánh đổi: phải embed và lưu nhiều vector hơn (tốn chi phí), và top-k dễ bị chiếm bởi nhiều chunk gần trùng nhau của cùng một đoạn nên giảm đa dạng kết quả.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của tôi khi lập trình các phần chính trong gói `src/2A202601424-NguyenQuangHa/`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex lookbehind `re.compile(r"(?<=[.!?])\s+")` để cắt tại **khoảng trắng đứng sau** dấu kết câu. Lookbehind quan trọng vì nó chỉ "nhìn lại" để xác nhận có dấu câu chứ **không nuốt** dấu câu — nếu viết `re.split(r"[.!?]\s+")` thì dấu chấm bị mất và khi ghép các câu lại chúng sẽ dính vào nhau. Edge case đã xử lý: `text` rỗng trả `[]`; `strip()` từng câu và loại chuỗi rỗng trước khi gom nhóm; luôn trả `list[str]` chứ không phải generator.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> `chunk()` chỉ lo phần vỏ (text rỗng → `[]`, strip/lọc kết quả), toàn bộ đệ quy nằm trong `_split(current_text, remaining_separators)`. Hai base case rõ ràng: (a) text đã ngắn hơn `chunk_size` → trả về nguyên; (b) hết separator **hoặc** separator là chuỗi rỗng → `_hard_split` cắt cứng theo `chunk_size`. Nếu separator hiện tại không xuất hiện thì gọi lại với `remaining_separators[1:]` — **mỗi lần gọi đệ quy đều phải hoặc bớt separator hoặc thu nhỏ text**, đó là điều kiện để không lặp vô hạn. Bước dễ bỏ sót nhất là **gom**: sau khi split phải nối các phần liền nhau tới sát `chunk_size` (dùng biến `buffer`), nếu không sẽ ra hàng loạt chunk vụn vài ký tự.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Chọn in-memory (`_use_chroma = False`) để mọi method đi qua đúng một đường code. Viết **hai helper trước, bốn method công khai sau** — làm ngược lại sẽ phải lặp cùng một logic bốn lần. `_make_record(doc)` chuẩn hoá một `Document` thành record `{id, doc_id, content, metadata, embedding}`: **copy** metadata bằng `dict(doc.metadata)` để không sửa nhầm dict của người gọi, và `metadata.setdefault("doc_id", doc.id)` để `delete_document` luôn có khoá; id record ghép `doc.id` với `_next_index` nên không bao giờ trùng. `_search_records(query, records, top_k)` embed query **một lần ngoài vòng lặp**, tính dot product với từng record, sort giảm dần rồi cắt `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> **Lọc TRƯỚC, xếp hạng SAU.** Nếu làm ngược (lấy top-k rồi loại cái không khớp) thì có thể còn 0 kết quả dù store vẫn còn tài liệu hợp lệ — ví dụ 3 chunk `seller` chiếm hết top-3, lọc `buyer` xong còn rỗng. Khi `metadata_filter` là `None` thì gọi thẳng `_search_records` trên toàn bộ `_store`, nên `search()` và `search_with_filter(..., None)` **dùng chung một hàm** và không thể lệch nhau — đây chính là test `test_no_filter_returns_all_candidates`. `delete_document` lọc lại `_store` bỏ mọi record có `metadata['doc_id'] == doc_id`, so sánh độ dài trước/sau để return `True`/`False`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> `__init__` chỉ lưu `store` và `llm_fn`; agent **không tự tính embedding** mà dùng lại store đã làm xong việc đó. `answer()` gọi `store.search(question, top_k)`; **store rỗng thì trả thông báo rõ ràng, không gọi LLM vô ích**. Context được đánh số `[1] (nguồn: doc_id::chunk_N | url: ...)` — phần đánh số này là thứ đáng đầu tư nhất vì nó cho phép truy vết câu trả lời về đúng chunk và đúng file khi debug (tiêu chí grounding trong `docs/EVALUATION.md`). Prompt gồm 4 phần: instruction "chỉ dùng context, nói rõ khi không đủ" → Context → Question → nhãn `Answer:`. Tôi tách `build_prompt()` và `format_context()` thành method riêng để `bench.py` tái sử dụng được mà không phải copy code.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\DEV\Project\AI_THUC_CHIEN\LAB\NGAY7\DAY7-2A202601424-NguyenQuangHa
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================== 42 passed in 0.25s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

Đối chiếu với từng checkpoint của đề:

| Lệnh | Kết quả |
|---|---|
| `pytest tests -k "Chunker or Similarity or Compare" -v` (CP3) | 23 passed, 19 deselected |
| `pytest tests -k "EmbeddingStore or SearchWithFilter or DeleteDocument" -v` (Task 4+5) | 14 passed, 28 deselected |
| `pytest tests/test_solution.py -k KnowledgeBaseAgent -v` (Task 6) | 2 passed, 40 deselected |
| `python -m pytest tests -v` (CP4) | **42 passed** |
| `python main.py "Chunking là gì?"` | Chạy hết pipeline, in đủ 3 phần: ingest → search → agent |

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Đo bằng `compute_similarity` trong gói của tôi. Cột `mock` = `MockEmbedder` (mặc định của 42 test); cột `lexical` = `LexicalEmbedder` TF-IDF (`lexical_embedding.py`).

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế (mock) | Điểm thực tế (lexical) | Đúng? |
|---|---|---|---|---|---|---|
| 1 | Chính sách đổi trả hàng hóa | Quy định hoàn trả sản phẩm | cao | −0.1285 | 0.0977 | **SAI cả hai** |
| 2 | Người bán phải công bố chính sách hoàn trả | (chính nó) | cao | 1.0000 | 1.0000 | Đúng |
| 3 | Thời hạn trả lời đề nghị giao kết là 12 giờ | Sàn phải thông báo trước ít nhất 5 ngày | thấp | −0.2073 | 0.0000 | Đúng |
| 4 | Chính sách kiểm hàng là điều kiện giao dịch chung | Điều kiện giao dịch chung phải công bố chính sách hoàn trả | cao | 0.0456 | 0.4168 | mock SAI, lexical Đúng |
| 5 | Thủ tục đăng ký website cung cấp dịch vụ TMĐT | Giá niêm yết được hiểu là đã bao gồm mọi chi phí | thấp | −0.0960 | 0.0553 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> **Cặp 1.** Hai câu gần như đồng nghĩa hoàn toàn ("đổi trả hàng hóa" ↔ "hoàn trả sản phẩm") nhưng cả hai backend đều cho điểm rất thấp, và lý do khác nhau ở mỗi backend: `MockEmbedder` là hash MD5 nên mọi cặp đều là nhiễu ngẫu nhiên (thậm chí ra số **âm**); `LexicalEmbedder` là TF-IDF nên nó **chỉ đo trùng từ**, hai câu không chia sẻ token nào ngoài "chính sách/quy định" nên gần như bằng 0.
>
> Điều này nói lên đúng bản chất: embedding **không phải** bản thân câu văn, nó chỉ là input để xếp hạng, và chất lượng xếp hạng bị chặn trên bởi chất lượng của mô hình nhúng. Cặp 2 (giống hệt → 1.0) và cặp 3 (mock ra −0.2073 cho hai câu chỉ đơn giản là không liên quan) cho thấy score cao/thấp là **tín hiệu xếp hạng, không phải bằng chứng nội dung đúng** — đây là bài học tôi dùng lại ở mục 5 khi phân tích failure case.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân trong gói `src/2A202601424-NguyenQuangHa/`. 5 câu hỏi này trùng với các thành viên cùng nhóm (xem `REPORT_NHOM.md`).

**Cấu hình:** `ParagraphChunker(max_chunk_size=700, min_chunk_size=450, keep_heading=True)` · corpus `data/k4_ecommerce` (9 tài liệu) → **65 chunk** · embedder `LexicalEmbedder` (dùng chung cả nhóm) · `top_k=3`
**Lệnh tái tạo:** `$env:EMBEDDING_PROVIDER="lexical"; python bench.py paragraph`

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? | Câu trả lời của Agent (tóm tắt) |
|---|---|---|---|---|---|
| 1 | Không công bố rõ thời hạn trả lời thì sau bao lâu đề nghị giao kết hết hiệu lực? | `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_8` — Điều 20 khoản 2 | 0.4102 | **Có** — chứa "12 (mười hai) giờ" | Trả lời đúng 12 giờ, trích dẫn `[1]` về đúng Điều 20 |
| 2 | Sàn phải thông báo trước bao nhiêu ngày khi thay đổi quy chế? | `nd52-quy-che-hoat-dong-san::chunk_3` — Điều 38 | 0.2979 | **Có** — chứa "ít nhất 5 ngày" | Trả lời đúng 5 ngày, trích đúng khoản 3 Điều 38 |
| 3 | Cơ chế rà soát và xác nhận hợp đồng phải hiển thị thông tin gì? | `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_3` — Điều 18, **phần dẫn** | 0.3909 | **Một phần** — đúng Điều nhưng thiếu danh sách a/b/c; chunk chứa đáp án đứng top-2 (0.2689) | Thiếu danh sách thông tin bắt buộc ở top-1 |
| 4 | Chính sách kiểm hàng có bắt buộc không? (**có filter** `customer_role=buyer`) | `nd85-2021-...::chunk_5` — mục 4 | 0.3591 | **Có** — chứa "chính sách kiểm hàng" | Trả lời đúng theo bản NĐ 85/2021, không lẫn bản 2013 |
| 5 | Giá niêm yết không nói rõ đã gồm thuế/phí thì hiểu sao? | `seller-listing::chunk_5` — Điều 31 | 0.2550 | **Có** — chứa "được hiểu là đã bao gồm mọi chi phí" | Trả lời đúng khoản 2 Điều 31 |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5 / 5**
**Điểm chunk-level theo rubric `docs/EVALUATION.md`:** **9 / 10** (Q3 chỉ được 1 vì chunk chứa đáp án đứng top-2 chứ không phải top-1).

### Failure case của tôi — Q3, có bằng chứng từ top-k

| Rank | doc_id::chunk | score | Chứa anchor `Tổng giá trị của hợp đồng`? | Nội dung |
|---|---|---|:---:|---|
| 1 | `nd52-quy-trinh...::chunk_3` | 0.3909 | ✗ | Điều 18, **câu dẫn**: "Website TMĐT phải có cơ chế cho phép khách hàng rà soát…" |
| 2 | `nd52-quy-trinh...::chunk_4` | 0.2689 | **✓** | Điều 18, danh sách: "c) **Tổng giá trị của hợp đồng** và các chi tiết…" |
| 3 | `seller-listing::chunk_9` | 0.2313 | ✗ | Điều 34, phương thức thanh toán |

**Nguyên nhân:** chunk chứa đáp án là một **danh sách gạch đầu dòng a/b/c** có mật độ từ khóa "rà soát / xác nhận" rất thấp, trong khi chunk câu dẫn lặp lại gần như nguyên văn cụm từ trong câu hỏi. Cosine đo **độ giống chủ đề**, không đo **mật độ thông tin trả lời được** → chunk *nói về* câu hỏi thắng chunk *trả lời* câu hỏi. Đây là hệ quả trực tiếp của việc tôi chọn đơn vị chunk nhỏ (một khoản): câu dẫn và danh sách của nó rơi vào hai chunk khác nhau.

**Đề xuất sửa:** nâng đơn vị chunk lên **cả Điều** để câu dẫn và danh sách không tách rời (bạn Quang làm đúng vậy và Q3 lên 2/2 — xem `REPORT_NHOM.md`); hoặc retrieve ở mức khoản cho chính xác rồi nạp vào context cả Điều chứa nó (small-to-big retrieval); hoặc lấy top-8 rồi rerank.

### Ablation: bước nào trong 3 bước của tôi thực sự đóng góp?

| Biến thể | Tắt gì | Chunks | Điểm | Mất bao nhiêu |
|---|---|---|---|---|
| `paragraph` | — (đầy đủ) | 65 | **9/10** | — |
| `paragraph_noheading` | `keep_heading=False` | 63 | 8/10 | **−1** (Q3) |
| `paragraph_nomerge` | `min_chunk_size=0` | 162 | 7/10 | **−2** (Q2, Q3) |

Đọc ngược bảng này thì rõ hơn: bản "thuần túy chia theo đoạn, không gộp không gắn tiêu đề" chỉ được 7/10 — **ngang hệt `recursive` và `sentence` baseline**. Toàn bộ khoảng cách 2 điểm đến từ hai bước hậu xử lý, không phải từ ý tưởng "chia theo dòng trống".

Cụ thể `nomerge` sinh 162 chunk thay vì 65, và chunk top-1 của nó ở Q3 đạt score **0.5223** — cao hơn hẳn 0.3909 của bản đầy đủ — nhưng lại **0 điểm**, vì đó là một mảnh ngắn không chứa đáp án. Đúng hiện tượng chunk-vụn-điểm-cao mà `min_chunk_size` sinh ra để chặn.

### Giới hạn phải ghi rõ

- **42 test đều dùng `MockEmbedder`.** Tôi chạy benchmark thêm một lần bằng mock để đối chứng: kết quả gần như nhiễu (`report/bench_output_mock.txt`). Mock là hash MD5, **không thể dùng để kết luận strategy nào tốt hơn**.
- `LexicalEmbedder` là TF-IDF: đo **trùng từ**, không đo ngữ nghĩa. Hợp với văn bản pháp luật vì câu hỏi thường dùng lại đúng thuật ngữ của văn bản, nhưng sẽ hỏng với câu hỏi diễn đạt lại (xem cặp 1 mục 4). Con số 9/10 ở trên là **9/10 với embedder lexical**, không phải 9/10 tuyệt đối.
- **`min_chunk_size=450` được chọn bằng cách quét trên chính 5 query dùng để chấm**, nên có thể đang **overfit** vào 5 câu hỏi cụ thể của nhóm. Muốn kết luận chắc chắn thì cần tách tập tune và tập đánh giá, mà 5 query thì quá ít để tách.
- Tôi chưa cài được `requirements-local.txt` (PyTorch) trong thời lượng lab nên chưa có số liệu với embedding đa ngữ thật.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Từ chiến lược `StructureChunker` của bạn Quang, tôi học được rằng **đơn vị ngữ nghĩa quan trọng hơn ranh giới ngữ pháp**: tôi chọn "một khoản" vì nó là ranh giới có sẵn dễ nhận biết nhất, nhưng đơn vị mà người đọc thực sự cần để trả lời một câu hỏi lại là "cả Điều" — và đó chính xác là chỗ tôi mất điểm ở Q3. Bài học thứ hai đến từ bạn Hải: `RecursiveChunker` có sẵn, chỉ đổi `chunk_size` từ 400 lên 650 mà đạt 9/10 bằng đúng chiến lược tôi tự viết. Nó nhắc tôi rằng **tune tham số nên làm trước khi viết code mới**, vì nó rẻ hơn nhiều và tái dùng được khi đổi domain.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 9 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 9 / 10 |
| **Tổng phần cá nhân** | **58 / 60** |
