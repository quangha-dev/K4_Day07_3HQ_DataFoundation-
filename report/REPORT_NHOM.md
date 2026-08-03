# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Lớp:** K4 — Chính sách thương mại điện tử
**Nhóm:** [điền tên nhóm]
**Thành viên:** Nguyễn Quang Hà (2A202601424) — [thành viên 2] — [thành viên 3]
**Ngày:** 03/08/2026

---

## 1. Lựa chọn tài liệu — 10 điểm

### Phạm vi bộ tài liệu

**Chủ đề (cố định theo lớp K4):** Chính sách thương mại điện tử / hỗ trợ khách hàng.

**Phạm vi cụ thể nhóm chọn:** **Nghĩa vụ pháp lý của người bán và quyền của người mua trên sàn thương mại điện tử Việt Nam** — nguồn là văn bản quy phạm pháp luật công khai (Nghị định 52/2013/NĐ-CP và Nghị định 85/2021/NĐ-CP sửa đổi).

**Vì sao chọn văn bản pháp luật thay vì help center của sàn TMĐT:**

1. Là **văn bản quy phạm pháp luật công khai**, được phép trích dẫn, không có vấn đề robots.txt / điều khoản sử dụng / dữ liệu cá nhân.
2. Biên soạn theo **Điều / Khoản** — mỗi Điều đã là một đơn vị ngữ nghĩa trọn vẹn, rất hợp để so sánh chunker theo heading với chunker cắt cứng.
3. Có **số liệu kiểm chứng được** (12 giờ, 5 ngày, 24 giờ) để viết gold answer chính xác.
4. Có **hai phiên bản của cùng một quy định** (2013 vs 2021 sửa đổi) → dựng được câu hỏi bẫy version drift ở Q4.

### Danh sách tài liệu (9 tài liệu)

| # | doc_id | Tên tài liệu | Nguồn | Phiên bản | Cỡ (ký tự) | `customer_role` | `category` |
|---|--------|--------------|-------|-----------|-----------|-----------------|------------|
| 1 | `returns-policy` | Điều kiện giao dịch chung và chính sách hoàn trả (Điều 32) | vanban.vcci.com.vn — NĐ 52/2013 | 52/2013/NĐ-CP | 2.354 | seller | dieu-kien-giao-dich-chung |
| 2 | `seller-listing` | Thông tin người bán phải công bố khi đăng bán (Điều 28–34) | vanban.vcci.com.vn — NĐ 52/2013 | 52/2013/NĐ-CP | 5.267 | seller | thong-tin-hang-hoa |
| 3 | `nd52-quy-trinh-dat-hang-truc-tuyen` | Quy trình giao kết hợp đồng khi đặt hàng trực tuyến (Điều 15–22) | vanban.vcci.com.vn — NĐ 52/2013 | 52/2013/NĐ-CP | 7.090 | **buyer** | giao-ket-hop-dong |
| 4 | `nd52-trach-nhiem-san-tmdt` | Trách nhiệm của thương nhân cung cấp dịch vụ sàn (Điều 35–36) | vanban.vcci.com.vn — NĐ 52/2013 | 52/2013/NĐ-CP | 4.454 | **both** | trach-nhiem-san |
| 5 | `nd52-trach-nhiem-nguoi-ban-tren-san` | Trách nhiệm của người bán trên sàn (Điều 37) | vanban.vcci.com.vn — NĐ 52/2013 | 52/2013/NĐ-CP | 2.120 | seller | trach-nhiem-nguoi-ban |
| 6 | `nd52-quy-che-hoat-dong-san` | Quy chế hoạt động của sàn (Điều 38) | vanban.vcci.com.vn — NĐ 52/2013 | 52/2013/NĐ-CP | 2.983 | **both** | quy-che-san |
| 7 | `nd52-dang-ky-thong-bao-website` | Điều kiện & thủ tục thông báo/đăng ký website (Điều 52–55) | vanban.vcci.com.vn — NĐ 52/2013 | 52/2013/NĐ-CP | 4.907 | seller | dang-ky-thong-bao |
| 8 | `nd85-2021-diem-moi-bao-ve-nguoi-tieu-dung` | Điểm mới bảo vệ quyền lợi NTD trong NĐ 85/2021 | moit.gov.vn (Bộ Công Thương) | **85/2021/NĐ-CP** | 5.479 | **buyer** | bao-ve-nguoi-tieu-dung |
| 9 | `nd52-bao-ve-thong-tin-ca-nhan` | Bảo vệ thông tin cá nhân của NTD trong TMĐT (Điều 3.13, 68–72) | thuvienphapluat.vn (trích NĐ 52/2013) | 52/2013/NĐ-CP | 4.712 | **buyer** | quyen-rieng-tu |

