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


# ── homelab 6: two doors, one public, one private ───────────────────────────
def remote(lang):
    L = {
        "en": labels(cap="Two doors. The public one opens 80 and 443, to the HTTPS proxy only. Everything else, administration included, goes through the private network: your devices reach home, the internet sees nothing.",
                     scan="Anyone on the internet", box="Your box", bsub="80, 443 only", proxy="HTTPS proxy",
                     phone="Your phone, laptop", psub="anywhere", tn="private network (WireGuard)", home="Home services",
                     hsub="admin, models, notes", closed="admin ports: closed", pub="public sites"),
        "fr": labels(cap="Deux portes. La publique n'ouvre que 80 et 443, vers le proxy HTTPS seulement. Tout le reste, administration comprise, passe par le réseau privé : vos appareils rejoignent la maison, Internet ne voit rien.",
                     scan="N'importe qui sur Internet", box="Votre box", bsub="80, 443 seulement", proxy="Proxy HTTPS",
                     phone="Votre téléphone, portable", psub="de partout", tn="réseau privé (WireGuard)", home="Services de la maison",
                     hsub="admin, modèles, notes", closed="ports d'admin : fermés", pub="sites publics"),
    }[lang]
    body = box(20, 40, 180, 54, L["scan"], None)
    body += box(290, 40, 150, 54, L["box"], L["bsub"])
    body += box(540, 40, 200, 54, L["proxy"], L["pub"])
    body += arrow(200, 67, 288, 67)
    body += arrow(440, 67, 538, 67)
    body += arrow(200, 85, 538, 190, None, BAD, dash=True, marker="bad")
    body += t(480, 140, L["closed"], 11, "middle", BAD)
    body += box(20, 190, 180, 54, L["phone"], L["psub"], stroke=GOOD)
    body += box(540, 190, 200, 54, L["home"], L["hsub"])
    body += arrow(200, 217, 538, 217, L["tn"], GOOD, marker="good", lx=370, ly=240)
    return figure("remote", 760, 260, L["cap"], body)


# ── homelab 7: two things to save ───────────────────────────────────────────
def photos(lang):
    L = {
        "en": labels(cap="Two things make a photo library: the files, and the database that knows albums, faces and dates. Immich dumps the database every night; the files you must copy yourself. One without the other restores nothing useful.",
                     phone="Phone app", psub="backs up in the background", srv="Immich", ssub="server + recognition",
                     db="Database", dbs="albums, faces, dates", files="Photo folder", fs="the originals",
                     dump="daily dump, 14 kept", copy="Your backup", csub="both, every night", yours="you copy it"),
        "fr": labels(cap="Une photothèque, c'est deux choses : les fichiers, et la base qui connaît albums, visages et dates. Immich exporte la base chaque nuit ; les fichiers, c'est à vous de les copier. L'un sans l'autre ne restaure rien d'utile.",
                     phone="App du téléphone", psub="sauvegarde en arrière-plan", srv="Immich", ssub="serveur + reconnaissance",
                     db="Base de données", dbs="albums, visages, dates", files="Dossier des photos", fs="les originaux",
                     dump="export quotidien, 14 gardés", copy="Votre sauvegarde", csub="les deux, chaque nuit", yours="à vous de le copier"),
    }[lang]
    body = box(20, 100, 160, 54, L["phone"], L["psub"])
    body += box(240, 100, 160, 54, L["srv"], L["ssub"])
    body += arrow(180, 127, 238, 127, "HTTPS", lx=209, ly=119)
    body += box(470, 30, 150, 54, L["db"], L["dbs"])
    body += box(470, 170, 150, 54, L["files"], L["fs"], stroke=ACCENT)
    body += arrow(400, 115, 468, 62)
    body += arrow(400, 140, 468, 192)
    body += box(660, 100, 120, 54, L["copy"], None, stroke=GOOD)
    body += arrow(620, 57, 670, 98, None, GOOD, marker="good")
    body += t(700, 20, L["dump"], 11, "middle", GOOD)
    body += arrow(620, 197, 670, 156, None, ACCENT, marker="acc")
    body += t(640, 242, L["yours"], 11, "middle", ACCENT)
    return figure("photos", 790, 255, L["cap"], body)


