# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** 3HQ
**Thành viên:** Trương Ngọc Hải, Nguyễn Nhật Quang, Vũ Văn Huy và Nguyễn Quang Hà
**Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K4):** Chính sách thương mại điện tử / hỗ trợ khách hàng (thanh toán, đổi trả, giao hàng, quyền riêng tư, điều kiện người bán…).

**Phạm vi cụ thể nhóm tập trung:**
> Các quy định về đặt hàng trực tuyến, niêm yết giá, điều kiện giao dịch chung, trách nhiệm của người bán và bảo vệ người tiêu dùng trên sàn thương mại điện tử.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Bảo vệ thông tin cá nhân của người tiêu dùng | Thư Viện Pháp Luật | 03/08/2026 — 52/2013/NĐ-CP | 5.291 | `doc_id`, `customer_role=buyer`, nguồn, phiên bản |
| 2 | Điều kiện và thủ tục thông báo, đăng ký website TMĐT | VCCI | 03/08/2026 — 52/2013/NĐ-CP | 3.876 | `doc_id`, `customer_role=seller`, nguồn, phiên bản |
| 3 | Quy chế hoạt động của sàn giao dịch TMĐT | VCCI | 03/08/2026 — 52/2013/NĐ-CP | 2.398 | `doc_id`, `customer_role=both`, nguồn, phiên bản |
| 4 | Quy trình giao kết hợp đồng khi đặt hàng trực tuyến | VCCI | 03/08/2026 — 52/2013/NĐ-CP | 5.445 | `doc_id`, `customer_role=buyer`, nguồn, phiên bản |
| 5 | Trách nhiệm của người bán trên sàn giao dịch TMĐT | VCCI | 03/08/2026 — 52/2013/NĐ-CP | 1.738 | `doc_id`, `customer_role=seller`, nguồn, phiên bản |
| 6 | Trách nhiệm của đơn vị cung cấp sàn giao dịch TMĐT | VCCI | 03/08/2026 — 52/2013/NĐ-CP | 3.577 | `doc_id`, `customer_role=both`, nguồn, phiên bản |
| 7 | Điểm mới về bảo vệ người tiêu dùng trong Nghị định 85/2021 | Bộ Công Thương | 03/08/2026 — 85/2021/NĐ-CP | 4.323 | `doc_id`, `customer_role=buyer`, nguồn, phiên bản |
| 8 | Điều kiện giao dịch chung và chính sách hoàn trả | VCCI | 03/08/2026 — 52/2013/NĐ-CP | 1.942 | `doc_id`, `customer_role=seller`, nguồn, phiên bản |
| 9 | Thông tin người bán phải công bố khi đăng bán | VCCI | 03/08/2026 — 52/2013/NĐ-CP | 4.199 | `doc_id`, `customer_role=seller`, nguồn, phiên bản |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | Chuỗi | `nd52-quy-trinh-dat-hang-truc-tuyen` | Nhận diện tài liệu gốc và kiểm tra đúng nguồn của chunk. |
| `customer_role` | Chuỗi phân loại | `buyer`, `seller`, `both` | Lọc kết quả theo đối tượng áp dụng của câu hỏi. |
| `source_url` | URL | `https://vanban.vcci.com.vn/...` | Truy vết và kiểm chứng nội dung pháp lý. |
| `retrieved_at` | Ngày | `2026-08-03` | Theo dõi thời điểm thu thập dữ liệu. |
| `document_version` | Chuỗi | `52/2013/ND-CP` | Phân biệt phiên bản văn bản và tránh dùng quy định lỗi thời. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Toàn bộ corpus K4 (khoảng 32.789 ký tự) | FixedSizeChunker (`fixed_size`, 500/50) | 67 | ≈489 | Trung bình; có thể cắt ngang điều khoản. |
| Toàn bộ corpus K4 (khoảng 32.789 ký tự) | SentenceChunker (`by_sentences`, 3 câu/chunk) | 69 | ≈475 | Khá, nhưng có thể tách phần dẫn và số liệu. |
| Toàn bộ corpus K4 (khoảng 32.789 ký tự) | RecursiveChunker (`recursive`, 400 ký tự) | 92 | ≈356 | Khá ở đoạn ngắn, nhưng tạo nhiều chunk và mất liên kết tiêu đề. |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Trương Ngọc Hải**
- **Loại chiến lược:** Custom Clause Chunking.
- **Mô tả & lý do chọn cho chủ đề này:** Chia theo mệnh đề với `max_chunk_size=700`, tối đa 3 câu và `min_chunk_size=120`, nhằm giữ từng quy định pháp lý thành đoạn ngắn. Chiến lược tạo 74 chunk nhưng các mệnh đề liên quan vẫn dễ bị tách khỏi số liệu hoặc tiêu đề của điều khoản.