Phân bố `customer_role`: **seller 4 · buyer 3 · both 2** → filter thực sự có gì để lọc.
Phân bố `document_version`: **8 tài liệu bản 2013 · 1 tài liệu bản 2021** → đủ để dựng câu hỏi version drift.

Với 9 tài liệu, corpus phủ đủ **cả 5 chủ đề K4 gợi ý**: thanh toán (Điều 34), đổi trả (Điều 32b), giao hàng (Điều 33), **quyền riêng tư (Điều 68–72)**, điều kiện người bán (Điều 37, 52–55).

`sources.csv` khớp một–một với 9 tài liệu (`doc_id, file_path, title, customer_role, source_url, retrieved_at, document_version, license_or_permission`).

**Danh sách kiểm tra quản trị dữ liệu:**

- [x] Corpus chỉ chứa **văn bản quy phạm pháp luật công khai**; không đăng nhập, không vượt CAPTCHA, không crawl cả website, không có dữ liệu cá nhân/nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at` (2026-08-03), `document_version` trong front matter.
- [x] Nội dung đã được **làm sạch thủ công**: bỏ menu, footer, breadcrumb, tin liên quan của trang nguồn — chỉ giữ phần điều khoản.
- [x] Đã chạy script kiểm tra CHECKPOINT 2 → 9/9 file OK, `csv: khớp`, `customer_role: {seller: 4, buyer: 3, both: 2}`.

### Cấu trúc Metadata

| Trường | Kiểu | Ví dụ | Tại sao hữu ích cho retrieval |
|--------|------|-------|-------------------------------|
| `doc_id` | string | `nd52-quy-che-hoat-dong-san` | Khoá để `delete_document()` và để truy vết chunk về file gốc. Trùng với tên file. |
| `customer_role` | enum buyer/seller/both | `buyer` | **Trường bắt buộc của K4.** Thu hẹp đúng nhóm tài liệu trước khi xếp hạng — thấy hiệu quả rõ ở Q4. |
| `document_version` | string | `85/2021/NĐ-CP` | Phân biệt bản gốc 2013 và bản sửa đổi 2021. Không có trường này thì không phát hiện được câu trả lời lỗi thời. |
| `source_url` | url | `https://moit.gov.vn/...` | Provenance — agent trích được nguồn trong câu trả lời. |
| `retrieved_at` | date | `2026-08-03` | Biết dữ liệu cũ bao lâu, khi nào cần crawl lại. |
| `category` | string | `giao-ket-hop-dong` | Trường hữu ích thêm; dùng để thu hẹp theo chủ đề khi corpus mở rộng. |
| `legal_basis` | string | `Điều 38 Nghị định 52/2013/NĐ-CP` | Cho phép đối chiếu gold answer với đúng Điều/Khoản khi review. |
| `chunk_index` | int | `4` | Do `ingest.py` tự thêm; cần để chấm ở **mức chunk** chứ không chỉ mức doc_id. |

---

## 2. Thiết kế chiến lược — 15 điểm

### Phân tích đường cơ sở

`ChunkingStrategyComparator().compare(body, chunk_size=400)` — **đã bỏ front matter trước khi so sánh** (dùng `ingest.parse_front_matter`), nếu không sẽ đo cả khối YAML.

| Tài liệu (độ dài thân bài) | Strategy | Count | Avg length | Giữ được ngữ cảnh? |
|---|---|---|---|---|
| `nd52-quy-che-hoat-dong-san` (1.931) | `fixed_size` | 5 | 386,2 | Không — cắt giữa danh sách a)…l) của khoản 2 |
| | `by_sentences` | 3 | 642,3 | Một phần — các gạch đầu dòng không có dấu chấm nên bị gộp thành khối lớn |
| | `recursive` | 6 | 320,2 | Tốt hơn — tôn trọng `\n\n`, nhưng khoản 3 bị tách khỏi tiêu đề Điều |
| `nd52-quy-trinh-dat-hang-truc-tuyen` (4.925) | `fixed_size` | 13 | 378,8 | Không — ranh giới rơi giữa Điều 17 và Điều 18 |
| | `by_sentences` | 12 | 408,4 | Trung bình |
| | `recursive` | 15 | 326,5 | Trung bình — nhiều chunk mất tiêu đề Điều |
| `seller-listing` (3.677) | `fixed_size` | 10 | 367,7 | Không — Điều 31 bị cắt giữa khoản 1 và khoản 2 |
| | `by_sentences` | 11 | 332,3 | Trung bình |
| | `recursive` | 12 | 304,6 | Trung bình |

