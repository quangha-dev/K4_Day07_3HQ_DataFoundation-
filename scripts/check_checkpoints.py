"""
scripts/check_checkpoints.py — Tu kiem TAT CA checkpoint cua Lab 07 truoc khi nop.

Chay tu thu muc goc repo:

    python scripts/check_checkpoints.py

Kiem CP2 (corpus + metadata), CP5 (5 query + bench.py), CP6 (bang so sanh nhom +
A/B filter + doc-level vs chunk-level) va CP7 (deliverable). Phan test 42/42
(CP1/CP3/CP4) chay bang pytest, xem README.

Moi dong in ra la PASS hoac FAIL — khong co dong FAIL nao thi du dieu kien nop.
"""
import sys; sys.path.insert(0, ".")
import os, csv, re, io, contextlib
from pathlib import Path
os.environ["EMBEDDING_PROVIDER"]="lexical"
G="\033[32mPASS\033[0m"; R="\033[31mFAIL\033[0m"
def chk(cond,msg): print(f"  {G if cond else R} {msg}")

print("===== CP2 (tiếp) · metadata + sources.csv =====")
D=Path('data/k4_ecommerce'); REQ=['doc_id','title','source_url','retrieved_at','document_version']
mds=sorted(D.glob('*.md')); rows=list(csv.DictReader(open(D/'sources.csv',encoding='utf-8')))
ids=[];roles={};bad=0
for p in mds:
    fm=dict(re.findall(r'^(\w+):\s*(.+)$',p.read_text(encoding='utf-8').split('---')[1],re.M))
    ids.append(fm.get('doc_id')); roles[fm.get('customer_role')]=roles.get(fm.get('customer_role'),0)+1
    if not(all(k in fm for k in REQ) and 'customer_role' in fm and fm.get('doc_id')==p.stem): bad+=1
chk(bad==0, f"mọi file đủ metadata bắt buộc ({len(mds)-bad}/{len(mds)})")
chk(sorted(r['doc_id'] for r in rows)==sorted(ids), "sources.csv khớp 1-1 với corpus")
chk(len(roles)>=2, f"customer_role có >=2 giá trị: {roles}")

print("===== CP5 · 5 query + gold answer + filter + bench.py =====")
from benchmark_queries import BENCHMARK_QUERIES as Q
chk(len(Q)==5, f"đúng 5 query ({len(Q)})")
chk(all(q['anchors'] for q in Q), "mọi query có anchors (chấm mức chunk)")
chk(all(q.get('gold_answer_vi') or q.get('gold_answer') for q in Q), "mọi query có gold answer")
chk(sum(1 for q in Q if q['metadata_filter'])>=1, "có >=1 query dùng metadata_filter bắt buộc của K4")
chk(len({q['kind'] for q in Q})==5, "5 loại câu hỏi khác nhau (số liệu/điều kiện/quy trình/liệt kê/ngoại lệ)")

import bench
from bench import STRATEGIES, GROUP_STRATEGIES, select_embedder, run_strategy
emb=select_embedder()
res={}
for name in STRATEGIES:
    buf=io.StringIO()
    with contextlib.redirect_stdout(buf): s=run_strategy(name, emb)
    res[name]=(s,buf.getvalue())
chk(all(s["chunks"]>0 for s,_ in res.values()), f"bench.py chạy được {len(res)}/{len(STRATEGIES)} cấu hình, đều nạp >0 chunk")
chk(all(txt.count("score=")>=15 for _,txt in res.values()), "mọi cấu hình in top-3 cho đủ 5 query")

print("===== CP6 · strategy riêng + bảng nhóm + A/B filter =====")
names={s for _,_,s in GROUP_STRATEGIES}
chk(len(names)==4, f"4 thành viên, 4 strategy KHÔNG trùng nhau: {sorted(names)}")
chunks={n:res[n][0]["chunks"] for _,_,n in GROUP_STRATEGIES}
chk(len(set(chunks.values()))==4, f"số chunk khác nhau -> thật sự khác strategy: {chunks}")
ab=sum(1 for _,t in res.values() if "A/B: ket qua KHAC NHAU" in t)
chk(ab==len(res), f"A/B metadata filter KHÁC NHAU ở {ab}/{len(res)} cấu hình")
# doc-level vs chunk-level
doc_all=[]
for name,(s,_) in res.items():
    d=0
    for q in Q:
        e=s["per_query"][q["id"]]; rr=e.get("filter",e["no_filter"])["results"]
        rk=[i for i,r in enumerate(rr,1) if r["metadata"].get("doc_id")==q["gold_doc_id"]]
        d+= 2 if rk and rk[0]==1 else (1 if rk else 0)
    doc_all.append((name,d,s["total_points"]))
chk(all(d==10 for _,d,_ in doc_all), "doc-level = 10/10 ở mọi cấu hình (phát hiện của nhóm)")
cl=[c for _,_,c in doc_all]
chk(min(cl)<max(cl), f"chunk-level trải rộng {min(cl)}->{max(cl)} (chunking CÓ ảnh hưởng)")
print("      bảng nhóm:", {n:res[n][0]["total_points"] for _,_,n in GROUP_STRATEGIES})

print("===== CP7 · deliverable =====")
for f in ["src","bench.py","ingest.py","main.py","tests","requirements.txt",
          "data/k4_ecommerce/sources.csv","report/REPORT_NHOM.md","report/REPORT_CANHAN.md",
          "report/bench_output_lexical.txt","report/bench_output_mock.txt"]:
    chk(Path(f).exists(), f"tồn tại: {f}")
reps=["2A202601424_NguyenQuangHa","K4_01452_NguyenNhatQuang","2A202601092_TruongNgocHai","K4_2A202601342_VuVanHuy"]
for r in reps:
    p=Path(f"report/{r}.md"); t=p.read_text(encoding="utf-8")
    secs=len(re.findall(r'^## [1-5]\.', t, re.M))
    chk(p.exists() and secs==5 and "failure" in t.lower() and "42 / 42" in t,
        f"report cá nhân {r}.md — 5 mục={secs}, có failure case, có 42/42")
import subprocess
heads=subprocess.run(["grep","-rl","class StructureChunker","src/"],capture_output=True,text=True).stdout.strip()
chk(bool(heads), f"có chunker theo heading/section: {heads}")
gi=Path(".gitignore").read_text()
chk(".env" in gi and ".venv" in gi, ".gitignore chặn .env và .venv")
chk(not Path(".env").exists(), "không có file .env trong repo")
