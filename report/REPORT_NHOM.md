# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Lớp:** D305
**Nhóm:** 3HQ
**Thành viên:**

| Họ tên | MSSV | Vai điều phối | Strategy cá nhân | Thư mục bài làm |
|---|---|---|---|---|
| Nguyễn Quang Hà | 2A202601424 | Data curator · Demo coordinator | `paragraph` — chia theo **đoạn** | `src/2A202601424-NguyenQuangHa/` |
| Nguyễn Nhật Quang | K4_01452 | Benchmark owner | `structure` — chia theo **cấu trúc / heading** | `src/K4_01452_NguyenNhatQuang/` |
| Trương Ngọc Hải | 2A202601092 | Strategy owner | `recursive_hai` — đệ quy, `chunk_size=650` | `src/2A202601092_TruongNgocHai/` |
| Vũ Văn Huy | K4_2A202601342 | Strategy owner | `fixed_huy` — cố định 600, overlap 150 | `src/K4_2A202601342_VuVanHuy/` |

Bốn chiến lược **không trùng nhau**, và có ít nhất một người (Quang) chunk **theo heading/section** đúng như CP7 yêu cầu.
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

Bốn thành viên dùng **chung corpus, chung 5 query, chung embedder (`LexicalEmbedder` TF-IDF), chung `top_k=3`, chung cách chấm điểm mức chunk**; chỉ khác **đúng một dòng chọn chunker** trong registry `STRATEGIES` của `bench.py`.

Để bảng so sánh thực sự công bằng, cả bốn chiến lược được chạy **trong cùng một tiến trình** bằng `python bench.py --group`. Hàm `member_chunker(package, class_name)` nạp class chunker trực tiếp từ thư mục bài làm của từng người (`src/<MSSV>-<HoTen>/`), nên không ai phải copy code của ai và cũng không có nguy cơ một biến nào đó bị lệch giữa các lần chạy riêng lẻ. Phần chấm điểm cá nhân không bị ảnh hưởng: 42 test vẫn chạy trên đúng gói của từng người qua biến `LAB_SOLUTION_PACKAGE`.

**Bốn chiến lược khác nhau về ĐƠN VỊ NGỮ NGHĨA, không chỉ khác tham số:**

| Thành viên | Ranh giới chunk là gì | Đơn vị thu được |
|---|---|---|
| Hà | dòng trống (2 lần Enter) | một **khoản** |
| Quang | dòng tiêu đề (`## Điều n.`) | một **Điều** trọn vẹn |
| Hải | đệ quy `\n\n` → `\n` → `. ` → ` ` | khối gom tới ~650 ký tự |
| Huy | số ký tự cố định + overlap | cửa sổ trượt 600/150 |

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

**Thành viên 2 — Nguyễn Nhật Quang (K4_01452)**

- **Loại chiến lược:** `StructureChunker` — **custom, chia theo CẤU TRÚC**, ranh giới là **dòng tiêu đề** (`## Điều 38. ...`, `# Chương V`, `Mục 2`). Đây cũng là chunker "theo heading hoặc section" mà CP7 bắt buộc nhóm phải có ít nhất một người làm.
- **Mô tả & lý do:** Văn bản quy phạm pháp luật được biên soạn theo Chương / Mục / **Điều**, và **mỗi Điều đã là một đơn vị ngữ nghĩa trọn vẹn** — câu dẫn, các khoản `1. 2. 3.`, các điểm `a) b) c)` và phần ngoại lệ đều thuộc về nhau. Cắt theo tiêu đề tức là dùng lại đúng ranh giới mà nhà làm luật đã định nghĩa, thay vì áp một ranh giới nhân tạo. So với `ParagraphChunker` của Hà: hai chiến lược cùng một triết lý "tôn trọng cấu trúc tác giả tạo ra" nhưng ở **hai mức độ to/nhỏ khác nhau** — Hà lấy một *khoản* làm chunk, Quang lấy cả một *Điều*. Nhờ vậy bảng benchmark so sánh được trực tiếp: chunk to giữ trọn điều kiện + ngoại lệ, chunk nhỏ chính xác hơn nhưng dễ đứt ngữ cảnh.
- **Hai tình huống biên phải xử lý** — cả hai đều rút ra từ số liệu benchmark, không phải đoán:
  1. **Section quá dài.** Điều 28–34 gộp lại hơn 5.000 ký tự. Khi vượt `max_section_size` thì hạ xuống tách theo **khoản** (`1.`, `a)`), gom các khoản liền nhau tới sát ngưỡng, khoản đơn lẻ vẫn quá dài thì hạ tiếp xuống `RecursiveChunker`.
  2. **Tiêu đề "trơ trọi".** File `.md` mở đầu bằng tiêu đề cấp 1 rồi xuống thẳng tiêu đề cấp 2, nên section của tiêu đề cấp 1 có **thân rỗng** → sinh ra một chunk chỉ chứa đúng một dòng tiêu đề. Đây chính là nguyên nhân failure case Q2 của nhóm (xem mục 3). `merge_lone_heading=True` nhập tiêu đề trơ trọi vào section kế tiếp thay vì để nó thành chunk riêng.
- **Code:** `src/K4_01452_NguyenNhatQuang/chunking.py::StructureChunker`