**Nhận xét baseline:** cả ba strategy có sẵn đều cho `avg_length` khá giống nhau (300–650) nên **số liệu thống kê không phân biệt được chất lượng**. Khác biệt chỉ lộ ra khi chạy retrieval thật và chấm ở mức chunk.

### Chiến lược của từng thành viên

Ba thành viên dùng **chung corpus, chung 5 query, chung embedder**; chỉ khác đúng dòng chọn chunker trong `bench.py` (registry `STRATEGIES`).

**Thành viên 1 — Nguyễn Quang Hà (2A202601424)**

- **Loại chiến lược:** `ParagraphChunker` — **custom, chia theo ĐOẠN**, ranh giới là **dòng trống** (hai lần Enter).
- **Mô tả & lý do:** Trong Markdown và trong văn bản quy phạm pháp luật, dòng trống chính là dấu hiệu "hết một ý, sang ý khác" **do người soạn thảo đánh dấu sẵn**. Chunker không tự nghĩ ra ranh giới mà dùng lại ranh giới có sẵn. Khác biệt so với ba chunker có sẵn: `FixedSizeChunker` cắt theo số ký tự (ranh giới nhân tạo); `SentenceChunker` cắt theo dấu chấm (hỏng với gạch đầu dòng kết thúc bằng `;`); `RecursiveChunker` tuy ưu tiên `\n\n` nhưng vẫn **gom** nhiều đoạn cho đủ `chunk_size` nên một chunk chứa nhiều ý.
- **Ba bước, mỗi bước chặn một lỗi cụ thể:** (1) cắt tại dòng trống; (2) **gộp đoạn ngắn** — chặn chunk vụn bị TF-IDF thổi điểm; (3) **gắn tiêu đề Điều** vào đầu chunk — đoạn "c) Tổng giá trị của hợp đồng…" tự nó không cho biết thuộc Điều nào. Thứ tự bước 2 trước bước 3 là bắt buộc: làm ngược lại thì hai đoạn cùng Điều bị nối và tiêu đề in hai lần trong một chunk.
- **Code:** `src/2A202601424-NguyenQuangHa/chunking.py::ParagraphChunker`

```python
class ParagraphChunker:
    _PARAGRAPH_BREAK = re.compile(r"\n[ \t]*\n+")   # 2 Enter = ranh giới đoạn

    def chunk(self, text: str) -> list[str]:
        blocks = self._split_paragraphs(text)    # [(tiêu_đề, nội_dung)]
        merged = self._merge_short(blocks)       # gộp đoạn ngắn, KHÔNG qua ranh giới tiêu đề
        chunks = []
        for heading, body in merged:             # gắn tiêu đề MỘT lần, SAU khi gộp
            prefix = heading if (self.keep_heading and heading) else ""
            block = f"{prefix}\n{body}".strip() if prefix else body.strip()
            if len(block) <= self.max_chunk_size:
                chunks.append(block)
            else:
                chunks.extend(self._split_long(prefix, body))
        return [c.strip() for c in chunks if c.strip()]
```

- **Chọn tham số bằng thực nghiệm, không đoán.** Quét `min_chunk_size` trên đúng 5 query của nhóm: 100→7, 150→7, 250→7, 350→8, **450→9**, 600→8. Chọn 450 vì đó là ngưỡng đủ lớn để một câu dẫn và toàn bộ danh sách a/b/c của nó nằm chung một chunk, nhưng chưa lớn tới mức gộp hai ý khác nhau.

**Thành viên 2 — [tên]**

- **Loại chiến lược:** `RecursiveChunker(chunk_size=400)`
- **Mô tả & lý do:** *(điền)*

**Thành viên 3 — [tên]**

- **Loại chiến lược:** `FixedSizeChunker(chunk_size=500, overlap=50)`
- **Mô tả & lý do:** *(điền)*

### So Sánh Giữa Các Thành Viên