# ── homelab 8: nothing reaches main without a green check ───────────────────
def forge(lang):
    L = {
        "en": labels(cap="Nobody, human or agent, pushes to main. A change arrives as a pull request; the runner picks its job by label and runs the tests; the protected branch accepts the merge only when the required check is green.",
                     who="You or an agent", wsub="works on a branch", pr="Pull request", psub="the proposed change",
                     run="Runner", rsub="label ubuntu-latest", job="Job container", jsub="image with node",
                     main="main", msub="protected", check="required check: green", blocked="direct push refused",
                     picks="picks the job by label"),
        "fr": labels(cap="Personne, humain ou agent, ne pousse sur main. Un changement arrive en pull request ; le runner prend son job selon son label et lance les tests ; la branche protégée n'accepte la fusion que si le contrôle exigé est vert.",
                     who="Vous ou un agent", wsub="travaille sur une branche", pr="Pull request", psub="le changement proposé",
                     run="Runner", rsub="label ubuntu-latest", job="Conteneur du job", jsub="image avec node",
                     main="main", msub="protégée", check="contrôle exigé : vert", blocked="push direct refusé",
                     picks="prend le job selon le label"),
    }[lang]
    body = box(20, 40, 160, 54, L["who"], L["wsub"])
    body += box(250, 40, 160, 54, L["pr"], L["psub"])
    body += box(250, 170, 160, 54, L["run"], L["rsub"])
    body += box(480, 170, 160, 54, L["job"], L["jsub"])
    body += box(560, 40, 160, 54, L["main"], L["msub"], stroke=ACCENT)
    body += arrow(180, 67, 248, 67)
    body += arrow(330, 94, 330, 168, L["picks"], lx=420, ly=158)
    body += arrow(410, 197, 478, 197)
    body += arrow(560, 168, 630, 96, None, GOOD, marker="good")
    body += t(680, 140, L["check"], 11, "middle", GOOD)
    body += arrow(410, 67, 558, 67, None, GOOD, marker="good")
    body += (f'<polyline points="100,94 100,122 600,122 600,98" fill="none" stroke="{BAD}" stroke-width="1.6" '
             f'stroke-dasharray="5 4" marker-end="url(#bad)"/>')
    body += t(170, 138, L["blocked"], 11, "middle", BAD)
    return figure("forge", 760, 245, L["cap"], body)


# ── homelab 9: one search for you and your agents ───────────────────────────
def search(lang):
    L = {
        "en": labels(cap="Your browser and your agents ask the same search engine at home. It asks dozens of engines for you and merges the answers: they see your server, not you. Agents read the JSON format.",
                     you="Your browser", ysub="HTML results", agents="Your agents", asub="JSON results", sx="SearXNG",
                     ssub="at home", engines="Search engines", esub="see your server only", merge="asks, then merges"),
        "fr": labels(cap="Votre navigateur et vos agents interrogent le même moteur à la maison. Il interroge des dizaines de moteurs pour vous et fusionne les réponses : eux voient votre serveur, pas vous. Les agents lisent le format JSON.",
                     you="Votre navigateur", ysub="résultats HTML", agents="Vos agents", asub="résultats JSON", sx="SearXNG",
                     ssub="à la maison", engines="Moteurs de recherche", esub="ne voient que votre serveur", merge="interroge, puis fusionne"),
    }[lang]
    body = box(20, 30, 160, 54, L["you"], L["ysub"])
    body += box(20, 140, 160, 54, L["agents"], L["asub"], stroke=ACCENT)
    body += box(270, 85, 150, 54, L["sx"], L["ssub"], stroke=GOOD)
    body += box(560, 85, 180, 54, L["engines"], L["esub"])
    body += arrow(180, 57, 268, 105)
    body += arrow(180, 167, 268, 120, None, ACCENT, marker="acc")
    body += arrow(420, 112, 558, 112, L["merge"], lx=489, ly=104)
    return figure("search", 760, 210, L["cap"], body)


# ── homelab 10: every machine can tap you on the shoulder ───────────────────
def notify(lang):
    L = {
        "en": labels(cap="Servers, backups and agents publish one line to a topic; your phone subscribes. With anonymous access denied, only accounts you created can publish or read.",
                     src=["Backups", "Agents", "Monitoring"], ntfy="ntfy", nsub="deny-all, accounts", phone="Your phone",
                     psub="ntfy app", pub="curl -d …", sub="subscribes"),
        "fr": labels(cap="Serveurs, sauvegardes et agents publient une ligne sur un sujet ; votre téléphone s'y abonne. Avec l'accès anonyme refusé, seuls les comptes que vous avez créés peuvent publier ou lire.",
                     src=["Sauvegardes", "Agents", "Supervision"], ntfy="ntfy", nsub="deny-all, comptes", phone="Votre téléphone",
                     psub="app ntfy", pub="curl -d …", sub="s'abonne"),
    }[lang]
    body = ""
    for i, name in enumerate(L["src"]):
        y = 20 + i * 64
        body += box(20, y, 150, 48, name, None)
        body += arrow(170, y + 24, 318, 108, L["pub"] if i == 0 else None, lx=236, ly=y + 14)
    body += box(320, 82, 160, 54, L["ntfy"], L["nsub"], stroke=ACCENT)
    body += box(580, 82, 160, 54, L["phone"], L["psub"], stroke=GOOD)
    body += arrow(578, 109, 482, 109, L["sub"], GOOD, marker="good", lx=530, ly=101)
    return figure("notify", 760, 220, L["cap"], body)


