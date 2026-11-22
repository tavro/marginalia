#!/usr/bin/env python3

import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
STATIC = ROOT / "static"
OUT = ROOT / "site"

SITE_NAME = "Marginalia"
SITE_LINE = "Essays related to computer science by tavro.se"
AUTHOR_URL = "https://tavro.se"

TOPICS = [
    ("ai", "AI", "Mercury",
     "What a green result actually claims, when the builders are agents."),
    ("security", "Cyber Security", "Saturn",
     "The attack built against my own toolchain, and which defences held."),
    ("compilers", "Compilers", "Sulphur",
     "A language and a compiler that eat their own tail."),
    ("os", "Operating Systems", "Earth",
     "A kernel small enough that every abstraction can be caught being wrong."),
    ("browsers", "Browsers", "Luna",
     "A rendering engine with no floats, a borrowed font and a framebuffer."),
    ("networking", "(Inter)Networking", "Air",
     "What a network looks like from inside its absence."),
]
TOPIC = {t[0]: t for t in TOPICS}

SHOW_TOPIC_BOX = False
SHOW_EMPTY_TOPICS = False
SHOW_TOPIC_HEADINGS = False

STATUS_WORDS = {"draft", "in progress", "finished", "abandoned"}

SPRITE = """<svg class="sprite" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">
<symbol id="sym-ai" viewBox="0 0 24 28"><g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M7.5 2.5c0 3 2 4.6 4.5 4.6s4.5-1.6 4.5-4.6"/><circle cx="12" cy="12.6" r="4.6"/><path d="M12 17.2v8.3M8.6 21.6h6.8"/></g></symbol>
<symbol id="sym-security" viewBox="0 0 24 28"><g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M9 2.5v15M5.5 6h7"/><path d="M9 13.2c2.2-3.4 8.6-3.2 8.2 1.6-.3 3.2-4 4.2-3.4 8.2.2 1.2 1 2 2 2.2"/></g></symbol>
<symbol id="sym-compilers" viewBox="0 0 24 28"><g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.8 19.5 15H4.5Z"/><path d="M12 15v10.5M8 20.6h8"/></g></symbol>
<symbol id="sym-os" viewBox="0 0 24 28"><g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="12" cy="14" r="8.2"/><path d="M12 5.8v16.4M3.8 14h16.4"/></g></symbol>
<symbol id="sym-browsers" viewBox="0 0 24 28"><path d="M15.5 4.2a9.8 9.8 0 1 0 0 19.6 8.2 8.2 0 1 1 0-19.6Z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></symbol>
<symbol id="sym-networking" viewBox="0 0 24 28"><g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4.2 21 22.6H3Z"/><path d="M6.3 15.8h11.4"/></g></symbol>
<defs><linearGradient id="gold-wide" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="160" y2="0"><stop offset="0" stop-color="#8f6f2e"/><stop offset="0.5" stop-color="#e8cc8c"/><stop offset="1" stop-color="#8f6f2e"/></linearGradient><linearGradient id="gold-centre" gradientUnits="userSpaceOnUse" x1="48" y1="0" x2="112" y2="0"><stop offset="0" stop-color="#8f6f2e"/><stop offset="0.5" stop-color="#e8cc8c"/><stop offset="1" stop-color="#8f6f2e"/></linearGradient></defs>
<symbol id="orn-fleuron" viewBox="0 0 160 28"><g fill="none" stroke="url(#gold-wide)" stroke-width="1.2" stroke-linecap="round"><path d="M4 14h44M112 14h44"/><path d="M80 5.5 86 14l-6 8.5-6-8.5Z" fill="url(#gold-wide)"/><path d="M73 14c-6 0-9-6-15-6-4.5 0-6.5 3.4-4.4 5.8 1.8 2 5.2.8 4.6-1.6M87 14c6 0 9 6 15 6 4.5 0 6.5-3.4 4.4-5.8-1.8-2-5.2-.8-4.6 1.6"/><path d="M73 14c-6 0-9 6-15 6-4.5 0-6.5-3.4-4.4-5.8M87 14c6 0 9-6 15-6 4.5 0 6.5 3.4 4.4 5.8"/><circle cx="52" cy="14" r="1.3" fill="url(#gold-wide)"/><circle cx="108" cy="14" r="1.3" fill="url(#gold-wide)"/></g></symbol>
<symbol id="orn-centre" viewBox="48 0 64 28"><g fill="none" stroke="url(#gold-centre)" stroke-width="1.2" stroke-linecap="round"><path d="M80 5.5 86 14l-6 8.5-6-8.5Z" fill="url(#gold-centre)"/><path d="M73 14c-6 0-9-6-15-6-4.5 0-6.5 3.4-4.4 5.8 1.8 2 5.2.8 4.6-1.6M87 14c6 0 9 6 15 6 4.5 0 6.5-3.4 4.4-5.8-1.8-2-5.2-.8-4.6 1.6"/><path d="M73 14c-6 0-9 6-15 6-4.5 0-6.5-3.4-4.4-5.8M87 14c6 0 9-6 15-6 4.5 0 6.5 3.4 4.4 5.8"/><circle cx="52" cy="14" r="1.3" fill="url(#gold-centre)"/><circle cx="108" cy="14" r="1.3" fill="url(#gold-centre)"/></g></symbol>
</svg>"""


