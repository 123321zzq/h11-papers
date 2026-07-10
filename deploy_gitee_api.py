"""Upload entire site to Gitee via Contents API (no git push needed)."""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = "h11-papers"
SKIP = {".git", "__pycache__", "tools", "deploy.zip", "gitee_token.txt"}


def load_token():
    for src in [
        os.environ.get("GITEE_TOKEN", ""),
        open(os.path.join(ROOT, "gitee_token.txt"), encoding="utf-8").read().strip()
        if os.path.exists(os.path.join(ROOT, "gitee_token.txt"))
        else "",
    ]:
        if src.strip():
            return src.strip()
    return ""


def api(token, method, path, data=None):
    url = "https://gitee.com/api/v5" + path
    sep = "&" if "?" in url else "?"
    url = url + sep + "access_token=" + urllib.parse.quote(token)
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("User-Agent", "h11-papers-deploy")
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gitee {e.code}: {text[:400]}")


def collect_files():
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP]
        for name in filenames:
            if name in SKIP or name.endswith(".pyc"):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, ROOT).replace("\\", "/")
            out.append((rel, full))
    return sorted(out)


def ensure_repo(token, login):
    try:
        api(token, "GET", f"/repos/{login}/{REPO}")
        print(f"Repo ready: https://gitee.com/{login}/{REPO}")
    except RuntimeError as e:
        if "404" in str(e):
            api(token, "POST", "/user/repos", {
                "name": REPO,
                "description": "Climate literature PDF viewer",
                "public": True,
                "has_issues": False,
                "has_wiki": False,
            })
            print(f"Created repo: https://gitee.com/{login}/{REPO}")
        else:
            raise


def upload_file(token, login, rel, full, sha_cache):
    with open(full, "rb") as f:
        content = base64.b64encode(f.read()).decode("ascii")
    size_mb = os.path.getsize(full) / (1024 * 1024)
    print(f"  Upload {rel} ({size_mb:.1f} MB)...", flush=True)

    payload = {
        "message": f"update {rel}",
        "content": content,
        "branch": "main",
    }
    if rel in sha_cache:
        payload["sha"] = sha_cache[rel]

    result = api(token, "POST", f"/repos/{login}/{REPO}/contents/{urllib.parse.quote(rel)}", payload)
    if result.get("content", {}).get("sha"):
        sha_cache[rel] = result["content"]["sha"]
    time.sleep(0.5)


def enable_pages(token, login):
    try:
        api(token, "POST", f"/repos/{login}/{REPO}/pages", {"build_directory": "/", "branch": "main"})
        print("Gitee Pages build triggered")
    except RuntimeError as e:
        print(f"Pages note: {e}")


def main():
    token = load_token()
    if not token:
        sys.exit("Missing GITEE_TOKEN. Set env var or create website/gitee_token.txt")

    user = api(token, "GET", "/user")
    login = user["login"]
    print(f"Logged in as {login}")

    ensure_repo(token, login)

    sha_cache = {}
    try:
        listing = api(token, "GET", f"/repos/{login}/{REPO}/git/trees/main?recursive=1")
        for item in listing.get("tree", []):
            if item.get("type") == "blob":
                sha_cache[item["path"]] = item.get("sha")
    except Exception:
        pass

    files = collect_files()
    print(f"Uploading {len(files)} files...")
    for rel, full in files:
        upload_file(token, login, rel, full, sha_cache)

    enable_pages(token, login)
    print(f"\nDone: https://{login}.gitee.io/{REPO}/#/")


if __name__ == "__main__":
    main()