# ── giving code work to a local agent ───────────────────────────────────────
def intent(lang):
    L = {
        "en": labels(cap="The agent never touches main. It gets a short, closed request with the real data, works on its own branch in a sandbox, must make a test that runs the code pass, and opens a pull request that a human or a stronger model reads before the merge.",
                     you="Your request", ysub="≤ 4 deliverables, real data", agent="Local agent", asub="own branch, sandbox",
                     tests="Tests", tsub="must execute the code", pr="Pull request", psub="read before merge",
                     main="main", reject="too wide: refused", red="red: back to work"),
        "fr": labels(cap="L'agent ne touche jamais main. Il reçoit une demande courte et fermée avec les vraies données, travaille sur sa branche dans un bac à sable, doit faire passer un test qui exécute le code, et ouvre une pull request qu'un humain ou un modèle plus fort relit avant la fusion.",
                     you="Votre demande", ysub="≤ 4 livrables, vraies données", agent="Agent local", asub="sa branche, bac à sable",
                     tests="Tests", tsub="doivent exécuter le code", pr="Pull request", psub="relue avant fusion",
                     main="main", reject="trop large : refusée", red="rouge : on recommence"),
    }[lang]
    body = box(10, 60, 150, 54, L["you"], L["ysub"])
    body += box(200, 60, 140, 54, L["agent"], L["asub"])
    body += box(380, 60, 140, 54, L["tests"], L["tsub"], stroke=ACCENT)
    body += box(560, 60, 120, 54, L["pr"], L["psub"])
    body += box(700, 60, 60, 54, L["main"], None, stroke=GOOD)
    body += arrow(160, 87, 198, 87)
    body += arrow(340, 87, 378, 87)
    body += arrow(520, 87, 558, 87, None, GOOD, marker="good")
    body += arrow(680, 87, 698, 87, None, GOOD, marker="good")
    body += (f'<polyline points="450,114 450,150 270,150 270,116" fill="none" stroke="{BAD}" stroke-width="1.6" '
             f'stroke-dasharray="5 4" marker-end="url(#bad)"/>')
    body += t(360, 168, L["red"], 11, "middle", BAD)
    body += t(85, 40, L["reject"], 11, "middle", BAD)
    return figure("intent", 770, 185, L["cap"], body)


# ── homelab 11: who talks to whom when you open a document ──────────────────
def office(lang):
    L = {
        "en": labels(cap="Opening a document involves three parties. Your browser gets the file list from Nextcloud but loads the editor from the document server; the document server fetches the file from Nextcloud and saves it back. Every request between them is signed with the same shared secret.",
                     br="Your browser", nc="Nextcloud", ncs="your files", oo="OnlyOffice", oos="document server",
                     files="file list", editor="loads the editor", fetch="fetches, then saves the file", jwt="same JWT secret on both sides"),
        "fr": labels(cap="Ouvrir un document fait parler trois acteurs. Votre navigateur obtient la liste des fichiers de Nextcloud mais charge l'éditeur depuis le serveur de documents ; celui-ci va chercher le fichier chez Nextcloud et l'y enregistre. Chaque requête entre eux est signée avec le même secret partagé.",
                     br="Votre navigateur", nc="Nextcloud", ncs="vos fichiers", oo="OnlyOffice", oos="serveur de documents",
                     files="liste des fichiers", editor="charge l'éditeur", fetch="récupère, puis enregistre le fichier", jwt="même secret JWT des deux côtés"),
    }[lang]
    body = box(300, 20, 160, 54, L["br"], None)
    body += box(60, 170, 170, 54, L["nc"], L["ncs"])
    body += box(530, 170, 170, 54, L["oo"], L["oos"], stroke=ACCENT)
    body += arrow(320, 74, 170, 168, L["files"], lx=200, ly=115)
    body += arrow(440, 74, 590, 168, L["editor"], ACCENT, marker="acc", lx=575, ly=115)
    body += arrow(528, 205, 232, 205, L["fetch"], lx=380, ly=197)
    body += t(380, 240, L["jwt"], 11, "middle", GOOD)
    return figure("office", 760, 255, L["cap"], body)


# ── homelab 12: paper in, searchable archive out ────────────────────────────
def paper(lang):
    L = {
        "en": labels(cap="Anything dropped in the consume folder is read (OCR in your language), converted, tagged and filed. The archive keeps the original and a searchable PDF; the exporter writes everything, files and metadata, for your backup.",
                     src=["Scanner", "Phone photo", "Office files, e-mail"], cons="Consume folder", csub="drop and forget",
                     pl="Paperless-ngx", psub="OCR fra · Tika · Gotenberg", arch="Archive", asub="original + searchable PDF",
                     exp="document_exporter", esub="→ your backup"),
        "fr": labels(cap="Tout ce qui tombe dans le dossier d'entrée est lu (OCR dans votre langue), converti, étiqueté et classé. L'archive garde l'original et un PDF où l'on peut chercher ; l'exportateur écrit tout, fichiers et métadonnées, pour votre sauvegarde.",
                     src=["Scanner", "Photo au téléphone", "Fichiers Office, e-mails"], cons="Dossier d'entrée", csub="on dépose et on oublie",
                     pl="Paperless-ngx", psub="OCR fra · Tika · Gotenberg", arch="Archive", asub="original + PDF consultable",
                     exp="document_exporter", esub="→ votre sauvegarde"),
    }[lang]
    body = ""
    for i, name in enumerate(L["src"]):
        y = 20 + i * 60
        body += box(10, y, 160, 46, name, None)
        body += arrow(170, y + 23, 228, 103)
    body += box(230, 76, 140, 54, L["cons"], L["csub"])
    body += box(410, 76, 170, 54, L["pl"], L["psub"], stroke=ACCENT)
    body += box(610, 40, 150, 54, L["arch"], L["asub"])
    body += box(610, 130, 150, 54, L["exp"], L["esub"], stroke=GOOD)
    body += arrow(370, 103, 408, 103)
    body += arrow(580, 95, 608, 72)
    body += arrow(580, 112, 608, 150, None, GOOD, marker="good")
    return figure("paper", 770, 205, L["cap"], body)


