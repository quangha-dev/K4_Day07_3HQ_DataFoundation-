# Demo so sánh bốn phương pháp chunking

Ứng dụng nằm hoàn toàn trong `demo/`; không sửa hoặc sao chép thuật toán của
các thành viên. `strategy_registry.py` import trực tiếp bốn class gốc:

- Nguyễn Quang Hà: `ParagraphChunker` — chia theo đoạn, gộp đoạn ngắn, giữ tiêu đề.
- Trương Ngọc Hải: `SentenceChunker` — chia theo câu, bảo vệ viết tắt và số thập phân.
- Vũ Văn Huy: `RecursiveChunker` — tách đệ quy theo ranh giới tự nhiên.
- Nguyễn Nhật Quang: `FixedSizeChunker` — 500 ký tự, overlap 50 ký tự.

Package của Quang còn `NotImplementedError` ở các task khác, nhưng
`FixedSizeChunker` là phần đã hoàn thiện sẵn và chạy độc lập đúng contract nên
được kế thừa an toàn cho benchmark này.

## Cài và chạy

Từ thư mục gốc repository:

```powershell
.venv\Scripts\python.exe -m pip install -r demo\requirements-demo.txt
.venv\Scripts\python.exe -m streamlit run demo\app.py
```

Mở địa chỉ Streamlit in trong terminal. Lần đầu model
`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` được nạp có thể
mất khoảng một phút; các lần sau ứng dụng dùng cache.

## Kiểm tra không cần giao diện

```powershell
.venv\Scripts\python.exe demo\smoke_test.py
```

Smoke test nạp cùng model embedding thật, xây bốn index và xác nhận mỗi phương
pháp trả đủ top-3 chunks với score.

## Chạy benchmark thật cho cả bốn phương pháp

```powershell
.venv\Scripts\python.exe demo\benchmark_real.py
```

Kết quả chi tiết được tạo trong `demo/outputs/benchmark_real.json` và bản dễ
đọc trong `demo/outputs/BENCHMARK_REAL.md`.

## Luồng demo gợi ý

1. Chọn Q4 và bật filter `buyer`.
2. Chuyển qua tab **Retrieval chunks** để mở nội dung top-3.
3. Trở lại **Câu trả lời** để chỉ ra citation `[1]`, `[2]` trỏ đúng chunks.
4. Mở **So sánh 4 phương pháp** để chứng minh chỉ thay chunker, còn corpus,
   câu hỏi, model embedding và top-k đều giữ nguyên.
