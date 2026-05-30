#!/usr/bin/env python3
"""
Générateur du site de veille — version 2.

Cette version intègre le cadre conceptuel du cours (M2 IPN) :
  - structure par types de veille (cf. typologie présentée en cours),
  - mise en visibilité des concepts du glossaire mobilisés,
  - rubrique « pour poursuivre » (activités, sondage, débat),
  - pages Méthode et À propos pour la dimension réflexive.

Architecture des fichiers de contenu :
  content/
    veille-courante.md          ← écrit chaque lundi par Cowork
    methode.md                  ← page méthodologique (statique, éditable)
    apropos.md                  ← page de positionnement (statique, éditable)
    archives/*.md               ← veilles précédentes

Structure attendue d'une veille hebdomadaire :
  ---
  date: 2026-05-25
  semaine: 22
  titre: Veille du 25 mai 2026
  edito: Phrase d'introduction de la semaine (facultatif).
  ---

  ## Veille institutionnelle
  - [Titre](url) — description

  ## Veille scientifique et technologique
  - ...

  ## Veille réglementaire, normative, juridique
  ## Veille image, e-réputation
  ## Veille commerciale, financière, marketing
  ## Veille sectorielle, stratégique, environnementale

  ## Concepts du glossaire mobilisés
  - **Concept** — comment il apparaît dans l'actualité de la semaine.

  ## Pistes pour poursuivre
  - Question pour le groupe, sondage, lecture approfondie...
"""

import os
import re
import shutil
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
DIST = ROOT / "dist"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"

SITE_TITLE = "Veille en sciences de l'éducation et de la formation"
SITE_SUBTITLE = "Synthèse hebdomadaire — M2 Ingénierie pédagogique et numérique"
SITE_URL = os.environ.get("SITE_URL", "")
GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY", "")  # ex: "pseudo/depot"

# Typologie issue du cours (slide « Les types de veille »).
# Chaque type a : un slug, un libellé canonique, une couleur d'accent.
TYPOLOGIE = [
    {
        "slug": "institutionnelle",
        "label": "Veille institutionnelle",
        "color": "#d27340",
        "match": ["institutionnel", "institution"],
        "desc": "Sources émanant des institutions publiques, ministères, académies, rectorats.",
    },
    {
        "slug": "scientifique",
        "label": "Veille scientifique et technologique",
        "color": "#6c6c6c",
        "match": ["scientifique", "technologique", "recherche"],
        "desc": "Surveillance des champs scientifiques et technologiques : recherche, innovations, technologies émergentes.",
    },
    {
        "slug": "reglementaire",
        "label": "Veille réglementaire, normative, juridique",
        "color": "#c79a1e",
        "match": ["réglementaire", "reglementaire", "normative", "juridique", "loi", "droit"],
        "desc": "Surveillance des évolutions législatives et réglementaires, des normes en vigueur.",
    },
    {
        "slug": "e-reputation",
        "label": "Veille image, e-réputation",
        "color": "#4a7ba6",
        "match": ["réputation", "reputation", "image", "médiatique", "mediatique"],
        "desc": "Évaluation de l'image et du discours médiatique sur les acteurs et les pratiques.",
    },
    {
        "slug": "commerciale",
        "label": "Veille commerciale, financière, marketing",
        "color": "#6f8e4d",
        "match": ["commercial", "financière", "financiere", "marketing", "concurrence", "edtech"],
        "desc": "Surveillance des évolutions du marché de la formation et des stratégies des acteurs.",
    },
    {
        "slug": "sectorielle",
        "label": "Veille sectorielle, stratégique, environnementale",
        "color": "#2c4f6d",
        "match": ["sectoriel", "stratégique", "strategique", "environnementale", "sociétale", "societale"],
        "desc": "Évolutions macro du champ : facteurs culturels, politiques, sociaux, historiques.",
    },
]

SPECIAL_SECTIONS = [
    {"slug": "edito", "label": "Édito", "match": ["édito", "edito", "editorial", "en bref"]},
    {"slug": "glossaire", "label": "Concepts du glossaire mobilisés", "match": ["glossaire", "concept", "notion"]},
    {"slug": "poursuivre", "label": "Pistes pour poursuivre", "match": ["poursuivre", "piste", "activité", "activite", "pour aller", "à faire", "a faire"]},
]


# ──────────────────────────────────────────────────────────
# Utilitaires
# ──────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    """Minuscules, sans accents, sans ponctuation."""
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text


def slugify(text: str) -> str:
    text = normalize(text)
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text