```python
class StructureChunker:
    _HEADING = re.compile(r"^\s*(?:#{1,6}\s+\S.*|(?:Điều|Chương|Mục)\s+\d+\s*[.:)]?.*)$", re.I)
    _CLAUSE  = re.compile(r"^\s*(?:\d+\.|[a-zA-ZđĐ]\))\s+")   # khoản 1. / điểm a)

    def chunk(self, text: str) -> list[str]:
        chunks = []
        for heading, body in self._split_sections(text):   # ranh giới = dòng tiêu đề
            whole = f"{heading}\n{body}".strip()
            if len(whole) <= self.max_section_size:
                chunks.append(whole)                       # CẢ ĐIỀU = MỘT chunk
            else:
                chunks.extend(self._split_section(heading, body))  # hạ xuống theo khoản
        return [c.strip() for c in chunks if c.strip()]
```

- **Chọn `max_section_size` bằng thực nghiệm.** Quét trên đúng 5 query của nhóm, chỉ đổi một biến này:

| `max_section_size` | Số chunk | Điểm chunk-level | Q1 | Q2 | Q3 | Q4 | Q5 |
|---|---|---|---|---|---|---|---|
| 400 | 86 | 7/10 | 2 | 1 | 0 | 2 | 2 |
| 600 | 63 | 8/10 | 2 | 2 | 0 | 2 | 2 |
| **900** | **49** | **10/10** | 2 | 2 | 2 | 2 | 2 |
| 1200 | 38 | 10/10 | 2 | 2 | 2 | 2 | 2 |
| 2000 | 36 | 10/10 | 2 | 2 | 2 | 2 | 2 |
| 4000 | 35 | 10/10 | 2 | 2 | 2 | 2 | 2 |

Chọn **900** vì đó là **giá trị nhỏ nhất** vẫn đạt trần 10/10. Dưới 900, Điều 18 bị cắt làm đôi và câu dẫn tách khỏi danh sách `a) b) c)` → Q3 rớt về 0. Trên 900 điểm không tăng thêm nhưng chunk to hơn, tức là context đưa vào LLM bị loãng và tốn token vô ích. Đây là tune tham số của chính chiến lược mình, đề bài cho phép; cái **không** được phép là đổi 5 query sau khi đã thấy kết quả.

**Thành viên 3 — Trương Ngọc Hải (2A202601092)**

- **Loại chiến lược:** `RecursiveChunker(chunk_size=650)` — đệ quy theo thứ tự ưu tiên separator `\n\n` → `\n` → `. ` → ` ` → `""`.
- **Mô tả & lý do:** Không tự định nghĩa ranh giới mới mà **tune** chunker có sẵn theo domain. Mặc định 400 làm 92 chunk, quá vụn với văn bản luật; nâng lên 650 còn 52 chunk, đủ để một Điều trung bình nằm trọn trong một chunk mà không cần viết thêm regex nhận diện "Điều"/"Khoản" nào cả. Đây là chiến lược **rẻ nhất về công sức và tái dùng được ngay khi đổi domain** — đó chính là giá trị nhóm muốn đo: một chunker generic được tune tốt thì cách một chunker viết riêng theo domain bao xa?
- **Code:** `src/2A202601092_TruongNgocHai/chunking.py::RecursiveChunker`

**Thành viên 4 — Vũ Văn Huy (K4_2A202601342)**

- **Loại chiến lược:** `FixedSizeChunker(chunk_size=600, overlap=150)` — cửa sổ trượt, overlap 25%.
- **Mô tả & lý do:** Là **nhóm đối chứng có chủ đích** của nhóm. Ba người kia đều tôn trọng cấu trúc văn bản theo cách nào đó; Huy cố tình **không** dùng thông tin cấu trúc nào cả, chỉ bù lại bằng overlap dày (150 so với 50 của baseline) để mỗi thông tin có nhiều hơn một cơ hội lọt top-k. Câu hỏi cần trả lời: **overlap có mua lại được phần chất lượng đã mất khi bỏ qua cấu trúc không?** Kết quả ở bảng dưới cho thấy là **có, nhưng không hoàn toàn** — 8/10 so với 6/10 của baseline `fixed(500/50)`, vẫn kém 2 điểm so với ba chiến lược có ý thức về cấu trúc.
- **Code:** `src/K4_2A202601342_VuVanHuy/chunking.py::FixedSizeChunker`

### So Sánh Giữa Các Thành Viên

Embedder dùng chung: `LexicalEmbedder` (TF-IDF dim=2048, `lexical_embedding.py`). Lệnh tái tạo toàn bộ bảng dưới đây trong **một lần chạy duy nhất**:

```powershell
$env:EMBEDDING_PROVIDER="lexical"; python bench.py --all > report/bench_output_lexical.txt
```

**Bảng so sánh chung của nhóm — 4 chiến lược chia chunk khác nhau** (`python bench.py --group`):

