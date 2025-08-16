from pyscript import document
from markdown import markdown as md
from js import setTimeout, clearTimeout
from pyodide.ffi import create_proxy
import re

status_text = document.querySelector("#status")
editor = document.querySelector("#editor")
preview = document.querySelector("#preview")
badge = document.querySelector("#pyscript-badge")
badge_extra = document.querySelector("#badge-extra")
show_html = document.querySelector("#show-html")

_idle_timer = None
IDLE_MS = 250

def _infer_pyscript_version() -> str:
    urls = []
    for s in document.querySelectorAll('script[type="module"]'):
        src = s.getAttribute("src")
        if src: urls.append(src)
    for l in document.querySelectorAll('link[rel="stylesheet"]'):
        href = l.getAttribute("href")
        if href: urls.append(href)
    pat = re.compile(r"/releases/([^/]+)/")
    for u in urls:
        m = pat.search(u)
        if m: return m.group(1)
    return ""

def set_status_rendering():
    status_text.innerText = "Rendering…"

def set_status_rendered():
    status_text.innerText = "Rendered ✓"

def _paint(html: str):
    if show_html.checked:
        preview.innerHTML = "<pre id='html-src'></pre>"
        document.querySelector("#html-src").innerText = html
    else:
        preview.innerHTML = html

def render_markdown():
    try:
        text = editor.value or ""
        html = md(text, extensions=["fenced_code", "sane_lists", "toc", "codehilite"])
        _paint(html)
    except Exception as exc:
        preview.innerHTML = f"<pre>Render error: {exc!r}</pre>"
        status_text.innerText = "Render error"

def _mark_rendered_cb(*args, **kwargs):
    set_status_rendered()

_mark_rendered_proxy = create_proxy(_mark_rendered_cb)

def on_input(event=None):
    global _idle_timer
    set_status_rendering()
    render_markdown()
    if _idle_timer is not None:
        clearTimeout(_idle_timer)
    _idle_timer = setTimeout(_mark_rendered_proxy, IDLE_MS)

def on_mode_toggle(event=None):
    on_input()

def enable_badge_link():
    version = _infer_pyscript_version()
    badge_extra.classList.remove("spinner")
    badge_extra.setAttribute("aria-label", "PyScript version")
    badge_extra.innerText = version
    badge.setAttribute("href", f"https://docs.pyscript.net/{version}/")
    badge.setAttribute("target", "_blank")
    badge.setAttribute("rel", "noopener noreferrer")
    badge.classList.remove("loading")  # re-enable click

enable_badge_link()
render_markdown()
set_status_rendered()
