"""Inline SVG diagrams, one per claim, in English and French.

Pages reference them as {{diagram:NAME}}; site_build replaces the marker with
the figure for the page's language. Hand-drawn shapes only: no library, no
script, no external image.
"""

from html import escape

ACCENT = "#f28c38"
MUTED = "#a9a5b6"
LINE = "#3a3644"
PANEL = "#1d1b23"
GOOD = "#7ee2a8"
BAD = "#ff6b6b"
FONT = 'font-family="system-ui, sans-serif"'


def labels(**text):
    """One language's strings for a diagram."""
    return text


def t(x, y, s, size=13, anchor="start", color="currentColor", weight=400):
    return (f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
            f'fill="{color}" font-weight="{weight}" {FONT}>{escape(s)}</text>')


def box(x, y, w, h, label, sub=None, stroke=LINE, fill=PANEL, color="currentColor"):
    out = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    if sub:
        out += t(x + w / 2, y + h / 2 - 3, label, 13, "middle", color, 600)
        out += t(x + w / 2, y + h / 2 + 14, sub, 11, "middle", MUTED)
    else:
        out += t(x + w / 2, y + h / 2 + 5, label, 13, "middle", color, 600)
    return out


def arrow(x1, y1, x2, y2, label=None, color="currentColor", dash=False, lx=None, ly=None, marker="a"):
    d = ' stroke-dasharray="5 4"' if dash else ""
    out = (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.6"{d} '
           f'marker-end="url(#{marker})"/>')
    if label:
        out += t(lx if lx is not None else (x1 + x2) / 2, ly if ly is not None else (y1 + y2) / 2 - 7,
                 label, 11, "middle", MUTED)
    return out


def svg(name, w, h, label, body):
    defs = "".join(
        f'<marker id="{m}-{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
        for m, c in (("a", "currentColor"), ("acc", ACCENT), ("bad", BAD), ("good", GOOD))
    )
    body = body.replace("url(#a)", f"url(#a-{name})").replace("url(#acc)", f"url(#acc-{name})")
    body = body.replace("url(#bad)", f"url(#bad-{name})").replace("url(#good)", f"url(#good-{name})")
    return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}" '
            f'style="max-width:100%;height:auto;color:var(--text)"><defs>{defs}</defs>{body}</svg>')


def figure(name, w, h, caption, body):
    return (f'<figure class="diagram">{svg(name, w, h, caption, body)}'
            f'<figcaption>{escape(caption)}</figcaption></figure>')


# ── hardware: which model fits under the 16 GB line ─────────────────────────
def hardware(lang):
    L = {
        "en": labels(cap="Left of the orange line fits on a 16 GB card. The 35B spills over: its experts move to system RAM.",
                   line="16 GB card", rows=["Qwen3 8B · Q4_K_M", "9B · Q8 · long context", "27B · IQ3_XXS · 64k", "35B-A3B · Q4_K_M"],
                   vals=["5.0 GB file", "9.4 GB measured", "14.2 GB measured", "22.1 GB file"], spill="experts → system RAM"),
        "fr": labels(cap="À gauche de la ligne orange, ça tient sur une carte de 16 Go. Le 35B déborde : ses experts partent en RAM.",
                   line="carte 16 Go", rows=["Qwen3 8B · Q4_K_M", "9B · Q8 · long contexte", "27B · IQ3_XXS · 64k", "35B-A3B · Q4_K_M"],
                   vals=["fichier 5,0 Go", "9,4 Go mesurés", "14,2 Go mesurés", "fichier 22,1 Go"], spill="experts → RAM système"),
    }[lang]
    x0, scale, top = 190, 20.0, 40  # 20 px per GB, 0..24 GB
    gb = [5.0, 9.4, 14.2, 22.1]
    body = ""
    for g in (0, 8, 16, 24):
        x = x0 + g * scale
        body += f'<line x1="{x}" y1="{top - 10}" x2="{x}" y2="{top + 4 * 44}" stroke="{LINE}" stroke-width="1"/>'
        body += t(x, top + 4 * 44 + 18, f"{g} GB" if lang == "en" else f"{g} Go", 11, "middle", MUTED)
    for i, (name, v, val) in enumerate(zip(L["rows"], gb, L["vals"])):
        y = top + i * 44
        body += t(x0 - 12, y + 19, name, 12, "end")
        fit = min(v, 16)
        body += f'<rect x="{x0}" y="{y + 4}" width="{fit * scale}" height="22" rx="4" fill="{MUTED}" fill-opacity="0.55"/>'
        if v > 16:
            body += (f'<rect x="{x0 + 16 * scale}" y="{y + 4}" width="{(v - 16) * scale}" height="22" rx="4" '
                     f'fill="none" stroke="{ACCENT}" stroke-width="1.5" stroke-dasharray="4 3"/>')
            body += t(x0 + v * scale + 8, y + 12, val, 11)
            body += t(x0 + v * scale + 8, y + 27, L["spill"], 11, color=ACCENT)
        else:
            body += t(x0 + v * scale + 8, y + 20, val, 11)
    xl = x0 + 16 * scale
    body += f'<line x1="{xl}" y1="{top - 18}" x2="{xl}" y2="{top + 4 * 44}" stroke="{ACCENT}" stroke-width="2"/>'
    body += t(xl, top - 22, L["line"], 12, "middle", ACCENT, 600)
    return figure("hardware", 820, 250, L["cap"], body)


