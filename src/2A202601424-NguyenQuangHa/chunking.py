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
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    # Cat tai khoang trang DUNG SAU dau ket cau.
    # Lookbehind (?<=[.!?]) chi "nhin lai" de xac nhan co dau cau, KHONG nuot no,
    # nen dau cham van nam lai o cuoi cau truoc. Neu viet [.!?]\s+ thi dau cau bi
    # an mat va cac cau ghep lai se dinh vao nhau.
    _SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        # Buoc 1: text rong -> tra list rong (khong phai [""]).
        if not text:
            return []

        # Buoc 2 + 3: tach cau, strip tung cau, bo phan rong.
        sentences = [
            sentence.strip()
            for sentence in self._SENTENCE_BOUNDARY.split(text)
            if sentence.strip()
        ]
        if not sentences:
            return []

        # Buoc 4 + 5: gom tung nhom `limit` cau, ghep bang mot dau cach.
        limit = self.max_sentences_per_chunk
        return [
            " ".join(sentences[index : index + limit])
            for index in range(0, len(sentences), limit)
        ]


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
        """Vo ngoai: xu ly text rong, goi de quy, roi don dep ket qua."""
        if not text:
            return []
        pieces = self._split(text, list(self.separators))
        return [piece.strip() for piece in pieces if piece and piece.strip()]

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        """Phan de quy. Moi lan goi lai PHAI hoac bot separator hoac thu nho text."""
        # Base case 1: da du ngan -> tra ve nguyen.
        if len(current_text) <= self.chunk_size:
            return [current_text]

        # Base case 2: het separator -> cat cung theo chunk_size.
        if not remaining_separators:
            return self._hard_split(current_text)

        separator = remaining_separators[0]
        rest = remaining_separators[1:]

        # Separator rong "" cung la tin hieu cat cung (muc uu tien thap nhat).
        if separator == "":
            return self._hard_split(current_text)

        # Separator khong xuat hien trong text -> ha xuong muc uu tien thap hon.
        if separator not in current_text:
            return self._split(current_text, rest)

        # Cat duoc: gom cac phan lien nhau cho toi truoc khi vuot chunk_size.
        # Bo buoc gom nay la loi pho bien nhat -> sinh ra hang loat chunk vun.
        chunks: list[str] = []
        buffer = ""
        for part in current_text.split(separator):
            candidate = part if not buffer else buffer + separator + part
            if len(candidate) <= self.chunk_size:
                buffer = candidate
                continue

            if buffer:
                chunks.append(buffer)
                buffer = ""

            if len(part) > self.chunk_size:
                # Mot manh don le van qua dai -> xu ly bang separator uu tien thap hon.
                chunks.extend(self._split(part, rest))
            else:
                buffer = part

        if buffer:
            chunks.append(buffer)
        return chunks

    def _hard_split(self, text: str) -> list[str]:
        """Cat co dinh theo chunk_size, khong quan tam ranh gioi ngu nghia."""
        size = max(1, self.chunk_size)
        return [text[index : index + size] for index in range(0, len(text), size)]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    # norm(v) = sqrt(dot(v, v)) — dung lai _dot co san.
    norm_a = math.sqrt(_dot(vec_a, vec_a))
    norm_b = math.sqrt(_dot(vec_b, vec_b))

    # Chan chia cho 0 TRUOC khi chia.
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    # Giong het -> 1 | vuong goc -> 0 | nguoc huong -> -1
    return _dot(vec_a, vec_b) / (norm_a * norm_b)


