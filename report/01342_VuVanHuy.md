# Báo cáo cá nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Vũ Văn Huy  
**MSSV:** 2A202601342  
**Nhóm:** 3HQ  
**Chiến lược cá nhân:** `SemanticSplitChunker`  
**Nguồn số liệu:** `report/bench_output_lexical.txt`

---

## 1. Khởi động

### Cosine similarity

Cosine similarity đo góc giữa hai vector embedding:

`cosine(a, b) = (a · b) / (||a|| × ||b||)`

Điểm cao cho biết hai vector cùng hướng, tức nội dung mà mô hình biểu diễn có xu hướng gần nhau. Cosine phù hợp cho text embedding hơn Euclid vì nó giảm ảnh hưởng của độ dài văn bản và tập trung vào hướng của vector.

Ví dụ, “Người bán phải công bố chính sách hoàn trả” và “Website phải nêu rõ quy định đổi trả” có ý nghĩa gần nhau. Ngược lại, câu về thời hạn trả lời đề nghị giao kết và câu về thời gian thông báo thay đổi quy chế cùng chứa số lượng thời gian nhưng khác chủ thể, điều kiện và nghĩa vụ nên độ tương tự nên thấp.

### Bài toán chunking

Với tài liệu 10.000 ký tự, `chunk_size=500` và `overlap=50`, bước trượt là 450 ký tự. Số chunk là:

`ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23`.

Nếu tăng overlap lên 100 thì có 25 chunk. Overlap cao làm tăng khả năng giữ đủ ngữ cảnh ở ranh giới chunk, nhưng tăng số vector, chi phí lưu trữ và nguy cơ các kết quả top-k bị lặp nội dung.

## 2. Hướng tiếp cận và phần code thực hiện

Tôi triển khai các thành phần chính trong gói `src/K4_2A202601342_VuVanHuy`:

- `SentenceChunker`: tách câu bằng dấu kết câu, loại chuỗi rỗng và gộp câu theo giới hạn cấu hình.
- `RecursiveChunker`: lần lượt tách theo các separator từ lớn đến nhỏ; khi không thể tách thì cắt cứng để bảo đảm không vượt kích thước chunk.
- `EmbeddingStore`: lưu document cùng embedding và metadata; khi tìm kiếm, embedding query được tính một lần, sau đó xếp hạng giảm dần theo điểm tương tự.
- `search_with_filter`: lọc metadata trước khi xếp hạng. Cách này không làm mất ứng viên hợp lệ chỉ vì top-k ban đầu bị chiếm bởi nhóm metadata khác.
- `delete_document`: xóa toàn bộ record mang cùng `doc_id` và trả về trạng thái thành công.
- `KnowledgeBaseAgent`: lấy top-k context, đánh số nguồn theo dạng `doc_id::chunk_N`, rồi đưa vào prompt. Nhờ vậy câu trả lời có thể truy vết về đúng chunk.

Chiến lược cá nhân là `SemanticSplitChunker(percentile=25, max_chunk_size=900, min_chunk_size=120)`. Tôi tách văn bản thành các đơn vị câu/dòng, embed mỗi đơn vị đúng một lần, tính cosine similarity giữa hai đơn vị kề nhau rồi cắt tại 25% điểm có similarity thấp nhất. Các mảnh dưới 120 ký tự được gộp lại và giới hạn 900 ký tự ngăn context quá dài. Đây là semantic splitting: ranh giới được suy ra từ sự thay đổi của biểu diễn embedding, thay vì chỉ dựa trên tiêu đề hay số ký tự.

## 3. Kiểm thử

Đã chạy:

```text
python -m pytest tests -v
42 passed in 0.02s
```

Toàn bộ 42/42 bài kiểm thử đều đạt, gồm chunking, embedding store, tìm kiếm có filter, xóa document, agent và cosine similarity.

## 4. Dự đoán độ tương tự

Tôi dùng `LexicalEmbedder` TF-IDF trong benchmark để có phép so sánh dựa trên từ vựng. Kết quả cần được hiểu đúng: TF-IDF đo mức trùng token, không hiểu hoàn toàn các câu đồng nghĩa.

| Cặp ví dụ | Dự đoán | Nhận xét thực tế |
|---|---|---|
| “Chính sách đổi trả hàng hóa” / “Quy định hoàn trả sản phẩm” | Cao | TF-IDF cho điểm thấp vì ít từ chung; đây là giới hạn của lexical embedding với paraphrase. |
| Một câu so với chính nó | Cao | Điểm 1.0; phù hợp kỳ vọng. |
| Thời hạn trả lời hợp đồng / thông báo đổi quy chế | Thấp | Khác nghĩa vụ và bối cảnh; lexical có thể cho gần 0 khi không trùng từ. |
| Chính sách kiểm hàng / nghĩa vụ công bố điều kiện giao dịch chung | Trung bình–cao | Có thuật ngữ pháp lý liên quan, nhưng cần đọc context để kết luận. |
| Giá không nêu thuế phí / quy định giá hàng hóa | Cao | Có nhiều thuật ngữ chung nên phù hợp cho truy xuất lexical. |

Kết luận: score là tín hiệu xếp hạng, không phải bằng chứng rằng câu trả lời đúng. Đặc biệt, câu diễn đạt lại tốt vẫn có thể bị TF-IDF xếp thấp.

## 5. Kết quả truy xuất