# ── docker: the layers and who provides each ────────────────────────────────
def docker_stack(lang):
    L = {
        "en": labels(cap="Five layers, one provider each. The CDI file describes the driver as it was: after a driver update, regenerate it.",
                   layers=[("Your model server", "llama-server, in a container"), ("Docker", "runs and isolates containers"),
                           ("NVIDIA Container Toolkit", "+ /etc/cdi/nvidia.yaml"), ("NVIDIA driver", "on the host"), ("GPU", "the card")],
                   who=["llama.cpp", "Docker", "NVIDIA", "your distribution", "hardware"], by="provided by",
                   trap="stale after a driver update", fix="nvidia-ctk cdi generate"),
        "fr": labels(cap="Cinq couches, un fournisseur chacune. Le fichier CDI décrit le pilote tel qu'il était : après une mise à jour du pilote, régénérez-le.",
                   layers=[("Votre serveur de modèles", "llama-server, dans un conteneur"), ("Docker", "lance et isole les conteneurs"),
                           ("NVIDIA Container Toolkit", "+ /etc/cdi/nvidia.yaml"), ("Pilote NVIDIA", "sur l'hôte"), ("GPU", "la carte")],
                   who=["llama.cpp", "Docker", "NVIDIA", "votre distribution", "matériel"], by="fourni par",
                   trap="périmé après une mise à jour", fix="nvidia-ctk cdi generate"),
    }[lang]
    body = t(640, 22, L["by"], 11, "start", MUTED)
    for i, ((name, sub), who) in enumerate(zip(L["layers"], L["who"])):
        y = 34 + i * 54
        accent = i == 2
        body += box(230, y, 360, 44, name, sub, stroke=ACCENT if accent else LINE, color=ACCENT if accent else "currentColor")
        body += t(640, y + 27, who, 12)
    body += arrow(210, 34 + 3 * 54 + 22, 210, 34 + 2 * 54 + 30, None, ACCENT, marker="acc")
    body += t(202, 34 + 2 * 54 + 64, L["trap"], 11, "end", ACCENT)
    body += t(202, 34 + 2 * 54 + 80, L["fix"], 11, "end", MUTED)
    return figure("docker", 800, 310, L["cap"], body)


