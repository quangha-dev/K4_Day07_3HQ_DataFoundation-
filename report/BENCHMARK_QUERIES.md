# Bộ 5 câu hỏi đánh giá — Nhóm chốt

**Lớp:** K4 — Chính sách thương mại điện tử
**Corpus:** `data/k4_ecommerce/` — 9 tài liệu, nguồn NĐ 52/2013/NĐ-CP và NĐ 85/2021/NĐ-CP
**Ngày chốt:** 03/08/2026
**Định nghĩa máy đọc:** `benchmark_queries.py`

> **Đã chốt — không đổi.** Đề bài: *"Không đổi query sau khi một strategy đã chạy tốt hoặc xấu."*
> Cả 4 thành viên chạy đúng bộ này trên đúng corpus này, chỉ khác chunker.

---

## Tại sao mỗi query có trường `anchors`

`anchors` là **chuỗi đặc trưng bắt buộc phải xuất hiện trong nội dung chunk** truy xuất được. Nhóm dùng nó để chấm ở **mức chunk**, không phải mức tài liệu.

Lý do: nhóm đã đo cả hai cách trên cùng một lần chạy. Chấm theo `doc_id` (chỉ kiểm tài liệu gold có trong top-3 không) cho **10/10 với mọi strategy** — bảng so sánh trở nên vô nghĩa. Chỉ khi kiểm ở mức chunk thì khoảng cách mới lộ ra (6 → 9).

Nguyên nhân: corpus toàn các Điều trong cùng một Nghị định, nói cùng chủ đề với từ vựng gần giống nhau, nên điểm rất sát và section nào lọt top-3 gần như ngẫu nhiên. Một strategy hoàn toàn có thể chiếm cả 3 slot bằng đúng tài liệu gold mà **không chunk nào chứa câu trả lời** — đã quan sát đúng hiện tượng này với `FixedSizeChunker` ở Q2.

---

## Bảng tổng hợp

| # | Loại | Câu hỏi | Tài liệu kỳ vọng | Anchor | Filter |
|---|------|---------|------------------|--------|--------|
| Q1 | số liệu | Nếu người bán không công bố rõ thời hạn trả lời, sau bao lâu đề nghị giao kết hợp đồng của khách hàng hết hiệu lực? | `nd52-quy-trinh-dat-hang-truc-tuyen` | `12 (mười hai) giờ` | — |
| Q2 | điều kiện | Sàn giao dịch TMĐT phải thông báo trước bao nhiêu ngày khi thay đổi quy chế hoạt động? | `nd52-quy-che-hoat-dong-san` | `ít nhất 5 ngày` | — |
| Q3 | quy trình | Cơ chế rà soát và xác nhận nội dung hợp đồng phải hiển thị những thông tin gì cho khách hàng trước khi đặt hàng? | `nd52-quy-trinh-dat-hang-truc-tuyen` | `Tổng giá trị của hợp đồng` | — |
| Q4 | liệt kê + **BẮT BUỘC FILTER** | Chính sách kiểm hàng có phải là một điều kiện giao dịch chung bắt buộc phải công bố không? | `nd85-2021-diem-moi-bao-ve-nguoi-tieu-dung` | `chính sách kiểm hàng` | **`{"customer_role": "buyer"}`** |
| Q5 | ngoại lệ | Website niêm yết giá mà không nói rõ đã bao gồm thuế và phí vận chuyển chưa thì hiểu thế nào? | `seller-listing` | `được hiểu là đã bao gồm mọi chi phí` | — |

Đủ 5 loại đề bài yêu cầu: **số liệu · điều kiện · quy trình · liệt kê · ngoại lệ**.

---

## Chi tiết từng câu

### Q1 — số liệu

**Câu hỏi:** Nếu người bán không công bố rõ thời hạn trả lời, sau bao lâu đề nghị giao kết hợp đồng của khách hàng hết hiệu lực?

**Gold answer:** Trong vòng **12 (mười hai) giờ** kể từ khi gửi đề nghị giao kết hợp đồng mà khách hàng không nhận được trả lời thì đề nghị được coi là chấm dứt hiệu lực.

**Nguồn:** khoản 2 Điều 20 Nghị định 52/2013/NĐ-CP — `nd52-quy-trinh-dat-hang-truc-tuyen`

**Vì sao chọn:** con số cụ thể, chỉ có đúng một chỗ trong corpus, không thể trả lời bằng phỏng đoán.

---

### Q2 — điều kiện

**Câu hỏi:** Sàn giao dịch thương mại điện tử phải thông báo trước bao nhiêu ngày khi thay đổi quy chế hoạt động?

**Gold answer:** Phải thông báo cho tất cả đối tượng sử dụng dịch vụ **ít nhất 5 ngày** trước khi áp dụng thay đổi.

**Nguồn:** khoản 3 Điều 38 Nghị định 52/2013/NĐ-CP — `nd52-quy-che-hoat-dong-san`