# ── homelab 13: one task list for you and your agents ───────────────────────
def tasks(lang):
    L = {
        "en": labels(cap="One task list, two kinds of users. You work from the web page and the phone; your agents read and write through the API, each with its own token limited to what it needs. A decision only you can take becomes a task waiting for you.",
                     you="You", ysub="web, phone app", vk="Vikunja", vsub="projects, tasks, due dates",
                     ag="Your agents", asub="API token, limited", plan="plan, tick off", file="file tasks, read status",
                     wait="a decision waits for you"),
        "fr": labels(cap="Une liste de tâches, deux sortes d'utilisateurs. Vous travaillez depuis la page web et le téléphone ; vos agents lisent et écrivent par l'API, chacun avec son jeton limité au nécessaire. Une décision que vous seul pouvez prendre devient une tâche qui vous attend.",
                     you="Vous", ysub="web, app du téléphone", vk="Vikunja", vsub="projets, tâches, échéances",
                     ag="Vos agents", asub="jeton d'API, limité", plan="planifier, cocher", file="créer des tâches, lire l'état",
                     wait="une décision vous attend"),
    }[lang]
    body = box(20, 60, 160, 54, L["you"], L["ysub"])
    body += box(300, 60, 170, 54, L["vk"], L["vsub"], stroke=ACCENT)
    body += box(625, 60, 140, 54, L["ag"], L["asub"])
    body += arrow(180, 80, 298, 80, L["plan"], lx=239, ly=72)
    body += arrow(623, 80, 472, 80, L["file"], lx=548, ly=72)
    body += arrow(298, 100, 182, 100, None, ACCENT, marker="acc")
    body += t(240, 128, L["wait"], 11, "middle", ACCENT)
    return figure("tasks", 770, 150, L["cap"], body)


# ── homelab 14: the decision cascade ────────────────────────────────────────
def cascade(lang):
    L = {
        "en": labels(cap="Each decision goes down the cheapest path that can settle it. Fixed rules first; if they cannot, a small local model; a hosted model only for public data; private and ambiguous goes to you, and nothing leaves home.",
                     ev="An event", esub="webhook, schedule", rules="Rules", rsub="deterministic", local="Local judge",
                     lsub="small model, CPU", hosted="Hosted model", hsub="public data only", you="Ask you",
                     ysub="task + notification", act="Act", unclear="not settled", unsure="unsure", public="public",
                     private="private", sure="settled by the rules"),
        "fr": labels(cap="Chaque décision prend le chemin le moins cher qui puisse la trancher. Les règles fixes d'abord ; si elles ne peuvent pas, un petit modèle local ; un modèle hébergé seulement pour les données publiques ; privé et ambigu vient à vous, et rien ne sort de la maison.",
                     ev="Un événement", esub="webhook, planning", rules="Règles", rsub="déterministes", local="Juge local",
                     lsub="petit modèle, CPU", hosted="Modèle hébergé", hsub="données publiques seulement", you="On vous demande",
                     ysub="tâche + notification", act="Agir", unclear="pas tranché", unsure="incertain", public="public",
                     private="privé", sure="tranché par les règles"),
    }[lang]
    body = box(10, 30, 130, 54, L["ev"], L["esub"])
    body += box(180, 30, 130, 54, L["rules"], L["rsub"])
    body += box(350, 30, 140, 54, L["local"], L["lsub"])
    body += box(530, 30, 110, 54, L["act"], None, stroke=GOOD)
    body += box(335, 160, 170, 54, L["hosted"], L["hsub"])
    body += box(530, 160, 140, 54, L["you"], L["ysub"], stroke=ACCENT)
    body += arrow(140, 57, 178, 57)
    body += arrow(310, 57, 348, 57)
    body += arrow(490, 57, 528, 57, None, GOOD, marker="good")
    body += (f'<polyline points="245,30 245,12 585,12 585,28" fill="none" stroke="{GOOD}" stroke-width="1.6" marker-end="url(#good)"/>')
    body += t(415, 8, L["sure"], 11, "middle", GOOD)
    body += arrow(420, 84, 420, 158, L["unsure"] + " · " + L["public"], lx=470, ly=125)
    body += (f'<polyline points="470,84 470,100 600,100 600,158" fill="none" stroke="{ACCENT}" stroke-width="1.6" marker-end="url(#acc)"/>')
    body += t(620, 128, L["unsure"] + " · " + L["private"], 11, "start", ACCENT)
    body += arrow(505, 175, 560, 86, None, GOOD, marker="good")
    return figure("cascade", 760, 230, L["cap"], body)