def sym(topic, cls="sym"):
    return f'<svg class="{cls}" aria-hidden="true"><use href="#sym-{topic}"/></svg>'


def slugify(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text).lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))


def parse(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
    if not m:
        raise SystemExit(f"{path.name}: missing --- header")
    meta = {}
    for line in m.group(1).splitlines():
        if line.strip():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    body, _, sources = m.group(2).partition("=== sources ===")
    meta["slug"] = path.stem
    meta["body_src"] = body.strip()
    meta["sources"] = [s.strip() for s in sources.strip().splitlines() if s.strip()]
    for key in ("title", "topic", "dek", "date", "status", "confidence", "importance"):
        if key not in meta:
            raise SystemExit(f"{path.name}: missing '{key}'")
    if meta["topic"] not in TOPIC:
        raise SystemExit(f"{path.name}: unknown topic {meta['topic']}")
    if meta["status"] not in STATUS_WORDS:
        raise SystemExit(f"{path.name}: unknown status {meta['status']}")
    return meta


def notes(body):
    count = 0

    def repl(m):
        nonlocal count
        kind, text = m.group(1), m.group(2).strip()
        if kind == "mn":
            return (f'<span class="sidenote marginnote side-r" role="note">'
                    f'<span class="mn-mark" aria-hidden="true">&#x2767;</span> {text}</span>')
        count += 1
        n = count
        side = "side-r" if n % 2 else "side-l"
        return (f'<span class="sn-ref" id="sn-ref-{n}" aria-label="Note {n}">{n}</span>'
                f'<span class="sidenote {side}" id="sn-{n}-text" role="note" data-n="{n}">'
                f'<span class="sn-num">{n}</span> {text}</span>')

    return re.sub(r"\{\{(sn|mn):(.*?)\}\}", repl, body, flags=re.S), count


def sections(body):
    toc = []

    def repl(m):
        inner = m.group(1).strip()
        sid = slugify(inner)
        toc.append((sid, inner))
        return (f'<h2 id="{sid}" class="sec-break"><span class="sec-title">{inner}</span>'
                f'<svg class="orn-centre" aria-hidden="true"><use href="#orn-centre"/></svg></h2>')

    return re.sub(r"<h2>(.*?)</h2>", repl, body, flags=re.S), toc


SKIP_TAGS = {"code", "pre", "svg", "script", "style", "title", "kbd"}
ACRO = re.compile(r"\b([A-Z][A-Z0-9]{2,})\b")
ACRO_KEEP = {"III"}


def smallcaps(body):
    parts = re.split(r"(<[^>]+>)", body)
    depth = 0
    for i, part in enumerate(parts):
        if part.startswith("<"):
            m = re.match(r"<(/?)([a-zA-Z0-9]+)", part)
            if m and m.group(2).lower() in SKIP_TAGS and not part.endswith("/>"):
                depth += -1 if m.group(1) else 1
            continue
        if depth == 0 and part:
            parts[i] = ACRO.sub(
                lambda m: m.group(1) if m.group(1) in ACRO_KEEP
                else f'<span class="sc">{m.group(1)}</span>', part)
    return "".join(parts)


def first_paragraph(body):
    return re.sub(r"(^|\n)<p>", r'\1<p class="opening">', body, count=1)


def word_count(src):
    text = re.sub(r"\{\{(sn|mn):.*?\}\}", " ", src, flags=re.S)
    text = re.sub(r"<(svg|pre|figure|table)\b.*?</\1>", " ", text, flags=re.S)
    return len(strip_tags(text).split())


def link_essays(body, essays, self_slug):
    targets = []

    def repl(m):
        attrs, slug, rest, inner = m.group(1), m.group(2), m.group(3), m.group(4)
        if slug not in essays or slug == self_slug:
            return m.group(0)
        targets.append(slug)
        t = essays[slug]["topic"]
        return (f'<a{attrs}href="{slug}.html"{rest} class="internal" data-preview="{slug}">'
                f'{inner}{sym(t, "link-sym")}</a>')

    out = re.sub(r'<a(\s+)href="([a-z0-9-]+)\.html"([^>]*)>(.*?)</a>', repl, body, flags=re.S)
    return out, targets


def external_links(body):
    return re.sub(r'<a href="(https?://[^"]+)"', r'<a class="external" href="\1" rel="noopener"', body)


def context_for(body_src, slug):
    for p in re.findall(r"<p[^>]*>(.*?)</p>", body_src, re.S):
        if f'href="{slug}.html"' in p:
            text = re.sub(r"\{\{(sn|mn):.*?\}\}", "", p, flags=re.S)
            text = " ".join(strip_tags(text).split())
            link = re.search(rf'href="{slug}\.html"[^>]*>(.*?)</a>', p, re.S)
            anchor = strip_tags(link.group(1)) if link else ""
            i = text.find(anchor) if anchor else 0
            start = max(0, i - 110)
            end = min(len(text), i + len(anchor) + 110)
            snippet = text[start:end]
            if start:
                snippet = "&hellip;" + html.escape(snippet.split(" ", 1)[-1])
            else:
                snippet = html.escape(snippet)
            if end < len(text):
                snippet = snippet.rsplit(" ", 1)[0] + "&hellip;"
            if anchor:
                snippet = snippet.replace(html.escape(anchor), f"<em>{html.escape(anchor)}</em>", 1)
            return snippet
    return ""


def head(title, desc):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="icon" href="icons/favicon.ico" sizes="16x16 32x32 48x48">
<link rel="icon" href="icons/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="theme-color" content="#050505">
<link rel="preload" href="fonts/eb-garamond-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="style.css">
</head>"""


def chrome_top(active):
    return f"""{SPRITE}
<a class="skip" href="#main">Skip to the text</a>"""


def chrome_bottom(previews):
    return f"""<footer class="site-foot">
  <p>If you think something here is wrong, write to <a href="mailto:th@tavro.se">th@tavro.se</a>, I would rather know. :-)</p>