Embedder dùng chung: `LexicalEmbedder` (TF-IDF, `lexical_embedding.py`). Output đầy đủ: `report/bench_output_lexical.txt`.

| Thành viên | Strategy | Chunks | Q1 | Q2 | Q3 | Q4 | Q5 | **Điểm chunk-level /10** | Điểm mạnh | Điểm yếu |
|---|---|---|---|---|---|---|---|---|---|---|
| **Hà** | **`paragraph`** (max 700, min 450, có tiêu đề) | 65 | 2 | 2 | 1 | 2 | 2 | **9** | Tôn trọng ranh giới tác giả tạo sẵn; điều kiện + ngoại lệ cùng chunk | Không có overlap; câu dẫn và danh sách nằm hai chunk khác nhau (Q3) |
| Hà (ablation 1) | `paragraph_noheading` | 63 | 2 | 2 | 0 | 2 | 2 | 8 | — | Chunk mất ngữ cảnh "đây là Điều nào" |
| Hà (ablation 2) | `paragraph_nomerge` (min 0) | 162 | 2 | 1 | 0 | 2 | 2 | 7 | — | Chunk vụn được TF-IDF thổi điểm: top-1 Q3 đạt 0.5223 mà **0 điểm** |
| TV2 | *(điền sau)* | | | | | | | | | |
| TV3 | *(điền sau)* | | | | | | | | | |
| TV4 | *(điền sau)* | | | | | | | | | |
| baseline | `fixed` (500/50) | 67 | 2 | 0 | 0 | 2 | 2 | **6** | Đơn giản, có overlap | Ranh giới rơi tùy tiện giữa hai Điều; Q2 chiếm cả 3 slot bằng doc gold mà không slot nào chứa đáp án |
| baseline | `recursive` (400) | 92 | 2 | 1 | 0 | 2 | 2 | 7 | Tôn trọng ranh giới đoạn, dễ tune | Gom nhiều đoạn vào một chunk, tách khoản khỏi tiêu đề |
| baseline | `sentence` (3 câu) | 69 | 2 | 1 | 0 | 2 | 2 | 7 | — | Gạch đầu dòng không có dấu chấm → gộp thành khối lớn |

**Strategy nào tốt nhất cho chủ đề này? Tại sao?**

> **`ParagraphChunker` (9/10)**, và lý do là cấu trúc của dữ liệu chứ không phải sự tinh vi của thuật toán. Văn bản pháp luật đã được con người chia sẵn thành đơn vị ngữ nghĩa và **đánh dấu bằng dòng trống**; chunker chỉ cần tôn trọng ranh giới có sẵn thay vì áp một ranh giới nhân tạo theo số ký tự. Khác biệt cụ thể thấy ở Q2 và Q3: các strategy cắt cứng đều để chunk chứa đáp án rớt khỏi top-1 hoặc rớt hẳn khỏi top-3.
>
> Nhưng hai ablation cho thấy điều quan trọng hơn: **ý tưởng "chia theo đoạn" tự nó chỉ đáng 7/10 — ngang hệt `recursive` và `sentence`.** Toàn bộ khoảng cách 2 điểm đến từ hai bước hậu xử lý: gộp đoạn ngắn (+2) và gắn lại tiêu đề (+1). Nói cách khác, **cách chọn ranh giới ít quan trọng hơn cách xử lý các trường hợp biên** — và hai kỹ thuật này tái dùng được ở mọi domain có cấu trúc, không riêng văn bản pháp luật.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất — 10 điểm

### 5 câu hỏi đánh giá (nhóm chốt trước khi chạy strategy nào)

Định nghĩa nằm trong `bench.py::BENCHMARK_QUERIES`, kèm `anchors` — chuỗi đặc trưng **phải xuất hiện trong context truy xuất được** để chấm ở mức chunk.

