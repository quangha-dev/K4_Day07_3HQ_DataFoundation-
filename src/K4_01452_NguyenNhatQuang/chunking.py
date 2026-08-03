from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        chunks: list[str] = []
        pos = 0
        n = len(text)
        step = max(1, self.chunk_size - self.overlap)

        while pos < n:
            sub = text[pos:]
            # Kiểm tra ký tự thứ 3 (index 2) hoặc thứ 4 (index 3) có phải dấu cách ' ' hay không
            has_space_at_3_or_4 = (len(sub) >= 3 and sub[2] == " ") or (len(sub) >= 4 and sub[3] == " ")
            next_newline = text.find("\n", pos)

            if has_space_at_3_or_4 and next_newline != -1 and (next_newline - pos) <= self.chunk_size:
                chunk_str = text[pos:next_newline]
                pos = next_newline + 1
            else:
                end = min(pos + self.chunk_size, n)
                if next_newline != -1 and pos < next_newline <= end:
                    chunk_str = text[pos:next_newline]
                    pos = next_newline + 1
                else:
                    chunk_str = text[pos:end]
                    if end == n:
                        pos = n
                    else:
                        pos = pos + step

            if chunk_str:
                chunks.append(chunk_str)

        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        sentences = [s.strip() for s in re.split(r'(?<=\. |\! |\? |\.\n)', text) if s.strip()]
        if not sentences:
            return []
        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            chunk_str = " ".join(sentences[i : i + self.max_sentences_per_chunk]).strip()
            if chunk_str:
                chunks.append(chunk_str)
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not current_text:
            return []
        if len(current_text) <= self.chunk_size:
            return [current_text]

        if not remaining_separators:
            return [current_text[i : i + self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]

        sep = remaining_separators[0]
        next_seps = remaining_separators[1:]

        if sep == "":
            return [current_text[i : i + self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]

        parts = current_text.split(sep)
        sub_chunks: list[str] = []
        for part in parts:
            if not part and sep == "\n\n":
                continue
            if len(part) > self.chunk_size:
                sub_chunks.extend(self._split(part, next_seps))
            else:
                sub_chunks.append(part)

        merged: list[str] = []
        curr = ""
        for item in sub_chunks:
            if not item:
                continue
            if not curr:
                curr = item
            elif len(curr) + len(sep) + len(item) <= self.chunk_size:
                curr = curr + sep + item
            else:
                merged.append(curr)
                curr = item
        if curr:
            merged.append(curr)

        return merged if merged else [current_text]


class StructureChunker:
    """
    CHIEN LUOC RIENG CUA NGUYEN NHAT QUANG (K4_01452) — Lab 07, muc 6 / CP5.

    Khong nam trong 42 test. Day la chunker THEO CAU TRUC (heading / section)
    ma CP7 yeu cau "it nhat mot thanh vien" phai co.

    Nguyen ly
    ---------
    Ranh gioi chunk la DONG TIEU DE, khong phai so ky tu va cung khong phai
    dong trong. Van ban quy pham phap luat duoc bien soan theo Chuong / Muc /
    Dieu; MOI DIEU DA LA MOT DON VI NGU NGHIA TRON VEN — cau dan, cac khoan
    1. 2. 3., cac diem a) b) c) va phan ngoai le deu thuoc ve nhau. Cat theo
    heading tuc la dung lai dung ranh gioi ma nha lam luat da dinh nghia.

    Khac biet so voi ba chunker co san va so voi ParagraphChunker cua ban Ha
    ----------------------------------------------------------------------
        FixedSizeChunker   ranh gioi = SO KY TU     -> nhan tao, cat giua cau
        SentenceChunker    ranh gioi = DAU CHAM     -> hong voi "a) ...;"
        RecursiveChunker   uu tien "\\n\\n" nhung GOM cho du chunk_size
        ParagraphChunker   ranh gioi = DONG TRONG   -> mot KHOAN = mot chunk
        StructureChunker   ranh gioi = TIEU DE      -> ca DIEU = mot chunk

    Hai chunker cuoi la hai muc do TO/NHO khac nhau cua cung mot y tuong "ton
    trong cau truc tac gia tao ra", nen bang benchmark o muc 6 so sanh duoc
    truc tiep: chunk to giu tron dieu kien + ngoai le, chunk nho thi chinh xac
    hon nhung de dut context.

    Hai tinh huong bien phai xu ly
    ------------------------------
    1. SECTION QUA DAI. Dieu 28-34 gop lai hon 5.000 ky tu, vuot moi gioi han
       hop ly cua mot chunk. Khi do ha xuong tach theo KHOAN (`1.`, `2.`,
       `a)`, `b)`) roi gom lai cho toi sat `max_section_size`; neu van con dai
       thi ha tiep xuong `RecursiveChunker`.
    2. MANH CON MAT TIEU DE. Day la chi tiet de bai noi thang la "de bo sot":
       khi cat nho mot section dai, tu manh thu hai tro di khong con biet minh
       thuoc Dieu nao. `repeat_heading=True` gan lai dong tieu de vao DAU MOI
       manh con. Dat False de lam ablation, do xem buoc nay dong gop bao nhieu
       diem trong bang benchmark.

    Chon `max_section_size`
    -----------------------
    Quet tren dung 5 benchmark query cua nhom (embedder lexical, top_k=3), chi
    doi mot bien nay, moi thu khac giu nguyen. Xem so lieu trong REPORT_NHOM.md
    muc 2. Chon 900 vi do la nguong nho nhat van giu duoc tron ven mot Dieu
    trung binh cua ND 52/2013 (cau dan + danh sach diem a/b/c) trong mot chunk.
    """

    #: Dong tieu de. Hai dang cung ton tai trong corpus cua nhom:
    #:   - Markdown:   "# ...", "## Dieu 32. Dieu kien giao dich chung"
    #:   - Van ban:    "Dieu 32.", "Chuong V", "Muc 2 ..."
    #: `^\s*` cho phep tieu de bi thut dau dong sau khi lam sach thu cong.
    _HEADING = re.compile(
        r"^\s*(?:#{1,6}\s+\S.*|(?:Điều|Chương|Mục)\s+\d+\s*[.:)]?.*)$",
        re.IGNORECASE,
    )

    #: Ranh gioi KHOAN / DIEM ben trong mot Dieu — dung khi section qua dai.
    #: Vi du: "1. ", "2. ", "a) ", "b) ", "đ) ".
    _CLAUSE = re.compile(r"^\s*(?:\d+\.|[a-zA-ZđĐ]\))\s+")

    def __init__(
        self,
        max_section_size: int = 900,
        repeat_heading: bool = True,
        merge_lone_heading: bool = True,
    ) -> None:
        self.max_section_size = max_section_size
        self.repeat_heading = repeat_heading
        # Xem docstring cua `_split_sections`. Dat False de tai hien failure
        # case cua nhom (chunk chi co dong tieu de doat top-1 ma khong co dap an).
        self.merge_lone_heading = merge_lone_heading

    def params(self) -> str:
        """In ra bang benchmark cua bench.py."""
        return (
            f"max_section_size={self.max_section_size}, "
            f"repeat_heading={self.repeat_heading}, "
            f"merge_lone_heading={self.merge_lone_heading}"
        )

    # ------------------------------------------------------------------
    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        chunks: list[str] = []
        for heading, body in self._split_sections(text):
            # Section vua kich thuoc -> giu nguyen ca Dieu lam MOT chunk.
            whole = f"{heading}\n{body}".strip() if heading else body.strip()
            if not whole:
                continue
            if len(whole) <= self.max_section_size:
                chunks.append(whole)
            else:
                chunks.extend(self._split_section(heading, body))

        return [c.strip() for c in chunks if c.strip()]

    # ------------------------------------------------------------------
    def _split_sections(self, text: str) -> list[tuple[str, str]]:
        """Duyet tung dong, gap tieu de thi MO SECTION MOI.

        Phan text nam TRUOC tieu de dau tien (neu co) van duoc giu lai voi
        heading rong — khong duoc vut di, vi do co the la phan mo dau tai lieu.

        `merge_lone_heading` — bai hoc rut ra tu benchmark
        --------------------------------------------------
        File .md cua nhom mo dau bang tieu de cap 1 ("# Quy che hoat dong cua
        san...") roi xuong thang tieu de cap 2 ("## Dieu 38. ..."). Section cua
        tieu de cap 1 vi vay co THAN RONG, va sinh ra mot chunk chi chua dung
        mot dong tieu de.

        Chunk do rat nguy hiem voi TF-IDF: no ngan, toan tu hiem, va trung gan
        het tu voi cau hoi -> cosine bi thoi len rat cao. Do chinh la nguyen
        nhan failure case Q2 cua nhom: chunk 46 ky tu chi co dong tieu de dat
        score 0.4480, doat top-1, trong khi dap an "it nhat 5 ngay" nam o chunk
        khac va bi day xuong hang 2 (2 diem -> 1 diem).

        Cach sua: tieu de "tro tro" (than rong) khong tao chunk rieng ma NHAP
        vao section ke tiep. Dat False de tai hien lai loi trong report.
        """
        sections: list[tuple[str, list[str]]] = []
        heading = ""
        buffer: list[str] = []

        for line in text.splitlines():
            if self._HEADING.match(line) and line.strip():
                # Chot section dang mo truoc khi sang section moi.
                if heading or any(l.strip() for l in buffer):
                    sections.append((heading, buffer))
                heading = line.strip()
                buffer = []
            else:
                buffer.append(line)

        if heading or any(l.strip() for l in buffer):
            sections.append((heading, buffer))

        pairs = [(h, "\n".join(lines).strip()) for h, lines in sections]
        if not self.merge_lone_heading:
            return pairs

        # Tieu de "tro tro" (than rong) -> nhap tieu de do vao section ke tiep
        # thay vi de no thanh mot chunk chi co mot dong.
        merged: list[tuple[str, str]] = []
        carry = ""
        for heading_text, body in pairs:
            if not body:
                carry = f"{carry}\n{heading_text}".strip() if carry else heading_text
                continue
            merged.append((f"{carry}\n{heading_text}".strip() if carry else heading_text, body))
            carry = ""
        if carry:
            # Tai lieu chi co tieu de, khong co than: van phai giu lai.
            merged.append((carry, ""))
        return merged

    # ------------------------------------------------------------------
    def _split_section(self, heading: str, body: str) -> list[str]:
        """Section vuot nguong -> tach theo KHOAN, gom lai, gan lai tieu de.

        Thu tu ba buoc nay quan trong:
            1. tach theo khoan  (don vi nho nhat con giu nghia)
            2. gom cac khoan lien tiep cho toi sat `max_section_size`
               -> tranh chunk vun vai chuc ky tu bi TF-IDF thoi diem len
            3. gan tieu de vao TUNG manh -> manh thu hai tro di khong mat
               ngu canh "day la Dieu nao"
        Gan tieu de o buoc 3 chu khong phai buoc 1, neu khong tieu de se bi
        dem hai lan khi hai khoan duoc gom lai voi nhau.
        """
        prefix = heading if (self.repeat_heading and heading) else ""
        budget = max(120, self.max_section_size - len(prefix) - 1)

        units = self._split_clauses(body)

        # Buoc 2: gom cac khoan lien tiep.
        packed: list[str] = []
        current = ""
        for unit in units:
            if not current:
                current = unit
            elif len(current) + 1 + len(unit) <= budget:
                current = f"{current}\n{unit}"
            else:
                packed.append(current)
                current = unit
        if current:
            packed.append(current)

        # Khoan don le van qua dai -> ha xuong RecursiveChunker (uu tien thap hon).
        expanded: list[str] = []
        for part in packed:
            if len(part) <= budget:
                expanded.append(part)
            else:
                expanded.extend(RecursiveChunker(chunk_size=budget).chunk(part))

        # Buoc 3: gan lai tieu de vao dau moi manh con.
        if not prefix:
            return expanded
        return [f"{prefix}\n{part}".strip() for part in expanded if part.strip()]

    # ------------------------------------------------------------------
    def _split_clauses(self, body: str) -> list[str]:
        """Cat body thanh cac khoan/diem. Dong khong mo khoan moi thi noi tiep
        vao khoan dang mo, de mot khoan xuong dong nhieu lan khong bi vo vun."""
        units: list[str] = []
        current: list[str] = []

        for line in body.splitlines():
            if not line.strip():
                # Dong trong: giu lai de khong dinh chu, nhung khong mo unit moi.
                if current:
                    current.append("")
                continue
            if self._CLAUSE.match(line) and current:
                units.append("\n".join(current).strip())
                current = [line]
            else:
                current.append(line)

        if current:
            units.append("\n".join(current).strip())

        return [u for u in units if u.strip()]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    dot = sum(x * y for x, y in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(x * x for x in vec_a))
    norm_b = math.sqrt(sum(y * y for y in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        fixed = FixedSizeChunker(chunk_size=chunk_size, overlap=0).chunk(text)
        sent = SentenceChunker().chunk(text)
        rec = RecursiveChunker(chunk_size=chunk_size).chunk(text)

        def _stats(chunks: list[str]) -> dict:
            count = len(chunks)
            avg_len = sum(len(c) for c in chunks) / count if count > 0 else 0.0
            return {
                "count": count,
                "avg_length": avg_len,
                "chunks": chunks,
            }

        return {
            "fixed_size": _stats(fixed),
            "by_sentences": _stats(sent),
            "recursive": _stats(rec),
        }
