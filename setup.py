import os
import shutil
import json

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static = os.path.join(base, "website", "static")
meta_path = os.path.join(base, "website", "papers_meta.json")

os.makedirs(static, exist_ok=True)

with open(meta_path, "r", encoding="utf-8") as f:
    papers_meta = json.load(f)

all_pdfs = [f for f in os.listdir(base) if f.lower().endswith(".pdf")]


def find_pdf(meta):
    if "match" in meta and meta["match"] in all_pdfs:
        return meta["match"]
    if "match_prefix" in meta:
        for f in all_pdfs:
            if f.startswith(meta["match_prefix"]):
                return f
    return None


papers = []
for meta in papers_meta:
    src_name = find_pdf(meta)
    if not src_name:
        print("MISSING:", meta["id"], meta.get("match") or meta.get("match_prefix"))
        continue
    src = os.path.join(base, src_name)
    dst = os.path.join(static, meta["id"] + ".pdf")
    shutil.copy2(src, dst)
    size_mb = os.path.getsize(dst) / (1024 * 1024)
    papers.append({
        "id": meta["id"],
        "title": meta["title"],
        "reference": meta["reference"],
        "size": f"{size_mb:.1f} MB",
        "url": "static/" + meta["id"] + ".pdf",
    })
    print(f"OK {meta['id']} {size_mb:.1f} MB <- {src_name}")

js_path = os.path.join(base, "website", "js", "papers-data.js")
with open(js_path, "w", encoding="utf-8") as f:
    f.write("var PDF_LIST = ")
    json.dump(papers, f, ensure_ascii=False, indent=2)
    f.write(";\n")

print(f"Copied {len(papers)}/14 PDFs")