# ── homelab 15: a voice that never leaves the house ─────────────────────────
def voice(lang):
    L = {
        "en": labels(cap="Home Assistant hears, thinks and answers without the cloud. Speech goes through one relay: the GPU pair answers when the card is free, the CPU pair when a game or a model holds it. Slower, never mute.",
                     ha="Home Assistant", hsub="Assist pipeline", relay="Voice relay", rsub="one address",
                     gpu="GPU pair", gsub="Whisper turbo + Kyutai TTS", cpu="CPU fallback", csub="Whisper small + Piper",
                     llm="Local model", lsub="OpenAI-compatible", wy="Wyoming: speech in, speech out", txt="text",
                     free="card free", busy="card busy"),
        "fr": labels(cap="Home Assistant entend, réfléchit et répond sans le cloud. La parole passe par un seul relais : le duo GPU répond quand la carte est libre, le duo CPU quand un jeu ou un modèle la tient. Plus lent, jamais muet.",
                     ha="Home Assistant", hsub="pipeline Assist", relay="Relais vocal", rsub="une seule adresse",
                     gpu="Duo GPU", gsub="Whisper turbo + TTS Kyutai", cpu="Repli CPU", csub="Whisper small + Piper",
                     llm="Modèle local", lsub="compatible OpenAI", wy="Wyoming : parole entrante, parole sortante", txt="texte",
                     free="carte libre", busy="carte prise"),
    }[lang]
    body = box(20, 90, 160, 54, L["ha"], L["hsub"], stroke=ACCENT)
    body += box(280, 90, 150, 54, L["relay"], L["rsub"])
    body += box(530, 30, 210, 54, L["gpu"], L["gsub"], stroke=GOOD)
    body += box(530, 150, 210, 54, L["cpu"], L["csub"])
    body += box(20, 220, 160, 50, L["llm"], L["lsub"])
    body += arrow(180, 117, 278, 117, None)
    body += t(229, 109, "Wyoming", 11, "middle", MUTED)
    body += arrow(430, 105, 528, 62, L["free"], GOOD, marker="good", lx=470, ly=72)
    body += arrow(430, 130, 528, 172, L["busy"], MUTED, marker="a", lx=470, ly=168)
    body += arrow(100, 144, 100, 218, L["txt"], lx=125, ly=185)
    return figure("voice", 760, 285, L["cap"], body)


# ── n8n 1: where the data goes ──────────────────────────────────────────────
def saas(lang):
    L = {
        "en": labels(cap="With a hosted automation service, every run carries your data through someone else's cloud, and each step is billed. Self-hosted, the runs stay home, call your local models, and cost nothing per execution.",
                     a="Hosted service", b="Self-hosted n8n", you="Your services", vendor="Vendor's cloud",
                     vsub="billed per task or operation", n8n="n8n at home", nsub="no per-run cost", models="Local models",
                     data="your data, every run", stays="stays home", home="your home", net="internet"),
        "fr": labels(cap="Avec un service d'automatisation hébergé, chaque exécution fait passer vos données par le cloud d'un autre, et chaque étape est facturée. Auto-hébergé, les exécutions restent à la maison, appellent vos modèles locaux, et ne coûtent rien à l'exécution.",
                     a="Service hébergé", b="n8n auto-hébergé", you="Vos services", vendor="Cloud du fournisseur",
                     vsub="facturé à la tâche ou à l'opération", n8n="n8n à la maison", nsub="aucun coût à l'exécution", models="Modèles locaux",
                     data="vos données, à chaque exécution", stays="reste à la maison", home="chez vous", net="Internet"),
    }[lang]
    body = ""
    for row, title in ((0, L["a"]), (1, L["b"])):
        y = 30 + row * 125
        body += t(20, y, title, 13, "start", ACCENT if row else "currentColor", 700)
        body += f'<line x1="400" y1="{y - 12}" x2="400" y2="{y + 90}" stroke="{LINE}" stroke-width="2" stroke-dasharray="6 5"/>'
        body += t(210, y, L["home"], 11, "middle", MUTED) + t(580, y, L["net"], 11, "middle", MUTED)
        body += box(20, y + 18, 150, 54, L["you"], None)
        if row == 0:
            body += box(520, y + 18, 220, 54, L["vendor"], L["vsub"])
            body += arrow(170, y + 45, 518, y + 45, L["data"], BAD, marker="bad", lx=345, ly=y + 37)
        else:
            body += box(220, y + 18, 150, 54, L["n8n"], L["nsub"], stroke=ACCENT)
            body += box(220, y + 92, 150, 40, L["models"], None)
            body += arrow(170, y + 45, 218, y + 45)
            body += arrow(295, y + 72, 295, y + 90, None, GOOD, marker="good")
            body += t(560, y + 50, L["stays"], 12, "middle", GOOD)
    return figure("saas", 760, 290, L["cap"], body)