def format_french_date(date_value) -> str:
    if isinstance(date_value, str):
        date_value = datetime.fromisoformat(date_value).date()
    mois = ["janvier", "février", "mars", "avril", "mai", "juin",
            "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    return f"{date_value.day} {mois[date_value.month - 1]} {date_value.year}"


def classify_section(title: str):
    """Retourne (kind, type_info) pour une section H2 donnée."""
    norm = normalize(title)
    # Sections spéciales en priorité
    for special in SPECIAL_SECTIONS:
        for m in special["match"]:
            if normalize(m) in norm:
                return special["slug"], special
    # Sinon, type de veille du cours
    for t in TYPOLOGIE:
        for m in t["match"]:
            if normalize(m) in norm:
                return "type", t
    return "autre", {"slug": slugify(title), "label": title}


def count_items(content: str) -> int:
    """Compte les items (- ou 1.) au premier niveau d'une section markdown."""
    n = 0
    for line in content.split("\n"):
        if re.match(r"^[-*]\s", line) or re.match(r"^\d+\.\s", line):
            n += 1
    return n


def parse_markdown_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    meta = {}
    body = text
    if text.startswith("---"):
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
        if match:
            meta = yaml.safe_load(match.group(1)) or {}
            body = match.group(2)
    return {"meta": meta, "body": body, "path": path}


def split_into_sections(body: str):
    """Découpe le corps en sections par H2."""
    parts = re.split(r"(?=^##\s)", body, flags=re.MULTILINE)
    sections = []
    # Préambule éventuel avant la première H2 = édito implicite
    if parts and not parts[0].lstrip().startswith("##"):
        intro = parts[0].strip()
        if intro:
            sections.append({"kind": "edito", "info": {"slug": "edito", "label": "Édito"},
                             "title": "", "content": intro, "item_count": 0})
        parts = parts[1:]
    for part in parts:
        m = re.match(r"^##\s+(.+?)(?:\n(.*))?$", part, re.DOTALL)
        if not m:
            continue
        title = m.group(1).strip()
        content = (m.group(2) or "").strip()
        kind, info = classify_section(title)
        sections.append({
            "kind": kind, "info": info, "title": title, "content": content,
            "item_count": count_items(content),
        })
    return sections


def md_to_html(text: str) -> str:
    return markdown.markdown(text, extensions=["extra", "sane_lists", "smarty"])


def render_template(name: str, **ctx) -> str:
    tpl = (TEMPLATES / name).read_text(encoding="utf-8")
    for k, v in ctx.items():
        tpl = tpl.replace("{{ " + k + " }}", str(v))
    return tpl


# ──────────────────────────────────────────────────────────
# Rendu d'une veille (page courante ou archive)
# ──────────────────────────────────────────────────────────

def render_typology_dashboard(sections) -> str:
    """Petit tableau de bord des types de veille présents cette semaine."""
    counts = {t["slug"]: 0 for t in TYPOLOGIE}
    total = 0
    for s in sections:
        if s["kind"] == "type":
            counts[s["info"]["slug"]] = s["item_count"]
            total += s["item_count"]
    if total == 0:
        return ""

    chips = []
    for t in TYPOLOGIE:
        n = counts[t["slug"]]
        if n == 0:
            continue
        chips.append(
            f'<a class="chip" href="#section-{t["slug"]}" style="--c:{t["color"]}">'
            f'<span class="chip-dot"></span>'
            f'<span class="chip-n">{n}</span>'
            f'<span class="chip-label">{t["label"].replace("Veille ", "")}</span>'
            f'</a>'
        )
    chips_html = "".join(chips)
    return f"""
    <div class="dashboard">
      <p class="dashboard-title">Répartition de la semaine — <span class="dashboard-total">{total} ressources</span></p>
      <div class="dashboard-chips">{chips_html}</div>
    </div>"""


def render_sections(sections) -> str:
    """Rend toutes les sections d'une veille."""
    out = []
    for s in sections:
        if s["kind"] == "edito":
            html = md_to_html(s["content"])
            out.append(f'<section class="edito"><div class="prose edito-prose">{html}</div></section>')

        elif s["kind"] == "type":
            t = s["info"]
            html = md_to_html(s["content"]) if s["content"] else "<p class='muted'>Pas de ressource cette semaine pour ce type.</p>"
            out.append(f"""
            <section class="vtype" id="section-{t['slug']}" style="--c:{t['color']}">
              <header class="vtype-header">
                <span class="vtype-marker"></span>
                <h2 class="vtype-title">{t['label']}</h2>
                <p class="vtype-desc">{t['desc']}</p>
              </header>
              <div class="prose">{html}</div>
            </section>""")

        elif s["kind"] == "glossaire":
            html = md_to_html(s["content"])
            out.append(f"""
            <section class="reflexive glossaire" id="section-glossaire">
              <header class="reflexive-header">
                <p class="reflexive-kicker">Cadre conceptuel</p>
                <h2 class="reflexive-title">Concepts du glossaire mobilisés cette semaine</h2>
              </header>
              <div class="prose">{html}</div>
            </section>""")

        elif s["kind"] == "poursuivre":
            html = md_to_html(s["content"])
            out.append(f"""
            <section class="reflexive poursuivre" id="section-poursuivre">
              <header class="reflexive-header">
                <p class="reflexive-kicker">Mise en activité</p>
                <h2 class="reflexive-title">Pistes pour poursuivre la veille</h2>
              </header>
              <div class="prose">{html}</div>
            </section>""")

        else:
            # Type non reconnu : on rend sans badge
            html = md_to_html(s["content"])
            out.append(f"<section class='vtype vtype--other'><h2>{s['title']}</h2><div class='prose'>{html}</div></section>")

    return "\n".join(out)


def build_navigation(active: str = "") -> str:
    items = [
        ("", "Veille courante", "index.html"),
        ("methode", "Méthode", "methode.html"),
        ("apropos", "À propos", "apropos.html"),
        ("archives", "Archives", "archives/"),
    ]
    links = []
    for slug, label, href in items:
        cls = "active" if slug == active else ""
        links.append(f'<a class="{cls}" href="{href}">{label}</a>')
    links.append('<a class="rss" href="feed.xml">RSS</a>')
    if GITHUB_REPO:
        links.append(f'<a class="contrib" href="https://github.com/{GITHUB_REPO}/issues/new?template=proposer-une-ressource.yml">＋ Contribuer</a>')
    return "<nav class='topnav'>" + "".join(links) + "</nav>"


def build_navigation_subpage(active: str = "") -> str:
    """Navigation pour les pages internes (chemins relatifs corrects)."""
    items = [
        ("", "Veille courante", "index.html"),
        ("methode", "Méthode", "methode.html"),
        ("apropos", "À propos", "apropos.html"),
        ("archives", "Archives", "archives/"),
    ]
    links = []
    for slug, label, href in items:
        cls = "active" if slug == active else ""
        links.append(f'<a class="{cls}" href="{href}">{label}</a>')
    links.append('<a class="rss" href="feed.xml">RSS</a>')
    if GITHUB_REPO:
        links.append(f'<a class="contrib" href="https://github.com/{GITHUB_REPO}/issues/new?template=proposer-une-ressource.yml">＋ Contribuer</a>')
    return "<nav class='topnav'>" + "".join(links) + "</nav>"


# ──────────────────────────────────────────────────────────
# Build complet
# ──────────────────────────────────────────────────────────

def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    (DIST / "archives").mkdir()
    if STATIC.exists():
        shutil.copytree(STATIC, DIST / "static")

    last_build = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")

    # 1. Veille courante
    current_path = CONTENT / "veille-courante.md"
    if current_path.exists():
        current = parse_markdown_file(current_path)
    else:
        current = {"meta": {"titre": "En attente de la prochaine veille",
                            "date": datetime.now().date().isoformat()},
                   "body": "La prochaine veille sera publiée lundi matin.",
                   "path": current_path}

    sections = split_into_sections(current["body"])
    dashboard = render_typology_dashboard(sections)
    sections_html = render_sections(sections)

    # 2. Archives (chargement)
    archives = []
    for path in sorted((CONTENT / "archives").glob("*.md"), reverse=True):
        archives.append(parse_markdown_file(path))

    archives_short = ""
    if archives:
        items = []
        for a in archives[:6]:
            a_date = a["meta"].get("date", "")
            a_titre = a["meta"].get("titre", a["path"].stem)
            a_slug = slugify(a["path"].stem)
            items.append(
                f'<li><a href="archives/{a_slug}.html">'
                f'<time>{format_french_date(a_date)}</time>'
                f'<span>{a_titre}</span></a></li>'
            )
        archives_short = "<ul class='archive-list'>" + "".join(items) + "</ul>"
    else:
        archives_short = "<p class='muted'>Les semaines à venir alimenteront cette section.</p>"

    # 3. Index.html (page courante)
    current_meta = current["meta"]
    index_html = render_template(
        "index.html",
        site_title=SITE_TITLE,
        site_subtitle=SITE_SUBTITLE,
        navigation=build_navigation(""),
        current_titre=current_meta.get("titre", "Veille de la semaine"),
        current_date=format_french_date(current_meta.get("date", datetime.now().date().isoformat())),
        semaine=current_meta.get("semaine", ""),
        dashboard=dashboard,
        sections=sections_html,
        archives_short=archives_short,
        archive_count=len(archives),
        last_build=last_build,
    )
    (DIST / "index.html").write_text(index_html, encoding="utf-8")

    # 4. Pages d'archive
    for a in archives:
        a_sections = split_into_sections(a["body"])
        a_dashboard = render_typology_dashboard(a_sections)
        a_html_sections = render_sections(a_sections)
        a_slug = slugify(a["path"].stem)
        archive_html = render_template(
            "archive.html",
            site_title=SITE_TITLE,
            navigation=build_navigation_subpage("archives").replace('href="index.html"', 'href="../index.html"')
                                                           .replace('href="methode.html"', 'href="../methode.html"')
                                                           .replace('href="apropos.html"', 'href="../apropos.html"')
                                                           .replace('href="archives/"', 'href="./"')
                                                           .replace('href="feed.xml"', 'href="../feed.xml"'),
            titre=a["meta"].get("titre", a["path"].stem),
            date=format_french_date(a["meta"].get("date", "")),
            dashboard=a_dashboard,
            sections=a_html_sections,
            last_build=last_build,
        )
        (DIST / "archives" / f"{a_slug}.html").write_text(archive_html, encoding="utf-8")

    # 5. Index des archives
    all_items = []
    for a in archives:
        a_date = a["meta"].get("date", "")
        a_titre = a["meta"].get("titre", a["path"].stem)
        a_slug = slugify(a["path"].stem)
        a_sections = split_into_sections(a["body"])
        n_total = sum(s["item_count"] for s in a_sections if s["kind"] == "type")
        all_items.append(
            f'<li><a href="{a_slug}.html">'
            f'<time>{format_french_date(a_date)}</time>'
            f'<span>{a_titre}</span>'
            f'<em class="count">{n_total} ressources</em></a></li>'
        )
    archives_index_html = render_template(
        "archives-index.html",
        site_title=SITE_TITLE,
        navigation=build_navigation_subpage("archives").replace('href="index.html"', 'href="../index.html"')
                                                       .replace('href="methode.html"', 'href="../methode.html"')
                                                       .replace('href="apropos.html"', 'href="../apropos.html"')
                                                       .replace('href="archives/"', 'href="./"')
                                                       .replace('href="feed.xml"', 'href="../feed.xml"'),
        archive_list="<ul class='archive-list'>" + "".join(all_items) + "</ul>" if all_items else "<p>Aucune archive.</p>",
        last_build=last_build,
    )
    (DIST / "archives" / "index.html").write_text(archives_index_html, encoding="utf-8")

    # 6. Pages statiques : Méthode, À propos
    for slug, template in [("methode", "page.html"), ("apropos", "page.html")]:
        md_path = CONTENT / f"{slug}.md"
        if md_path.exists():
            page = parse_markdown_file(md_path)
            html = md_to_html(page["body"])
            page_html = render_template(
                template,
                site_title=SITE_TITLE,
                navigation=build_navigation(slug),
                titre=page["meta"].get("titre", slug.capitalize()),
                kicker=page["meta"].get("kicker", ""),
                content=html,
                last_build=last_build,
            )
            (DIST / f"{slug}.html").write_text(page_html, encoding="utf-8")

    # 7. Flux RSS
    feed_items = []
    all_entries = [current] + archives
    for entry in all_entries[:20]:
        e_date = entry["meta"].get("date", datetime.now().date().isoformat())
        if isinstance(e_date, str):
            try:
                e_date_obj = datetime.fromisoformat(e_date)
            except ValueError:
                e_date_obj = datetime.now()
        else:
            e_date_obj = datetime.combine(e_date, datetime.min.time())
        rfc822 = e_date_obj.strftime("%a, %d %b %Y 00:00:00 +0000")
        titre = entry["meta"].get("titre", "Veille")
        if entry is current:
            link = SITE_URL
        else:
            link = f"{SITE_URL}/archives/{slugify(entry['path'].stem)}.html"
        body_html = md_to_html(entry["body"])
        feed_items.append(f"""
    <item>
      <title>{titre}</title>
      <link>{link}</link>
      <guid>{link}</guid>
      <pubDate>{rfc822}</pubDate>
      <description><![CDATA[{body_html}]]></description>
    </item>""")
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{SITE_TITLE}</title>
    <link>{SITE_URL}</link>
    <description>{SITE_SUBTITLE}</description>
    <language>fr-FR</language>
    <lastBuildDate>{datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>
    {"".join(feed_items)}
  </channel>
</rss>"""
    (DIST / "feed.xml").write_text(rss, encoding="utf-8")

    print(f"✓ Site v2 généré dans {DIST}")
    print(f"  - page courante (semaine {current_meta.get('semaine', '?')})")
    print(f"  - {len(archives)} archives")
    print(f"  - pages Méthode et À propos")
    print(f"  - flux RSS")


if __name__ == "__main__":
    build()