# ── first model: the path of one request ────────────────────────────────────
def request_path(lang):
    L = {
        "en": labels(cap="One request, start to finish, without leaving the machine: the port only listens on 127.0.0.1.",
                   you="curl / your tool", port="127.0.0.1:8080", srv="llama-server", gpu="GPU memory",
                   gsub="weights 5.0 GB + context", post="POST /v1/chat/completions", fwd="port mapping", load="-ngl 99",
                   machine="this machine", net="internet", blocked="not exposed"),
        "fr": labels(cap="Une requête, du début à la fin, sans quitter la machine : le port n'écoute que sur 127.0.0.1.",
                   you="curl / votre outil", port="127.0.0.1:8080", srv="llama-server", gpu="Mémoire GPU",
                   gsub="poids 5,0 Go + contexte", post="POST /v1/chat/completions", fwd="port publié", load="-ngl 99",
                   machine="cette machine", net="Internet", blocked="non exposé"),
    }[lang]
    body = (f'<rect x="10" y="30" width="750" height="120" rx="12" fill="none" stroke="{LINE}" stroke-dasharray="6 5"/>'
            + t(24, 50, L["machine"], 11, "start", MUTED))
    body += box(30, 70, 130, 54, L["you"])
    body += box(220, 70, 130, 54, L["port"])
    body += box(410, 70, 120, 54, L["srv"], "container")
    body += box(580, 70, 166, 54, L["gpu"], L["gsub"], stroke=ACCENT)
    body += arrow(160, 97, 218, 97, L["post"], lx=190, ly=62)
    body += arrow(350, 97, 408, 97, L["fwd"], lx=380, ly=88)
    body += arrow(530, 97, 578, 97, L["load"], lx=554, ly=88)
    body += t(285, 200, L["net"], 12, "middle", MUTED)
    body += arrow(285, 185, 285, 128, None, BAD, dash=True, marker="bad")
    body += t(300, 170, L["blocked"], 11, "start", BAD)
    return figure("request", 770, 215, L["cap"], body)


def kv_trap(lang):
    L = {
        "en": labels(cap="Same model, same card, one flag changed. Reading a 7,758-token prompt: 21 times slower with ‑ctv q4_0.",
                   unit="tokens/s, reading the prompt", same="generation: 54 tok/s in both cases"),
        "fr": labels(cap="Même modèle, même carte, un seul réglage changé. Lecture d'un prompt de 7 758 jetons : 21 fois plus lent avec ‑ctv q4_0.",
                   unit="jetons/s, lecture du prompt", same="génération : 54 jetons/s dans les deux cas"),
    }[lang]
    x0, w = 150, 470
    body = t(x0, 22, L["unit"], 11, "start", MUTED)
    body += t(x0 - 12, 52, "-ctv q8_0", 13, "end", weight=600)
    body += f'<rect x="{x0}" y="36" width="{w}" height="24" rx="4" fill="{GOOD}" fill-opacity="0.75"/>'
    body += t(x0 + w + 8, 53, "1 330" if lang == "fr" else "1,330", 13, weight=600)
    body += t(x0 - 12, 96, "-ctv q4_0", 13, "end", ACCENT, 600)
    body += f'<rect x="{x0}" y="80" width="{w * 62.7 / 1330:.1f}" height="24" rx="4" fill="{ACCENT}"/>'
    body += t(x0 + w * 62.7 / 1330 + 8, 97, "62,7" if lang == "fr" else "62.7", 13, color=ACCENT, weight=600)
    body += t(x0, 132, L["same"], 11, "start", MUTED)
    return figure("kv", 720, 145, L["cap"], body)