# ── n8n 2: the agentic clock ────────────────────────────────────────────────
def clock(lang):
    L = {
        "en": labels(cap="Every job declares its cadence in a registry. Once a minute the tick compares each job's last sign of life with its period plus slack, and writes an event. A watchdog on another machine checks that the tick itself is alive.",
                     reg="Registry", rsub="job, period, slack, severity", tick="Tick", tsub="every minute",
                     ev="Events table", esub="info · warning · critical", al="Alerts", asub="critical → phone",
                     dog="Watchdog", dsub="other machine, every 2 min", jobs="Your workflows", jsub="their signs of life",
                     age="age of the last tick"),
        "fr": labels(cap="Chaque tâche déclare sa cadence dans un registre. Une fois par minute, le tick compare le dernier signe de vie de chaque tâche à sa période plus sa marge, et écrit un événement. Un chien de garde sur une autre machine vérifie que le tick lui-même est vivant.",
                     reg="Registre", rsub="tâche, période, marge, gravité", tick="Tick", tsub="chaque minute",
                     ev="Table des événements", esub="info · warning · critical", al="Alertes", asub="critical → téléphone",
                     dog="Chien de garde", dsub="autre machine, toutes les 2 min", jobs="Vos workflows", jsub="leurs signes de vie",
                     age="âge du dernier tick"),
    }[lang]
    body = box(20, 20, 180, 54, L["reg"], L["rsub"])
    body += box(20, 120, 180, 54, L["jobs"], L["jsub"])
    body += box(280, 70, 140, 54, L["tick"], L["tsub"], stroke=ACCENT)
    body += box(500, 70, 170, 54, L["ev"], L["esub"])
    body += box(500, 170, 170, 54, L["al"], L["asub"], stroke=BAD)
    body += box(265, 190, 190, 54, L["dog"], L["dsub"], stroke=GOOD)
    body += arrow(200, 47, 278, 88)
    body += arrow(200, 147, 278, 108)
    body += arrow(420, 97, 498, 97)
    body += arrow(585, 124, 585, 168, None, BAD, marker="bad")
    body += arrow(350, 188, 350, 126, None, GOOD, dash=True, marker="good")
    body += t(358, 160, L["age"], 11, "start", GOOD)
    body += arrow(455, 217, 498, 200, None, GOOD, marker="good")
    return figure("clock", 760, 260, L["cap"], body)


# ── n8n 3: route with guardrails ────────────────────────────────────────────
def route(lang):
    L = {
        "en": labels(cap="A request in plain words becomes an action only through checks. The signature proves who sent it, the judge classifies it (private by default), fixed rules decide, the result is verified, one retry after 25 seconds, and every outcome is written down.",
                     hook="Signed webhook", hsub="HMAC checked", judge="Judge", jsub="classifies, private by default",
                     rules="Rules", rsub="what is allowed", act="Act", asub="then verify", retry="one retry, +25 s",
                     ev="Event", esub="ok · failed", no="refused: bad signature"),
        "fr": labels(cap="Une demande en mots simples ne devient une action qu'à travers des contrôles. La signature prouve qui l'envoie, le juge la classe (privée par défaut), des règles fixes décident, le résultat est vérifié, une seule reprise après 25 secondes, et chaque issue est consignée.",
                     hook="Webhook signé", hsub="HMAC vérifié", judge="Juge", jsub="classe, privé par défaut",
                     rules="Règles", rsub="ce qui est permis", act="Agir", asub="puis vérifier", retry="une reprise, +25 s",
                     ev="Événement", esub="ok · failed", no="refusé : mauvaise signature"),
    }[lang]
    body = box(10, 40, 130, 54, L["hook"], L["hsub"], stroke=ACCENT)
    body += box(170, 40, 150, 54, L["judge"], L["jsub"])
    body += box(350, 40, 120, 54, L["rules"], L["rsub"])
    body += box(500, 40, 110, 54, L["act"], L["asub"])
    body += box(640, 40, 110, 54, L["ev"], L["esub"], stroke=GOOD)
    for x1, x2 in ((140, 168), (320, 348), (470, 498), (610, 638)):
        body += arrow(x1, 67, x2, 67)
    body += (f'<polyline points="555,94 555,130 520,130 520,96" fill="none" stroke="{ACCENT}" stroke-width="1.6" marker-end="url(#acc)"/>')
    body += t(560, 146, L["retry"], 11, "middle", ACCENT)
    body += arrow(75, 94, 75, 128, None, BAD, marker="bad")
    body += t(75, 146, L["no"], 11, "middle", BAD)
    return figure("route", 760, 160, L["cap"], body)