| Thành viên | Strategy | Đơn vị ngữ nghĩa | Chunks | Q1 | Q2 | Q3 | Q4 | Q5 | **Tổng /10** |
|---|---|---|---|---|---|---|---|---|---|
| **Nguyễn Nhật Quang** (K4_01452) | **`structure`** (900, no-repeat-heading) | một **Điều** | **49** | 2 | 2 | 2 | 2 | 2 | **10** |
| **Nguyễn Quang Hà** (2A202601424) | **`paragraph`** (max 700, min 450) | một **khoản** | 65 | 2 | 2 | **1** | 2 | 2 | **9** |
| **Trương Ngọc Hải** (2A202601092) | **`recursive_hai`** (chunk_size 650) | khối ~650 ký tự | 52 | **1** | 2 | 2 | 2 | 2 | **9** |
| **Vũ Văn Huy** (K4_2A202601342) | **`fixed_huy`** (600/150) | cửa sổ trượt | 63 | 2 | 2 | **0** | 2 | 2 | **8** |

**Ablation và baseline** (không tính là chiến lược của ai, dùng để giải thích khoảng cách ở bảng trên):

| Nhóm | Strategy | Chunks | Q1 | Q2 | Q3 | Q4 | Q5 | Tổng | Điều ablation này chứng minh |
|---|---|---|---|---|---|---|---|---|---|
| Quang | `structure_repeatheading` | 50 | 2 | 2 | **1** | 2 | 2 | 9 | Gắn lại tiêu đề vào mảnh con **làm giảm** 1 điểm — ngược với dự đoán, xem "Phát hiện" bên dưới |
| Quang | `structure_loneheading` | 57 | 2 | **1** | 2 | 2 | 2 | 8 | Tiêu đề trơ trọi thành chunk riêng → mất 1 điểm ở Q2 (failure case) |
| Hà | `paragraph_noheading` | 63 | 2 | 2 | **0** | 2 | 2 | 8 | Bỏ bước gắn tiêu đề → mất 1 điểm |
| Hà | `paragraph_nomerge` (min 0) | 162 | 2 | **1** | **0** | 2 | 2 | 7 | Không gộp đoạn ngắn → mất 2 điểm |
| baseline | `recursive` (400) | 92 | 2 | 1 | 0 | 2 | 2 | 7 | Hải tune 400→650 đổi được **+2 điểm**, không sửa một dòng code nào |
| baseline | `sentence` (3 câu) | 69 | 2 | 1 | 0 | 2 | 2 | 7 | Gạch đầu dòng kết thúc bằng `;` → không tách được câu |
| baseline | `fixed` (500/50) | 67 | 2 | **0** | **0** | 2 | 2 | **6** | Huy tăng overlap 50→150 đổi được **+2 điểm** |

**Nhận xét từng chiến lược:**

| Thành viên | Điểm mạnh (có bằng chứng top-k) | Điểm yếu (có bằng chứng top-k) |
|---|---|---|
| Quang · `structure` | Chiến lược duy nhất đạt trần. Q3 top-1 = `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_3` score 0.2856 — chứa trọn câu dẫn Điều 18 **và** danh sách `a) b) c)` gồm anchor "Tổng giá trị của hợp đồng". Ít chunk nhất (49) nên rẻ nhất khi embed | Chunk to nhất → context đưa vào LLM loãng nhất. Rất phụ thuộc chất lượng heading: nếu tài liệu crawl về không có `##` thì toàn bộ file thành một section khổng lồ và phải rơi hết xuống nhánh fallback |
| Hà · `paragraph` | Q2 top-1 chứa đúng anchor "ít nhất 5 ngày". Chunk nhỏ, chính xác, context sạch | Q3 chỉ được 1/2: câu dẫn Điều 18 (`chunk_3`, 0.3909) và danh sách `a) b) c)` chứa anchor (`chunk_4`, 0.2689) là **hai chunk khác nhau** → chunk có đáp án bị đẩy xuống hạng 2. Đây chính là cái giá của việc lấy đơn vị nhỏ hơn Quang |
| Hải · `recursive_hai` | Không viết thêm dòng code nào, chỉ đổi `chunk_size` mà bằng điểm chiến lược tự viết của Hà. Q3 đạt 2/2 | Q1 chỉ 1/2: `chunk_5` (Điều 20 khoản 1, **không** chứa đáp án) score 0.3668, `chunk_6` chứa anchor "12 (mười hai) giờ" score 0.3606 — **lệch 0.0062**. Ranh giới đệ quy rơi đúng giữa khoản 1 và khoản 2 của Điều 20, tách phần "có công bố" khỏi phần "không công bố" |
| Huy · `fixed_huy` | Overlap 150 cứu được Q2 (baseline 500/50 ăn 0 điểm ở đây) | Q3 ăn **0 điểm** — đúng `doc_id` nhưng **sai section**: cả `chunk_2` và `chunk_4` đều thuộc file gold mà không chunk nào chứa anchor. Preview cho thấy chunk mở đầu bằng "sử dụng chức năng đặt hàng trực tuyến…" và "…anh toán 1. Thương nhân…" — **cắt giữa từ**, bằng chứng trực quan nhất rằng ranh giới theo số ký tự là nhân tạo |

**Strategy nào tốt nhất cho chủ đề này? Tại sao?**

