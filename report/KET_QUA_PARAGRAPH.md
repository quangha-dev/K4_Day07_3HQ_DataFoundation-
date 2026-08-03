# Ket qua benchmark — strategy `paragraph`

**Nguyen Quang Ha · 2A202601424 · Lab 07 (K4)**

| Muc | Gia tri |
|---|---|
| Strategy | `paragraph` (`ParagraphChunker`) |
| Tham so | `max_chunk_size=700, min_chunk_size=450, keep_heading=True` |
| Corpus | `data/k4_ecommerce` |
| So chunk da nap | **65** |
| Embedding backend | `mock embeddings fallback` |
| top_k | 3 |

> ⚠️ Dang chay **MockEmbedder** (hash MD5). Score khong mang ngu nghia, khong dung ket qua nay de ket luan chat luong. Chay lai voi `EMBEDDING_PROVIDER=lexical`.

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
| 1 | +0.3023 | `nd52-quy-che-hoat-dong-san` | 3 | both | ## Điều 38. Quy chế hoạt động của sàn giao dịch thương mại điện tử l) Biện pháp xử lý vi phạm đối với những người không tuân thủ quy chế hoạt động của… |
| 2 | +0.2343 | `nd52-bao-ve-thong-tin-ca-nhan` | 7 | buyer | ## Điều 70. Xin phép người tiêu dùng khi tiến hành thu thập thông tin a) Thu thập thông tin cá nhân đã công bố công khai trên các website thương mại đ… |
| 3 | +0.2050 | `nd52-bao-ve-thong-tin-ca-nhan` | 4 | buyer | ## Điều 69. Chính sách bảo vệ thông tin cá nhân của người tiêu dùng e) Phương thức và công cụ để người tiêu dùng tiếp cận và chỉnh sửa dữ liệu cá nhân… |

**Cham chunk-level:** 0 — khong chunk nao chua anchor

**Cham doc-level (de doi chieu):** 0/2

**Cau tra loi cua agent:**