# ── one gateway, names that do not lie ──────────────────────────────────────
def gateway(lang):
    L = {
        "en": labels(cap="Every client knows one address. The gateway's list of models is generated from what the cards actually serve, and each name says exactly which weights answer: no alias, no silent fallback to another model.",
                     clients=["Agents", "Apps, phone", "Home Assistant"], gw="Gateway", gsub="one address, private network",
                     gen="generated from the served models", m=["9B · card 0", "27B · card 1", "3B · CPU"], down="not loaded: fails, never substitutes"),
        "fr": labels(cap="Chaque client connaît une seule adresse. La liste des modèles de la passerelle est générée à partir de ce que les cartes servent vraiment, et chaque nom dit exactement quels poids répondent : pas d'alias, pas de repli silencieux vers un autre modèle.",
                     clients=["Agents", "Apps, téléphone", "Home Assistant"], gw="Passerelle", gsub="une adresse, réseau privé",
                     gen="générée depuis les modèles servis", m=["9B · carte 0", "27B · carte 1", "3B · CPU"], down="non chargé : échoue, ne remplace jamais"),
    }[lang]
    body = ""
    for i, c in enumerate(L["clients"]):
        y = 20 + i * 62
        body += box(10, y, 150, 46, c, None)
        body += arrow(160, y + 23, 278, 103)
    body += box(280, 76, 160, 54, L["gw"], L["gsub"], stroke=ACCENT)
    for i, m in enumerate(L["m"]):
        y = 20 + i * 62
        body += box(560, y, 170, 46, m, None, stroke=GOOD if i < 2 else LINE)
        body += arrow(440, 103, 558, y + 23)
    body += t(360, 160, L["gen"], 11, "middle", ACCENT)
    body += t(645, 206, L["down"], 11, "middle", MUTED)
    return figure("gateway", 760, 220, L["cap"], body)


# ── the grid: models × cards ────────────────────────────────────────────────
def grid(lang):
    L = {
        "en": labels(cap="Each model exists once per place it can run: card 0, card 1, or both cards together. One cell is one container, created once. Swapping is stopping one cell and starting another; a game simply takes card 0 and gives it back.",
                     cols=["card 0", "card 1", "both cards"], rows=["9B", "14B coder", "27B", "177B"],
                     declared="serving", game="free-c0: card 0 for a game", cost="swap: 0.5–0.75 s per GB loaded"),
        "fr": labels(cap="Chaque modèle existe une fois par endroit où il peut tourner : carte 0, carte 1, ou les deux cartes ensemble. Une case est un conteneur, créé une fois. Basculer, c'est arrêter une case et en démarrer une autre ; un jeu prend simplement la carte 0 et la rend.",
                     cols=["carte 0", "carte 1", "les deux cartes"], rows=["9B", "14B coder", "27B", "177B"],
                     declared="en service", game="free-c0 : la carte 0 pour un jeu", cost="bascule : 0,5–0,75 s par Go chargé"),
    }[lang]
    x0, y0, cw, rh = 150, 40, 150, 44
    body = ""
    for j, c in enumerate(L["cols"]):
        body += t(x0 + j * cw + cw / 2, y0 - 12, c, 12, "middle", MUTED, 600)
    on = {(0, 0), (2, 1)}
    absent = {(3, 1)}
    for i, r in enumerate(L["rows"]):
        y = y0 + i * rh
        body += t(x0 - 14, y + 26, r, 13, "end", weight=600)
        for j in range(3):
            x = x0 + j * cw
            if (i, j) in absent:
                continue
            serving = (i, j) in on
            fill = "#2a3a30" if serving else PANEL
            stroke = GOOD if serving else LINE
            body += f'<rect x="{x + 6}" y="{y + 6}" width="{cw - 12}" height="{rh - 10}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
            if serving:
                body += t(x + cw / 2, y + 27, L["declared"], 11, "middle", GOOD, 600)
    body += t(x0, y0 + 4 * rh + 24, L["game"], 11, "start", ACCENT)
    body += t(x0, y0 + 4 * rh + 42, L["cost"], 11, "start", MUTED)
    return figure("grid", 640, 275, L["cap"], body)


# ── snapshots: undo any change ──────────────────────────────────────────────
def snapshots(lang):
    L = {
        "en": labels(cap="A snapshot is a photo of a folder at an instant, taken in a second and costing only what changes afterwards. Take one before touching anything; if the change goes wrong, bring the file back from the photo.",
                     tl="every hour, kept 7 days + 2 weeks", before="before the change", change="your change", oops="it breaks",
                     undo="undochange: the file comes back", now="now"),
        "fr": labels(cap="Un instantané est une photo d'un dossier à un instant, prise en une seconde et qui ne coûte que ce qui change ensuite. Prenez-en une avant de toucher à quoi que ce soit ; si le changement tourne mal, faites revenir le fichier depuis la photo.",
                     tl="chaque heure, gardés 7 jours + 2 semaines", before="avant le changement", change="votre changement", oops="ça casse",
                     undo="undochange : le fichier revient", now="maintenant"),
    }[lang]
    body = f'<line x1="30" y1="90" x2="720" y2="90" stroke="{LINE}" stroke-width="3"/>'
    for x in (60, 130, 200, 270):
        body += f'<circle cx="{x}" cy="90" r="7" fill="{MUTED}"/>'
    body += t(165, 70, L["tl"], 11, "middle", MUTED)
    body += f'<circle cx="400" cy="90" r="10" fill="{ACCENT}"/>' + t(400, 66, L["before"], 12, "middle", ACCENT, 600)
    body += f'<rect x="450" y="80" width="90" height="20" rx="4" fill="{PANEL}" stroke="{LINE}"/>' + t(495, 120, L["change"], 11, "middle")
    body += f'<circle cx="610" cy="90" r="8" fill="{BAD}"/>' + t(610, 70, L["oops"], 12, "middle", BAD, 600)
    body += t(700, 120, L["now"], 11, "middle", MUTED)
    body += f'<path d="M610,104 C600,170 420,170 404,104" fill="none" stroke="{GOOD}" stroke-width="1.8" marker-end="url(#good)"/>'
    body += t(505, 182, L["undo"], 12, "middle", GOOD, 600)
    return figure("snapshots", 750, 200, L["cap"], body)


