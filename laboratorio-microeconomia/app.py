"""Laboratório de Microeconomia — modelos do Varian (9ª ed.) em Streamlit.

Rodar:  streamlit run app.py
"""
import streamlit as st

from micro import pages_consumer, pages_firm, pages_market, pages_ge, pages_extra, pages_extra2, pages_extra3  # noqa: F401  (registram as páginas)
from micro.registry import PAGES, CHAPTERS
from micro.ui import page_style, render_equations

st.set_page_config(page_title="Laboratório de Microeconomia", page_icon="📈", layout="wide")

PAGES_SORTED = sorted(PAGES, key=lambda e: e["ch"])


def make(entry):
    def run():
        page_style()
        entry["fn"]()
        render_equations()
    run.__name__ = entry["id"].replace("-", "_")
    title = f'{entry["ch"]} · {CHAPTERS[entry["ch"]]}' + (f' — {entry["nav"]}' if entry["nav"] else "")
    return st.Page(run, title=title, url_path=entry["id"], default=entry is PAGES_SORTED[0])


ST_PAGES = {e["id"]: make(e) for e in PAGES_SORTED}

# O menu padrão do Streamlit fica oculto: o menu lateral abaixo mostra os capítulos
# e só abre os subtópicos do capítulo em que se clica.
nav = st.navigation(list(ST_PAGES.values()), position="hidden")
current = getattr(nav, "title", None)

# Menu lateral com o mesmo desenho do app web. Os itens são botões estilizados (navegam sem recarregar a página);
# os capítulos com mais de um modelo abrem e fecham, mostrando os subtópicos.
cur_id = next((e["id"] for e in PAGES_SORTED if ST_PAGES[e["id"]].title == current), PAGES_SORTED[0]["id"])
cur_ch = next(e["ch"] for e in PAGES_SORTED if e["id"] == cur_id)
if st.session_state.get("_nav_page") != cur_id:          # ao chegar numa página, abre o capítulo dela
    st.session_state["_nav_page"] = cur_id
    st.session_state["_nav_open"] = cur_ch

with st.sidebar:
    st.markdown('<div class="toc-title">Capítulos</div>', unsafe_allow_html=True)
    for ch in sorted({e["ch"] for e in PAGES_SORTED}):
        group = [e for e in PAGES_SORTED if e["ch"] == ch]
        label = f"**{ch}** {CHAPTERS[ch]}"
        if len(group) == 1:
            e = group[0]
            if st.button(label, key=("navcur-" if e["id"] == cur_id else "navone-") + e["id"]) and e["id"] != cur_id:
                st.switch_page(ST_PAGES[e["id"]])
            continue
        is_open = st.session_state.get("_nav_open") == ch
        if st.button(label, key=f"navg{'o' if is_open else 'c'}-{ch}"):
            st.session_state["_nav_open"] = None if is_open else ch
            st.rerun()
        if is_open:
            for e in group:
                if st.button(e["nav"] or CHAPTERS[ch], key=("navscur-" if e["id"] == cur_id else "navs-") + e["id"]) and e["id"] != cur_id:
                    st.switch_page(ST_PAGES[e["id"]])

nav.run()