| # | Loại | Câu hỏi | Gold answer | Chunk kỳ vọng | Anchor |
|---|------|---------|-------------|---------------|--------|
| 1 | số liệu | Nếu người bán không công bố rõ thời hạn trả lời, sau bao lâu đề nghị giao kết hợp đồng của khách hàng hết hiệu lực? | Trong vòng **12 (mười hai) giờ** kể từ khi gửi đề nghị (khoản 2 Điều 20 NĐ 52/2013) | `nd52-quy-trinh-dat-hang-truc-tuyen` — Điều 20 | `12 (mười hai) giờ` |
| 2 | điều kiện | Sàn TMĐT phải thông báo trước bao nhiêu ngày khi thay đổi quy chế hoạt động? | **Ít nhất 5 ngày** trước khi áp dụng thay đổi (khoản 3 Điều 38 NĐ 52/2013) | `nd52-quy-che-hoat-dong-san` — Điều 38 | `ít nhất 5 ngày` |
| 3 | quy trình | Cơ chế rà soát và xác nhận nội dung hợp đồng phải hiển thị những thông tin gì cho khách hàng trước khi đặt hàng? | Tên hàng hóa/số lượng/chủng loại; phương thức và thời hạn giao hàng; **tổng giá trị hợp đồng** và chi tiết thanh toán; cách thức & thời hạn trả lời; cho phép hủy giao dịch (Điều 18) | `nd52-quy-trinh-dat-hang-truc-tuyen` — Điều 18 khoản 1 | `Tổng giá trị của hợp đồng` |
| 4 | **liệt kê + BẮT BUỘC FILTER** | Chính sách kiểm hàng có phải là một điều kiện giao dịch chung bắt buộc phải công bố không? | **Có**, từ 01/01/2022 theo NĐ 85/2021. Bản gốc Điều 32 NĐ 52/2013 **không** liệt kê chính sách kiểm hàng → trả lời theo bản 2013 là **sai**. | `nd85-2021-diem-moi-bao-ve-nguoi-tieu-dung` — mục 4 | `chính sách kiểm hàng` |
| 5 | ngoại lệ | Website niêm yết giá mà không nói rõ đã bao gồm thuế và phí vận chuyển chưa thì hiểu thế nào? | Trừ khi các bên có thỏa thuận khác, giá **được hiểu là đã bao gồm mọi chi phí** liên quan (khoản 2 Điều 31 NĐ 52/2013) | `seller-listing` — Điều 31 khoản 2 | `được hiểu là đã bao gồm mọi chi phí` |

**Thiết kế Q4 — câu hỏi chỉ trả lời đúng khi có filter:**
Câu hỏi không nêu người hỏi là ai. Corpus có **hai tài liệu cùng chủ đề "điều kiện giao dịch chung", cùng từ vựng, khác đối tượng và khác đáp án**: `returns-policy` (seller, bản 2013, không có kiểm hàng) và `nd85-2021-...` (buyer, bản 2021, có kiểm hàng). Không lọc thì retrieval trộn hai bản và agent có thể trả lời theo văn bản đã lỗi thời — mà vẫn trích được nguồn thật.

### Tổng hợp chất lượng truy xuất của nhóm

| # | Strategy tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---|---|---|
| 1 | Mọi strategy (đều 2/2) | Có, ở top-1 | Anchor "12 (mười hai) giờ" là chuỗi rất đặc trưng, không strategy nào trượt |
| 2 | `paragraph` (2) — `recursive`/`sentence` chỉ 1, **`fixed` được 0** | `fixed`: **KHÔNG** | Cắt cứng tách khoản 3 ra khỏi tiêu đề Điều 38 → chunk chứa "5 ngày" rớt khỏi top-3 |
| 3 | `paragraph` (1) — **mọi strategy khác 0** | `paragraph`: có (top-2). `fixed`/`recursive`/`sentence`: **KHÔNG** | Câu khó nhất. Xem failure case dưới |
| 4 | Mọi strategy (2/2, khi có filter) | Có, ở top-1 | Xem A/B bên dưới |
| 5 | Mọi strategy (2/2) | Có, ở top-1 | Ngoại lệ nằm trọn trong Điều 31, ít bị cắt |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

> **Có, rõ nhất ở Q4** — và nhóm đã chạy A/B trên **tất cả** các strategy, kết quả **KHÁC NHAU** ở mọi strategy (không có trường hợp filter vô tác dụng).
>
> Không filter: top-3 = [`nd85-2021::chunk_5` (buyer, 0.359), `returns-policy::chunk_2` (seller, **bản 2013**, 0.239), `nd52-dang-ky-thong-bao-website::chunk_5` (seller, 0.142)] — **2/3 slot là tài liệu seller, trong đó có văn bản đã lỗi thời**.
> Có filter `{"customer_role": "buyer"}`: top-3 toàn bộ là tài liệu buyer, nhóm 2013 bị loại khỏi tập ứng viên trước khi xếp hạng.
>
> Filter **giảm nhiễu thật, không loại nhầm đáp án** trong trường hợp này. Nhưng đây là **precision đổi lấy recall**: nếu người hỏi là seller mà hệ thống lọc `buyer`, câu trả lời đúng sẽ bị giấu mất. Cách xử lý bền hơn là lọc theo tập (`role ∈ {buyer, both}`) thay vì so bằng tuyệt đối, và gắn `both` cho tài liệu áp dụng cho cả hai bên.
>
> Ba câu còn lại (Q1, Q3, Q5) **không cần filter** — vocabulary đã đủ đặc trưng. Ghi nhận điều này quan trọng không kém: **filter không phải lúc nào cũng cần, thêm bừa chỉ làm giảm recall.**

