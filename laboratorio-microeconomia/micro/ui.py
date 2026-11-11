"""Peças de interface: estilo, cabeçalho, controles, gráficos e painéis de resultado."""
import math
import re
import plotly.graph_objects as go
import streamlit as st
from . import core as _C

COL = dict(navy="#0A1E57", royal="#2A64B8", yellow="#F2C200", gold="#C99A00", coral="#D2553A",
           teal="#178F7E", ink="#0D1A3A", muted="#8A97B3", grid="#E5EAF3", faint="#B9C7E2")
SCALE = [[0, "#0A1E57"], [0.45, "#2A64B8"], [0.8, "#8FB3E6"], [1, "#F2C200"]]


def _tile_svg(w=2200, h=220):
    """Padrão de ladrilhos da faixa do cabeçalho (mesma regra do app web)."""
    import base64
    seed = 7

    def rnd():
        nonlocal seed
        seed = (seed * 16807) % 2147483647
        return seed / 2147483647
    S, gap, out = 54, 12, []
    y = -20
    while y < h:
        x = -10
        while x < w:
            a = rnd()
            if a >= 0.25:
                if a > 0.93:
                    c = "rgba(255,255,255,0.20)"
                elif a > 0.6:
                    c = f"rgba(70,130,215,{0.20 + 0.3 * rnd():.3f})"
                else:
                    c = f"rgba(8,40,110,{0.25 + 0.3 * rnd():.3f})"
                out.append(f'<rect x="{x}" y="{y}" width="{S}" height="{S}" rx="9" fill="{c}"/>')
            x += S + gap
        y += S + gap
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">{"".join(out)}</svg>'
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


