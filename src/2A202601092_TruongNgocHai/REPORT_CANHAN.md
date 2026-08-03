# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trương Ngọc Hải - 2A202601092
**Nhóm:** 3HQ
**Ngày:** 3/8/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)
Độ tương tự cosine là độ đo dùng để đo mức độ tương đồng về mặt ngữ nghĩa giữa 2 vector biểu diễn. Độ đo cosine similarity có giá trị trong khoảng [-1;1]. 

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ đo càng cao thì mức độ tương đồng giữa 2 vector biểu diễn ngữ nghĩa càng cao.

**Ví dụ có độ tương tự CAO:**
- Câu A: Hôm nay tôi đi học.
- Câu B: Tôi đến trường đi học hôm nay.
- Tại sao tương đồng: Cùng biểu diễn một nghĩa: tôi đi học hôm nay

**Ví dụ có độ tương tự THẤP:**
- Câu A: Hệ mặt trời có 8 hành tinh.
- Câu B: Chủ tịch Hồ Chí Minh ra đi tìm đường cứu nước vào ngày 5/6/1911.
- Tại sao khác: Hai câu có ý nghĩa hoàn toàn khác nhau

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:*
Độ đo cosine similarity phụ thuộc vào góc của hai vector, còn độ đo Euclid phụ thuộc vào độ lớn vector nên nó không ổn định.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
Bước dịch giữa hai chunk:

500−50=450 ký tự

Số chunk:

10000 / [450] + 1 = 23 chunks

Đáp án: 23 chunks

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
Khi overlap = 100, bước dịch còn 500−100=400 ký tự, nên số chunk tăng lên 25 chunks. Overlap lớn hơn giúp giữ lại ngữ cảnh và hạn chế việc thông tin quan trọng bị cắt đứt tại ranh giới giữa các chunk, nhưng làm tăng dữ liệu trùng lặp và chi phí xử lý.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
Regex dùng để nhận diện vị trí kết thúc câu qua các dấu ., !, ?. Trước khi tách, hàm tạm thay dấu chấm trong chữ viết tắt như TS., Dr. và số thập phân như 3.14 bằng <DOT>, nhờ đó các trường hợp này không bị hiểu nhầm là kết thúc câu.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
Hàm ưu tiên tách theo separator. Nếu không thể tách tiếp thì cắt cứng theo chunk_size. Các đoạn nhỏ sau đó được gom lại để tránh tạo quá nhiều chunk vụn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
Mỗi tài liệu được lưu cùng metadata, embedding và ID riêng. Khi tìm kiếm, query chỉ được embed một lần, sau đó tính độ tương đồng và lấy top_k kết quả tốt nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
Tôi lọc metadata trước rồi mới xếp hạng để không bỏ sót kết quả phù hợp. Khi xoá, hệ thống loại toàn bộ chunk thuộc cùng một doc_id.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
Prompt gồm ba phần: Instruction, Context và Question. Agent tìm các chunk liên quan, đưa vào Context kèm nguồn rồi mới gọi LLM; nếu không có dữ liệu thì trả thông báo ngay.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
# Dán kết quả (output) của: pytest tests/ -v
===================================== test session starts =====================================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0 -- D:\Miniconda\envs\ai-action\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Admin\OneDrive - Hanoi University of Science and Technology\Desktop\lab7
plugins: anyio-4.14.2, langsmith-0.10.10, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 42 items                                                                             

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED    [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED             [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED      [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED       [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED            [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED  [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED   [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED   [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED              [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED          [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED     [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED       [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED             [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED  [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED    [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED     [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED              [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED             [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED        [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED    [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED   [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED         [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED   [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

===================================== 42 passed in 0.22s ==
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | cao / thấp | | |
| 2 | | | cao / thấp | | |
| 3 | | | cao / thấp | | |
| 4 | | | cao / thấp | | |
| 5 | | | cao / thấp | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:*

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