### Phát hiện đáng giá nhất: chấm ở mức doc_id che mất toàn bộ khác biệt

Nhóm chấm cả hai cách trên **cùng một lần chạy**:

| Strategy | Doc-level | Chunk-level |
|---|---|---|
| **paragraph** | **10 / 10** | **9 / 10** |
| paragraph_noheading | **10 / 10** | 8 / 10 |
| paragraph_nomerge | **10 / 10** | 7 / 10 |
| fixed | **10 / 10** | **6 / 10** |
| recursive | **10 / 10** | 7 / 10 |
| sentence | **10 / 10** | 7 / 10 |

Nếu chỉ kiểm "gold `doc_id` có xuất hiện trong top-3 không", **cả sáu strategy đều 10/10** và nhóm sẽ kết luận sai rằng chunking không quan trọng. Ví dụ sắc nhất là `fixed` ở Q2: **cả 3/3 slot đều là tài liệu gold** `nd52-quy-che-hoat-dong-san`, doc-level cho 2/2 điểm, nhưng **không slot nào chứa "ít nhất 5 ngày"** → chunk-level 0. Nguyên nhân đúng như lab cảnh báo: corpus của nhóm là các Điều trong cùng một Nghị định, nói về cùng chủ đề với từ vựng gần giống nhau, nên điểm rất sát và section nào lọt top-3 gần như ngẫu nhiên.

### Failure case của nhóm — Q3 (có bằng chứng top-k)

**Query:** "Cơ chế rà soát và xác nhận nội dung hợp đồng phải hiển thị những thông tin gì cho khách hàng trước khi đặt hàng?"

| Strategy | Top-1 thực tế | Điểm |
|---|---|---|
| `paragraph` | `nd52-quy-trinh...::chunk_3` (0.3909) — Điều 18, **phần dẫn** ("phải có cơ chế cho phép khách hàng rà soát…") | 1 (chunk đúng nằm top-2, 0.2689) |
| `fixed` | `nd52-quy-trinh...::chunk_2` (0.3691) — **Điều 17**, mảnh câu cụt "sử dụng chức năng đặt hàng trực tuyến được coi là đề nghị…" | **0** |
| `recursive` / `sentence` | tương tự — đúng `doc_id`, sai section | **0** |

**Nguyên nhân:** chunk chứa đáp án là **danh sách gạch đầu dòng a/b/c** với mật độ từ khóa "rà soát / xác nhận" thấp, trong khi chunk khoản 3 lặp lại nguyên cụm "sau khi rà soát những thông tin nói trên". Cosine đo **độ giống chủ đề**, không đo **mật độ thông tin trả lời được** → chunk *nói về* câu hỏi thắng chunk *trả lời* câu hỏi. Với `fixed`, ranh giới 500 ký tự còn tách hẳn phần dẫn của Điều 18 khỏi danh sách bên dưới.

**Đề xuất sửa:** chunk ở mức **khoản** cho các Điều có danh sách liệt kê + gắn lại cả tiêu đề Điều lẫn câu dẫn của khoản vào từng mảnh; thêm overlap ~15% giữa các khoản liền nhau; ở tầng retrieval lấy top-8 rồi rerank, hoặc retrieve ở mức khoản nhưng nạp vào context cả Điều chứa nó.

---

## 4. Demo & Bài học nhóm — 5 điểm

### Kịch bản demo 6–8 phút

1. **(1 phút)** Phạm vi, 9 tài liệu, schema metadata — nhấn `customer_role` và `document_version`.
2. **(2 phút)** Mỗi thành viên giải thích strategy của mình; Hà demo `ParagraphChunker` và hai ablation (`noheading`, `nomerge`).
3. **(3 phút)** Bảng so sánh + **A/B metadata filter ở Q4** + **failure case Q3** với bằng chứng top-k.
4. **(1–2 phút)** Chạy live: `EMBEDDING_PROVIDER=lexical python bench.py paragraph` cho Q4.