> **`StructureChunker` của Quang (10/10)** — và lý do nằm ở **cấu trúc của dữ liệu, không phải độ tinh vi của thuật toán**. Nghị định 52/2013 được soạn theo Điều, mỗi Điều là một đơn vị lập luận khép kín gồm câu dẫn + các khoản + ngoại lệ. Chunker nào lấy đúng **một Điều** làm một chunk thì mọi thành phần của một câu trả lời đều nằm chung một chỗ. Q3 là câu phân loại rõ nhất: câu hỏi hỏi "phải hiển thị những thông tin gì", đáp án là một danh sách `a) b) c)` nằm **sau** câu dẫn — Quang giữ được cả hai (2 điểm), Hà tách làm đôi (1 điểm), Huy cắt giữa từ (0 điểm).
>
> **Nhưng khoảng cách giữa 4 chiến lược chỉ là 2 điểm, trong khi khoảng cách giữa một chiến lược và chính nó khi tune sai cũng là 2 điểm** (`fixed` 6 → `fixed_huy` 8; `recursive` 7 → `recursive_hai` 9; `paragraph_nomerge` 7 → `paragraph` 9). Đây là kết luận nhóm thấy đáng giá nhất: **chọn đúng loại chunker quan trọng ngang với — chứ không hơn — việc xử lý tử tế các trường hợp biên.** Một `RecursiveChunker` có sẵn được tune đúng (Hải, 9/10) đã bám sát một chunker viết riêng theo domain, mà lại tái dùng được ngay khi đổi sang domain khác.
>
> **Cảnh báo về overfitting:** cả bốn con số trên đo bằng **5 query**, sai số một câu là 10% điểm. Nhóm không kết luận `structure` "tốt hơn `paragraph` 10%", chỉ kết luận rằng với loại câu hỏi liệt kê theo danh sách (Q3), đơn vị "cả Điều" thắng đơn vị "một khoản" một cách có giải thích được.

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

Điểm của **4 chiến lược thành viên** trên từng câu (2 = anchor ở top-1, 1 = anchor trong top-3 nhưng không top-1, 0 = không có bằng chứng đáp án trong top-3):

| # | Loại | Quang `structure` | Hà `paragraph` | Hải `recursive_hai` | Huy `fixed_huy` | Câu này phân loại được điều gì |
|---|---|:---:|:---:|:---:|:---:|---|
| 1 | số liệu | 2 | 2 | **1** | 2 | Anchor "12 (mười hai) giờ" rất đặc trưng nên hầu như ai cũng bắt được — trừ khi ranh giới rơi đúng **giữa khoản 1 và khoản 2** của Điều 20 như trường hợp của Hải |
| 2 | điều kiện | 2 | 2 | 2 | 2 | Cả 4 chiến lược thành viên đều qua; chỉ baseline `fixed(500/50)` ăn **0** vì cắt khoản 3 rời khỏi tiêu đề Điều 38 |
| 3 | quy trình | **2** | **1** | 2 | **0** | **Câu phân loại mạnh nhất.** Đáp án là một danh sách `a) b) c)` nằm sau câu dẫn → chỉ chiến lược nào giữ được **cả câu dẫn lẫn danh sách trong một chunk** mới ăn trọn điểm |
| 4 | liệt kê + filter | 2 | 2 | 2 | 2 | Không phân loại được chunking, nhưng là câu duy nhất phân loại được **metadata filter** — xem A/B bên dưới |
| 5 | ngoại lệ | 2 | 2 | 2 | 2 | Ngoại lệ nằm gọn trong khoản 2 Điều 31, ngắn và ít bị cắt nên mọi chiến lược đều qua |
| | **Tổng** | **10** | **9** | **9** | **8** | |

**Đọc bảng theo cột dọc thì thấy điều bảng tổng không nói:** 3 trong 5 câu (Q2, Q4, Q5) **không phân biệt được chiến lược nào cả** — cả bốn đều 2/2. Toàn bộ khác biệt 10 vs 9 vs 8 đến từ **đúng hai câu: Q1 và Q3**. Nhóm ghi nhận đây là giới hạn của bộ benchmark: 5 query là mức tối thiểu đề bài yêu cầu, và trên thực tế chỉ có 2 query mang thông tin phân loại. Nếu làm lại, nhóm sẽ thiết kế nhiều câu thuộc dạng "đáp án nằm trong danh sách liệt kê" hơn, vì đó là dạng làm lộ ra khác biệt giữa các cách chia chunk.

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