</footer>
<script id="previews" type="application/json">{json.dumps(previews, ensure_ascii=False)}</script>
<script src="app.js" defer></script>
</body>
</html>
"""


def fmt_date(iso):
    y, m, d = iso.split("-")
    months = "January February March April May June July August September October November December".split()
    return f"{int(d)} {months[int(m) - 1]} {y}"


def render_essay(e, essays, order, previews):

    sources = ""
    if e["sources"]:
        plain = [re.sub(r"</?code>", "", src) for src in e["sources"]]
        items = external_links("\n".join(f"<li>{src}</li>" for src in plain))
        sources = f'<section class="foot-block" aria-label="Sources"><ol class="sources">\n{items}\n</ol></section>'

    backlinks = ""
    if e["backlinks"]:
        items = "\n".join(
            f'<li><a href="{b}.html" class="internal" data-preview="{b}">{essays[b]["title"]}'
            f'{sym(essays[b]["topic"], "link-sym")}</a>'
            f'<blockquote>{context_for(essays[b]["body_src"], e["slug"])}</blockquote></li>'
            for b in e["backlinks"])
        backlinks = f'<section class="foot-block"><h2>Linked from</h2><ul class="backlinks">\n{items}\n</ul></section>'

    return f"""{head(f"{e['title']} · {SITE_NAME}", e['dek'])}