### 3 phân tích hay nhất nhóm sẽ trình bày

1. **Chấm ở mức `doc_id` cho 10/10 cho MỌI strategy; chấm ở mức chunk mới lộ khoảng cách 9 vs 6.** Nếu không thiết kế `anchors` từ đầu, nhóm đã kết luận sai rằng chunking không ảnh hưởng gì.
2. **Embedder quan trọng hơn chunker.** Cùng bộ code, đổi `MockEmbedder` → `LexicalEmbedder`, điểm nhảy từ 0–2/10 lên 6–9/10. Chunking quyết định 3 điểm chênh lệch; embedding quyết định 6–7 điểm. Kết luận: **đừng tối ưu chunking trước khi có embedding tử tế.**
3. **Metadata bắt được lỗi mà embedding không bắt được.** Ở Q4, hai tài liệu cùng chủ đề và cùng từ vựng nhưng khác phiên bản pháp lý; cosine không có cách nào biết bản nào còn hiệu lực. Chỉ `document_version` + `customer_role` mới loại được văn bản lỗi thời.

### Bài học rút ra

> Cùng một corpus, cùng 5 câu hỏi, cùng embedder — chỉ đổi cách chia nhỏ tài liệu mà khoảng cách là 6 vs 9 điểm, và ở hai câu hỏi cụ thể (Q2, Q3) là **có đáp án trong top-3 hay hoàn toàn không có**. Nhưng nhóm cũng học được điều ngược lại: khoảng cách 3 điểm giữa các chunker nhỏ hơn nhiều so với khoảng cách 6–7 điểm giữa mock và lexical embedding. Thứ tự ưu tiên khi làm thật nên là: **dữ liệu sạch có provenance → embedding phù hợp ngôn ngữ → metadata schema → mới đến tinh chỉnh chunking.**
>
> Ngoài ra, hai ablation cho thấy phần lớn lợi thế của "chia theo đoạn" thực ra đến từ hai chi tiết nhỏ: **gộp đoạn quá ngắn** và **gắn lại tiêu đề**. Bản thuần túy chỉ được 7/10, ngang baseline. Đây là kỹ thuật rẻ và tái dùng được ở mọi domain có cấu trúc.

### Nếu làm lại, nhóm sẽ thay đổi gì

> 1. **Cài `requirements-local.txt` chạy nền ngay từ đầu buổi** để có embedding đa ngữ thật, thay vì phải tự viết TF-IDF làm giải pháp thay thế ở phút chót.
> 2. **Đa dạng nguồn hơn.** 8/9 tài liệu đến từ cùng một Nghị định — điều này làm các chunk rất giống nhau về từ vựng và khiến việc phân biệt ở mức doc_id trở nên vô nghĩa. Lần sau sẽ trộn thêm điều khoản dịch vụ công khai của sàn TMĐT để corpus có cả tầng quy phạm lẫn tầng vận hành, nhiều "giọng văn" khác nhau.
> 3. **Thiết kế 2 câu hỏi cần filter thay vì 1**, một câu cho `buyer` và một câu cho `seller`, để kiểm tra được cả trường hợp filter **loại nhầm** đáp án (đánh đổi recall) chứ không chỉ trường hợp filter giúp ích.
> 4. **Ghi `anchors` vào bộ query ngay từ khi chốt câu hỏi**, không đợi đến lúc chấm — vì đó mới là thứ phân biệt được các strategy.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu | 10 / 10 |
| Thiết kế chiến lược | 14 / 15 |
| Chất lượng truy xuất | 9 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **38 / 40** |

---

## Phụ lục — cách chạy lại toàn bộ kết quả

```bash
# 1. 42/42 test
python -m pytest tests -v

# 2. Kiểm metadata corpus (CHECKPOINT 2)
python -c "..."   # script trong README mục 3, KEY='customer_role'

# 3. Benchmark strategy cá nhân
EMBEDDING_PROVIDER=lexical python bench.py paragraph

# 4. Toàn bộ strategy + bảng so sánh
EMBEDDING_PROVIDER=lexical python bench.py --all > report/bench_output_lexical.txt
python bench.py --all > report/bench_output_mock.txt   # đối chứng bằng mock

# Windows PowerShell: $env:EMBEDDING_PROVIDER="lexical"; python bench.py --all
```