> **Có, rõ nhất ở Q4** — nhóm chạy A/B (một lần có `metadata_filter`, một lần không) trên **cả 4 chiến lược thành viên lẫn 7 cấu hình ablation/baseline**. Kết quả: `bench.py` báo **`A/B: ket qua KHAC NHAU`** ở **11/11 cấu hình** — không có trường hợp nào filter vô tác dụng. Điều này xác nhận corpus được thiết kế đúng: field `customer_role` có 3 giá trị (buyer 3 · seller 4 · both 2) nên thực sự có tài liệu để loại.
>
> Không filter: top-3 = [`nd85-2021::chunk_5` (buyer, 0.359), `returns-policy::chunk_2` (seller, **bản 2013**, 0.239), `nd52-dang-ky-thong-bao-website::chunk_5` (seller, 0.142)] — **2/3 slot là tài liệu seller, trong đó có văn bản đã lỗi thời**.
> Có filter `{"customer_role": "buyer"}`: top-3 toàn bộ là tài liệu buyer, nhóm 2013 bị loại khỏi tập ứng viên trước khi xếp hạng.
>
> Filter **giảm nhiễu thật, không loại nhầm đáp án** trong trường hợp này. Nhưng đây là **precision đổi lấy recall**: nếu người hỏi là seller mà hệ thống lọc `buyer`, câu trả lời đúng sẽ bị giấu mất. Cách xử lý bền hơn là lọc theo tập (`role ∈ {buyer, both}`) thay vì so bằng tuyệt đối, và gắn `both` cho tài liệu áp dụng cho cả hai bên.
>
> Ba câu còn lại (Q1, Q3, Q5) **không cần filter** — vocabulary đã đủ đặc trưng. Ghi nhận điều này quan trọng không kém: **filter không phải lúc nào cũng cần, thêm bừa chỉ làm giảm recall.**

### Phát hiện đáng giá nhất: chấm ở mức doc_id che mất toàn bộ khác biệt

Nhóm chấm cả hai cách trên **cùng một lần chạy**:

| Strategy | Ai | Doc-level | Chunk-level |
|---|---|---|---|
| **structure** | Quang | **10 / 10** | **10 / 10** |
| **paragraph** | Hà | **10 / 10** | 9 / 10 |
| **recursive_hai** | Hải | **10 / 10** | 9 / 10 |
| **fixed_huy** | Huy | **10 / 10** | 8 / 10 |
| structure_repeatheading | ablation | **10 / 10** | 9 / 10 |
| structure_loneheading | ablation | **10 / 10** | 9 / 10 |
| paragraph_noheading | ablation | **10 / 10** | 8 / 10 |
| paragraph_nomerge | ablation | **10 / 10** | 7 / 10 |
| recursive (400) | baseline | **10 / 10** | 7 / 10 |
| sentence (3 câu) | baseline | **10 / 10** | 7 / 10 |
| fixed (500/50) | baseline | **10 / 10** | **6 / 10** |

Nếu chỉ kiểm "gold `doc_id` có xuất hiện trong top-3 không" thì **cả 11 cấu hình đều đạt 10/10 tuyệt đối** — không một chiến lược nào tách khỏi phần còn lại, và nhóm sẽ kết luận sai rằng cách chia chunk không quan trọng. Chấm ở mức chunk, cùng 11 cấu hình đó trải từ **6 đến 10 điểm**.

Ví dụ sắc nhất là `fixed` ở Q2: **cả 3/3 slot đều là tài liệu gold** `nd52-quy-che-hoat-dong-san`, doc-level cho 2/2 điểm tuyệt đối, nhưng **không slot nào chứa "ít nhất 5 ngày"** → chunk-level 0. Ví dụ thứ hai là `fixed_huy` ở Q3: đúng `doc_id` ở cả hai slot mà không slot nào chứa anchor (`bench.py` in thẳng ghi chú `DUNG doc_id nhung SAI section`).

Nguyên nhân đúng như lab cảnh báo, và corpus của nhóm là trường hợp xấu nhất có thể của hiện tượng đó: **9 tài liệu đều là các Điều trích từ cùng một Nghị định**, cùng văn phong, cùng từ vựng pháp lý. Chỉ cần retrieval trúng đúng file là doc-level đã trọn điểm, trong khi việc trúng đúng *section* nào trong file lại gần như quyết định toàn bộ chất lượng câu trả lời. Đây là lý do nhóm khai báo `anchors` — chuỗi đặc trưng bắt buộc phải xuất hiện trong context — ngay từ khi chốt 5 query, **trước** khi chạy strategy nào.

### Failure case 1 của nhóm — Q3, "chunk *nói về* câu hỏi thắng chunk *trả lời* câu hỏi"

**Query:** "Cơ chế rà soát và xác nhận nội dung hợp đồng phải hiển thị những thông tin gì cho khách hàng trước khi đặt hàng?"
**Anchor:** `Tổng giá trị của hợp đồng` · **Gold doc:** `nd52-quy-trinh-dat-hang-truc-tuyen` (Điều 18)

**Bằng chứng top-k, ba chiến lược cùng một query:**

| Strategy | Rank | doc_id::chunk | score | Chứa anchor? | Nội dung |
|---|---|---|---|:---:|---|
| **Huy `fixed_huy`** | 1 | `nd52-quy-trinh...::chunk_2` | 0.3734 | ✗ | "sử dụng chức năng đặt hàng trực tuyến được coi là đề nghị giao kết…" — **Điều 17**, mở đầu bằng câu cụt |
| | 2 | `seller-listing::chunk_7` | 0.2316 | ✗ | "…anh toán 1. Thương nhân, tổ chức…" — **cắt giữa từ** "thanh toán" |
| | 3 | `nd52-quy-trinh...::chunk_4` | 0.1957 | ✗ | "àng những thông tin về cách thức trả lời…" — lại cắt giữa từ |
| | | | | | → **0 điểm** — đúng `doc_id`, sai section |
| **Hà `paragraph`** | 1 | `nd52-quy-trinh...::chunk_3` | 0.3909 | ✗ | Điều 18, **câu dẫn**: "Website TMĐT phải có cơ chế cho phép khách hàng rà soát…" |
| | 2 | `nd52-quy-trinh...::chunk_4` | 0.2689 | **✓** | Điều 18, danh sách: "c) **Tổng giá trị của hợp đồng** và các chi tiết…" |
| | | | | | → **1 điểm** — chunk đúng bị đẩy xuống hạng 2 |
| **Quang `structure`** | 1 | `nd52-quy-trinh...::chunk_3` | 0.2856 | **✓** | **Cả câu dẫn + cả danh sách `a) b) c)` trong một chunk** |
| | | | | | → **2 điểm** |