```
[MOCK LLM] Tra loi dua tren context: [1] (nguon: nd52-quy-che-hoat-dong-san::chunk_3 | url: https://vanban.vcci.com.vn/nghi-dinh-522013nd-cp-cua-chinh-phu-ve-thuong-mai-dien-tu) | ## Điều 38. Quy chế hoạt động của sàn giao dịch thương mại điện tử | l) Biện pháp xử lý vi phạm đối với những người không tuân thủ quy chế hoạt động của sàn giao dịch thương mại điện tử. | 3. Khi có thay đổi về một trong các nội dung nêu tại Khoản 2 Điều này, thương nhân, tổ chức cung cấp dịch vụ sàn giao dịch thương mại điện tử phải thông báo cho tất cả các đối tượng sử dụng dịch vụ sàn giao dịch thương mại điện tử 
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
| 1 | +0.2006 | `nd52-quy-trinh-dat-hang-truc-tuyen` | 5 | buyer | ## Điều 19. Trả lời đề nghị giao kết hợp đồng 1. Trả lời chấp nhận hoặc không chấp nhận đề nghị giao kết hợp đồng phải được thực hiện dưới hình thức p… |
| 2 | +0.1773 | `nd52-quy-trinh-dat-hang-truc-tuyen` | 8 | buyer | ## Điều 20. Chấm dứt đề nghị giao kết hợp đồng 2. Trường hợp thương nhân, tổ chức, cá nhân bán hàng không công bố rõ thời hạn trả lời đề nghị giao kết… |
| 3 | +0.1594 | `nd52-quy-trinh-dat-hang-truc-tuyen` | 2 | buyer | ## Điều 17. Đề nghị giao kết hợp đồng Chứng từ điện tử do khách hàng khởi tạo và gửi đi bằng cách sử dụng chức năng đặt hàng trực tuyến được coi là đề… |

**Cham chunk-level:** 0 — khong chunk nao chua anchor

**Cham doc-level (de doi chieu):** 0/2

**Cau tra loi cua agent:**

```
[MOCK LLM] Tra loi dua tren context: [1] (nguon: nd52-quy-trinh-dat-hang-truc-tuyen::chunk_5 | url: https://vanban.vcci.com.vn/nghi-dinh-522013nd-cp-cua-chinh-phu-ve-thuong-mai-dien-tu) | ## Điều 19. Trả lời đề nghị giao kết hợp đồng | 1. Trả lời chấp nhận hoặc không chấp nhận đề nghị giao kết hợp đồng phải được thực hiện dưới hình thức phù hợp để thông tin có thể lưu trữ, in và hiển thị được tại hệ thống thông tin của khách hàng. | 2. Khi trả lời chấp nhận đề nghị giao kết hợp đồng của khách hàng, thương nhân, tổ chức, cá nhân bán hàng phải cung cấp cho khách hàng những thông tin sau: | a) Da
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
| 1 | +0.2620 | `seller-listing` | 3 | seller | ## Điều 29. Thông tin về người sở hữu website 3. Số điện thoại hoặc một phương thức liên hệ trực tuyến khác. |
| 2 | +0.2285 | `nd52-trach-nhiem-san-tmdt` | 3 | both | ## Điều 36. Trách nhiệm của thương nhân, tổ chức cung cấp dịch vụ sàn giao dịch thương mại điện tử 3. Yêu cầu thương nhân, tổ chức, cá nhân là người b… |
| 3 | +0.2192 | `nd52-trach-nhiem-san-tmdt` | 1 | both | ## Điều 35. Cung cấp dịch vụ sàn giao dịch thương mại điện tử b) Website cho phép người tham gia được lập các website nhánh để trưng bày, giới thiệu h… |

**Cham chunk-level:** 0 — khong chunk nao chua anchor

**Cham doc-level (de doi chieu):** 0/2

**Cau tra loi cua agent:**

```
[MOCK LLM] Tra loi dua tren context: [1] (nguon: seller-listing::chunk_3 | url: https://vanban.vcci.com.vn/nghi-dinh-522013nd-cp-cua-chinh-phu-ve-thuong-mai-dien-tu) | ## Điều 29. Thông tin về người sở hữu website | 3. Số điện thoại hoặc một phương thức liên hệ trực tuyến khác. | [2] (nguon: nd52-trach-nhiem-san-tmdt::chunk_3 | url: https://vanban.vcci.com.vn/nghi-dinh-522013nd-cp-cua-chinh-phu-ve-thuong-mai-dien-tu) | ## Điều 36. Trách nhiệm của thương nhân, tổ chức cung cấp dịch vụ sàn giao dịch thương mại điện tử | 3. Yêu cầu thương nhân, tổ chức, cá nhân là người bán trên sàn giao dịch thư
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
| 1 | +0.3161 | `nd52-quy-che-hoat-dong-san` | 0 | both | ## Điều 38. Quy chế hoạt động của sàn giao dịch thương mại điện tử 1. Quy chế hoạt động của sàn giao dịch thương mại điện tử phải được thể hiện trên t… |
| 2 | +0.2193 | `nd52-quy-trinh-dat-hang-truc-tuyen` | 3 | buyer | ## Điều 18. Rà soát và xác nhận nội dung hợp đồng Website thương mại điện tử phải có cơ chế cho phép khách hàng rà soát, bổ sung, sửa đổi và xác nhận … |
| 3 | +0.2152 | `nd52-dang-ky-thong-bao-website` | 1 | seller | ## Điều 53. Thủ tục thông báo thiết lập website thương mại điện tử bán hàng 1. Thương nhân, tổ chức, cá nhân thiết lập website thương mại điện tử bán … |

**Co filter `{'customer_role': 'buyer'}`**

| # | score | doc_id | chunk | role | Trich noi dung |
|---|-------|--------|-------|------|----------------|
| 1 | +0.2193 | `nd52-quy-trinh-dat-hang-truc-tuyen` | 3 | buyer | ## Điều 18. Rà soát và xác nhận nội dung hợp đồng Website thương mại điện tử phải có cơ chế cho phép khách hàng rà soát, bổ sung, sửa đổi và xác nhận … |
| 2 | +0.1963 | `nd52-quy-trinh-dat-hang-truc-tuyen` | 2 | buyer | ## Điều 17. Đề nghị giao kết hợp đồng Chứng từ điện tử do khách hàng khởi tạo và gửi đi bằng cách sử dụng chức năng đặt hàng trực tuyến được coi là đề… |
| 3 | +0.1810 | `nd85-2021-diem-moi-bao-ve-nguoi-tieu-dung` | 3 | buyer | ## 2. Trách nhiệm cung cấp thông tin về hàng hóa, dịch vụ của người bán - Thông tin về hàng hóa công bố trên website phải bao gồm các nội dung bắt buộ… |

**A/B filter:** ket qua **KHAC NHAU**

**Cham chunk-level:** 0 — khong chunk nao chua anchor (DUNG doc_id nhung SAI section)

**Cham doc-level (de doi chieu):** 1/2

**Cau tra loi cua agent:**

```
[MOCK LLM] Tra loi dua tren context: [1] (nguon: nd52-quy-trinh-dat-hang-truc-tuyen::chunk_3 | url: https://vanban.vcci.com.vn/nghi-dinh-522013nd-cp-cua-chinh-phu-ve-thuong-mai-dien-tu) | ## Điều 18. Rà soát và xác nhận nội dung hợp đồng | Website thương mại điện tử phải có cơ chế cho phép khách hàng rà soát, bổ sung, sửa đổi và xác nhận nội dung giao dịch trước khi sử dụng chức năng đặt hàng trực tuyến để gửi đề nghị giao kết hợp đồng. Cơ chế rà soát và xác nhận này phải đáp ứng các điều kiện sau: | 1. Hiển thị cho khách hàng những thông tin sau: | a) Tên hàng hóa hoặc dịch vụ, số lượng và ch
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
| 1 | +0.1643 | `seller-listing` | 6 | seller | ## Điều 31. Thông tin về giá cả 3. Đối với dịch vụ trên các website cung cấp dịch vụ thương mại điện tử quy định tại Mục 2 và 4 Chương này, website ph… |
| 2 | +0.1484 | `nd52-bao-ve-thong-tin-ca-nhan` | 9 | buyer | ## Điều 72. Bảo đảm an toàn, an ninh thông tin cá nhân 3. Trong trường hợp hệ thống thông tin bị tấn công làm phát sinh nguy cơ mất thông tin của ngườ… |
| 3 | +0.1452 | `nd52-bao-ve-thong-tin-ca-nhan` | 5 | buyer | ## Điều 70. Xin phép người tiêu dùng khi tiến hành thu thập thông tin 1. Trừ trường hợp quy định tại khoản 4 Điều này, đơn vị thu thập và sử dụng thôn… |

**Cham chunk-level:** 0 — khong chunk nao chua anchor (DUNG doc_id nhung SAI section)

**Cham doc-level (de doi chieu):** 2/2

**Cau tra loi cua agent:**

```
[MOCK LLM] Tra loi dua tren context: [1] (nguon: seller-listing::chunk_6 | url: https://vanban.vcci.com.vn/nghi-dinh-522013nd-cp-cua-chinh-phu-ve-thuong-mai-dien-tu) | ## Điều 31. Thông tin về giá cả | 3. Đối với dịch vụ trên các website cung cấp dịch vụ thương mại điện tử quy định tại Mục 2 và 4 Chương này, website phải công bố thông tin chi tiết về cách thức tính phí dịch vụ và cơ chế thanh toán. | [2] (nguon: nd52-bao-ve-thong-tin-ca-nhan::chunk_9 | url: https://thuvienphapluat.vn/chinh-sach-phap-luat-moi/vn/chong-lua-dao/58992/05-quy-dinh-ve-bao-ve-thong-tin-ca-nhan-trong-thuong-mai-dien-t
```

---

## Tong ket

| Query | Loai | Doc-level | Chunk-level | Ghi chu |
|-------|------|-----------|-------------|---------|
| Q1 | so lieu | 0 | 0 | khong chunk nao chua anchor |
| Q2 | dieu kien | 0 | 0 | khong chunk nao chua anchor |
| Q3 | quy trinh | 0 | 0 | khong chunk nao chua anchor |
| Q4 | liet ke + FILTER BAT BUOC | 1 | 0 | khong chunk nao chua anchor (DUNG doc_id nhung SAI section) |
| Q5 | ngoai le | 2 | 0 | khong chunk nao chua anchor (DUNG doc_id nhung SAI section) |
| **TONG** | | **3/10** | **0/10** | |

Chenh lech **3 vs 0**: cham theo `doc_id` cho diem cao hon vi chi can lay dung TAI LIEU la duoc, du chunk lay ve khong chua cau tra loi. Day la ly do bo query phai co `anchors`.