# ── home: cloud only versus hybrid ──────────────────────────────────────────
def hybrid(lang):
    L = {
        "en": labels(cap="What crosses the border. Cloud only: everything, private data included. Hybrid: only the hard tasks, without your data.",
                   a="Cloud only", b="Hybrid", home="your home", net="internet", you="You", agent="Local agent",
                   asub="held by rules", cloud="Frontier model", csub="subscription", all="everything, private data too",
                   hard="hard tasks only", priv="private data, routine", stays="stays home"),
        "fr": labels(cap="Ce qui traverse la frontière. Cloud seul : tout, données privées comprises. Hybride : seulement les tâches dures, sans vos données.",
                   a="Cloud seul", b="Hybride", home="chez vous", net="Internet", you="Vous", agent="Agent local",
                   asub="encadré par des règles", cloud="Modèle frontier", csub="abonnement", all="tout, données privées aussi",
                   hard="tâches dures seulement", priv="données privées, courant", stays="reste à la maison"),
    }[lang]
    body = ""
    for row, title in ((0, L["a"]), (1, L["b"])):
        y = 30 + row * 130
        body += t(20, y + 4, title, 13, "start", ACCENT if row else "currentColor", 700)
        body += t(250, y + 4, L["home"], 11, "middle", MUTED) + t(590, y + 4, L["net"], 11, "middle", MUTED)
        body += f'<line x1="440" y1="{y - 10}" x2="440" y2="{y + 100}" stroke="{LINE}" stroke-width="2" stroke-dasharray="6 5"/>'
        body += box(20, y + 24, 110, 54, L["you"])
        body += box(560, y + 24, 140, 54, L["cloud"], L["csub"])
        if row == 0:
            body += arrow(130, y + 51, 558, y + 51, L["all"], BAD, marker="bad", lx=345, ly=y + 43)
        else:
            body += box(230, y + 24, 150, 54, L["agent"], L["asub"], stroke=ACCENT)
            body += arrow(130, y + 51, 228, y + 51)
            body += arrow(380, y + 51, 558, y + 51, L["hard"], GOOD, marker="good", lx=470, ly=y + 43)
            body += t(305, y + 98, L["priv"] + " · " + L["stays"], 11, "middle", ACCENT)
    return figure("hybrid", 720, 280, L["cap"], body)


# ── proxmox: one machine, many guests, backups, admin path ──────────────────
def proxmox(lang):
    L = {
        "en": labels(cap="One machine runs every service in its own guest. Backups go to a second disk every night; administration goes through a private network, never the internet.",
                   node="One machine · Proxmox VE", guests=["proxy", "office", "photos", "forge", "automation", "search", "tasks"],
                   nvme="SSD · guests", hdd="2nd disk · backups", nightly="nightly backup", you="Your laptop",
                   ts="Tailscale / WireGuard", net="internet", no="port 8006 closed"),
        "fr": labels(cap="Une machine fait tourner chaque service dans son propre invité. Les sauvegardes partent chaque nuit sur un second disque ; l'administration passe par un réseau privé, jamais par Internet.",
                   node="Une machine · Proxmox VE", guests=["proxy", "bureautique", "photos", "forge", "automatisation", "recherche", "tâches"],
                   nvme="SSD · invités", hdd="2e disque · sauvegardes", nightly="sauvegarde nocturne", you="Votre portable",
                   ts="Tailscale / WireGuard", net="Internet", no="port 8006 fermé"),
    }[lang]
    body = f'<rect x="200" y="20" width="500" height="250" rx="12" fill="none" stroke="{LINE}" stroke-width="1.5"/>'
    body += t(220, 42, L["node"], 13, "start", weight=700)
    for i, g in enumerate(L["guests"]):
        col, row = i % 4, i // 4
        kind = "CT" if i == 6 else "VM"
        body += box(220 + col * 118, 58 + row * 62, 106, 50, g, kind)
    body += box(220, 196, 200, 54, L["nvme"])
    body += box(480, 196, 200, 54, L["hdd"], stroke=ACCENT)
    body += arrow(420, 223, 478, 223, L["nightly"], ACCENT, marker="acc", lx=450, ly=190)
    body += box(10, 70, 150, 50, L["you"])
    body += arrow(160, 95, 218, 95, None, GOOD, marker="good")
    body += t(85, 140, L["ts"], 11, "middle", GOOD)
    body += t(85, 222, L["net"], 12, "middle", MUTED)
    body += arrow(130, 228, 198, 228, None, BAD, dash=True, marker="bad")
    body += t(85, 246, L["no"], 11, "middle", BAD)
    return figure("proxmox", 720, 285, L["cap"], body)