<body class="page-essay topic-{e['topic']}">
{chrome_top('essay')}
<main id="main">
<article class="essay">
  <header class="essay-head">
    <h1><a href="index.html">{e['title']}</a></h1>
    <p class="dek">{e['dek']}</p>
  </header>
  <div class="body">
{e['body']}
    <div class="finis" aria-hidden="true"><svg class="orn-centre"><use href="#orn-centre"/></svg></div>
  </div>
  <footer class="essay-foot">
    {sources}
    {backlinks}
  </footer>
</article>
</main>
{chrome_bottom(previews)}"""


def render_index(essays, order, previews):
    clavis_items = "\n".join(
        f'<li><a href="#{k}">{sym(k, "sym sym-clavis")}<span class="cl-name">{name}</span></a></li>'
        for k, name, sign, _ in TOPICS)
    clavis = ""
    if SHOW_TOPIC_BOX:
        clavis = f"""  <section class="clavis" id="clavis" aria-label="Topics">
    <ul>
{clavis_items}
    </ul>
  </section>
"""

    groups = []
    for n, (k, name, sign, line) in enumerate(TOPICS, 1):
        rows = []
        for slug in order:
            e = essays[slug]
            if e["topic"] != k:
                continue
            rows.append(f"""<li class="entry">
  <a href="{slug}.html" class="entry-title">{e['title']}</a>
  <span class="entry-date">(<time datetime="{e['date']}">{fmt_date(e['date'])}</time>)</span>
</li>""")
        if not rows:
            if not SHOW_EMPTY_TOPICS:
                continue
            rows.append('<li class="entry entry-empty">Nothing yet.</li>')
        heading = (f'\n  <h2>{sym(k, "sym sym-topic")}<span class="topic-name">{name}</span></h2>'
                   if SHOW_TOPIC_HEADINGS else "")
        groups.append(f"""<section class="topic" id="{k}">{heading}
  <ol class="entries">
{''.join(rows)}
  </ol>
</section>""")

    return f"""{head(SITE_NAME, SITE_LINE)}
<body class="page-index">
{chrome_top('index')}
<main id="main" class="index">
  <header class="title-page">
    <svg class="orn" aria-hidden="true"><use href="#orn-fleuron"/></svg>
    <h1>{SITE_NAME}</h1>
    <p class="subtitle">{SITE_LINE.replace("tavro.se", f'<a href="{AUTHOR_URL}">tavro.se</a>')}</p>
    <svg class="orn" aria-hidden="true"><use href="#orn-fleuron"/></svg>
  </header>

{clavis}
{''.join(groups)}
</main>
{chrome_bottom(previews)}"""


def main():
    files = sorted((SRC / "essays").glob("*.html"))
    essays = {}
    for f in files:
        e = parse(f)
        essays[e["slug"]] = e

    topic_rank = {t[0]: i for i, t in enumerate(TOPICS)}
    order = sorted(essays, key=lambda s: essays[s]["date"], reverse=True)
    order = sorted(order, key=lambda s: topic_rank[essays[s]["topic"]])

    for slug in order:
        e = essays[slug]
        body = e["body_src"]
        body, e["notes"] = notes(body)
        body, e["toc"] = sections(body)
        body, e["links"] = link_essays(body, essays, slug)
        body = external_links(body)
        body = first_paragraph(body)
        body = smallcaps(body)
        e["body"] = body
        e["words"] = word_count(e["body_src"])

    for slug in order:
        essays[slug]["backlinks"] = [s for s in order if slug in essays[s]["links"]]

    previews = {
        s: {"title": essays[s]["title"], "dek": essays[s]["dek"], "topic": essays[s]["topic"],
            "topicName": TOPIC[essays[s]["topic"]][1], "date": fmt_date(essays[s]["date"]),
            "words": essays[s]["words"], "confidence": essays[s]["confidence"]}
        for s in order
    }

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(STATIC, OUT)
    (OUT / "index.html").write_text(render_index(essays, order, previews), encoding="utf-8")
    for slug in order:
        (OUT / f"{slug}.html").write_text(render_essay(essays[slug], essays, order, previews),
                                          encoding="utf-8")
    print(f"built {len(order)} essays + index into {OUT.relative_to(ROOT)}/")
    for slug in order:
        e = essays[slug]
        print(f"  {e['topic']:<11} {e['words']:>5} words  {e['notes']} notes  "
              f"{len(e['toc'])} sections  {slug}")


if __name__ == "__main__":
    main()