**Vì sao chọn:** Điều 38 có một danh sách rất dài (khoản 2, các điểm a→l). Câu trả lời nằm ở khoản 3, **ngay sau danh sách đó**. Đây là bẫy cho chunker cắt theo số ký tự: ranh giới dễ rơi vào giữa danh sách và khoản 3 bị đẩy sang chunk khác, hoặc bị nuốt mất khỏi top-3.

---

### Q3 — quy trình

**Câu hỏi:** Cơ chế rà soát và xác nhận nội dung hợp đồng phải hiển thị những thông tin gì cho khách hàng trước khi đặt hàng?

**Gold answer:** Tên hàng hóa/dịch vụ, số lượng và chủng loại; phương thức và thời hạn giao hàng; **tổng giá trị hợp đồng** và chi tiết phương thức thanh toán. Ngoài ra phải hiển thị cách thức và thời hạn trả lời đề nghị giao kết, và cho phép hủy giao dịch.

**Nguồn:** Điều 18 khoản 1 Nghị định 52/2013/NĐ-CP — `nd52-quy-trinh-dat-hang-truc-tuyen`

**Vì sao chọn:** đây là **câu khó nhất** của bộ, và nhóm giữ nó vì lý do đó. Từ khóa của câu hỏi ("rà soát", "xác nhận", "hiển thị") nằm ở **câu dẫn**, còn đáp án nằm ở **danh sách a/b/c bên dưới**. Cosine đo độ giống chủ đề nên chunk chứa câu dẫn luôn thắng chunk chứa đáp án. Không strategy nào trong nhóm đạt 2/2 ở câu này — đó là failure case chung.

---

### Q4 — liệt kê + **bắt buộc filter**

**Câu hỏi:** Chính sách kiểm hàng có phải là một điều kiện giao dịch chung bắt buộc phải công bố không?

**Gold answer:** **Có.** Từ ngày 01/01/2022, chính sách kiểm hàng là một trong những điều kiện giao dịch chung bắt buộc phải công bố trên website TMĐT (Nghị định 85/2021/NĐ-CP). Bản gốc Điều 32 Nghị định 52/2013/NĐ-CP **không** liệt kê chính sách kiểm hàng — trả lời theo bản 2013 là **sai**.

**Nguồn:** `nd85-2021-diem-moi-bao-ve-nguoi-tieu-dung`, `document_version: 85/2021/NĐ-CP`

**Filter bắt buộc:** `metadata_filter={"customer_role": "buyer"}`

**Thiết kế câu bẫy:** câu hỏi **không nêu người hỏi là ai**. Corpus có **hai tài liệu cùng chủ đề "điều kiện giao dịch chung", cùng từ vựng, khác đối tượng và khác đáp án**:

| Tài liệu | `customer_role` | `document_version` | Nói gì về kiểm hàng |
|---|---|---|---|
| `returns-policy` (Điều 32) | `seller` | 52/2013/NĐ-CP | **Không liệt kê** |
| `nd85-2021-diem-moi-...` (mục 4) | `buyer` | **85/2021/NĐ-CP** | **Bắt buộc từ 01/01/2022** |

Không lọc thì retrieval trộn hai bản, agent có thể trả lời theo văn bản **đã lỗi thời** mà vẫn trích được nguồn thật — kiểu sai nguy hiểm nhất vì nó **có dẫn chứng**. Đây chính là loại câu hỏi biến thể K4 yêu cầu.

---

### Q5 — ngoại lệ

**Câu hỏi:** Website niêm yết giá mà không nói rõ đã bao gồm thuế và phí vận chuyển chưa thì hiểu thế nào?

**Gold answer:** Trừ trường hợp các bên có thỏa thuận khác, giá niêm yết **được hiểu là đã bao gồm mọi chi phí** liên quan như thuế, phí đóng gói, phí vận chuyển và chi phí phát sinh khác.

**Nguồn:** khoản 2 Điều 31 Nghị định 52/2013/NĐ-CP — `seller-listing`

**Vì sao chọn:** kiểm tra **chunk coherence**. Khoản 1 nêu nghĩa vụ, khoản 2 nêu hệ quả khi không làm đúng nghĩa vụ đó — hai khoản phải nằm cùng một chunk thì câu trả lời mới đầy đủ. Chunker nào cắt giữa khoản 1 và khoản 2 sẽ trả về context thiếu vế "trừ trường hợp các bên có thỏa thuận khác".

---

## Cách chấm (theo `docs/SCORING.md`)

| Điểm | Điều kiện |
|---|---|
| **2** | Top-3 chứa chunk có anchor **và** chunk đó ở top-1 |
| **1** | Chunk có anchor nằm trong top-3 nhưng **không** ở top-1 |
| **0** | Không chunk nào trong top-3 chứa anchor |

Tối đa **10 điểm** cho 5 query. Q4 chấm theo lần **có** `metadata_filter`.

---

## Cách chạy

```powershell
$env:EMBEDDING_PROVIDER="lexical"

python bench.py                 # strategy cá nhân
python bench.py --all           # tất cả, kèm bảng so sánh
python export_ket_qua.py        # xuất báo cáo Markdown của riêng mình
```