# ── homelab 2: one public entrance, many private services ───────────────────
def proxy(lang):
    L = {
        "en": labels(cap="One entrance. The box forwards only 80 and 443 to the proxy; the proxy reads the requested name and passes the request to the right service on your network. The admin port 81 never leaves home.",
                     net="internet", dns="DNS: *.yourdomain → your public IP", box="Your box", bsub="forwards 80, 443",
                     npm="Reverse proxy", nsub="HTTPS, certificates", home="your network",
                     svc=[("site", "port 8000"), ("forge", "port 8001"), ("photos", "port 8002")],
                     host="by requested name", admin="admin :81, LAN only", le="Let's Encrypt checks port 80"),
        "fr": labels(cap="Une seule entrée. La box ne transmet que 80 et 443 au proxy ; le proxy lit le nom demandé et passe la requête au bon service de votre réseau. Le port d'administration 81 ne sort jamais de la maison.",
                     net="Internet", dns="DNS : *.votredomaine → votre IP publique", box="Votre box", bsub="transmet 80, 443",
                     npm="Proxy inverse", nsub="HTTPS, certificats", home="votre réseau",
                     svc=[("site", "port 8000"), ("forge", "port 8001"), ("photos", "port 8002")],
                     host="selon le nom demandé", admin="admin :81, LAN seulement", le="Let's Encrypt vérifie le port 80"),
    }[lang]
    body = t(60, 30, L["net"], 12, "middle", MUTED)
    body += t(60, 48, "visitor", 11, "middle", MUTED) if lang == "en" else t(60, 48, "visiteur", 11, "middle", MUTED)
    body += t(20, 250, L["dns"], 11, "start", MUTED)
    body += f'<rect x="170" y="14" width="590" height="215" rx="12" fill="none" stroke="{LINE}" stroke-dasharray="6 5"/>'
    body += t(186, 34, L["home"], 11, "start", MUTED)
    body += box(10, 90, 100, 50, "https://", None)
    body += box(190, 90, 120, 50, L["box"], L["bsub"])
    body += box(370, 90, 150, 50, L["npm"], L["nsub"], stroke=ACCENT)
    body += arrow(110, 115, 188, 115, "443", lx=150, ly=107)
    body += arrow(310, 115, 368, 115)
    for i, (name, port) in enumerate(L["svc"]):
        y = 44 + i * 58
        body += box(610, y, 130, 46, name, port)
        body += arrow(520, 115, 608, y + 23, None, ACCENT, marker="acc")
    body += t(675, 222, L["host"], 11, "middle", ACCENT)
    body += t(445, 162, L["admin"], 11, "middle", MUTED)
    body += t(250, 162, L["le"], 11, "middle", MUTED)
    return figure("proxy", 770, 265, L["cap"], body)


# ── homelab 3: where each secret lives ──────────────────────────────────────
def vault(lang):
    L = {
        "en": labels(cap="Your devices encrypt before sending: the server only ever stores ciphertext. The one secret that opens everything is typed on the device and lives on paper, not in the vault.",
                     dev="Your devices", dsub="app, browser extension", enc="encrypts here", paper="Master password",
                     psub="on paper, at home", typed="typed, never sent", proxy="HTTPS proxy", vw="Vaultwarden",
                     vsub="one container", db="db.sqlite3", dbsub="ciphertext only", backup="2nd disk", bsub="sqlite3 .backup",
                     nightly="nightly", sends="encrypted items"),
        "fr": labels(cap="Vos appareils chiffrent avant d'envoyer : le serveur ne stocke jamais que du chiffré. Le seul secret qui ouvre tout se tape sur l'appareil et vit sur papier, pas dans le coffre.",
                     dev="Vos appareils", dsub="app, extension navigateur", enc="chiffre ici", paper="Mot de passe maître",
                     psub="sur papier, à la maison", typed="tapé, jamais envoyé", proxy="Proxy HTTPS", vw="Vaultwarden",
                     vsub="un conteneur", db="db.sqlite3", dbsub="du chiffré seulement", backup="2e disque", bsub="sqlite3 .backup",
                     nightly="chaque nuit", sends="fiches chiffrées"),
    }[lang]
    body = box(20, 30, 160, 50, L["paper"], L["psub"])
    body += arrow(100, 80, 100, 128, None, dash=True)
    body += t(110, 108, L["typed"], 11, "start", MUTED)
    body += box(20, 130, 160, 54, L["dev"], L["dsub"], stroke=ACCENT)
    body += t(100, 202, L["enc"], 11, "middle", ACCENT, 600)
    body += box(250, 130, 120, 54, L["proxy"])
    body += box(420, 130, 130, 54, L["vw"], L["vsub"])
    body += box(600, 130, 140, 54, L["db"], L["dbsub"])
    body += arrow(180, 157, 248, 157, L["sends"], lx=214, ly=149)
    body += arrow(370, 157, 418, 157)
    body += arrow(550, 157, 598, 157)
    body += box(600, 240, 140, 50, L["backup"], L["bsub"], stroke=ACCENT)
    body += arrow(670, 184, 670, 238, L["nightly"], ACCENT, marker="acc", lx=715, ly=215)
    return figure("vault", 760, 305, L["cap"], body)


