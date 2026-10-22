#!/usr/bin/env python3
"""revue-jour.py — la revue quotidienne de freedzhost.cloud.

Karakeep (bookmarks pointés par Ben) → Qwen local rédige 2-3 phrases par item,
dans la ligne éditoriale : tech, IT, SaaS, IA, homelab, DIY, souveraineté
numérique → content/revue/YYYY-MM-DD.md → rebuild + déploy + commit.

Usage: revue-jour.py [--date YYYY-MM-DD] [--no-deploy]
Config: ~/.config/freedzhost-site/revue.env
    KARAKEEP_URL   (défaut http://192.168.1.55:3400)
    KARAKEEP_API_KEY (obligatoire — karakeep → Settings → API Keys)
    REVUE_TAG      (défaut "revue" : seuls les bookmarks tagués passent)
"""
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
SITE = HOME / "Work" / "freedzhost-site"
QWEN = "http://127.0.0.1:8098/v1/chat/completions"
LIGNE = "tech, IT, SaaS, IA, homelab, DIY, souveraineté numérique"

env_file = HOME / ".config" / "freedzhost-site" / "revue.env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

KARAKEEP = os.environ.get("KARAKEEP_URL", "http://192.168.1.55:3400")
KEY = os.environ.get("KARAKEEP_API_KEY", "")
TAG = os.environ.get("REVUE_TAG", "revue")
FORGEJO_API = os.environ.get("FORGEJO_API_URL", "")
FORGEJO_TOKEN = os.environ.get("FORGEJO_TOKEN", "")


def api(path):
    req = urllib.request.Request(f"{KARAKEEP}{path}",
                                 headers={"Authorization": f"Bearer {KEY}",
                                          "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def bookmarks_tagues():
    """Bookmarks karakeep portant le tag revue, les plus récents d'abord."""
    out = api("/api/v1/bookmarks?limit=40")
    items = []
    for b in out.get("bookmarks", []):
        tags = [t.get("name", "").lower() for t in b.get("tags", [])]
        if TAG.lower() not in tags:
            continue
        content = b.get("content", {})
        url = content.get("url") or ""
        title = b.get("title") or content.get("title") or url
        summary = b.get("summary") or content.get("description") or ""
        items.append({"title": title.strip(), "url": url, "resume_source": summary[:800]})
    return items


def qwen(prompt, max_tokens=350):
    body = json.dumps({
        "model": "/models/Q3.8-OPUS-27BIQ3XXS.gguf",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens, "temperature": 0.5,
    }).encode()
    req = urllib.request.Request(QWEN, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        txt = json.load(r)["choices"][0]["message"]["content"]
    return re.sub(r"<think>.*?</think>", "", txt, flags=re.DOTALL).strip()


def redige(item):
    prompt = f"""Tu rédiges la revue quotidienne de freedzhost.cloud, site de tutos IA locale et homelab.
Ligne éditoriale : {LIGNE}.

Article à présenter :
Titre : {item['title']}
URL : {item['url']}
Extrait : {item['resume_source'] or '(pas d extrait disponible)'}

Écris un résumé de 2-3 phrases en français : de quoi ça parle, et pourquoi c'est pertinent
pour quelqu'un qui monte son homelab et son IA à la maison. Ton direct, tutoiement interdit,
pas de hype, pas de "révolutionnaire". Si l'article touche la souveraineté numérique ou le
DIY, mets-le en avant. Réponds UNIQUEMENT avec le résumé."""
    return qwen(prompt)


def source_de(url):
    m = re.search(r"https?://(?:www\.)?([^/]+)", url)
    return m.group(1) if m else "lien"


def forgejo_api(method, path, body=None):
    url = f"{FORGEJO_API}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Authorization": f"token {FORGEJO_TOKEN}",
                                          "Content-Type": "application/json",
                                          "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r) if r.status != 204 and r.headers.get("Content-Length") != "0" else None


def wait_checks(sha, timeout=300):
    import time
    start = time.time()
    while time.time() - start < timeout:
        status = forgejo_api("GET", f"/repos/bengua/freedzhost-site/commits/{sha}/status")
        state = status.get("state")
        if state == "success":
            return
        if state in ("failure", "error"):
            sys.exit(f"checks échoués: {state}")
        time.sleep(5)
    sys.exit("timeout en attendant les checks CI")


def main():
    jour = sys.argv[sys.argv.index("--date") + 1] if "--date" in sys.argv else datetime.now(timezone.utc).date().isoformat()
    no_deploy = "--no-deploy" in sys.argv
    if not KEY:
        sys.exit("KARAKEEP_API_KEY manquante — ~/.config/freedzhost-site/revue.env")
    candidats = bookmarks_tagues()[:6]
    if not candidats:
        print(f"aucun bookmark tagué '{TAG}' — rien à publier")
        return
    items = []
    for c in candidats:
        try:
            resume = redige(c)
        except (urllib.error.URLError, OSError, ValueError) as e:
            print(f"  skip {c['title'][:50]}: {e}")
            continue
        items.append({"title": c["title"], "url": c["url"],
                      "source": source_de(c["url"]), "resume": resume})
        print(f"  + {c['title'][:60]}")
    if not items:
        sys.exit("tous les résumés ont échoué")
    payload = json.dumps({"date": jour, "items": items}, ensure_ascii=False)
    dest = SITE / "content" / "revue" / f"{jour}.md"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(f"<!-- {payload} -->\n", encoding="utf-8")
    print(f"revue écrite: {dest} ({len(items)} items)")
    subprocess.run(["python3", "site_build.py"], cwd=SITE, check=True)
    if no_deploy:
        return
    subprocess.run(["rsync", "-a", "--delete", "-e", "ssh -i " + str(HOME / ".ssh/id_ed25519"),
                    str(SITE / "public") + "/", "root@192.168.1.50:/opt/freedzhost-site/public/"],
                   check=True)
    if not FORGEJO_API or not FORGEJO_TOKEN:
        sys.exit("FORGEJO_API_URL et FORGEJO_TOKEN manquants — impossible de créer la PR")

    branch = f"revue/{jour}"
    try:
        subprocess.run(["git", "fetch", "origin"], cwd=SITE, check=True)
        subprocess.run(["git", "checkout", "-B", branch, "origin/main"], cwd=SITE, check=True)
        subprocess.run(["git", "add", "content/revue"], cwd=SITE, check=True)
        subprocess.run(["git", "commit", "-m", f"Revue du {jour}"], cwd=SITE, check=True)
        subprocess.run(["git", "push", "-u", "origin", branch], cwd=SITE, check=True)

        pr = forgejo_api("POST", "/repos/bengua/freedzhost-site/pulls", {
            "title": f"Revue du {jour}",
            "head": branch,
            "base": "main",
            "body": f"Revue quotidienne du {jour}.",
        })
        pr_num = pr["number"]
        print(f"PR créée: #{pr_num}")

        wait_checks(pr["head"]["sha"])
        forgejo_api("POST", f"/repos/bengua/freedzhost-site/pulls/{pr_num}/merge",
                    {"Do": "merge", "delete_branch_after_merge": True})
        print(f"PR #{pr_num} mergée")
    finally:
        subprocess.run(["git", "checkout", "main"], cwd=SITE, check=False)
        subprocess.run(["git", "pull", "--ff-only"], cwd=SITE, check=False)
        subprocess.run(["git", "branch", "-D", branch], cwd=SITE, check=False)
    print("revue déployée et commitée")


if __name__ == "__main__":
    main()