**Nguyên nhân.** Chunk chứa đáp án là một **danh sách gạch đầu dòng a/b/c** có mật độ từ khóa "rà soát / xác nhận / hợp đồng" rất thấp, trong khi chunk câu dẫn lặp lại gần như nguyên văn cụm từ trong câu hỏi. Cosine đo **độ giống chủ đề**, không đo **mật độ thông tin trả lời được** — nên khi hai chunk cùng thuộc một Điều, chunk *nói về* câu hỏi luôn thắng chunk *trả lời* câu hỏi. Với `fixed_huy`, ranh giới theo số ký tự còn tệ hơn một bậc: nó cắt **giữa từ**, khiến cả top-3 không mảnh nào là một đơn vị đọc được.

**Đây chính xác là điều mà chấm theo `doc_id` che mất:** cả ba chiến lược đều 10/10 doc-level ở câu này.

**Đề xuất sửa (đã kiểm chứng một phần).** Cách nhóm đã thử và có số liệu: nâng đơn vị chunk lên **cả Điều** để câu dẫn và danh sách không bao giờ tách rời — đúng cái `StructureChunker` làm, và nó đưa Q3 từ 0/1 điểm lên 2 điểm. Cách chưa thử vì hết thời gian: retrieve ở mức **khoản** cho chính xác rồi **nạp vào context cả Điều chứa nó** (small-to-big retrieval) — giữ được độ chính xác xếp hạng của chunk nhỏ mà không mất ngữ cảnh; hoặc lấy top-8 rồi rerank.

### Failure case 2 — Q2, chunk chỉ có một dòng tiêu đề đoạt top-1

Failure case này riêng của `StructureChunker`, và là lý do class đó có tham số `merge_lone_heading`. Tái tạo bằng `python bench.py structure_loneheading`.

**Query:** "Sàn TMĐT phải thông báo trước bao nhiêu ngày khi thay đổi quy chế hoạt động?" · **Anchor:** `ít nhất 5 ngày`

| Rank | doc_id::chunk | score | Chứa anchor? | Nội dung |
|---|---|---|:---:|---|
| 1 | `nd52-quy-che-hoat-dong-san::chunk_0` | **0.4480** | ✗ | `# Quy chế hoạt động của sàn giao dịch thương mại điện tử` — **chunk 46 ký tự, chỉ có đúng một dòng tiêu đề** |
| 2 | `nd52-trach-nhiem-san-tmdt::chunk_0` | 0.2731 | ✗ | Lại là một dòng tiêu đề trơ trọi của file khác |
| 3 | `nd52-quy-che-hoat-dong-san::chunk_3` | 0.2677 | **✓** | "3. Khi có thay đổi… phải thông báo… **ít nhất 5 ngày**" |

→ **1 điểm** thay vì 2. Hai slot đầu bị hai chunk **không chứa nội dung nào** chiếm chỗ.

**Nguyên nhân.** File `.md` của nhóm mở đầu bằng tiêu đề cấp 1 rồi xuống thẳng tiêu đề cấp 2, nên section của tiêu đề cấp 1 có **thân rỗng** và sinh ra một chunk chỉ chứa dòng tiêu đề. Chunk như vậy cực kỳ nguy hiểm với TF-IDF: nó **ngắn**, toàn **từ hiếm**, và trùng gần hết từ với câu hỏi — sau khi chuẩn hoá L2, vector của nó gần như trỏ thẳng vào vector câu hỏi, cho score 0.4480 cao nhất toàn benchmark. Nhóm gặp đúng hiện tượng này lần thứ hai (lần đầu ở ablation `paragraph_nomerge` của Hà: một chunk 64 ký tự đạt 0.6109 mà 0 điểm) — nên nhóm coi đây là **quy luật, không phải trùng hợp: chunk càng ngắn thì score càng dễ bị thổi lên, và score cao không phải bằng chứng nội dung đúng.**

**Sửa và kết quả đo được:** tiêu đề "trơ trọi" (thân rỗng) không tạo chunk riêng mà **nhập vào section kế tiếp**. Chunk-level của `structure`: **8 → 9 → 10** qua ba bước (`merge_lone_heading`, rồi tune `max_section_size`). Số chunk giảm 57 → 49 và không mất thông tin nào, vì dòng tiêu đề vẫn còn nguyên — chỉ là nó nằm cùng với phần thân mà nó giới thiệu.

### Phát hiện ngược với dự đoán: gắn lại tiêu đề vào mảnh con **làm giảm** điểm

