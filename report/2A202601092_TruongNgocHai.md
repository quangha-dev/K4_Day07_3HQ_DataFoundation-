# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trương Ngọc Hải\
**MSSV:** 2A202601092\
**Nhóm:** 3HQ\
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

**Gói bài làm của tôi:** `src/2A202601092_TruongNgocHai/` · **Chiến lược cá nhân:** `RecursiveChunker(chunk_size=650)` — tune chunker có sẵn theo domain thay vì viết class mới.

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector gần như cùng hướng trong không gian embedding, nghĩa là mô hình coi hai đoạn text nói về cùng một chuyện. Cosine chỉ quan tâm góc giữa hai vector, không quan tâm vector đó dài hay ngắn.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sàn thương mại điện tử phải công bố quy chế hoạt động."
- Câu B: "Quy chế hoạt động của sàn giao dịch phải được công khai."
- Tại sao tương đồng: cùng một nghĩa vụ pháp lý của sàn, chỉ đảo trật tự câu và thay "công bố" bằng "công khai".

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Thủ tục đăng ký website cung cấp dịch vụ thương mại điện tử."
- Câu B: "Chính sách bảo vệ thông tin cá nhân của người tiêu dùng."
- Tại sao khác: một bên là thủ tục hành chính với Bộ Công Thương, một bên là quyền riêng tư của người mua — khác chủ thể, khác nghĩa vụ, không chia sẻ thuật ngữ nào.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Vì độ dài vector text embedding chủ yếu phản ánh **độ dài đoạn văn**, không phản ánh nội dung. Euclid sẽ coi một câu ngắn và một đoạn dài cùng chủ đề là "xa nhau" chỉ vì chênh lệch độ lớn, còn cosine chuẩn hoá độ lớn đi nên so được đúng phần ngữ nghĩa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Mỗi chunk mới tiến thêm `step = chunk_size − overlap = 500 − 50 = 450` ký tự.
> Số chunk = `ceil((10000 − 50) / 450)` = `ceil(9950 / 450)` = `ceil(22.11)`

