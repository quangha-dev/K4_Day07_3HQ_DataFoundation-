# Ket qua benchmark — strategy `paragraph`

**Nguyen Quang Ha · 2A202601424 · Lab 07 (K4)**

| Muc | Gia tri |
|---|---|
| Strategy | `paragraph` (`ParagraphChunker`) |
| Tham so | `max_chunk_size=700, min_chunk_size=450, keep_heading=True` |
| Corpus | `data/k4_ecommerce` |
| So chunk da nap | **65** |
| Embedding backend | `lexical tf-idf (dim=2048)` |
| top_k | 3 |

Sinh tu dong boi `export_ket_qua.py`. Khong sua tay file nay.

---

## Q1 — so lieu

**Cau hoi:** Nếu người bán không công bố rõ thời hạn trả lời, sau bao lâu đề nghị giao kết hợp đồng của khách hàng hết hiệu lực?

**Gold answer:** Trong vòng 12 (mười hai) giờ kể từ khi gửi đề nghị giao kết hợp đồng mà khách hàng không nhận được trả lời thì đề nghị được coi là chấm dứt hiệu lực (khoản 2 Điều 20 Nghị định 52/2013/NĐ-CP).

**Tai lieu ky vong:** `nd52-quy-trinh-dat-hang-truc-tuyen`

**Anchor (chuoi phai xuat hien trong chunk):** `12 (mười hai) giờ`

**Khong filter**

| # | score | doc_id | chunk | role | Trich noi dung |
|---|-------|--------|-------|------|----------------|
| 1 | +0.4102 | `nd52-quy-trinh-dat-hang-truc-tuyen` | 8 | buyer | ## Điều 20. Chấm dứt đề nghị giao kết hợp đồng 2. Trường hợp thương nhân, tổ chức, cá nhân bán hàng không công bố rõ thời hạn trả lời đề nghị giao kết… |
| 2 | +0.3668 | `nd52-quy-trinh-dat-hang-truc-tuyen` | 7 | buyer | ## Điều 20. Chấm dứt đề nghị giao kết hợp đồng 1. Trường hợp thương nhân, tổ chức, cá nhân bán hàng có công bố thời hạn trả lời đề nghị giao kết hợp đ… |
| 3 | +0.2489 | `nd52-quy-trinh-dat-hang-truc-tuyen` | 5 | buyer | ## Điều 19. Trả lời đề nghị giao kết hợp đồng 1. Trả lời chấp nhận hoặc không chấp nhận đề nghị giao kết hợp đồng phải được thực hiện dưới hình thức p… |

**Cham chunk-level:** 2 — anchor nam o chunk top-1

**Cham doc-level (de doi chieu):** 2/2

**Cau tra loi cua agent:**

```
[MOCK LLM] Tra loi dua tren context: [1] (nguon: nd52-quy-trinh-dat-hang-truc-tuyen::chunk_8 | url: https://vanban.vcci.com.vn/nghi-dinh-522013nd-cp-cua-chinh-phu-ve-thuong-mai-dien-tu) | ## Điều 20. Chấm dứt đề nghị giao kết hợp đồng | 2. Trường hợp thương nhân, tổ chức, cá nhân bán hàng không công bố rõ thời hạn trả lời đề nghị giao kết hợp đồng, nếu trong vòng 12 (mười hai) giờ kể từ khi gửi đề nghị giao kết hợp đồng, khách hàng không nhận được trả lời đề nghị giao kết hợp đồng thì đề nghị giao kết hợp đồng của khách hàng được coi là chấm dứt hiệu lực. | [2] (nguon: nd52-quy-trinh-dat-hang-
```

---

## Q2 — dieu kien

**Cau hoi:** Sàn giao dịch thương mại điện tử phải thông báo trước bao nhiêu ngày khi thay đổi quy chế hoạt động?

**Gold answer:** Phải thông báo cho tất cả đối tượng sử dụng dịch vụ ít nhất 5 ngày trước khi áp dụng thay đổi (khoản 3 Điều 38 Nghị định 52/2013/NĐ-CP).

**Tai lieu ky vong:** `nd52-quy-che-hoat-dong-san`

**Anchor (chuoi phai xuat hien trong chunk):** `ít nhất 5 ngày`

**Khong filter**