Đề bài gợi ý rõ: *"khi cắt nhỏ một section dài, nên gắn lại tiêu đề vào từng mảnh con, nếu không mảnh thứ hai trở đi mất ngữ cảnh."* Nhóm làm đúng vậy, rồi đo, và **số liệu nói ngược lại**:

| Cấu hình | Chunks | Q3 | Tổng |
|---|---|:---:|---|
| `structure` (`repeat_heading=False`) | 49 | **2** | **10/10** |
| `structure_repeatheading` (`repeat_heading=True`) | 50 | **1** | 9/10 |

**Bằng chứng top-k ở Q3.** Điều 18 dài nên bị cắt làm hai mảnh: `chunk_3` (câu dẫn + danh sách `a) b) c)`, **có anchor**) và `chunk_4` (khoản 3, không có anchor).

- `repeat_heading=True`: cả hai mảnh đều được gắn thêm `## Điều 18. Rà soát và xác nhận nội dung hợp đồng`. Kết quả: `chunk_4` **0.3495** > `chunk_3` **0.3067** → mảnh **không** chứa đáp án lên top-1.
- `repeat_heading=False`: `chunk_3` **0.2856** lên top-1, `chunk_4` tụt xuống hạng 3.

**Giải thích.** Dòng tiêu đề chứa gần hết từ khoá của câu hỏi ("rà soát", "xác nhận", "nội dung hợp đồng"), nên nó cộng **cùng một lượng từ** vào cả hai mảnh. Nhưng TF-IDF chuẩn hoá vector theo độ dài: mảnh **ngắn hơn** thì phần đóng góp của tiêu đề chiếm **tỷ trọng lớn hơn** trong vector của nó. Kết quả là việc lặp tiêu đề **ưu ái mảnh ngắn** một cách hệ thống — mà mảnh ngắn thường là mảnh phụ, không phải mảnh chứa danh sách đáp án.

**Kết luận nhóm rút ra (và giới hạn của nó).** Gắn lại tiêu đề giúp **recall ở mức tài liệu** (kéo cả hai mảnh về đúng file) nhưng **bóp méo xếp hạng bên trong tài liệu**, theo hướng có hại. Nhóm **không** kết luận "đừng bao giờ lặp tiêu đề": kết quả này đo trên **embedder TF-IDF từ vựng**, nơi trùng từ được thưởng trực tiếp. Với embedder ngữ nghĩa thật (`paraphrase-multilingual-MiniLM`), hiệu ứng nhiều khả năng yếu hơn hoặc đảo chiều, vì tiêu đề đóng góp *ngữ nghĩa* chứ không đóng góp *tần suất từ*. Đây là việc nhóm sẽ kiểm chứng đầu tiên nếu có thêm thời gian — và cũng là lý do nhóm ghi rõ giới hạn embedder ở mục dưới.

---

## 4. Demo & Bài học nhóm — 5 điểm

### Kịch bản demo 6–8 phút

1. **(1 phút)** Phạm vi, 9 tài liệu, schema metadata — nhấn `customer_role` và `document_version`.
2. **(2 phút)** Bốn thành viên, bốn **đơn vị ngữ nghĩa** khác nhau: Quang = cả Điều (`structure`), Hà = một khoản (`paragraph`), Hải = khối ~650 ký tự (`recursive_hai`), Huy = cửa sổ trượt (`fixed_huy`). Mỗi người nói 30 giây về đơn vị mình chọn và vì sao.
3. **(3 phút)** Bảng so sánh chung (`python bench.py --group`) + **A/B metadata filter ở Q4** + **hai failure case** có bằng chứng top-k (Q3 "chunk nói về vs chunk trả lời", Q2 "tiêu đề trơ trọi đoạt top-1").
4. **(1–2 phút)** Chạy live `python bench.py --group`, dừng ở Q3 để chỉ ra ba mức điểm 2/1/0 trên cùng một câu hỏi.

### 3 phân tích hay nhất nhóm sẽ trình bày

1. **Chấm ở mức `doc_id` cho 10/10 cho cả 11 cấu hình; chấm ở mức chunk mới trải ra 6→10.** Nếu không thiết kế `anchors` từ đầu, nhóm đã kết luận sai rằng chunking không ảnh hưởng gì. Bằng chứng đắt nhất: `fixed` ở Q2 chiếm trọn 3/3 slot bằng đúng tài liệu gold mà không slot nào chứa đáp án.
2. **Chunk càng ngắn thì score càng dễ bị thổi lên — và score cao không phải bằng chứng nội dung đúng.** Nhóm gặp hiện tượng này hai lần độc lập: chunk 46 ký tự chỉ có dòng tiêu đề đạt 0.4480 (top-1 Q2, 0 nội dung), và chunk 64 ký tự đạt 0.6109 (cao nhất toàn benchmark, 0 điểm). Đây là lý do cả `ParagraphChunker` lẫn `StructureChunker` đều phải có một bước gộp các mảnh quá ngắn.
3. **Làm đúng theo hướng dẫn vẫn có thể sai — phải đo.** Đề bài dặn gắn lại tiêu đề vào mảnh con; nhóm làm vậy và **mất 1 điểm** ở Q3, vì tiêu đề cộng cùng một lượng từ vào mọi mảnh nhưng TF-IDF chuẩn hoá theo độ dài nên ưu ái mảnh ngắn. Không có ablation thì không ai phát hiện ra.