# ── free the cards for AI, still play ───────────────────────────────────────
def gpu_split(lang):
    L = {
        "en": labels(cap="The desktop lives on the integrated GPU, so the NVIDIA cards display nothing and all their memory goes to AI. When a Steam game starts, a watcher moves the models off one card; the game renders there, and its frames reach the screen through the integrated GPU (option A) or a second cable (option B).",
                     igpu="Integrated GPU", isub="desktop, always", screen="Screen", c0="RTX 5080", c0a="AI models", c0b="or: the game",
                     c1="RTX 4070 Ti S", c1s="AI models, always", a="A: PRIME offload, frames copied", b="B: 2nd cable, switch input",
                     watch="Watcher", wsub="Steam game seen?", free="models leave, then return"),
        "fr": labels(cap="Le bureau vit sur le GPU intégré : les cartes NVIDIA n'affichent rien et toute leur mémoire va à l'IA. Quand un jeu Steam démarre, un veilleur retire les modèles d'une carte ; le jeu y est calculé, et ses images rejoignent l'écran par le GPU intégré (option A) ou par un second câble (option B).",
                     igpu="GPU intégré", isub="le bureau, toujours", screen="Écran", c0="RTX 5080", c0a="modèles IA", c0b="ou : le jeu",
                     c1="RTX 4070 Ti S", c1s="modèles IA, toujours", a="A : PRIME offload, images copiées", b="B : 2e câble, changer d'entrée",
                     watch="Veilleur", wsub="un jeu Steam ?", free="les modèles partent, puis reviennent"),
    }[lang]
    body = box(30, 30, 170, 54, L["igpu"], L["isub"])
    body += box(600, 30, 140, 54, L["screen"], None)
    body += arrow(200, 57, 598, 57, None)
    body += box(30, 150, 170, 64, L["c0"], L["c0a"] + " · " + L["c0b"], stroke=ACCENT)
    body += box(30, 260, 170, 54, L["c1"], L["c1s"])
    body += arrow(115, 150, 115, 86, None, ACCENT, dash=True, marker="acc")
    body += t(127, 122, L["a"], 11, "start", ACCENT)
    body += arrow(200, 190, 640, 86, None, GOOD, marker="good")
    body += t(500, 160, L["b"], 11, "middle", GOOD)
    body += box(320, 240, 160, 54, L["watch"], L["wsub"])
    body += arrow(320, 255, 202, 195, None, MUTED)
    body += t(400, 312, L["free"], 11, "middle", MUTED)
    return figure("gpu", 760, 325, L["cap"], body)