# ── homelab 16: keep what you read ──────────────────────────────────────────
def keep(lang):
    L = {
        "en": labels(cap="Save a page from the browser or the phone. Karakeep archives the whole page, a small local model tags and summarises it, and a webhook hands it to your knowledge base, where your agents can search it a minute later.",
                     src="Browser, phone", ssub="share → save", kk="Karakeep", ksub="full archive", ai="Local model",
                     asub="tags + summary", hook="Webhook", hsub="token in a header", kb="Your knowledge base", kbs="searchable by agents"),
        "fr": labels(cap="Gardez une page depuis le navigateur ou le téléphone. Karakeep archive la page entière, un petit modèle local l'étiquette et la résume, et un webhook la passe à votre base de connaissance, où vos agents peuvent la chercher une minute plus tard.",
                     src="Navigateur, téléphone", ssub="partager → garder", kk="Karakeep", ksub="archive complète", ai="Modèle local",
                     asub="étiquettes + résumé", hook="Webhook", hsub="jeton dans un en-tête", kb="Votre base de connaissance", kbs="interrogeable par les agents"),
    }[lang]
    body = box(10, 40, 150, 54, L["src"], L["ssub"])
    body += box(200, 40, 140, 54, L["kk"], L["ksub"], stroke=ACCENT)
    body += box(200, 150, 140, 54, L["ai"], L["asub"])
    body += box(390, 40, 140, 54, L["hook"], L["hsub"])
    body += box(570, 40, 205, 54, L["kb"], L["kbs"], stroke=GOOD)
    body += arrow(160, 67, 198, 67)
    body += arrow(270, 94, 270, 148)
    body += arrow(300, 148, 300, 96)
    body += arrow(340, 67, 388, 67)
    body += arrow(530, 67, 568, 67, None, GOOD, marker="good")
    return figure("keep", 785, 220, L["cap"], body)


# ── rotating passwords: vault first, then the service ───────────────────────
def rotation(lang):
    L = {
        "en": labels(cap="The order that never locks you out: the new password is stored in the vault before it is applied. If the vault write fails, nothing changed. If the service change fails, the vault keeps the old value in its history.",
                     steps=[("Generate", "long, random"), ("Store in vault", "first!"), ("Apply", "on the service"), ("Prove", "a real login")],
                     f1="fails → nothing changed", f2="fails → old value in history"),
        "fr": labels(cap="L'ordre qui ne vous enferme jamais dehors : le nouveau mot de passe est rangé dans le coffre avant d'être appliqué. Si l'écriture au coffre échoue, rien n'a changé. Si le changement sur le service échoue, le coffre garde l'ancienne valeur dans son historique.",
                     steps=[("Générer", "long, aléatoire"), ("Ranger au coffre", "d'abord !"), ("Appliquer", "sur le service"), ("Prouver", "une vraie connexion")],
                     f1="échoue → rien n'a changé", f2="échoue → ancienne valeur dans l'historique"),
    }[lang]
    body = ""
    for i, (a, b) in enumerate(L["steps"]):
        x = 10 + i * 190
        body += box(x, 40, 160, 54, a, b, stroke=ACCENT if i == 1 else (GOOD if i == 3 else LINE))
        if i:
            body += arrow(x - 30, 67, x - 2, 67)
    body += t(280, 120, L["f1"], 11, "middle", GOOD)
    body += t(470, 136, L["f2"], 11, "middle", GOOD)
    return figure("rotation", 760, 150, L["cap"], body)


DIAGRAMS = {"hardware": hardware, "docker": docker_stack, "request": request_path,
            "kv": kv_trap, "hybrid": hybrid, "proxmox": proxmox,
            "proxy": proxy, "vault": vault,
            "gpu": gpu_split, "stream": stream, "wake": wake,
            "dns": dns, "backups": backups,
            "remote": remote, "photos": photos,
            "forge": forge, "search": search, "notify": notify,
            "intent": intent, "office": office,
            "paper": paper, "tasks": tasks,
            "cascade": cascade, "voice": voice,
            "saas": saas, "clock": clock, "route": route,
            "gateway": gateway, "grid": grid, "snapshots": snapshots, "keep": keep,
            "rotation": rotation}


def render(name, lang):
    return DIAGRAMS[name](lang)