### Bài học rút ra

> Cùng một corpus, cùng 5 câu hỏi, cùng embedder — chỉ đổi cách chia nhỏ tài liệu mà khoảng cách là **6 vs 10 điểm**, và ở hai câu hỏi cụ thể (Q2, Q3) là **có đáp án trong top-3 hay hoàn toàn không có**.
>
> Nhưng ba con số nhóm thấy đáng nhớ hơn cả là ba khoảng cách này, xếp theo độ lớn:
> - **mock → lexical embedding: ~6–7 điểm.** Đổi embedder ăn đứt mọi thứ khác.
> - **cùng một chunker, tune sai vs tune đúng: 2 điểm** (`fixed` 6→8, `recursive` 7→9, `paragraph_nomerge` 7→9, `structure_loneheading` 8→10).
> - **bốn loại chunker khác hẳn nhau: cũng chỉ 2 điểm** (10, 9, 9, 8).
>
> Nói cách khác, **chọn loại chunker nào quan trọng ngang với — chứ không hơn — việc xử lý tử tế các trường hợp biên của chính chunker đó**, và cả hai đều đứng sau việc có embedding phù hợp ngôn ngữ. Thứ tự ưu tiên khi làm thật: **dữ liệu sạch có provenance → embedding phù hợp ngôn ngữ → metadata schema → loại chunker → tinh chỉnh biên.**
>
> Bằng chứng cụ thể cho vế "xử lý biên": `RecursiveChunker` có sẵn, chỉ đổi `chunk_size` 400→650 mà đạt 9/10 — bằng chiến lược tự viết của Hà, và chỉ kém chiến lược tốt nhất 1 điểm, mà không thêm một dòng code nào và tái dùng được ngay khi đổi domain.

### Nếu làm lại, nhóm sẽ thay đổi gì

> 1. **Cài `requirements-local.txt` chạy nền ngay từ đầu buổi** để có embedding đa ngữ thật, thay vì phải tự viết TF-IDF làm giải pháp thay thế ở phút chót.
> 2. **Đa dạng nguồn hơn.** 8/9 tài liệu đến từ cùng một Nghị định — điều này làm các chunk rất giống nhau về từ vựng và khiến việc phân biệt ở mức doc_id trở nên vô nghĩa. Lần sau sẽ trộn thêm điều khoản dịch vụ công khai của sàn TMĐT để corpus có cả tầng quy phạm lẫn tầng vận hành, nhiều "giọng văn" khác nhau.
> 3. **Thiết kế 2 câu hỏi cần filter thay vì 1**, một câu cho `buyer` và một câu cho `seller`, để kiểm tra được cả trường hợp filter **loại nhầm** đáp án (đánh đổi recall) chứ không chỉ trường hợp filter giúp ích.
> 4. **Ghi `anchors` vào bộ query ngay từ khi chốt câu hỏi**, không đợi đến lúc chấm — vì đó mới là thứ phân biệt được các strategy.
> 5. **Thiết kế query có khả năng phân loại.** Nhìn lại thì 3/5 câu (Q2, Q4, Q5) cho cả bốn chiến lược cùng 2/2 điểm, tức là **không mang thông tin phân biệt nào**; toàn bộ kết luận của nhóm dựa trên đúng 2 câu. Lần sau sẽ chốt query theo *dạng cấu trúc của đáp án* (đáp án nằm trong danh sách liệt kê / đáp án trải qua hai khoản / đáp án là ngoại lệ của một quy tắc nêu ở trên) chứ không chỉ theo *loại câu hỏi* (số liệu / điều kiện / quy trình).
> 6. **Chạy lại toàn bộ ablation bằng embedder ngữ nghĩa.** Phát hiện "gắn lại tiêu đề làm giảm điểm" hiện chỉ đúng với TF-IDF, nơi trùng từ được thưởng trực tiếp. Nhóm chưa dám tổng quát hoá, và đó là thí nghiệm đầu tiên sẽ làm nếu có thêm thời gian.

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

# 3. Benchmark strategy cá nhân (thay tên strategy của mình)
EMBEDDING_PROVIDER=lexical python bench.py paragraph        # Hà
EMBEDDING_PROVIDER=lexical python bench.py structure        # Quang
EMBEDDING_PROVIDER=lexical python bench.py recursive_hai    # Hải
EMBEDDING_PROVIDER=lexical python bench.py fixed_huy        # Huy

# 4. BẢNG SO SÁNH CHUNG CỦA NHÓM — 4 chiến lược, một lần chạy
EMBEDDING_PROVIDER=lexical python bench.py --group

# 5. Toàn bộ strategy + ablation + baseline + bảng nhóm
EMBEDDING_PROVIDER=lexical python bench.py --all > report/bench_output_lexical.txt
python bench.py --all > report/bench_output_mock.txt   # đối chứng bằng mock

# 6. Chấm bài từng thành viên (42 test trên đúng gói của người đó)
LAB_SOLUTION_PACKAGE=src.K4_01452_NguyenNhatQuang python -m pytest tests -v

# Windows PowerShell: $env:EMBEDDING_PROVIDER="lexical"; python bench.py --all
```