# ── headless node that still plays ──────────────────────────────────────────
def stream(lang):
    L = {
        "en": labels(cap="No screen on the tower. A virtual 120 Hz display exists only for the kernel; the streaming server captures it, the integrated GPU encodes the video, and the handheld plays it. The NVIDIA cards keep computing.",
                     tower="The tower, no screen", virt="Virtual display", vsub="EDID forced at boot", cap1="Apollo",
                     csub="captures (KMS)", enc="Integrated GPU", esub="encodes HEVC", hand="Android handheld",
                     hsub="Artemis / Moonlight", net="Wi-Fi or tailnet", input="buttons, touch", nv="NVIDIA cards",
                     nvs="models · or the game", draws="the game draws here"),
        "fr": labels(cap="Pas d'écran sur la tour. Un écran virtuel à 120 Hz n'existe que pour le noyau ; le serveur de streaming le capture, le GPU intégré encode la vidéo, et la console portable la joue. Les cartes NVIDIA continuent de calculer.",
                     tower="La tour, sans écran", virt="Écran virtuel", vsub="EDID forcé au démarrage", cap1="Apollo",
                     csub="capture (KMS)", enc="GPU intégré", esub="encode en HEVC", hand="Console Android",
                     hsub="Artemis / Moonlight", net="Wi-Fi ou tailnet", input="boutons, tactile", nv="Cartes NVIDIA",
                     nvs="modèles · ou le jeu", draws="le jeu y dessine"),
    }[lang]
    body = f'<rect x="10" y="20" width="520" height="230" rx="12" fill="none" stroke="{LINE}" stroke-dasharray="6 5"/>'
    body += t(26, 40, L["tower"], 11, "start", MUTED)
    body += box(30, 60, 150, 54, L["virt"], L["vsub"])
    body += box(210, 60, 130, 54, L["cap1"], L["csub"])
    body += box(370, 60, 140, 54, L["enc"], L["esub"], stroke=ACCENT)
    body += arrow(180, 87, 208, 87)
    body += arrow(340, 87, 368, 87)
    body += box(30, 170, 150, 54, L["nv"], L["nvs"])
    body += arrow(105, 168, 105, 116, None, MUTED, dash=True)
    body += t(115, 146, L["draws"], 11, "start", MUTED)
    body += box(600, 60, 150, 54, L["hand"], L["hsub"], stroke=ACCENT)
    body += arrow(510, 80, 598, 80, L["net"], ACCENT, marker="acc", lx=555, ly=72)
    body += arrow(598, 100, 512, 100, L["input"], lx=555, ly=118)
    return figure("stream", 770, 265, L["cap"], body)


# ── sleep when idle, wake on demand ─────────────────────────────────────────
def wake(lang):
    L = {
        "en": labels(cap="The big tower sleeps. A small machine that is always on sends the magic packet on the local network; the tower wakes, and the wake command waits until SSH and the model gateway really answer.",
                     you="Phone or laptop", ysub="anywhere, via tailnet", relay="Always-on node", rsub="small, low power",
                     pkt="magic packet (LAN broadcast)", tower="The tower", tsub="asleep → awake", ready="ready = SSH + gateway answer",
                     ask="wake command"),
        "fr": labels(cap="La grosse tour dort. Une petite machine toujours allumée envoie le paquet magique sur le réseau local ; la tour se réveille, et la commande de réveil attend que SSH et la passerelle des modèles répondent vraiment.",
                     you="Téléphone ou portable", ysub="de partout, via le tailnet", relay="Nœud toujours allumé", rsub="petit, peu gourmand",
                     pkt="paquet magique (diffusion LAN)", tower="La tour", tsub="endormie → réveillée", ready="prête = SSH + passerelle répondent",
                     ask="commande de réveil"),
    }[lang]
    body = box(20, 50, 170, 54, L["you"], L["ysub"])
    body += box(290, 50, 170, 54, L["relay"], L["rsub"])
    body += box(570, 50, 170, 54, L["tower"], L["tsub"], stroke=ACCENT)
    body += arrow(190, 77, 288, 77, L["ask"], lx=239, ly=69)
    body += arrow(460, 77, 568, 77, L["pkt"], ACCENT, marker="acc", lx=514, ly=66)
    body += arrow(655, 104, 655, 140, None, GOOD, marker="good")
    body += t(655, 158, L["ready"], 11, "middle", GOOD)
    return figure("wake", 760, 175, L["cap"], body)