| # | score | doc_id | chunk | role | Trich noi dung |
|---|-------|--------|-------|------|----------------|
| 1 | +0.2979 | `nd52-quy-che-hoat-dong-san` | 3 | both | ## Điều 38. Quy chế hoạt động của sàn giao dịch thương mại điện tử l) Biện pháp xử lý vi phạm đối với những người không tuân thủ quy chế hoạt động của… |
| 2 | +0.2353 | `nd52-quy-che-hoat-dong-san` | 0 | both | ## Điều 38. Quy chế hoạt động của sàn giao dịch thương mại điện tử 1. Quy chế hoạt động của sàn giao dịch thương mại điện tử phải được thể hiện trên t… |
| 3 | +0.2299 | `nd52-trach-nhiem-san-tmdt` | 2 | both | ## Điều 36. Trách nhiệm của thương nhân, tổ chức cung cấp dịch vụ sàn giao dịch thương mại điện tử 1. Đăng ký thiết lập website cung cấp dịch vụ sàn g… |

**Cham chunk-level:** 2 — anchor nam o chunk top-1

**Cham doc-level (de doi chieu):** 2/2

**Cau tra loi cua agent:**

```
[MOCK LLM] Tra loi dua tren context: [1] (nguon: nd52-quy-che-hoat-dong-san::chunk_3 | url: https://vanban.vcci.com.vn/nghi-dinh-522013nd-cp-cua-chinh-phu-ve-thuong-mai-dien-tu) | ## Điều 38. Quy chế hoạt động của sàn giao dịch thương mại điện tử | l) Biện pháp xử lý vi phạm đối với những người không tuân thủ quy chế hoạt động của sàn giao dịch thương mại điện tử. | 3. Khi có thay đổi về một trong các nội dung nêu tại Khoản 2 Điều này, thương nhân, tổ chức cung cấp dịch vụ sàn giao dịch thương mại điện tử phải thông báo cho tất cả các đối tượng sử dụng dịch vụ sàn giao dịch thương mại điện tử 
```

---

## Q3 — quy trinh

**Cau hoi:** Cơ chế rà soát và xác nhận nội dung hợp đồng phải hiển thị những thông tin gì cho khách hàng trước khi đặt hàng?

**Gold answer:** Tên hàng hóa/dịch vụ, số lượng và chủng loại; phương thức và thời hạn giao hàng; tổng giá trị hợp đồng và chi tiết phương thức thanh toán. Ngoài ra phải hiển thị cách thức và thời hạn trả lời đề nghị giao kết, và cho phép hủy giao dịch (Điều 18 Nghị định 52/2013/NĐ-CP).

**Tai lieu ky vong:** `nd52-quy-trinh-dat-hang-truc-tuyen`

**Anchor (chuoi phai xuat hien trong chunk):** `Tổng giá trị của hợp đồng`

**Khong filter**

| # | score | doc_id | chunk | role | Trich noi dung |
|---|-------|--------|-------|------|----------------|
| 1 | +0.3909 | `nd52-quy-trinh-dat-hang-truc-tuyen` | 3 | buyer | ## Điều 18. Rà soát và xác nhận nội dung hợp đồng Website thương mại điện tử phải có cơ chế cho phép khách hàng rà soát, bổ sung, sửa đổi và xác nhận … |
| 2 | +0.2689 | `nd52-quy-trinh-dat-hang-truc-tuyen` | 4 | buyer | ## Điều 18. Rà soát và xác nhận nội dung hợp đồng c) Tổng giá trị của hợp đồng và các chi tiết liên quan đến phương thức thanh toán được khách hàng lự… |
| 3 | +0.2313 | `seller-listing` | 9 | seller | ## Điều 34. Thông tin về các phương thức thanh toán 1. Thương nhân, tổ chức, cá nhân phải công bố toàn bộ các phương thức thanh toán áp dụng cho hàng … |

**Cham chunk-level:** 1 — anchor nam o top-2, khong phai top-1

**Cham doc-level (de doi chieu):** 2/2

**Cau tra loi cua agent:**