Benchmark sử dụng backend **lexical TF-IDF (dim=2048)** trên 9 tài liệu `data/k4_ecommerce`. Chiến lược semantic tạo **55 chunks** và đạt **6/10**.

| Câu | Top-1 truy xuất | Điểm | Đánh giá |
|---|---|---:|---|
| Q1: Không công bố thời hạn trả lời | `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_4` | 0.3347 | Chunk đáp án ở top-2, nên đạt 1/2 điểm. |
| Q2: Thay đổi quy chế sàn | `nd52-quy-che-hoat-dong-san::chunk_0` | 0.4006 | Chunk đáp án ở top-2, nên đạt 1/2 điểm. |
| Q3: Rà soát hợp đồng | `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_2` | 0.4081 | Không có chunk chứa anchor trong top-3; đạt 0/2 điểm. |
| Q4: Chính sách kiểm hàng | `nd85-2021-diem-moi-bao-ve-nguoi-tieu-dung::chunk_4` | 0.3084 | Đúng khi dùng filter `customer_role=buyer`. |
| Q5: Giá chưa nêu thuế/phí | `seller-listing::chunk_5` | 0.2240 | Đúng; chứa đáp án ở top-1. |

4/5 câu có chunk liên quan trong top-3. Precision@1 là 2/5 (40%); Q1 và Q2 chứa đáp án ở top-2, còn Q3 không có anchor trong top-3. Tổng điểm chunk-level là 6/10.

### So sánh với baseline

| Strategy | Số chunks | Điểm chunk-level |
|---|---:|---:|
| Semantic của Vũ Văn Huy | 55 | **6/10** |
| Heading (lần benchmark trước) | 50 | 9/10 |
| Fixed baseline (lần benchmark trước) | 67 | 6/10 |
| Recursive baseline (lần benchmark trước) | 92 | 7/10 |
| Sentence baseline (lần benchmark trước) | 69 | 7/10 |

Semantic dùng 55 chunks, ít hơn các baseline fixed/recursive/sentence trước đó nhưng đạt 6/10. Với corpus pháp luật có Điều/Khoản được đánh dấu sẵn, kết quả này cho thấy semantic splitting với TF-IDF chưa tốt hơn ranh giới cấu trúc do con người biên soạn.

## 6. Phân tích metadata filter

Ở Q4, filter `{"customer_role": "buyer"}` tạo ra kết quả A/B khác nhau:

- Không filter: top-2 và top-3 có các chunk role `seller`, bao gồm tài liệu phiên bản 2013 có thể gây mâu thuẫn với quy định mới.
- Có filter: các ứng viên top-3 đều là role `buyer`; chunk đúng vẫn giữ top-1 với điểm 0.3591.

Filter vì thế giảm nhiễu và giúp context nhất quán hơn. Đánh đổi là recall: nếu gắn role quá chặt, kết quả đúng có metadata khác có thể bị loại. Với quy định áp dụng cho cả hai phía, nên thiết kế metadata `both` hoặc hỗ trợ điều kiện `role in {buyer, both}`.

## 7. Failure case và bài học

Q3 là failure case rõ nhất. Top-1 là chunk 2 của Điều 18, chứa cụm từ “rà soát và xác nhận nội dung hợp đồng”, nhưng không có chunk top-3 nào chứa anchor “Tổng giá trị của hợp đồng”. TF-IDF ưu tiên cụm từ trùng với query “rà soát/xác nhận” hơn đơn vị có nội dung trả lời trực tiếp; bước semantic splitting vì vậy đã không giữ phần danh sách đáp án trong tập ứng viên tốt nhất.

Q1 và Q2 cũng có anchor ở top-2 thay vì top-1. Điều này nhấn mạnh rằng đúng `doc_id` chưa đủ: một chunk nói cùng chủ đề nhưng sai khoản vẫn có thể xếp cao hơn đoạn chứa câu trả lời. Vì vậy cần chấm theo chunk/anchor thay vì chỉ theo tài liệu.

Hướng cải thiện:

- Chia ở mức khoản đối với Điều có danh sách liệt kê, đồng thời gắn heading và câu dẫn vào mỗi mảnh.
- Thêm overlap nhỏ giữa các khoản liền nhau.
- Retrieve top-8 rồi rerank, hoặc mở rộng context bằng các chunk lân cận của chunk được truy xuất.
- Dùng embedding đa ngữ có ngữ nghĩa khi có điều kiện thay cho TF-IDF, đặc biệt với query diễn đạt lại.

## 8. Tự đánh giá

| Hạng mục | Điểm tự đánh giá |
|---|---:|
| Khởi động | 5/5 |
| Hướng tiếp cận | 9/10 |
| Hoàn thiện code (42/42 test) | 30/30 |
| Dự đoán độ tương tự | 5/5 |
| Kết quả truy xuất | 6/10 |
| **Tổng phần cá nhân** | **55/60** |

## Kết luận

`SemanticSplitChunker` đã chạy ổn định với 55 chunks và đạt 6/10 ở benchmark lexical. Kết quả không vượt chiến lược heading trước đó là một phát hiện quan trọng: TF-IDF chỉ đo trùng từ nên chưa cung cấp tín hiệu ngữ nghĩa đủ tốt để suy ra ranh giới trong văn bản pháp luật. Để semantic chunking phát huy hiệu quả, cần thay bằng embedding đa ngữ có ngữ nghĩa và thử nghiệm thêm ngưỡng/percentile trên tập validation.