**Thành viên 2 — Nguyễn Nhật Quang**
- **Loại chiến lược:** Custom Heading Chunking.
- **Mô tả & lý do chọn:** Chia theo cấu trúc heading, giữ breadcrumb, với `max_chunk_size=900` và `min_chunk_size=120`. Cách này phù hợp văn bản pháp luật vì giữ tên điều/mục cùng nội dung, tạo 50 chunk và đạt 9/10.

**Thành viên 3 — Vũ Văn Huy**
- **Loại chiến lược:** Custom Semantic Chunking.
- **Mô tả & lý do chọn:** Dùng ngưỡng percentile 25 để phát hiện điểm đổi chủ đề, giới hạn chunk từ 120 đến 900 ký tự. Chiến lược tạo 55 chunk, giảm số lượng chunk nhưng đôi khi gộp hoặc tách chưa đúng ranh giới điều khoản.

**Thành viên 4 — Phụ trách `paragraph.txt` (file kết quả chưa ghi tên)**
- **Loại chiến lược:** Custom Paragraph Chunking.
- **Mô tả & lý do chọn:** Chia theo đoạn, giữ heading, với `max_chunk_size=700` và `min_chunk_size=450`. Việc gộp các đoạn ngắn nhưng vẫn giữ tiêu đề tạo 65 chunk và đạt 9/10; ablation bỏ heading chỉ đạt 8/10, còn không gộp đoạn chỉ đạt 7/10.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Trương Ngọc Hải | Clause | 1/10 | Chunk ngắn, bám ranh giới câu/mệnh đề. | Tách rời tiêu đề, số liệu và nội dung; 4/5 câu không có anchor trong top-3. |
| Nguyễn Nhật Quang | Heading | 9/10 | Giữ cấu trúc điều/mục; chỉ 50 chunk; Q1, Q2, Q4, Q5 đúng top-1. | Q3 chỉ xuất hiện ở top-2 nên chưa đạt điểm tối đa. |
| Vũ Văn Huy | Semantic | 6/10 | Ít chunk, thích ứng theo thay đổi nội dung; Q4 và Q5 đúng top-1. | Q1, Q2 chỉ ở top-2 và Q3 không tìm thấy anchor. |
| Nguyễn Quang Hà | Paragraph | 9/10 | Giữ heading, gộp đoạn ngắn; Q1, Q2, Q4, Q5 đúng top-1. | Q3 chỉ ở top-2; cần tinh chỉnh gộp đoạn quanh danh sách. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Heading và Paragraph cùng đạt 9/10, cao nhất trong bốn chiến lược. Với văn bản pháp luật có cấu trúc điều/mục rõ ràng, Heading được ưu tiên vì chỉ cần 50 chunk mà vẫn giữ tiêu đề với nội dung, trong khi Paragraph cũng rất hiệu quả nhờ giữ heading và gộp các đoạn ngắn; kết quả ablation cho thấy bỏ heading làm điểm giảm từ 9 xuống 8.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Nếu người bán không công bố rõ thời hạn trả lời, sau bao lâu đề nghị giao kết hợp đồng của khách hàng hết hiệu lực? | 12 (mười hai) giờ kể từ thời điểm gửi đề nghị giao kết hợp đồng. | `nd52-quy-trinh-dat-hang-truc-tuyen`, Điều 20 |
| 2 | Sàn giao dịch thương mại điện tử phải thông báo trước bao nhiêu ngày khi thay đổi quy chế hoạt động? | Phải thông báo cho các đối tượng sử dụng dịch vụ ít nhất 5 ngày trước khi áp dụng thay đổi. | `nd52-quy-che-hoat-dong-san`, Điều 38 |
| 3 | Cơ chế rà soát và xác nhận nội dung hợp đồng phải hiển thị những thông tin gì cho khách hàng trước khi đặt hàng? | Phải hiển thị tên hàng hóa/dịch vụ, số lượng, phương thức và thời hạn giao hàng/cung ứng, tổng giá trị hợp đồng và chi tiết phương thức thanh toán. | `nd52-quy-trinh-dat-hang-truc-tuyen`, Điều 18 |
| 4 | Chính sách kiểm hàng có phải là một điều kiện giao dịch chung bắt buộc phải công bố không? | Có. Từ 01/01/2022, chính sách kiểm hàng là một điều kiện giao dịch chung bắt buộc phải công bố. | `nd85-2021-diem-moi-bao-ve-nguoi-tieu-dung`, mục 4 |
| 5 | Website niêm yết giá mà không nói rõ đã bao gồm thuế và phí vận chuyển chưa thì hiểu thế nào? | Trừ khi các bên có thỏa thuận khác, giá được hiểu là đã bao gồm mọi chi phí liên quan đến hàng hóa hoặc dịch vụ. | `seller-listing`, phần thông tin về giá cả |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Thời hạn đề nghị giao kết hợp đồng | Heading hoặc Paragraph | Có — top-1 | Cả hai chiến lược đạt 2 điểm. |
| 2 | Thời hạn báo trước khi đổi quy chế | Heading hoặc Paragraph | Có — top-1 | Cả hai chiến lược đạt 2 điểm. |
| 3 | Thông tin phải hiển thị trước khi đặt hàng | Heading hoặc Paragraph | Có — top-2 | Anchor đúng nhưng không ở top-1, đạt 1 điểm. |
| 4 | Chính sách kiểm hàng bắt buộc | Heading hoặc Paragraph | Có — top-1 | Chấm theo lần chạy có `customer_role=buyer`; cả hai đạt 2 điểm. |
| 5 | Cách hiểu giá chưa nói rõ thuế/phí | Heading hoặc Paragraph | Có — top-1 | Cả hai chiến lược đạt 2 điểm. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, metadata filter được áp dụng ở câu 4 với `customer_role=buyer`. Bộ lọc loại các chunk dành riêng cho người bán, làm tập ứng viên tập trung hơn; tác động rõ nhất ở Clause khi chunk chứa “chính sách kiểm hàng” được đưa vào top-3, dù chưa lên top-1. Với Heading và Paragraph, đáp án vốn đã ở top-1 nhưng bộ lọc vẫn giảm nhiễu.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> - Giữ heading/breadcrumb đặc biệt quan trọng với văn bản pháp luật vì tiêu đề điều khoản cung cấp ngữ cảnh trực tiếp cho nội dung.
> - Paragraph có heading đạt 9/10; bỏ heading giảm còn 8/10 và không gộp đoạn giảm còn 7/10, chứng minh cả tiêu đề lẫn bước gộp đoạn ngắn đều có ích.
> - Ít chunk không đồng nghĩa với truy xuất tốt hơn: Semantic có 55 chunk nhưng chỉ đạt 6/10, trong khi Heading có 50 chunk và đạt 9/10 nhờ ranh giới cấu trúc chính xác hơn.

**Bài học rút ra khi so sánh trong nhóm:**
> Trên cùng corpus và cùng năm câu hỏi, điểm số dao động từ 1/10 đến 9/10, cho thấy ranh giới chunk ảnh hưởng trực tiếp đến khả năng giữ câu hỏi, điều khoản và số liệu trong cùng ngữ cảnh. Các chiến lược bám cấu trúc tài liệu như Heading và Paragraph vượt trội hơn cách chia mệnh đề hoặc chỉ dựa trên độ tương đồng ngữ nghĩa.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ kết hợp Heading với Paragraph: giữ breadcrumb, gộp đoạn ngắn nhưng không tách danh sách khỏi câu dẫn, đặc biệt quanh Điều 18 là câu duy nhất chưa đạt top-1. Nhóm cũng sẽ chuẩn hóa thêm metadata theo số điều, loại văn bản và ngày hiệu lực để có thể lọc chính xác hơn trước khi xếp hạng.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 9 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **39 / 40** |
