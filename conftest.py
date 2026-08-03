"""
conftest.py — Tro pytest ve dung goi bai lam ca nhan.

`tests/test_solution.py` doc bien moi truong `LAB_SOLUTION_PACKAGE` (mac dinh
la "src"). Nhom co 4 nguoi, moi nguoi mot thu muc rieng trong `src/`, nen file
nay dat san bien do truoc khi pytest import test module.

Nho vay lenh trong de bai chay nguyen van, khong phai them gi:

    python -m pytest tests -v        ->  42 passed

Van co the ghi de tu ben ngoai khi muon cham bai cua nguoi khac:

    $env:LAB_SOLUTION_PACKAGE="src.<MSSV>-<HoTen>"; python -m pytest tests -v
"""
import os

from solution import PACKAGE_NAME

# setdefault: chi dat khi nguoi dung CHUA tu dat bien nay.
os.environ.setdefault("LAB_SOLUTION_PACKAGE", PACKAGE_NAME)