> *Đáp án:* **23 chunk**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> `step` giảm còn 400 → số chunk = `ceil((10000 − 100) / 400) = ceil(24.75) = 25` chunk, tức là **tăng thêm 2 chunk**.
>
> Muốn overlap nhiều hơn vì nó là **bảo hiểm cho ranh giới**: khi một câu điều kiện hoặc một con số rơi đúng chỗ cắt, chunk kế bên vẫn giữ lại được phần đó nên thông tin vẫn có cơ hội lọt top-k. Đánh đổi là số vector phải embed và lưu tăng lên, và top-k dễ bị chiếm bởi mấy chunk gần trùng nhau.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của tôi khi lập trình các phần chính trong gói `src/2A202601092_TruongNgocHai/`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi không tách câu bằng một regex duy nhất mà làm **ba bước bảo vệ trước, tách sau**. Bước 1: thay dấu chấm trong các chữ viết tắt (`TS.`, `ThS.`, `GS.`, `Dr.`, `Prof.`…) bằng token `<DOT>` để không bị coi là hết câu. Bước 2: dùng lookbehind `(?<=\d)\.(?=\d)` bảo vệ dấu chấm trong **số thập phân**. Bước 3: mới tách bằng `([.!?]+["”’)\]]*)\s+` — phần `["”’)\]]*` cho phép dấu kết câu đứng trước dấu nháy hoặc ngoặc đóng, vì trong văn bản luật rất hay có dạng `…(sau đây gọi tắt là "sàn").` Sau khi tách xong mới đổi `<DOT>` ngược lại thành dấu chấm. Edge case: text rỗng hoặc chỉ có khoảng trắng trả `[]`, mọi câu đều được `strip()` và bỏ chuỗi rỗng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> `chunk()` lo phần kiểm tra đầu vào: text rỗng trả `[]`, và **`chunk_size <= 0` thì raise `ValueError`** thay vì để hàm chạy vào vòng lặp vô hạn. Toàn bộ đệ quy nằm trong `_split(current_text, remaining_separators)` với hai base case: (a) text đã ngắn hơn `chunk_size` → trả về nguyên; (b) hết separator **hoặc** separator là chuỗi rỗng → cắt cứng theo `chunk_size`. Separator hiện tại không xuất hiện trong text thì gọi lại với `later_separators` — mỗi lần gọi đệ quy đều **bớt đi ít nhất một separator** nên chắc chắn dừng. Phần tôi mất nhiều thời gian nhất là bước **gom**: sau khi split phải nối các mảnh liền nhau vào biến `pending` cho tới sát `chunk_size`; mảnh nào tự nó đã dài hơn `chunk_size` thì flush `pending` ra trước rồi mới đệ quy xuống separator ưu tiên thấp hơn. Bỏ bước này thì kết quả ra hàng loạt chunk vụn vài ký tự.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> `_make_record(doc)` chuẩn hoá mỗi `Document` thành record `{id, content, metadata, embedding}`, trong đó metadata được **copy** ra dict mới và `setdefault("doc_id", doc.id)` để `delete_document` luôn có khoá; id record ghép `doc.id` với `_next_index` nên nạp cùng một file hai lần cũng không trùng id. Tôi có viết nhánh đồng bộ sang ChromaDB, nhưng bọc trong `try/except` và **nếu Chroma lỗi thì tự đặt `_use_chroma = False`** để rơi về in-memory — nhờ vậy không bao giờ rơi vào tình huống "code đúng mà test đỏ" mà Phụ lục A cảnh báo. `_search_records(query, records, top_k)` embed query **một lần duy nhất ngoài vòng lặp**, tính dot product với từng record, sort giảm dần rồi cắt `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> **Lọc trước, xếp hạng sau.** Duyệt `_store` giữ lại record khớp **toàn bộ** cặp key/value trong `metadata_filter`, xong mới đưa tập còn lại vào `_search_records`. Làm ngược lại (lấy top-k rồi loại) có thể trả về rỗng dù store vẫn còn tài liệu hợp lệ. Khi `metadata_filter` là `None` tôi gọi thẳng `_search_records` trên toàn bộ `_store` — cùng một hàm với `search()` nên hai đường không thể lệch nhau, đó chính là test `test_no_filter_returns_all_candidates`. `delete_document` lọc lại `_store` bỏ mọi record có `metadata['doc_id']` khớp, so sánh số lượng trước/sau để trả `True`/`False`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> `__init__` chỉ lưu `store` và `llm_fn`; agent không tự embed lại mà dùng kết quả của store. Tôi tách `build_prompt()` ra thành method riêng để test và debug được độc lập với `answer()`. Context ghép từ các chunk theo dạng `[1] …`, `[2] …` — đánh số để câu trả lời trích dẫn được về đúng chunk. Prompt gồm instruction ("chỉ dùng context bên dưới, nếu context không đủ thì nói rõ là không biết") → Context → Question → nhãn `Answer:`. Khi không có kết quả nào, `build_prompt` chèn câu "No relevant context was found in the knowledge base" thay vì để phần Context trống, để LLM biết rõ là nó không có gì để dựa vào chứ không tự bịa.

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

============================== 42 passed in 0.28s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

> Lệnh chấm bài làm của tôi trong repo chung của nhóm:
> `$env:LAB_SOLUTION_PACKAGE="src.2A202601092_TruongNgocHai"; python -m pytest tests -v`

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Đo bằng `compute_similarity` trong gói của tôi. Cột `mock` = `MockEmbedder` (mặc định của 42 test); cột `lexical` = `LexicalEmbedder` TF-IDF (`lexical_embedding.py`) — backend nhóm dùng chung để benchmark.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế (mock) | Điểm thực tế (lexical) | Đúng? |
|---|---|---|---|---|---|---|
| 1 | Sàn TMĐT phải công bố quy chế hoạt động | Quy chế hoạt động của sàn giao dịch phải được công khai | cao | −0.2166 | 0.3605 | mock **SAI**, lexical Đúng |
| 2 | Người bán trên sàn phải cung cấp thông tin về hàng hóa | Trách nhiệm của người bán là cung cấp đầy đủ thông tin hàng hóa | cao | 0.2530 | 0.2451 | Đúng cả hai (nhưng mock chỉ đúng do may) |
| 3 | Thủ tục đăng ký website cung cấp dịch vụ TMĐT | Chính sách bảo vệ thông tin cá nhân của người tiêu dùng | thấp | 0.1703 | **0.0000** | Đúng (lexical dứt khoát hơn) |
| 4 | Cơ chế rà soát và xác nhận nội dung hợp đồng | Khách hàng được rà soát, sửa đổi và xác nhận nội dung giao dịch | cao | 0.0908 | **0.4828** | mock **SAI**, lexical Đúng |
| 5 | Thời hạn trả lời đề nghị giao kết hợp đồng | Phương thức thanh toán áp dụng cho hàng hóa dịch vụ | thấp | −0.1859 | **0.0000** | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> **Cặp 1 với `MockEmbedder`: −0.2166.** Hai câu gần như đồng nghĩa hoàn toàn mà lại ra số **âm**, tức là mô hình coi chúng *ngược hướng* nhau. Đặt cạnh cặp 2 (mock ra 0.2530, tình cờ "đúng") thì rõ vấn đề: mock là hash MD5 nên mọi điểm số chỉ là nhiễu ngẫu nhiên, và **một kết quả đúng của nó cũng không có giá trị gì** vì nó đúng do may chứ không do hiểu.
>
> Điều này nói lên rằng embedding không phải bản thân câu văn mà chỉ là **input để xếp hạng**, và chất lượng xếp hạng bị chặn trên bởi chất lượng mô hình nhúng. Cặp 3 và cặp 5 với lexical ra đúng **0.0000** cũng đáng chú ý theo hướng ngược lại: TF-IDF chỉ đo trùng từ, hai câu không chia sẻ token nào thì bằng 0 tuyệt đối — nó không "hiểu" là hai câu không liên quan, nó chỉ thấy không có từ chung. Đây là giới hạn tôi phải ghi nhớ khi đọc điểm số ở mục 5.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân trong gói `src/2A202601092_TruongNgocHai/`. 5 câu hỏi này trùng với các thành viên cùng nhóm (xem `REPORT_NHOM.md`).

**Cấu hình:** `RecursiveChunker(chunk_size=650)`, separator `["\n\n", "\n", ". ", " ", ""]` · corpus `data/k4_ecommerce` (9 tài liệu) → **52 chunk** · embedder `LexicalEmbedder` (dùng chung cả nhóm) · `top_k=3`
**Lệnh tái tạo:** `$env:EMBEDDING_PROVIDER="lexical"; python bench.py recursive_hai`

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? | Câu trả lời của Agent (tóm tắt) |
|---|---|---|---|---|---|
| 1 | Không công bố rõ thời hạn trả lời thì sau bao lâu đề nghị giao kết hết hiệu lực? | `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_5` — Điều 20 **khoản 1** ("trường hợp CÓ công bố") | 0.3668 | **Một phần** — sai khoản; chunk chứa "12 (mười hai) giờ" đứng top-2 (0.3606) | Trả lời theo khoản 1, thiếu mốc 12 giờ ở top-1 |
| 2 | Sàn phải thông báo trước bao nhiêu ngày khi thay đổi quy chế? | `nd52-quy-che-hoat-dong-san::chunk_3` — Điều 38 khoản 3 | 0.2677 | **Có** — chứa "ít nhất 5 ngày" | Trả lời đúng 5 ngày |
| 3 | Cơ chế rà soát và xác nhận hợp đồng phải hiển thị thông tin gì? | `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_2` — Điều 18, câu dẫn **+ danh sách a/b/c** | 0.3230 | **Có** — chứa "Tổng giá trị của hợp đồng" | Liệt kê đủ các thông tin bắt buộc hiển thị |
| 4 | Chính sách kiểm hàng có bắt buộc không? (**có filter** `customer_role=buyer`) | `nd85-2021-...::chunk_5` — mục 4 | 0.3160 | **Có** — chứa "chính sách kiểm hàng" | Trả lời đúng theo NĐ 85/2021, không lẫn bản 2013 |
| 5 | Giá niêm yết không nói rõ đã gồm thuế/phí thì hiểu sao? | `seller-listing::chunk_3` — Điều 31 khoản 2 | 0.2405 | **Có** — chứa "được hiểu là đã bao gồm mọi chi phí" | Trả lời đúng khoản 2 Điều 31 |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5 / 5**
**Điểm chunk-level theo rubric `docs/EVALUATION.md`:** **9 / 10** (Q1 chỉ được 1 vì chunk chứa đáp án đứng top-2 chứ không phải top-1).

### Vì sao tôi chọn tune thay vì viết chunker mới

Trong nhóm có hai bạn viết class chunker riêng (`ParagraphChunker`, `StructureChunker`). Tôi cố tình đi hướng khác để trả lời một câu hỏi cụ thể: **một chunker generic được tune tử tế thì cách một chunker viết riêng theo domain bao xa?**

| Cấu hình | Chunks | Điểm | Ghi chú |
|---|---|---|---|
| `RecursiveChunker(400)` — baseline mặc định | 92 | 7/10 | Quá vụn với văn bản luật, khoản bị tách khỏi tiêu đề Điều |
| **`RecursiveChunker(650)` — của tôi** | **52** | **9/10** | Một Điều trung bình nằm gọn trong một chunk |

**Chỉ đổi một con số, không thêm một dòng code nào, mà được thêm 2 điểm** — bằng đúng điểm của bạn Hà với chunker tự viết, và chỉ kém bạn Quang 1 điểm. Kết luận tôi rút ra: tune tham số nên là việc **làm trước**, vì nó rẻ hơn nhiều lần và tái dùng được ngay khi đổi sang domain khác, còn chunker viết riêng thì gắn chặt với đặc điểm của một loại tài liệu.

### Failure case của tôi — Q1, có bằng chứng từ top-k

| Rank | doc_id::chunk | score | Chứa anchor `12 (mười hai) giờ`? | Nội dung |
|---|---|---|:---:|---|
| 1 | `nd52-quy-trinh...::chunk_5` | **0.3668** | ✗ | Điều 20 **khoản 1**: "Trường hợp thương nhân… **có** công bố rõ thời hạn trả lời…" |
| 2 | `nd52-quy-trinh...::chunk_6` | **0.3606** | **✓** | Điều 20 **khoản 2**: "Trường hợp… **không** công bố rõ thời hạn… **12 (mười hai) giờ**" |
| 3 | `nd52-quy-trinh...::chunk_3` | 0.2550 | ✗ | Điều 17, thông tin phải lưu trữ được |

**Nguyên nhân.** Câu hỏi hỏi trường hợp "**không** công bố rõ thời hạn", đáp án nằm ở khoản 2. Nhưng ranh giới đệ quy của tôi rơi **đúng vào giữa khoản 1 và khoản 2** của Điều 20, tách hai vế "có công bố" và "không công bố" thành hai chunk riêng. Hai khoản này gần như giống hệt nhau về từ vựng — chỉ khác đúng một chữ "không" — nên TF-IDF cho điểm gần bằng nhau: **chênh lệch chỉ 0.0062**. Chữ "không" là từ cực kỳ phổ biến nên IDF của nó gần 0, tức là **từ mang toàn bộ ý nghĩa phân biệt lại là từ mà TF-IDF gần như bỏ qua**.

Đây là bài học đắt nhất của tôi trong buổi lab: chunk **đúng chủ đề** không có nghĩa là chunk **đúng trường hợp**, và với embedder từ vựng thì các cặp quy định dạng "nếu có… / nếu không…" là điểm mù có hệ thống.

**Đề xuất sửa:**
1. **Thêm overlap giữa các mảnh đệ quy** (hiện `RecursiveChunker` cắt sạch, không chồng lấn) để hai khoản liền nhau chia sẻ phần biên — mỗi thông tin có nhiều hơn một cơ hội lọt top-1.
2. **Giữ cả Điều 20 làm một chunk** như cách bạn Quang làm — chunk đó chứa cả hai khoản nên không thể chọn nhầm; bạn Quang được 2/2 ở Q1.
3. Ở tầng retrieval: lấy top-5 rồi rerank bằng mô hình cross-encoder, vì cross-encoder đọc cả câu hỏi lẫn chunk cùng lúc nên "không" mới có trọng lượng.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Điều tôi thấy giá trị nhất là cách nhóm chấm điểm **ở mức chunk chứ không ở mức `doc_id`**. Cả 11 cấu hình của nhóm đều đạt 10/10 doc-level — nếu chấm kiểu đó thì bài của tôi và bài của mọi người đều "hoàn hảo" và tôi đã không bao giờ phát hiện ra lỗi Q1 ở trên. Thứ hai, từ hai bạn viết chunker riêng tôi học được rằng phần quyết định điểm không nằm ở ý tưởng chia chunk mà ở **cách xử lý các trường hợp biên** (đoạn quá ngắn, tiêu đề trơ trọi, câu dẫn tách khỏi danh sách) — cả hai bạn đều mất/được 1–2 điểm chỉ vì mấy chi tiết đó, đúng bằng khoảng cách giữa bốn chiến lược khác hẳn nhau.

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
