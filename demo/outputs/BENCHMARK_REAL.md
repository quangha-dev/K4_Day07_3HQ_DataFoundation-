# Benchmark bốn phương pháp — embedding thật

Model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

Cách chấm ở mức chunk: anchor ở top-1 = 2 điểm; top-2/3 = 1 điểm; không có trong top-3 = 0 điểm.

| Thành viên | Phương pháp | Chunks | Q1 | Q2 | Q3 | Q4 | Q5 | Tổng /10 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Nguyễn Quang Hà · 2A202601424 | `ParagraphChunker` | 65 | 2 | 2 | 2 | 2 | 2 | **10** |
| Trương Ngọc Hải · 2A202601092 | `SentenceChunker` | 69 | 2 | 2 | 1 | 2 | 2 | **9** |
| Vũ Văn Huy · 2A202601342 | `RecursiveChunker` | 74 | 2 | 2 | 1 | 2 | 2 | **9** |
| Nguyễn Nhật Quang · 01452 | `FixedSizeChunker` | 67 | 2 | 1 | 0 | 2 | 2 | **7** |

## Bằng chứng top-3 và failure case

### Theo đoạn · Hà — 10/10

Tham số: `max_chunk_size=700 · min_chunk_size=450 · keep_heading=True`

- **Q1 · 2/2:** anchor ở top-1.
  - #1 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_8` · score `0.8425`
  - #2 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_7` · score `0.8100`
  - #3 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_9` · score `0.6886`
- **Q2 · 2/2:** anchor ở top-1.
  - #1 `nd52-quy-che-hoat-dong-san::chunk_3` · score `0.8053`
  - #2 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_9` · score `0.7281`
  - #3 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_8` · score `0.6384`
- **Q3 · 2/2:** anchor ở top-1.
  - #1 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_4` · score `0.8163`
  - #2 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_3` · score `0.7767`
  - #3 `seller-listing::chunk_1` · score `0.7561`
- **Q4 · 2/2:** anchor ở top-1.
  - #1 `nd85-2021-diem-moi-bao-ve-nguoi-tieu-dung::chunk_5` · score `0.8254`
  - #2 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_3` · score `0.5505`
  - #3 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_7` · score `0.5472`
- **Q5 · 2/2:** anchor ở top-1.
  - #1 `seller-listing::chunk_5` · score `0.6200`
  - #2 `seller-listing::chunk_6` · score `0.5622`
  - #3 `nd52-dang-ky-thong-bao-website::chunk_0` · score `0.5286`
- Không có failure case theo rubric top-1 trên bộ 5 query này.

### Theo câu · Hải — 9/10

Tham số: `max_sentences_per_chunk=3`

- **Q1 · 2/2:** anchor ở top-1.
  - #1 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_8` · score `0.8673`
  - #2 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_7` · score `0.8275`
  - #3 `seller-listing::chunk_8` · score `0.7172`
- **Q2 · 2/2:** anchor ở top-1.
  - #1 `nd52-quy-che-hoat-dong-san::chunk_2` · score `0.8288`
  - #2 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_9` · score `0.7448`
  - #3 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_8` · score `0.6528`
- **Q3 · 1/2:** anchor ở top-3.
  - #1 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_4` · score `0.8093`
  - #2 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_2` · score `0.7695`
  - #3 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_3` · score `0.7370`
- **Q4 · 2/2:** anchor ở top-1.
  - #1 `nd85-2021-diem-moi-bao-ve-nguoi-tieu-dung::chunk_4` · score `0.8144`
  - #2 `nd52-bao-ve-thong-tin-ca-nhan::chunk_2` · score `0.5952`
  - #3 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_7` · score `0.5766`
- **Q5 · 2/2:** anchor ở top-1.
  - #1 `seller-listing::chunk_6` · score `0.7028`
  - #2 `seller-listing::chunk_5` · score `0.5149`
  - #3 `nd52-dang-ky-thong-bao-website::chunk_1` · score `0.5128`
- **Failure cases cần phân tích:** Q3.

### Đệ quy · Huy — 9/10

Tham số: `chunk_size=500 · separators=đoạn → dòng → câu → từ → ký tự`

- **Q1 · 2/2:** anchor ở top-1.
  - #1 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_8` · score `0.8676`
  - #2 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_7` · score `0.8643`
  - #3 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_12` · score `0.7726`
- **Q2 · 2/2:** anchor ở top-1.
  - #1 `nd52-quy-che-hoat-dong-san::chunk_4` · score `0.8633`
  - #2 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_9` · score `0.7339`
  - #3 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_8` · score `0.6643`
- **Q3 · 1/2:** anchor ở top-2.
  - #1 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_5` · score `0.8020`
  - #2 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_4` · score `0.7908`
  - #3 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_3` · score `0.7539`
- **Q4 · 2/2:** anchor ở top-1.
  - #1 `nd85-2021-diem-moi-bao-ve-nguoi-tieu-dung::chunk_6` · score `0.7675`
  - #2 `nd85-2021-diem-moi-bao-ve-nguoi-tieu-dung::chunk_5` · score `0.6590`
  - #3 `nd52-bao-ve-thong-tin-ca-nhan::chunk_3` · score `0.6442`
- **Q5 · 2/2:** anchor ở top-1.
  - #1 `seller-listing::chunk_5` · score `0.7024`
  - #2 `seller-listing::chunk_6` · score `0.5575`
  - #3 `seller-listing::chunk_1` · score `0.5193`
- **Failure cases cần phân tích:** Q3.

### Kích thước cố định · Quang — 7/10

Tham số: `chunk_size=500 · overlap=50`

- **Q1 · 2/2:** anchor ở top-1.
  - #1 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_7` · score `0.8120`
  - #2 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_6` · score `0.8094`
  - #3 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_4` · score `0.7133`
- **Q2 · 1/2:** anchor ở top-2.
  - #1 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_7` · score `0.7416`
  - #2 `nd52-quy-che-hoat-dong-san::chunk_4` · score `0.7408`
  - #3 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_8` · score `0.6685`
- **Q3 · 0/2:** không có anchor trong top-3.
  - #1 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_4` · score `0.7555`
  - #2 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_5` · score `0.7440`
  - #3 `nd52-quy-trinh-dat-hang-truc-tuyen::chunk_9` · score `0.7388`
- **Q4 · 2/2:** anchor ở top-1.
  - #1 `nd85-2021-diem-moi-bao-ve-nguoi-tieu-dung::chunk_5` · score `0.7825`
  - #2 `nd85-2021-diem-moi-bao-ve-nguoi-tieu-dung::chunk_4` · score `0.6920`
  - #3 `nd85-2021-diem-moi-bao-ve-nguoi-tieu-dung::chunk_6` · score `0.6282`
- **Q5 · 2/2:** anchor ở top-1.
  - #1 `seller-listing::chunk_4` · score `0.6788`
  - #2 `seller-listing::chunk_5` · score `0.5655`
  - #3 `seller-listing::chunk_3` · score `0.5543`
- **Failure cases cần phân tích:** Q2, Q3.