# ── homelab 4: three answers from one DNS ───────────────────────────────────
def dns(lang):
    L = {
        "en": labels(cap="Every device asks the same DNS. An ad or tracker gets nothing; your own domain gets the proxy's address on the local network, so internal traffic stays home and stays filtered; everything else goes out encrypted.",
                     dev="Every device", dsub="via the box's DHCP", ag="AdGuard Home", asub="filters, rewrites, caches",
                     ad="ads.tracker.example", adr="blocked: no answer", own="cloud.yourdomain", ownr="→ proxy, local address",
                     rest="anything else", restr="→ upstream, encrypted (DoH)", up="Upstream resolver"),
        "fr": labels(cap="Chaque appareil interroge le même DNS. Une pub ou un traceur n'obtient rien ; votre propre domaine obtient l'adresse locale du proxy, donc le trafic interne reste à la maison et reste filtré ; tout le reste sort chiffré.",
                     dev="Chaque appareil", dsub="via le DHCP de la box", ag="AdGuard Home", asub="filtre, réécrit, met en cache",
                     ad="pub.traceur.example", adr="bloqué : pas de réponse", own="cloud.votredomaine", ownr="→ proxy, adresse locale",
                     rest="tout le reste", restr="→ résolveur amont, chiffré (DoH)", up="Résolveur amont"),
    }[lang]
    body = box(20, 110, 150, 54, L["dev"], L["dsub"])
    body += box(250, 110, 170, 54, L["ag"], L["asub"], stroke=ACCENT)
    body += arrow(170, 137, 248, 137)
    rows = [(L["ad"], L["adr"], BAD, "bad"), (L["own"], L["ownr"], GOOD, "good"), (L["rest"], L["restr"], MUTED, "a")]
    for i, (q, a, c, m) in enumerate(rows):
        y = 30 + i * 90
        body += arrow(420, 137, 500, y + 20, None, c, marker=m)
        body += t(510, y + 16, q, 12, "start", weight=600)
        body += t(510, y + 34, a, 11, "start", c)
    return figure("dns", 760, 290, L["cap"], body)


# ── homelab 5: the copy is pulled, never pushed ─────────────────────────────
def backups(lang):
    L = {
        "en": labels(cap="Copy 1 is written by the hypervisor every night. Copy 2 is pulled by another machine, with a key that can only read: whatever takes over the hypervisor cannot reach it.",
                     pve="Hypervisor", psub="writes copy 1, 02:00", d1="Copy 1", d1s="external disk, 7 daily + 4 weekly",
                     other="Another machine", osub="pulls copy 2, 03:00", d2="Copy 2", d2s="mirror + quarantine",
                     key="pulled with a read-only key (rrsync -ro)", bad="no access, no write", nightly="nightly backup"),
        "fr": labels(cap="La copie 1 est écrite par l'hyperviseur chaque nuit. La copie 2 est tirée par une autre machine, avec une clé qui ne sait que lire : ce qui prendrait le contrôle de l'hyperviseur ne peut pas l'atteindre.",
                     pve="Hyperviseur", psub="écrit la copie 1, 02:00", d1="Copie 1", d1s="disque externe, 7 jours + 4 semaines",
                     other="Une autre machine", osub="tire la copie 2, 03:00", d2="Copie 2", d2s="miroir + quarantaine",
                     key="tirée avec une clé en lecture seule (rrsync -ro)", bad="aucun accès, aucune écriture", nightly="sauvegarde nocturne"),
    }[lang]
    body = box(20, 40, 210, 54, L["pve"], L["psub"])
    body += box(20, 170, 210, 54, L["d1"], L["d1s"])
    body += arrow(125, 94, 125, 168, L["nightly"], lx=180, ly=135)
    body += box(540, 40, 200, 54, L["other"], L["osub"], stroke=ACCENT)
    body += box(540, 170, 200, 54, L["d2"], L["d2s"], stroke=ACCENT)
    body += arrow(640, 94, 640, 168)
    body += arrow(230, 190, 538, 90, None, ACCENT, marker="acc")
    body += t(400, 222, L["key"], 11, "middle", ACCENT)
    body += arrow(230, 58, 538, 58, None, BAD, dash=True, marker="bad")
    body += t(384, 50, L["bad"], 11, "middle", BAD)
    return figure("backups", 760, 240, L["cap"], body)


DIAGRAMS = {"hardware": hardware, "docker": docker_stack, "request": request_path,
            "kv": kv_trap, "hybrid": hybrid, "proxmox": proxmox,
            "proxy": proxy, "vault": vault,
            "gpu": gpu_split, "stream": stream, "wake": wake,
            "dns": dns, "backups": backups}


def render(name, lang):
    return DIAGRAMS[name](lang)