```
[MOCK LLM] Tra loi dua tren context: [1] (nguon: nd52-quy-trinh-dat-hang-truc-tuyen::chunk_3 | url: https://vanban.vcci.com.vn/nghi-dinh-522013nd-cp-cua-chinh-phu-ve-thuong-mai-dien-tu) | ## Điều 18. Rà soát và xác nhận nội dung hợp đồng | Website thương mại điện tử phải có cơ chế cho phép khách hàng rà soát, bổ sung, sửa đổi và xác nhận nội dung giao dịch trước khi sử dụng chức năng đặt hàng trực tuyến để gửi đề nghị giao kết hợp đồng. Cơ chế rà soát và xác nhận này phải đáp ứng các điều kiện sau: | 1. Hiển thị cho khách hàng những thông tin sau: | a) Tên hàng hóa hoặc dịch vụ, số lượng và ch
```

---

## Q4 — liet ke + FILTER BAT BUOC

**Cau hoi:** Chính sách kiểm hàng có phải là một điều kiện giao dịch chung bắt buộc phải công bố không?

**Gold answer:** Có. Từ ngày 01/01/2022, chính sách kiểm hàng là một trong những điều kiện giao dịch chung bắt buộc phải công bố trên website TMĐT (Nghị định 85/2021/NĐ-CP). Bản gốc Điều 32 Nghị định 52/2013/NĐ-CP KHÔNG liệt kê chính sách kiểm hàng — trả lời theo bản 2013 là sai.

**Tai lieu ky vong:** `nd85-2021-diem-moi-bao-ve-nguoi-tieu-dung`

**Anchor (chuoi phai xuat hien trong chunk):** `chính sách kiểm hàng`

**Khong filter**

| # | score | doc_id | chunk | role | Trich noi dung |
|---|-------|--------|-------|------|----------------|
| 1 | +0.3591 | `nd85-2021-diem-moi-bao-ve-nguoi-tieu-dung` | 5 | buyer | ## 4. Chính sách kiểm hàng là điều kiện giao dịch chung bắt buộc Từ ngày 01/01/2022, chính sách kiểm hàng được coi là một trong những điều kiện giao d… |
| 2 | +0.2388 | `returns-policy` | 3 | seller | ## Ghi chú về phiên bản Đây là văn bản gốc năm 2013. Danh mục điều kiện giao dịch chung tại khoản 1 Điều 32 bản 2013 KHÔNG liệt kê chính sách kiểm hàn… |
| 3 | +0.1612 | `returns-policy` | 0 | seller | ## Điều 32. Thông tin về điều kiện giao dịch chung 1. Thương nhân, tổ chức, cá nhân phải công bố những điều kiện giao dịch chung đối với hàng hóa hoặc… |

**Co filter `{'customer_role': 'buyer'}`**

| # | score | doc_id | chunk | role | Trich noi dung |
|---|-------|--------|-------|------|----------------|
| 1 | +0.3591 | `nd85-2021-diem-moi-bao-ve-nguoi-tieu-dung` | 5 | buyer | ## 4. Chính sách kiểm hàng là điều kiện giao dịch chung bắt buộc Từ ngày 01/01/2022, chính sách kiểm hàng được coi là một trong những điều kiện giao d… |
| 2 | +0.1260 | `nd52-quy-trinh-dat-hang-truc-tuyen` | 7 | buyer | ## Điều 20. Chấm dứt đề nghị giao kết hợp đồng 1. Trường hợp thương nhân, tổ chức, cá nhân bán hàng có công bố thời hạn trả lời đề nghị giao kết hợp đ… |
| 3 | +0.1194 | `nd85-2021-diem-moi-bao-ve-nguoi-tieu-dung` | 3 | buyer | ## 2. Trách nhiệm cung cấp thông tin về hàng hóa, dịch vụ của người bán - Thông tin về hàng hóa công bố trên website phải bao gồm các nội dung bắt buộ… |

**A/B filter:** ket qua **KHAC NHAU**

**Cham chunk-level:** 2 — anchor nam o chunk top-1

**Cham doc-level (de doi chieu):** 2/2

**Cau tra loi cua agent:**