class ParagraphChunker:
    """
    CHIEN LUOC RIENG CUA NGUYEN QUANG HA (2A202601424) — Lab 07, muc 6 / CP5.

    Khong nam trong 42 test. Day la phan tu thiet ke theo domain cua nhom.

    Nguyen ly
    ---------
    Chia theo DOAN. Ranh gioi la DONG TRONG — tuc la cho nguoi soan thao go
    Enter hai lan. Trong Markdown va trong van ban quy pham phap luat, dong
    trong chinh la dau hieu "het mot y, sang y khac" do CON NGUOI danh dau san.

    Khac voi ba chunker co san:
        FixedSizeChunker  cat theo SO KY TU      -> ranh gioi nhan tao
        SentenceChunker   cat theo DAU CHAM      -> hong voi gach dau dong
                                                    ket thuc bang dau ";"
        RecursiveChunker  co uu tien "\\n\\n" nhung van GOM nhieu doan lai
                          cho du chunk_size, nen mot chunk co the chua nhieu y
        ParagraphChunker  moi doan la MOT chunk  -> ton trong dung ranh gioi
                                                    tac gia da tao

    Vi sao hop voi corpus cua nhom: file .md cua nhom viet moi khoan / moi diem
    a) b) c) thanh mot doan rieng, cach nhau bang dong trong. Cat theo doan
    chinh la cat theo khoan ma khong can regex nhan dien "1." hay "a)".

    Ba tinh huong phai xu ly, neu bo qua thi ket qua rat te
    -------------------------------------------------------
    1. DOAN QUA NGAN. "a) Ten hang hoa, so luong va chung loai;" chi ~45 ky tu.
       De rieng thi vo nghia, va con nguy hiem hon the: voi TF-IDF, vector cua
       text ngan ma toan tu hiem se co cosine bi THOI LEN rat cao du khong chua
       cau tra loi. Nhom da quan sat dung loi nay — mot chunk 64 ky tu chi chua
       dong tieu de dat score 0.6109, cao nhat toan benchmark. Vi vay phai GOP
       cac doan ngan lien tiep lai (`min_chunk_size`).
    2. DOAN QUA DAI. Vuot `max_chunk_size` thi ha xuong RecursiveChunker.
    3. MAT NGU CANH. Doan "c) Tong gia tri cua hop dong..." khong cho biet no
       thuoc Dieu nao. `keep_heading=True` gan tieu de gan nhat vao dau moi
       chunk. Dat False de lam ablation, chung minh tac dung cua buoc nay.

    Chon `min_chunk_size` — do bang thuc nghiem, khong doan
    -------------------------------------------------------
    Quet tham so tren dung 5 benchmark query cua nhom (embedder lexical):

        min_chunk_size   so chunk   diem chunk-level
                   100        156          7 / 10
                   150        137          7 / 10
                   250         97          7 / 10
                   350         75          8 / 10
                   450         65          9 / 10   <- chon
                   600         63          8 / 10

    Nguong 450 la diem can bang: du lon de mot cau dan va toan bo danh sach
    a) b) c) cua no nam CHUNG mot chunk (day la ly do Q3 tu 0 len 1 diem va Q2
    tu 1 len 2), nhung chua lon toi muc gop hai y khac nhau lam mot (600 lai
    tut xuong 8). Day la tune tham so cua chinh chien luoc minh — de bai cho
    phep ("Dung 1 trong 3 chien luoc co san voi tham so toi uu"). Cai KHONG
    duoc phep la doi 5 query sau khi da thay ket qua.
    """

    #: Hai (hoac nhieu hon) dau xuong dong lien tiep = ranh gioi doan.
    #: `[ \t]*` cho phep dong "trong" van con khoang trang/tab thua.
    _PARAGRAPH_BREAK = re.compile(r"\n[ \t]*\n+")

    #: Dong tieu de Markdown ("# ...", "## Dieu 32. ...") hoac kieu van ban
    #: phap luat ("Dieu 32.", "Chuong V", "Muc 2").
    _HEADING = re.compile(r"^(#{1,6}\s+.*|(Điều|Chương|Mục)\s+\d+[.:]?.*)$", re.IGNORECASE)

    def __init__(
        self,
        max_chunk_size: int = 700,
        min_chunk_size: int = 450,
        keep_heading: bool = True,
    ) -> None:
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.keep_heading = keep_heading

    def params(self) -> str:
        """In ra bang benchmark cua bench.py."""
        return (
            f"max_chunk_size={self.max_chunk_size}, "
            f"min_chunk_size={self.min_chunk_size}, "
            f"keep_heading={self.keep_heading}"
        )

    # ------------------------------------------------------------------
    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        # Buoc 1: cat tai moi dong trong -> list (tieu_de, noi_dung_doan).
        blocks = self._split_paragraphs(text)
        if not blocks:
            return []

        # Buoc 2: gop cac doan ngan lien tiep (chi gop trong cung mot tieu de).
        merged = self._merge_short(blocks)

        # Buoc 3: gan tieu de MOT lan cho moi block, cat block qua dai.
        # THU TU QUAN TRONG: gan tieu de SAU khi gop. Neu gan truoc roi moi gop
        # thi hai doan cung tieu de bi noi lai -> tieu de xuat hien hai lan
        # trong mot chunk, vua thua vua lam TF-IDF thoi diem cua chunk do len.
        chunks: list[str] = []
        for heading, body in merged:
            prefix = heading if (self.keep_heading and heading) else ""
            block = f"{prefix}\n{body}".strip() if prefix else body.strip()

            if len(block) <= self.max_chunk_size:
                chunks.append(block)
            else:
                chunks.extend(self._split_long(prefix, body))

        return [chunk.strip() for chunk in chunks if chunk.strip()]

    # ------------------------------------------------------------------
    def _split_paragraphs(self, text: str) -> list[tuple[str, str]]:
        """Cat theo dong trong, kem theo tieu de dang hieu luc cho tung doan.

        Doan nao BAN THAN chi la mot dong tieu de thi khong tao block rieng —
        no chi cap nhat `current_heading` cho cac doan phia sau.
        """
        blocks: list[tuple[str, str]] = []
        current_heading = ""

        for raw in self._PARAGRAPH_BREAK.split(text):
            paragraph = raw.strip()
            if not paragraph:
                continue

            lines = paragraph.splitlines()
            first_line = lines[0].strip()

            if self._HEADING.match(first_line):
                current_heading = first_line
                remainder = "\n".join(lines[1:]).strip()
                if not remainder:
                    continue
                paragraph = remainder

            blocks.append((current_heading, paragraph))

        return blocks

    def _merge_short(self, blocks: list[tuple[str, str]]) -> list[tuple[str, str]]:
        """Gop block ngan hon `min_chunk_size` vao block KE TIEP cung tieu de.

        Gop XUOI (khong phai nguoc) vi trong van ban phap luat, doan ngan
        thuong la CAU DAN cua danh sach ben duoi no:
            "1. Hien thi cho khach hang nhung thong tin sau:"   <- ngan, la dan
            "a) Ten hang hoa..."                                <- noi dung
        Gop xuoi giu duoc quan he dan -> noi dung.

        Khong gop qua ranh gioi tieu de: hai Dieu khac nhau khong duoc nhap lam
        mot chunk, du ca hai deu ngan.
        """
        merged: list[tuple[str, str]] = []
        carry_heading = ""
        carry_body = ""

        for heading, body in blocks:
            # Doi tieu de -> chot phan dang gom lai truoc da.
            if carry_body and heading != carry_heading:
                merged.append((carry_heading, carry_body))
                carry_heading, carry_body = "", ""

            candidate = f"{carry_body}\n{body}".strip() if carry_body else body

            if len(carry_heading or heading) + len(candidate) < self.min_chunk_size:
                carry_heading, carry_body = heading, candidate
                continue

            merged.append((heading, candidate))
            carry_heading, carry_body = "", ""

        # Phan du cuoi: nhap vao block truoc neu cung tieu de, khong thi de rieng.
        if carry_body:
            if merged and merged[-1][0] == carry_heading:
                last_heading, last_body = merged[-1]
                merged[-1] = (last_heading, f"{last_body}\n{carry_body}".strip())
            else:
                merged.append((carry_heading, carry_body))

        return merged

    def _split_long(self, heading: str, body: str) -> list[str]:
        """Block qua dai -> ha xuong RecursiveChunker, gan lai tieu de tung manh."""
        budget = self.max_chunk_size - (len(heading) + 1 if heading else 0)
        pieces = RecursiveChunker(chunk_size=max(150, budget)).chunk(body)

        if not heading:
            return pieces
        return [f"{heading}\n{piece}".strip() for piece in pieces]


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        # Ba key PHAI dung ten nay, test so tung ky tu.
        runs = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=0).chunk(text),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3).chunk(text),
            "recursive": RecursiveChunker(chunk_size=chunk_size).chunk(text),
        }

        comparison: dict = {}
        for name, chunks in runs.items():
            count = len(chunks)
            total_length = sum(len(chunk) for chunk in chunks)
            comparison[name] = {
                "count": count,
                # Text rong -> count = 0 -> phai chan truoc khi chia.
                "avg_length": (total_length / count) if count else 0.0,
                "chunks": chunks,
            }
        return comparison