TILE_BG = _tile_svg()

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..100,400..800&display=swap');
:root { --royal: #134C95; --navy: #0A1E57; --yellow: #F2C200; --paper: #F2F5FA; --line: #D6DEEB; --muted: #5B6A88; --ink: #0D1A3A; }
.stApp :is(p, label, li, h1, h2, h3, h4, input, textarea, button, a, .lede, .tile, .chip, .lab-band, .mhead, .ctl-title, .ctl-group, .eq-label, .side-title) {
  font-family: 'Archivo', 'Helvetica Neue', Arial, sans-serif; }
.stApp { background: var(--paper); }
/* barra do Streamlit transparente, sem o botão de publicar */
[data-testid="stHeader"] { background: transparent; pointer-events: none; }
[data-testid="stHeader"] * { pointer-events: auto; }
[data-testid="stAppDeployButton"], [data-testid="stDecoration"] { display: none !important; }
[data-testid="stMainMenu"] svg, [data-testid="stMainMenu"] button { color: #fff; fill: #fff; }
.block-container { padding: 0 2.4rem 3rem !important; max-width: none !important; }
/* ---------- cabeçalho: faixa azul com ladrilhos e faixa marinho ---------- */
.lab-band { margin: 0 -2.4rem 1.6rem; background-color: #134C95; background-image: url("__TILES__"); background-repeat: repeat-x; background-position: 0 0; }
.lab-band .top { height: 34px; }
.lab-band .top a { color: #fff; text-underline-offset: 3px; }
.lab-band .navy { background: #0A1E57; padding: 18px max(16px, 3vw) 16px; }
.lab-band h1 { margin: 0; padding: 0; font-weight: 800; font-stretch: 85%; text-transform: uppercase; color: #fff;
  font-size: clamp(28px, 4.4vw, 50px); line-height: 1; letter-spacing: -.01em; }
.lab-band h1 .hl { color: #F2C200; }
.lab-band .rule { height: 2px; background: #F2C200; margin: 12px 0 8px; max-width: 760px; transform-origin: left; animation: grow .9s cubic-bezier(.6,0,.2,1) .2s both; }
.lab-band p { margin: 0; color: #E6ECF7; font-size: 16px; }
/* ---------- painel de parâmetros (coluna da esquerda, fixa ao rolar) ---------- */
[data-testid="stColumn"]:has([class*="st-key-ctlpanel"]) { position: sticky; top: 1rem; align-self: flex-start; }
[class*="st-key-ctlpanel"] { background: #fff; border: 1px solid var(--line) !important; border-radius: 8px; padding: 14px 16px 16px; gap: .55rem; }
[class*="st-key-ctlpanel"] [data-testid="stSlider"] label p, [class*="st-key-ctlpanel"] [data-testid="stWidgetLabel"] p { font-size: 13.5px; font-weight: 600; color: var(--ink); }
[class*="st-key-ctlpanel"] [data-testid="stCaptionContainer"] p { font-size: 12px; line-height: 1.35; color: var(--muted); }
[class*="st-key-eqcard"] { background: #fff; border: 1px solid var(--line); border-radius: 8px; padding: 10px 18px 8px; margin-bottom: 1.1rem; overflow: visible; }
[class*="st-key-eqcard"] .katex-display, [class*="st-key-eqcard"] .katex-display > .katex { margin: .15rem 0 .45rem !important; text-align: left !important; }
[class*="st-key-eqcard"] .katex { font-size: 1.02em; }
[class*="st-key-eqcard"] [data-testid="stColumn"] { min-width: 0; overflow-x: clip; overflow-y: visible; }
[class*="st-key-eqcard"] [data-testid="stColumn"] * { overflow-y: visible !important; }
[class*="st-key-eqcard"] .katex { line-height: 1.6; }
[class*="st-key-eqcard"] [data-testid="stMarkdownContainer"] p { margin: .15rem 0 .4rem; padding: 2px 0 8px; text-align: left; line-height: 1.6; overflow: visible !important; }
[class*="st-key-eqcard"] [data-testid="stVerticalBlock"] { gap: 0; }
[class*="st-key-eqcard"] [data-testid="stMarkdownContainer"] { overflow: visible !important; }
.ctl-title { font-size: 11px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); margin-bottom: .1rem; }
.ctl-group { font-size: 12.5px; font-weight: 700; color: var(--royal); border-bottom: 1px solid var(--line); padding: .35rem 0 .15rem; margin: .3rem 0 .1rem; }
.eq-label { font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin-top: .3rem; }
/* gráfico num cartão branco */
[data-testid="stPlotlyChart"] { background: #fff; outline: 1px solid var(--line); border-radius: 8px; padding: 0 !important; overflow: hidden !important; margin-bottom: .4rem; }
[data-testid="stPlotlyChart"] > div, [data-testid="stPlotlyChart"] .js-plotly-plot { overflow: hidden !important; }
/* botões de opção segmentados, como no app web */
[data-testid="stButtonGroup"] { flex-wrap: wrap; }
[data-testid="stButtonGroup"] button { font-size: 12.5px; font-weight: 600; }
[data-testid="stBaseButton-segmented_controlActive"] { background: #134C95 !important; border-color: #134C95 !important; }
[data-testid="stBaseButton-segmented_controlActive"] p { color: #fff !important; }
[data-testid="stBaseButton-segmented_control"] p { color: #134C95; }
.mhead { display: flex; align-items: baseline; gap: 14px; flex-wrap: wrap; }
.mhead .num { font-weight: 800; font-size: 40px; line-height: 1; color: #134C95; font-variant-numeric: tabular-nums; }
.mhead h2 { margin: 0; padding: 0; font-weight: 800; font-stretch: 90%; font-size: clamp(22px, 2.6vw, 32px); color: #0A1E57; }
.mhead .src { flex-basis: 100%; font-size: 13px; color: #5B6A88; }
.mrule { height: 2px; background: #F2C200; margin: 10px 0 14px; max-width: 760px; }
.lede { max-width: 72ch; color: #26365C; margin-bottom: 1rem; font-size: 15.5px; line-height: 1.5; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px; margin: .4rem 0 .8rem; }
.tile { background: #fff; border: 1px solid #D6DEEB; border-top: 3px solid #134C95; border-radius: 6px; padding: 9px 12px 10px; }
.tile.key { border-top-color: #F2C200; }
.tile.small .v { font-size: 17px; }
.tile .k { font-size: 12px; color: #5B6A88; line-height: 1.3; }
.tile { min-width: 0; overflow-wrap: anywhere; }
.tile .v { font-size: 23px; font-weight: 700; color: #0A1E57; font-variant-numeric: tabular-nums; line-height: 1.25; }
.tile .s { font-size: 12px; color: #5B6A88; }
.chip { display: inline-block; font-size: 12px; font-weight: 700; padding: 2px 9px; border-radius: 999px; margin-top: 4px; }
.chip.good { background: #DDF2EC; color: #0E6A5C; } .chip.warn { background: #FFF1C2; color: #7A5B00; }
.chip.bad { background: #FBE1DA; color: #9A2F17; } .chip.info { background: #E1EAF8; color: #134C95; }
.gtable { border-collapse: collapse; margin: .3rem 0 .8rem; font-size: 14px; }
.gtable th, .gtable td { border: 1px solid #D6DEEB; padding: 6px 12px; text-align: center; background: #fff; }
.gtable th { color: #0A1E57; }
.gtable td.hit { background: #FFF1C2; box-shadow: inset 0 0 0 2px #F2C200; font-weight: 700; }
.rho-inf { font-weight: 700; color: #134C95; font-size: 15px; margin: -.4rem 0 .2rem; }
.stButton button { border-radius: 999px; font-size: 13px; padding: .2rem .8rem; min-height: 0; }
.gtable .a { color: #0A1E57; font-weight: 700; } .gtable .b { color: #D2553A; font-weight: 700; }
/* ---------- menu lateral, como no app web ---------- */
[data-testid="stSidebar"] { min-width: 268px !important; max-width: 268px !important; width: 268px !important; }
[data-testid="stSidebarUserContent"] { padding: 0 0 28px !important; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0 !important; }
[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.toc-title) { margin: 6px 0 12px; }
[data-testid="stSidebar"] .toc-title { padding: 8px 20px 8px; font-family: 'Archivo', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; font-weight: 800;
  letter-spacing: .16em; text-transform: uppercase; color: #8EA1CC; border-bottom: 1px solid rgba(142,161,204,.25); }
[data-testid="stSidebar"] [class*="st-key-nav"], [data-testid="stSidebar"] [class*="st-key-nav"] .stButton, [data-testid="stSidebar"] [class*="st-key-nav"] button { width: 100% !important; }
[data-testid="stSidebar"] [class*="st-key-nav"] button {
  display: block; text-align: left; border: 0 !important; border-left: 3px solid transparent !important; border-radius: 0 !important; box-shadow: none !important;
  background: transparent !important; color: #D5DDF0 !important; padding: 7px 18px 7px 17px !important; min-height: 0 !important; margin: 0 !important;
  transition: background .2s, color .2s, padding-left .2s; }
[data-testid="stSidebar"] [class*="st-key-nav"] button > div, [data-testid="stSidebar"] [class*="st-key-nav"] button [data-testid="stMarkdownContainer"] { display: block !important; width: 100% !important; }
[data-testid="stSidebar"] [class*="st-key-nav"] button p { width: 100% !important; }
[data-testid="stSidebar"] [class*="st-key-nav"] button p {
  display: grid !important; grid-template-columns: 30px 1fr; gap: 6px; align-items: baseline; margin: 0 !important; text-align: left;
  font-family: 'Archivo', 'Helvetica Neue', Arial, sans-serif; font-size: 14.5px !important; line-height: 1.3 !important; color: inherit !important;
  white-space: normal !important; overflow: visible !important; }
[data-testid="stSidebar"] [class*="st-key-nav"] button strong { color: #F2C200; font-size: 13px; font-weight: 700; font-variant-numeric: tabular-nums; }
[data-testid="stSidebar"] [class*="st-key-nav"] button:hover { background: rgba(255,255,255,.06) !important; color: #fff !important; padding-left: 21px !important; }
[data-testid="stSidebar"] [class*="st-key-nav"] button:focus:not(:focus-visible) { box-shadow: none !important; }
[data-testid="stSidebar"] [class*="st-key-navcur"] button { background: rgba(255,255,255,.10) !important; border-left-color: #F2C200 !important; color: #fff !important; }
[data-testid="stSidebar"] [class*="st-key-navcur"] button p { font-weight: 700; }
/* capítulos com subtópicos: seta à direita */
[data-testid="stSidebar"] [class*="st-key-navg"] button p { grid-template-columns: 30px 1fr 14px; }
[data-testid="stSidebar"] [class*="st-key-navg"] button p::after { content: ''; align-self: center; justify-self: center; width: 8px; height: 8px;
  border-right: 2px solid #8EA1CC; border-bottom: 2px solid #8EA1CC; transform: rotate(-45deg); transition: transform .3s cubic-bezier(.3,1.4,.5,1); }
[data-testid="stSidebar"] [class*="st-key-navgo"] button { background: rgba(255,255,255,.05) !important; color: #fff !important; }
[data-testid="stSidebar"] [class*="st-key-navgo"] button p::after { transform: rotate(45deg); border-color: #F2C200; }
/* subtópicos */
[data-testid="stSidebar"] [class*="st-key-navs"] button { position: relative; padding: 5px 18px 5px 53px !important; color: #AFBEDD !important; animation: slidein .35s cubic-bezier(.2,.8,.2,1) both; }
[data-testid="stSidebar"] [class*="st-key-navs"] button p { display: block !important; font-size: 14px !important; }
[data-testid="stSidebar"] [class*="st-key-navs"] button:hover, [data-testid="stSidebar"] [class*="st-key-navs"] button:focus { padding-left: 57px !important; }
[data-testid="stSidebar"] [class*="st-key-navscur"] button, [data-testid="stSidebar"] [class*="st-key-navscur"] button:hover { padding-left: 53px !important; }
[data-testid="stSidebar"] [class*="st-key-navs"] button::before { content: ''; position: absolute; left: 36px; top: 50%; width: 6px; height: 6px; margin-top: -3px;
  border-radius: 50%; background: #5D74A8; transition: background .2s, transform .2s; }
[data-testid="stSidebar"] [class*="st-key-navs"] button:hover::before, [data-testid="stSidebar"] [class*="st-key-navscur"] button::before { background: #F2C200; transform: scale(1.3); }
[data-testid="stSidebar"] [class*="st-key-navscur"] button { background: rgba(255,255,255,.09) !important; border-left-color: #F2C200 !important; color: #fff !important; }
[data-testid="stSidebar"] [class*="st-key-navscur"] button p { font-weight: 700; }
[data-testid="stSidebar"] [class*="st-key-navs"]:last-of-type button { margin-bottom: 4px !important; }
/* sem barras de rolagem desnecessárias */
[data-testid="stMain"] { overflow-x: hidden; }
[data-testid="stElementToolbar"] { display: none !important; }
/* botão para reabrir o menu quando ele está recolhido: bem visível */
:is([data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] button) {
  background: #F2C200 !important; color: #0A1E57 !important; border-radius: 0 10px 10px 0 !important; width: 44px !important; height: 44px !important;
  box-shadow: 0 4px 14px rgba(10,30,87,.35) !important; opacity: 1 !important; }
:is([data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] button) :is(svg, span) { color: #0A1E57 !important; fill: #0A1E57 !important; font-size: 26px !important; }
:is([data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] button):hover { background: #FFD43B !important; transform: translateX(3px); }
[data-testid="stSidebarCollapsedControl"] { opacity: 1 !important; visibility: visible !important; }
body:has([data-testid="stSidebar"][aria-expanded="false"]) .curtain { left: 0; }
/* botão de recolher, dentro do menu */
[data-testid="stSidebarCollapseButton"] button, [data-testid="stSidebarCollapseButton"] { color: #F2C200 !important; opacity: 1 !important; visibility: visible !important; }
[data-testid="stElementContainer"]:has(style):not(:has(.lab-band)) { display: none; }
.stApp .katex-display { overflow: visible !important; padding: 2px 0; }
/* ---------- movimento: a página se desenha ----------
   As animações rodam mesmo com "efeitos de animação" desligados no Windows (que o navegador repassa como
   prefers-reduced-motion), porque aqui elas fazem parte da proposta do laboratório. */
:root { --t0: .95s; }   /* quando a cortina começa a abrir */
.curtain { position: fixed; top: 0; right: 0; bottom: 0; left: 268px; z-index: 999991; overflow: hidden; pointer-events: none;
  animation: ctbg 1.75s ease both; }
.curtain i { position: absolute; width: 72px; height: 72px; border-radius: 10px; opacity: 0; animation: cttile 1.45s cubic-bezier(.3,1.2,.5,1) both; }
.ct-label { position: absolute; inset: 0; display: grid; place-content: center; justify-items: center; text-align: center; color: #fff; opacity: 0;
  animation: ctlab 1.75s ease both; font-family: 'Archivo', 'Helvetica Neue', Arial, sans-serif; }
.ct-kicker { font-size: 13px; font-weight: 700; letter-spacing: .3em; text-transform: uppercase; color: #C9D6EE; }
.ct-num { font-weight: 800; font-size: clamp(90px, 12vw, 160px); line-height: .95; color: #F2C200; }
.ct-name { font-weight: 800; font-stretch: 85%; text-transform: uppercase; font-size: clamp(26px, 3.4vw, 46px); line-height: 1.05; max-width: 16ch; }
.ct-rule { display: block; width: 220px; height: 3px; background: #F2C200; margin-top: 14px; transform-origin: center; animation: grow .5s ease .55s both; }
@keyframes ctbg { 0%, 22% { background: rgba(19,76,149,0); } 34%, 60% { background: rgba(19,76,149,1); } 76%, 100% { background: rgba(19,76,149,0); } }
@keyframes cttile { 0% { transform: scale(0) rotate(-25deg); opacity: 0; } 24%, 58% { transform: none; opacity: 1; } 82%, 100% { transform: scale(0) rotate(25deg); opacity: 0; } }
@keyframes ctlab { 0%, 22% { opacity: 0; transform: scale(.92); } 34%, 58% { opacity: 1; transform: none; } 70%, 100% { opacity: 0; transform: translateY(-14px); } }
/* bloco amarelo que passa sobre o título e o revela */
.rv { position: relative; display: inline-block; }
.rv::after { content: ''; position: absolute; inset: -3px -6px; background: #F2C200; transform: scaleX(0); pointer-events: none; }
.mhead h2.rv { animation: rvtext 0s linear calc(var(--t0) + .45s) both; }
.mhead h2.rv::after { animation: rvblock .8s cubic-bezier(.7,0,.3,1) calc(var(--t0) + .05s) both; }
.lab-band h1.rv, .lab-band h1.rv .hl { animation: rvtext 0s linear .65s both; }
.lab-band h1.rv::after { animation: rvblock .9s cubic-bezier(.7,0,.3,1) .2s both; }
@keyframes rvblock { 0% { transform: scaleX(0); transform-origin: left; } 50% { transform: scaleX(1); transform-origin: left; } 50.1% { transform: scaleX(1); transform-origin: right; } 100% { transform: scaleX(0); transform-origin: right; } }
@keyframes rvtext { from { color: transparent; } to { } }
.mhead .num { display: inline-block; animation: pop .6s cubic-bezier(.3,1.6,.5,1) var(--t0) both; }
.mhead .src { animation: rise .5s cubic-bezier(.2,.8,.2,1) calc(var(--t0) + .35s) both; }
.mrule { transform-origin: left; animation: grow .8s cubic-bezier(.6,0,.2,1) calc(var(--t0) + .15s) both; }
.lede { animation: rise .55s cubic-bezier(.2,.8,.2,1) calc(var(--t0) + .25s) both; }
/* cartões: a caneta amarela contorna e o conteúdo aparece */
[class*="st-key-eqcard"] { animation: pen .9s cubic-bezier(.6,0,.3,1) calc(var(--t0) + .3s) both; }
[class*="st-key-ctlpanel"] { animation: pen 1s cubic-bezier(.6,0,.3,1) calc(var(--t0) + .4s) both; }
[data-testid="stTabs"] { animation: rise .5s cubic-bezier(.2,.8,.2,1) calc(var(--t0) + .45s) both; }
[data-testid="stPlotlyChart"] { animation: pen 1s cubic-bezier(.6,0,.3,1) .5s both; }
@keyframes pen {
  0% { clip-path: inset(0 100% 100% 0 round 8px); box-shadow: inset 0 0 0 2px #F2C200; }
  55% { clip-path: inset(0 0 0 0 round 8px); box-shadow: inset 0 0 0 2px #F2C200; }
  100% { clip-path: inset(0 0 0 0 round 8px); box-shadow: inset 0 0 0 0 rgba(242,194,0,0); } }
/* cartões de resultado: aparecem rápido a cada mudança, como no app web */
.tiles .tile { animation: tilein .45s cubic-bezier(.2,.8,.2,1) both; }
.tiles .tile:nth-child(2) { animation-delay: .04s; } .tiles .tile:nth-child(3) { animation-delay: .08s; } .tiles .tile:nth-child(4) { animation-delay: .12s; } .tiles .tile:nth-child(n+5) { animation-delay: .16s; }
@keyframes tilein { 0% { opacity: 0; transform: translateY(8px); background: #FFF4C2; } 60% { opacity: 1; transform: none; background: #FFF4C2; } 100% { background: #fff; } }
.tile { transition: transform .2s, box-shadow .2s; }
.tile:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(10,30,87,.10); }
.stTabs [data-baseweb="tab"] { transition: color .2s, background .2s; border-radius: 6px 6px 0 0; }
.stTabs [data-baseweb="tab"]:hover { background: #E5EBF5; }
.stTabs [data-baseweb="tab-highlight"] { background-color: #F2C200; height: 3px; transition: transform .38s cubic-bezier(.3,1.25,.5,1), width .38s cubic-bezier(.3,1.25,.5,1) !important; }
.stButton button, .stRadio label { transition: transform .12s, background .2s; }
.stButton button:active { transform: scale(.96); }
/* o gráfico se desenha: grade, curvas traçadas uma a uma, depois pontos e rótulos */
[data-testid="stPlotlyChart"] .gridlayer, [data-testid="stPlotlyChart"] .zerolinelayer, [data-testid="stPlotlyChart"] .xtick, [data-testid="stPlotlyChart"] .ytick, [data-testid="stPlotlyChart"] .legend { animation: fadein .5s ease-out both; }
[data-testid="stPlotlyChart"] .legend { animation-delay: .2s; }
[data-testid="stPlotlyChart"] .scatterlayer .trace { --d: 2.4s; }
[data-testid="stPlotlyChart"] .scatterlayer .trace:nth-child(1) { --d: 0.35s; }
[data-testid="stPlotlyChart"] .scatterlayer .trace:nth-child(2) { --d: 0.57s; }
[data-testid="stPlotlyChart"] .scatterlayer .trace:nth-child(3) { --d: 0.79s; }
[data-testid="stPlotlyChart"] .scatterlayer .trace:nth-child(4) { --d: 1.01s; }
[data-testid="stPlotlyChart"] .scatterlayer .trace:nth-child(5) { --d: 1.23s; }
[data-testid="stPlotlyChart"] .scatterlayer .trace:nth-child(6) { --d: 1.45s; }
[data-testid="stPlotlyChart"] .scatterlayer .trace:nth-child(7) { --d: 1.67s; }
[data-testid="stPlotlyChart"] .scatterlayer .trace:nth-child(8) { --d: 1.89s; }
[data-testid="stPlotlyChart"] .scatterlayer .trace:nth-child(9) { --d: 2.11s; }
[data-testid="stPlotlyChart"] .scatterlayer .trace:nth-child(10) { --d: 2.33s; }
[data-testid="stPlotlyChart"] .scatterlayer path.js-line { animation: draw 1.6s cubic-bezier(.45,.05,.35,1) var(--d) both; }
[data-testid="stPlotlyChart"] .scatterlayer path.js-fill, [data-testid="stPlotlyChart"] .scatterlayer path.js-tonext { animation: fadein .8s ease-out var(--d) both; }
[data-testid="stPlotlyChart"] .scatterlayer .points path, [data-testid="stPlotlyChart"] .scatterlayer .textpoint { animation: fadein .45s ease-out calc(var(--d) + .9s) both; }
[data-testid="stPlotlyChart"] .barlayer .point path { transform-box: fill-box; transform-origin: bottom; animation: growy .7s cubic-bezier(.2,.8,.2,1) .35s both; }
[data-testid="stPlotlyChart"] .annotation, [data-testid="stPlotlyChart"] .shapelayer path { animation: fadein .5s ease-out 1.8s both; }
[data-testid="stPlotlyChart"] .gl-container, [data-testid="stPlotlyChart"] .contourlayer, [data-testid="stPlotlyChart"] .heatmaplayer { animation: zoomin .8s cubic-bezier(.2,.8,.2,1) both; }
@keyframes draw { from { stroke-dasharray: 2400px 2400px; stroke-dashoffset: 2400px; } to { stroke-dasharray: 2400px 2400px; stroke-dashoffset: 0; } }
@keyframes fadein { from { opacity: 0; } to { opacity: 1; } }
@keyframes growy { from { transform: scaleY(0); } to { transform: scaleY(1); } }
@keyframes zoomin { from { opacity: 0; transform: scale(.94); } to { opacity: 1; transform: none; } }
@keyframes rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@keyframes slidein { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: none; } }
@keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
@keyframes pop { 0% { transform: scale(.4) rotate(-12deg); opacity: 0; } 100% { transform: none; opacity: 1; } }
</style>
"""

def _version():
    try:
        return tuple(int(x) for x in st.__version__.split(".")[:2])
    except Exception:
        return (0, 0)


_ST_VERSION = _version()
REPO = "https://github.com/amaral-vitor/Hal-Varian-s-models-from-Intermediate-Microeconomics-/tree/master"


def page_style():
    st.markdown(CSS.replace("__TILES__", TILE_BG), unsafe_allow_html=True)
    band = ('<div class="lab-band"><div class="top"></div>'
            '<div class="navy"><h1 class="rv"><span class="hl">Laboratório</span> de Microeconomia</h1><div class="rule"></div>'
            '<p>Os modelos de <i>Microeconomia: uma abordagem moderna</i>, de Hal R. Varian, para explorar no navegador</p></div></div>')
    st.markdown(band, unsafe_allow_html=True)


_EQS = []
_EQ_SLOT = [None]
_PANEL = [0]
_PID = ["p"]


def _curtain(ch, chapter):
    """Cortina de ladrilhos (como a capa) que cobre a página ao trocar de capítulo e se recolhe em diagonal."""
    seed = ch * 97 + 13

    def rnd():
        nonlocal seed
        seed = (seed * 16807) % 2147483647
        return seed / 2147483647
    pal = ["#0F3F86", "#0A1E57", "#2A64B8", "#134C95", "#1B57A8", "#0D2C6E"]
    S, G, cols, rows = 72, 12, 21, 13
    tiles = []
    for j in range(rows):
        for i in range(cols):
            a = rnd()
            c = "#F2C200" if a > 0.95 else pal[int(rnd() * len(pal))]
            d = (i + j) / (cols + rows) * 0.38
            tiles.append(f'<i style="left:{i * (S + G) - 6}px;top:{j * (S + G) - 6}px;background:{c};animation-delay:{d:.3f}s"></i>')
    return (f'<div class="curtain" aria-hidden="true">{"".join(tiles)}'
            f'<div class="ct-label"><span class="ct-kicker">Capítulo</span><b class="ct-num">{ch}</b><span class="ct-name">{chapter}</span><span class="ct-rule"></span></div></div>')


def header(ch, chapter, title, lede, eqs):
    """Título, capítulo e texto de abertura. As equações entram logo abaixo, num espaço reservado
    (preenchido no fim da página, quando a forma funcional já foi escolhida)."""
    _PID[0] = re.sub(r"[^a-z0-9]+", "-", f"{ch}-{title}".lower())[:40]
    st.markdown(_curtain(ch, chapter), unsafe_allow_html=True)
    st.markdown(f'<div class="mhead"><span class="num">{ch}</span><h2 class="rv">{title}</h2><span class="src">Capítulo {ch} · {chapter}</span></div>'
                f'<div class="mrule"></div><div class="lede">{lede}</div>', unsafe_allow_html=True)
    _EQ_SLOT[0] = st.empty()
    _PANEL[0] = 0
    _EQS.clear()
    _EQS.extend(eqs)


def render_equations():
    if not _EQS:
        return
    slot = _EQ_SLOT[0]
    with (slot.container() if slot is not None else _Plain()):
        with st.container(key=f"eqcard-{_PID[0]}"):
            longest = max(len(tex) for _, tex in _EQS)
            n = min(len(_EQS), 3 if longest < 55 else 2 if longest < 100 else 1)
            cs = st.columns(n)
            for i, (label, tex) in enumerate(_EQS):
                with cs[i % n]:
                    st.markdown(f'<div class="eq-label">{label or "&nbsp;"}</div>\n\n$\\displaystyle {tex}$', unsafe_allow_html=True)
    _EQS.clear()


# ---------------------------------------------------------------- painel de parâmetros em grade
_FLOW = []


class Controls:
    """Painel de parâmetros na coluna da esquerda (como a bancada do app web). Os controles ficam um embaixo do outro."""
    def __init__(self, parent):
        self.parent = parent
        self.cols = None

    def __enter__(self):
        self.parent.__enter__()
        _PANEL[0] += 1
        self.box = st.container(key=f"ctlpanel-{_PID[0]}-{_PANEL[0]}")
        self.box.__enter__()
        st.markdown('<div class="ctl-title">Parâmetros</div>', unsafe_allow_html=True)
        _FLOW.append(self)
        return self

    def __exit__(self, *exc):
        _FLOW.pop()
        self.box.__exit__(*exc)
        return self.parent.__exit__(*exc)


class _Plain:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def split(n=3):
    """Bancada: parâmetros à esquerda, gráfico e resultados à direita."""
    left, right = st.columns([0.27, 0.73], gap="medium")
    return Controls(left), right


def _slot():
    if not _FLOW or not _FLOW[-1].cols:
        return _Plain()
    f = _FLOW[-1]
    c = f.cols[f.i % len(f.cols)]
    f.i += 1
    return c


def group(text):
    """Subtítulo dentro do painel de parâmetros."""
    st.markdown(f'<div class="ctl-group">{text}</div>', unsafe_allow_html=True)


def rd(label, options, key):
    """Opções em botões segmentados (como no app web); cai para rádio em versões antigas."""
    keep = "_keep-" + key
    with _slot():
        if hasattr(st, "segmented_control"):
            v = st.segmented_control(label, options, default=st.session_state.get(keep, options[0]), key=key)
        else:
            v = st.radio(label, options, key=key)
    if v is None:          # clicar na opção já marcada a desmarca: mantém a anterior
        v = st.session_state.get(keep, options[0])
    st.session_state[keep] = v
    return v


def cb(label, key):
    with _slot():
        return st.checkbox(label, key=key)


# ---------------------------------------------------------------- formatação
def fmt(x, d=2):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    if isinstance(x, float) and math.isinf(x):
        return "∞" if x > 0 else "−∞"
    s = f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s.replace("-", "−")


def sgn(x, d=2):
    return ("+" if x > 0 else "") + fmt(x, d)


def tiles(items):
    html = '<div class="tiles">'
    for t in items:
        chip = f'<span class="chip {t["chip"][1]}">{t["chip"][0]}</span>' if t.get("chip") else ""
        sub = f'<div class="s">{t["s"]}</div>' if t.get("s") else ""
        html += f'<div class="tile{" key" if t.get("key") else ""}{" small" if t.get("small") else ""}"><div class="k">{t["k"]}</div><div class="v">{t["v"]}</div>{sub}{chip}</div>'
    st.markdown(html + "</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------- controles
def sl(mid, key, label, lo, hi, val, step, hint=None):
    is_int = all(float(v).is_integer() for v in (lo, hi, val, step)) and step >= 1
    cast = int if is_int else float
    keep = f"_keep-{mid}-{key}"   # guarda o valor quando o controle some (ex.: ao trocar a forma funcional)
    with _slot():
        v = st.slider(label, min_value=cast(lo), max_value=cast(hi), value=cast(st.session_state.get(keep, val)), step=cast(step), key=f"{mid}-{key}")
        st.session_state[keep] = v
        if hint:
            st.caption(hint)
        return v


RHO_HINT = ("σ = 1/(1−ρ). Use os atalhos para os três casos especiais: complementares perfeitos (ρ → −∞), Cobb-Douglas (ρ = 0) "
            "e substitutos perfeitos (ρ = 1). Com ρ > 1 as curvas ficam côncavas e a escolha vai para um canto.")


def _set_preset(mid, kind):
    st.session_state[f"{mid}-leo"] = kind == "leo"
    if kind == "cd":
        st.session_state[f"{mid}-rho"] = 0.0
    if kind == "ps":
        st.session_state[f"{mid}-rho"] = 1.0


def _clear_leo(mid):
    st.session_state[f"{mid}-leo"] = False


def ces_controls(mid, rho_default=0.5, label="Grau de substituição (ρ)", hint=RHO_HINT):
    """ρ da CES com três atalhos: complementares perfeitos (ρ → −∞), Cobb-Douglas (ρ = 0) e substitutos perfeitos (ρ = 1).
    Devolve (ρ, mode) com mode = "leo" no limite dos complementares."""
    lk, rk = f"{mid}-leo", f"{mid}-rho"
    st.session_state.setdefault(lk, False)
    with _slot():
        rho = st.slider(label, min_value=-10.0, max_value=5.0, value=float(rho_default), step=0.1, key=rk,
                        on_change=_clear_leo, args=(mid,))
        leo = st.session_state[lk]
        if leo:
            st.markdown('<div class="rho-inf">ρ → −∞</div>', unsafe_allow_html=True)
        st.caption(hint)
        for kind, text in (("leo", "Complementares perfeitos (ρ → −∞)"), ("cd", "Cobb-Douglas (ρ = 0)"), ("ps", "Substitutos perfeitos (ρ = 1)")):
            on = leo if kind == "leo" else (not leo and abs(rho - (0 if kind == "cd" else 1)) < 1e-9)
            st.button(text, key=f"{mid}-pre-{kind}", type="primary" if on else "secondary", on_click=_set_preset, args=(mid, kind))
    return rho, ("leo" if leo else None)


def pref_mode(form, rho, leo, k=None, a=None):
    """Forma efetiva usada nas contas e nas fórmulas."""
    if form == "ql":
        return dict(form="ql", a=a)
    if leo:
        return dict(form="comp", k=k)
    return dict(form="cd" if abs(rho) < 1e-9 else "sub" if abs(rho - 1) < 1e-9 else "ces")


def pref_controls(mid, w="delta", wl=None, x1="x₁", x2="x₂", value="ces", rho=None, a=(1, 20, 0.5, 5), k=(0.2, 5, 0.1, 1), wv=0.5, title="Preferências",
                  extra=None, label="Forma funcional"):
    """O mesmo menu em todos os capítulos: CES (com ρ e atalhos) ou quase-linear.
    extra: {rótulo: chave} com casos atípicos (só na galeria do cap. 3).
    Devolve um dicionário com form, o peso (chave w), rho, k, a e mode."""
    group(title)
    opts = {"CES": "ces", "Quase-linear": "ql", **(extra or {})}
    form = opts[rd(label, list(opts), f"{mid}-form")]
    out = dict(form=form, rho=0.0, k=k[3], a=a[3])
    out[w] = wv
    if form not in ("ces", "ql"):
        out["mode"] = dict(form=form)
        return out
    leo = form == "ces" and st.session_state.get(f"{mid}-leo", False)
    if form == "ces":
        if not leo:
            out[w] = sl(mid, w, wl or f"Peso de {x1} (δ)", 0.1, 0.9, wv, 0.05,
                        hint=f"Com ρ = 0 (Cobb-Douglas), δ é a fração da renda gasta em {x1}; com ρ = 1 (substitutos), {x1} e {x2} se trocam à taxa fixa δ/(1−δ).")
        out["rho"], m = ces_controls(mid, 0.0 if value == "cd" else (0.5 if rho is None else rho))
        leo = m == "leo"
        if leo:
            out["k"] = sl(mid, "k", f"Proporção fixa: unidades de {x2} para cada {x1} (k)", *k[:2], k[3], k[2],
                          hint=f"No limite ρ → −∞ os pesos deixam de importar e U = min{{k·{x1}, {x2}}}: os bens só servem juntos, na proporção {x2} = k·{x1}.")
    else:
        out["a"] = sl(mid, "a", f"Intensidade da preferência por {x1} (a)", a[0], a[1], a[3], a[2],
                      hint=f"U = a·ln {x1} + {x2}: a demanda de {x1} não depende da renda (se a renda for suficiente); toda renda extra vai para {x2}.")
    out["mode"] = pref_mode(form, out["rho"], leo, out["k"], out["a"])
    return out


def pref2_controls(mid, aA=0.5, aB=0.3, value="ces"):
    """Versão para dois consumidores (caixa de Edgeworth): mesma forma, parâmetros de cada um."""
    group("Preferências (a mesma forma para A e B)")
    form = rd("Forma funcional", ["CES", "Quase-linear"], f"{mid}-form")
    form = "ql" if form == "Quase-linear" else "ces"
    out = dict(form=form, aA=aA, aB=aB, rho=0.0, kA=1.0, kB=2.0, vA=3.0, vB=4.0)
    leo = form == "ces" and st.session_state.get(f"{mid}-leo", False)
    if form == "ces":
        if not leo:
            out["aA"] = sl(mid, "aA", "Peso do bem 1 de A (δᴬ)", 0.1, 0.9, aA, 0.05,
                           hint="Com ρ = 0 (Cobb-Douglas), δ é a fração da renda gasta no bem 1; com ρ = 1 (substitutos), a taxa de troca é δ/(1−δ).")
            out["aB"] = sl(mid, "aB", "Peso do bem 1 de B (δᴮ)", 0.1, 0.9, aB, 0.05)
        out["rho"], m = ces_controls(mid, 0.0 if value == "cd" else 0.5, label="Grau de substituição (ρ), comum aos dois")
        leo = m == "leo"
        if leo:
            out["kA"] = sl(mid, "kA", "Proporção fixa de A (kᴬ)", 0.2, 5.0, 1.0, 0.1, hint="U = min{k·x₁, x₂}: cada consumidor usa os bens na proporção x₂ = k·x₁.")
            out["kB"] = sl(mid, "kB", "Proporção fixa de B (kᴮ)", 0.2, 5.0, 2.0, 0.1)
    else:
        out["vA"] = sl(mid, "vA", "Intensidade da preferência pelo bem 1 de A (aᴬ)", 0.5, 10.0, 3.0, 0.1, hint="U = a·ln x₁ + x₂: a demanda do bem 1 não depende da renda.")
        out["vB"] = sl(mid, "vB", "Intensidade da preferência pelo bem 1 de B (aᴮ)", 0.5, 10.0, 4.0, 0.1)
    out["mode"] = pref_mode(form, out["rho"], leo)
    return out


def u_tex(f, U="U", v1="x_1", v2="x_2", w=r"\delta", k="k", a="a"):
    """Fórmula da forma escolhida, em LaTeX."""
    return {"comp": rf"{U}=\min\{{{k}\,{v1},\;{v2}\}}", "cd": rf"{U}={v1}^{{{w}}}\,{v2}^{{1-{w}}}", "sub": rf"{U}={w}\,{v1}+(1-{w})\,{v2}",
            "ces": rf"{U}=\left[{w}\,{v1}^{{\rho}}+(1-{w})\,{v2}^{{\rho}}\right]^{{1/\rho}}", "ql": rf"{U}={a}\ln {v1}+{v2}"}.get(f, "")


def demand_tex(f):
    return {"comp": r"x_1=\dfrac{m}{p_1+k\,p_2},\quad x_2=k\,x_1", "cd": r"x_1=\dfrac{\delta\, m}{p_1},\quad x_2=\dfrac{(1-\delta)\,m}{p_2}",
            "sub": r"x_1=\dfrac{m}{p_1}\ \text{se}\ \dfrac{\delta}{1-\delta}>\dfrac{p_1}{p_2};\quad x_1=0\ \text{se menor}",
            "ces": r"\dfrac{x_2}{x_1}=\left[\dfrac{p_1(1-\delta)}{p_2\,\delta}\right]^{\frac{1}{1-\rho}}",
            "ql": r"x_1=\dfrac{a\,p_2}{p_1}\ \ (\text{se } m\ge a\,p_2)"}.get(f, "")


AGENT_EQ = dict(label="Utilidade de cada consumidor i = A, B", U="u_i", v1="x_{1i}", v2="x_{2i}", w=r"\delta_i", k="k_i", a="a_i")


def pref_eqs(p, label="Utilidade", demand=False, **names):
    """Põe a fórmula da forma escolhida no topo das equações do modelo."""
    f = p["mode"]["form"]
    extra = [(label, u_tex(f, **names))] + ([("Demanda", demand_tex(f))] if demand else [])
    _EQS[0:0] = extra


def _fx(v):
    s = fmt(v, 2)
    return s[:-3] if s.endswith(",00") else s[:-1] if s.endswith("0") and "," in s else s


def u_text(f, p, v1="x₁", v2="x₂", w="delta"):
    """Fórmula com os números atuais, em texto."""
    d = p.get(w, 0.5)
    return {"comp": f"U = min({_fx(p['k'])}·{v1}, {v2})", "cd": f"U = {v1}^{_fx(d)} · {v2}^{_fx(1 - d)}", "sub": f"U = {_fx(d)}·{v1} + {_fx(1 - d)}·{v2}",
            "ces": f"U = [{_fx(d)}·{v1}^{_fx(p['rho'])} + {_fx(1 - d)}·{v2}^{_fx(p['rho'])}]^(1/{_fx(p['rho'])})", "ql": f"U = {_fx(p['a'])}·ln {v1} + {v2}"}.get(f, "")


# ---------------------------------------------------------------- gráficos
def clean(arr):
    out = []
    for v in arr:
        if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))) or abs(v) > 1e8:
            out.append(None)
        else:
            out.append(v)
    return out


def ln(x, y, name, color, width=2.6, dash="solid", legend=True, opacity=1.0, hover="%{x:.2f} · %{y:.2f}", yaxis=None, shape="linear"):
    return go.Scatter(mode="lines", x=list(x), y=clean(y), name=name, showlegend=legend, opacity=opacity,
                      line=dict(color=color, width=width, dash=dash, shape=shape), connectgaps=False,
                      hovertemplate=hover + f"<extra>{name}</extra>", **({"yaxis": yaxis} if yaxis else {}))


def dot(x, y, name, color, size=13, symbol="circle", edge=None, text=None, tp="top right", legend=True):
    return go.Scatter(mode="markers+text" if text else "markers", x=[x], y=[y], name=name, showlegend=legend,
                      text=[text] if text else None, textposition=tp, textfont=dict(size=13, color=COL["navy"]),
                      marker=dict(size=size, color=color, symbol=symbol, line=dict(color=edge or COL["navy"], width=1.6)),
                      hovertemplate=f"%{{x:.3f}} · %{{y:.3f}}<extra>{name}</extra>", cliponaxis=False)


def area(x, y, name, color, legend=True):
    return go.Scatter(mode="lines", x=list(x), y=list(y), name=name, fill="toself", fillcolor=color,
                      line=dict(width=0), hoverinfo="name", showlegend=legend)


def rect(x0, x1, y0, y1, name, color):
    return area([x0, x1, x1, x0], [y0, y0, y1, y1], name, color)


def arrow(x0, y0, x1, y1, color):
    return dict(x=x1, y=y1, ax=x0, ay=y0, xref="x", yref="y", axref="x", ayref="y", showarrow=True,
                arrowhead=3, arrowsize=1.1, arrowwidth=2, arrowcolor=color, text="", standoff=8, startstandoff=8)


def fig2d(traces, xt, yt, xr=None, yr=None, square=False, legend=True, annotations=None):
    fig = go.Figure(traces)
    ax = dict(gridcolor=COL["grid"], zeroline=True, zerolinecolor="#9AA8C4", ticks="outside", tickcolor="#9AA8C4", linecolor="#9AA8C4")
    fig.update_layout(font=dict(family="Archivo, Helvetica Neue, Arial, sans-serif", size=12.5, color=COL["ink"]),
                      separators=",.", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FFFFFF",
                      margin=dict(l=66, r=28, t=24, b=60), legend=dict(font=dict(size=12), bgcolor="rgba(255,255,255,0.85)"),
                      hovermode="closest", showlegend=legend, annotations=annotations or [],
                      transition=dict(duration=450, easing="cubic-in-out"))
    fig.update_xaxes(title_text=xt, range=xr, rangemode="tozero", **ax)
    fig.update_yaxes(title_text=yt, range=yr, rangemode="tozero", **ax)
    if square:
        # proporção travada: encolhe a área do gráfico em vez de alargar um eixo (mantém a origem)
        fig.update_xaxes(constrain="domain")
        fig.update_yaxes(scaleanchor="x", constrain="domain")
    return fig


def fig3d(traces, xt, yt, zt):
    fig = go.Figure(traces)
    fig.update_layout(font=dict(family="Archivo, Helvetica Neue, Arial, sans-serif", size=12, color=COL["ink"]), separators=",.",
                      paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=6, b=0),
                      scene=dict(xaxis_title=xt, yaxis_title=yt, zaxis_title=zt, aspectmode="cube",
                                 camera=dict(eye=dict(x=1.55, y=-1.55, z=0.95))),
                      legend=dict(font=dict(size=12)))
    return fig


def _get(obj, k):
    try:
        return obj[k]
    except Exception:
        return getattr(obj, k, None)


def chart(fig, height=540, key=None):
    """Gráfico fixo: sem barra de ferramentas, sem zoom nem arraste (o passar do mouse continua mostrando os valores)
    e com a legenda fora da área do gráfico, para nada ficar por cima das curvas."""
    fig.update_layout(height=height)
    ttype = lambda t: t.get("type") if isinstance(t, dict) else getattr(t, "type", None)
    if not any(ttype(t) in ("surface", "scatter3d") for t in fig.data):   # 2D
        fig.update_layout(dragmode=False)
        fig.update_xaxes(fixedrange=True)
        fig.update_yaxes(fixedrange=True)
        try:
            x2 = fig.layout["xaxis2"]
            top_axis = bool(x2) and x2["side"] == "top"
        except Exception:
            top_axis = False
        lay = fig.layout
        if top_axis:   # caixa de Edgeworth: eixos de B em cima e à direita, legenda embaixo
            fig.update_layout(legend=dict(orientation="h", x=0, xanchor="left", y=-0.1, yanchor="top"))
        else:
            fig.update_layout(legend=dict(orientation="h", x=0, xanchor="left", y=1.02, yanchor="bottom", bgcolor="rgba(0,0,0,0)"),
                              margin=dict(t=24 if _get(lay, "showlegend") is False else 40))
    fig.update_layout(paper_bgcolor="#FFFFFF")
    cfg = {"displaylogo": False, "displayModeBar": False, "scrollZoom": False, "doubleClick": False}
    if _ST_VERSION >= (1, 46):
        st.plotly_chart(fig, width="stretch", theme=None, config=cfg, key=key)
    else:
        st.plotly_chart(fig, use_container_width=True, theme=None, config=cfg, key=key)


def ic_traces(U, d, rho, mode, xmax, ymax, ces_level, label="Curva de indiferença", levels=(0.6, 1.0, 1.45)):
    out = []
    for f in levels:
        xs, ys = ces_level(U * f if U > 0 else U + (f - 1) * max(abs(U), 1), d, rho, mode, xmax, ymax)
        main = f == 1.0
        out.append(ln(xs, ys, label if main else "Outros níveis de U", COL["royal"] if main else COL["faint"],
                      width=2.6 if main else 1.6, legend=main or f == levels[0]))
    return out


def budget(m, p1, p2, name, color, **kw):
    return ln([0, m / p1], [m / p2, 0], name, color, **kw)


KIND = dict(interior=("Solução interior", "good"), corner1=("Canto: só o bem 1", "warn"), corner2=("Canto: só o bem 2", "warn"),
            leo=("Complementares perfeitos: consumo na proporção fixa", "info"), tie=("Toda a reta é ótima", "info"))


def sigma_text(rho, mode):
    f = mode["form"] if isinstance(mode, dict) else "comp" if mode == "leo" else "ces"
    if f == "comp":
        return "0"
    if f == "cd":
        return "1"
    if f == "sub":
        return "∞"
    if f == "ql":
        return "varia"
    if abs(rho - 1) < 1e-9:
        return "∞"
    return fmt(1 / (1 - rho))


# ---------------------------------------------------------------- caixa de Edgeworth (forma comum aos dois consumidores)
def _freeze(p):
    return tuple(sorted((k, tuple(sorted(v.items())) if isinstance(v, dict) else v) for k, v in p.items() if not callable(v)))


@st.cache_data(show_spinner=False, max_entries=256)
def _cached(name, key):
    p = {k: dict(v) if isinstance(v, tuple) else v for k, v in key}
    return getattr(_C, name)(p)


def cached(name, p):
    """Contas pesadas do equilíbrio geral, guardadas para não refazer a cada clique."""
    return _cached(name, _freeze(p))


def box_ic(p, who, u):
    """Curva de indiferença na caixa (B medido a partir do canto oposto)."""
    g = _C.agents(p)[0 if who == "A" else 1]
    xs, ys = _C.ces_level(u, g["d"], g["rho"], g["mode"], 10, 10)
    X = [None if y is None else (x if who == "A" else 10 - x) for x, y in zip(xs, ys)]
    Y = [None if (y is None or y > 10.5) else (y if who == "A" else 10 - y) for y in ys]
    return ln(X, Y, "Indiferença de " + who, COL["royal"] if who == "A" else COL["coral"], width=2.4)


def contract_trace(cc):
    return ln([q["x"] for q in cc], [q["y"] for q in cc], "Curva de contrato", COL["muted"], dash="dot", width=2.2)