```
[MOCK LLM] Tra loi dua tren context: [1] (nguon: nd85-2021-diem-moi-bao-ve-nguoi-tieu-dung::chunk_5 | url: https://moit.gov.vn/tin-tuc/thong-bao/mot-so-diem-moi-ve-bao-ve-quyen-loi-nguoi-tieu-dung-trong-nghi-dinh-so-85-2021-nd-cp-ve-thuong-mai-dien-tu.html) | ## 4. Chính sách kiểm hàng là điều kiện giao dịch chung bắt buộc | Từ ngày 01/01/2022, chính sách kiểm hàng được coi là một trong những điều kiện giao dịch chung bắt buộc mà thương nhân, tổ chức, cá nhân phải công bố trên website thương mại điện tử. Quy định này giúp người tiêu dùng hiểu rõ về chính sách kiểm hàng của từng doanh nghiệp tr
```

---

## Q5 — ngoai le

**Cau hoi:** Website niêm yết giá mà không nói rõ đã bao gồm thuế và phí vận chuyển chưa thì hiểu thế nào?

**Gold answer:** Trừ trường hợp các bên có thỏa thuận khác, giá niêm yết được hiểu là đã bao gồm mọi chi phí liên quan như thuế, phí đóng gói, phí vận chuyển và chi phí phát sinh khác (khoản 2 Điều 31 Nghị định 52/2013/NĐ-CP).

**Tai lieu ky vong:** `seller-listing`

**Anchor (chuoi phai xuat hien trong chunk):** `được hiểu là đã bao gồm mọi chi phí`

**Khong filter**

| # | score | doc_id | chunk | role | Trich noi dung |
|---|-------|--------|-------|------|----------------|
| 1 | +0.2550 | `seller-listing` | 5 | seller | ## Điều 31. Thông tin về giá cả 1. Thông tin về giá hàng hóa hoặc dịch vụ, nếu có, phải thể hiện rõ giá đó đã bao gồm hay chưa bao gồm những chi phí l… |
| 2 | +0.0976 | `seller-listing` | 7 | seller | ## Điều 33. Thông tin về vận chuyển và giao nhận 1. Thương nhân, tổ chức, cá nhân phải công bố những thông tin sau về điều kiện vận chuyển và giao nhậ… |
| 3 | +0.0939 | `nd52-quy-trinh-dat-hang-truc-tuyen` | 5 | buyer | ## Điều 19. Trả lời đề nghị giao kết hợp đồng 1. Trả lời chấp nhận hoặc không chấp nhận đề nghị giao kết hợp đồng phải được thực hiện dưới hình thức p… |

**Cham chunk-level:** 2 — anchor nam o chunk top-1

**Cham doc-level (de doi chieu):** 2/2

**Cau tra loi cua agent:**

```
[MOCK LLM] Tra loi dua tren context: [1] (nguon: seller-listing::chunk_5 | url: https://vanban.vcci.com.vn/nghi-dinh-522013nd-cp-cua-chinh-phu-ve-thuong-mai-dien-tu) | ## Điều 31. Thông tin về giá cả | 1. Thông tin về giá hàng hóa hoặc dịch vụ, nếu có, phải thể hiện rõ giá đó đã bao gồm hay chưa bao gồm những chi phí liên quan đến việc mua hàng hóa hoặc dịch vụ như thuế, phí đóng gói, phí vận chuyển và các chi phí phát sinh khác. | 2. Trừ trường hợp các bên có thỏa thuận khác, nếu thông tin giá hàng hóa hoặc dịch vụ niêm yết trên website không thể hiện rõ giá đó đã bao gồm hay chưa bao gồm nhữ
```

---

## Tong ket

| Query | Loai | Doc-level | Chunk-level | Ghi chu |
|-------|------|-----------|-------------|---------|
| Q1 | so lieu | 2 | 2 | anchor nam o chunk top-1 |
| Q2 | dieu kien | 2 | 2 | anchor nam o chunk top-1 |
| Q3 | quy trinh | 2 | 1 | anchor nam o top-2, khong phai top-1 |
| Q4 | liet ke + FILTER BAT BUOC | 2 | 2 | anchor nam o chunk top-1 |
| Q5 | ngoai le | 2 | 2 | anchor nam o chunk top-1 |
| **TONG** | | **10/10** | **9/10** | |

Chenh lech **10 vs 9**: cham theo `doc_id` cho diem cao hon vi chi can lay dung TAI LIEU la duoc, du chunk lay ve khong chua cau tra loi. Day la ly do bo query phai co `anchors`.
