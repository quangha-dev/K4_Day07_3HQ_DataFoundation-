"""
benchmark_queries.py — BO 5 CAU HOI DANH GIA CUA NHOM (Lab 07 · K4).

=============================================================================
FILE NAY LA PHAN DUNG CHUNG — DA CHOT, KHONG AI DUOC SUA.
=============================================================================
De bai: "Khong doi query sau khi mot strategy da chay tot hoac xau."

Bon thanh vien deu chay DUNG bo query nay tren DUNG corpus nay. Chi khac nhau
o chunker. Co vay bang so sanh trong REPORT_NHOM.md moi cong bang.

Cau truc mot query
------------------
    id               Q1..Q5
    kind             loai cau hoi: so lieu / dieu kien / quy trinh /
                     liet ke + filter / ngoai le  (de bai yeu cau du 5 loai)
    question         ban khong dau, de doc trong code
    question_vi      ban CO DAU — day moi la chuoi thuc su dua vao search()
    gold_answer      dap an chuan, trich TRUC TIEP tu corpus
    gold_doc_id      tai lieu ky vong
    anchors          chuoi dac trung PHAI xuat hien trong context truy xuat duoc

                     Day la thu quan trong nhat. Neu chi kiem `gold_doc_id` co
                     trong top-3 hay khong thi MOI strategy deu duoc 10/10 va
                     bang so sanh vo nghia — nhom da do va xac nhan dieu nay.
                     Chi khi kiem o muc CHUNK (anchor co nam trong noi dung
                     chunk khong) thi khac biet moi lo ra.

    metadata_filter  None, tru Q4 — cau bat buoc dung filter cua lop K4

Ban doc duoc cho nguoi: report/BENCHMARK_QUERIES.md
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# 5 BENCHMARK QUERY — nhom chot, KHONG doi sau khi da chay strategy nao do.
#   anchors: chuoi dac trung PHAI xuat hien trong context truy xuat duoc.
#            Cham o muc CHUNK, khong chi kiem doc_id (xem docs/EVALUATION.md).
# ---------------------------------------------------------------------------
BENCHMARK_QUERIES = [
    {
        "id": "Q1",
        "kind": "so lieu",
        "question": (
            "Neu nguoi ban khong cong bo ro thoi han tra loi, sau bao lau de nghi "
            "giao ket hop dong cua khach hang het hieu luc?"
        ),
        "question_vi": (
            "Nếu người bán không công bố rõ thời hạn trả lời, sau bao lâu đề nghị "
            "giao kết hợp đồng của khách hàng hết hiệu lực?"
        ),
        "gold_answer": (
            "Trong vòng 12 (mười hai) giờ kể từ khi gửi đề nghị giao kết hợp đồng "
            "mà khách hàng không nhận được trả lời thì đề nghị được coi là chấm dứt "
            "hiệu lực (khoản 2 Điều 20 Nghị định 52/2013/NĐ-CP)."
        ),
        "gold_doc_id": "nd52-quy-trinh-dat-hang-truc-tuyen",
        "anchors": ["12 (mười hai) giờ"],
        "metadata_filter": None,
    },
    {
        "id": "Q2",
        "kind": "dieu kien",
        "question": (
            "San giao dich thuong mai dien tu phai thong bao truoc bao nhieu ngay khi "
            "thay doi quy che hoat dong?"
        ),
        "question_vi": (
            "Sàn giao dịch thương mại điện tử phải thông báo trước bao nhiêu ngày khi "
            "thay đổi quy chế hoạt động?"
        ),
        "gold_answer": (
            "Phải thông báo cho tất cả đối tượng sử dụng dịch vụ ít nhất 5 ngày trước "
            "khi áp dụng thay đổi (khoản 3 Điều 38 Nghị định 52/2013/NĐ-CP)."
        ),
        "gold_doc_id": "nd52-quy-che-hoat-dong-san",
        "anchors": ["ít nhất 5 ngày"],
        "metadata_filter": None,
    },
    {
        "id": "Q3",
        "kind": "quy trinh",
        "question": (
            "Co che ra soat va xac nhan noi dung hop dong phai hien thi nhung thong tin "
            "gi cho khach hang truoc khi dat hang?"
        ),
        "question_vi": (
            "Cơ chế rà soát và xác nhận nội dung hợp đồng phải hiển thị những thông tin "
            "gì cho khách hàng trước khi đặt hàng?"
        ),
        "gold_answer": (
            "Tên hàng hóa/dịch vụ, số lượng và chủng loại; phương thức và thời hạn giao "
            "hàng; tổng giá trị hợp đồng và chi tiết phương thức thanh toán. Ngoài ra "
            "phải hiển thị cách thức và thời hạn trả lời đề nghị giao kết, và cho phép "
            "hủy giao dịch (Điều 18 Nghị định 52/2013/NĐ-CP)."
        ),
        "gold_doc_id": "nd52-quy-trinh-dat-hang-truc-tuyen",
        "anchors": ["Tổng giá trị của hợp đồng"],
        "metadata_filter": None,
    },
    {
        "id": "Q4",
        "kind": "liet ke + FILTER BAT BUOC",
        "question": (
            "Chinh sach kiem hang co phai la mot dieu kien giao dich chung bat buoc phai "
            "cong bo khong?"
        ),
        "question_vi": (
            "Chính sách kiểm hàng có phải là một điều kiện giao dịch chung bắt buộc "
            "phải công bố không?"
        ),
        "gold_answer": (
            "Có. Từ ngày 01/01/2022, chính sách kiểm hàng là một trong những điều kiện "
            "giao dịch chung bắt buộc phải công bố trên website TMĐT (Nghị định "
            "85/2021/NĐ-CP). Bản gốc Điều 32 Nghị định 52/2013/NĐ-CP KHÔNG liệt kê "
            "chính sách kiểm hàng — trả lời theo bản 2013 là sai."
        ),
        "gold_doc_id": "nd85-2021-diem-moi-bao-ve-nguoi-tieu-dung",
        "anchors": ["chính sách kiểm hàng"],
        "metadata_filter": {"customer_role": "buyer"},
    },
    {
        "id": "Q5",
        "kind": "ngoai le",
        "question": (
            "Website niem yet gia ma khong noi ro da bao gom thue va phi van chuyen "
            "chua thi hieu the nao?"
        ),
        "question_vi": (
            "Website niêm yết giá mà không nói rõ đã bao gồm thuế và phí vận chuyển "
            "chưa thì hiểu thế nào?"
        ),
        "gold_answer": (
            "Trừ trường hợp các bên có thỏa thuận khác, giá niêm yết được hiểu là đã "
            "bao gồm mọi chi phí liên quan như thuế, phí đóng gói, phí vận chuyển và "
            "chi phí phát sinh khác (khoản 2 Điều 31 Nghị định 52/2013/NĐ-CP)."
        ),
        "gold_doc_id": "seller-listing",
        "anchors": ["được hiểu là đã bao gồm mọi chi phí"],
        "metadata_filter": None,
    },
]
