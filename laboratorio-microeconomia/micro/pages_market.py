"""Capítulos 25 a 29: poder de mercado e estratégia."""
import streamlit as st
from . import core as C
from .registry import page, CHAPTERS
from .ui import split, group, cb, COL, header, sl, tiles, fmt, chart, fig2d, ln, dot, area, rect


def cols(n=3):
    return split(n)


@page("monopolio", 25)
def monopolio():
    mid = "monop"
    header(25, CHAPTERS[25], "Monopólio com demanda linear",
           "O monopolista produz onde a receita marginal iguala o custo marginal e cobra o que a demanda aceita pagar por essa quantidade. A diferença para a concorrência é o peso morto.",
           [("Problema", r"\max_q (a-bq)q-cq"), ("Solução", r"q^m=\frac{a-c}{2b},\ \ p^m=\frac{a+c}{2}"), ("Lerner", r"L=\frac{p-c}{p}")])
    left, right = cols()
    with left:
        p = dict(a=sl(mid, "a", "Intercepto da demanda (a)", 10, 100, 50, 1), b=sl(mid, "b", "Inclinação da demanda (b)", 0.1, 5.0, 1.0, 0.1),
                 c=sl(mid, "c", "Custo marginal (c)", 0, 100, 10, 1))
    r = C.monopoly(p)
    with right:
        qx = p["a"] / p["b"]
        tr = []
        if r["ok"]:
            tr += [area([0, 0, r["qm"]], [p["a"], r["pm"], r["pm"]], "Excedente do consumidor", "rgba(42,100,184,.16)"),
                   rect(0, r["qm"], p["c"], r["pm"], "Lucro do monopolista", "rgba(242,194,0,.42)"),
                   area([r["qm"], r["qc"], r["qm"]], [r["pm"], p["c"], p["c"]], "Peso morto", "rgba(210,85,58,.42)")]
        else:
            st.warning("O custo marginal precisa ficar abaixo do intercepto da demanda (c < a); caso contrário não vale a pena produzir.")
        tr += [ln([0, qx], [p["a"], 0], "Demanda p = a − bq", COL["navy"], width=3), ln([0, p["a"] / (2 * p["b"])], [p["a"], 0], "Receita marginal", COL["royal"], dash="dash", width=2.4),
               ln([0, qx], [p["c"], p["c"]], "Custo marginal", COL["coral"], width=2.4)]
        if r["ok"]:
            tr += [ln([r["qm"]] * 2, [0, r["pm"]], "q de monopólio", COL["muted"], dash="dot", width=1.4, legend=False),
                   dot(r["qm"], r["pm"], "Monopólio (qᵐ, pᵐ)", COL["yellow"], size=14), dot(r["qc"], p["c"], "Concorrência", COL["coral"], size=10, edge="#fff")]
        chart(fig2d(tr, "Quantidade (q)", "Preço, receita e custo", [0, qx * 1.02], [0, p["a"] * 1.05]))
        if r["ok"]:
            tiles([dict(k="Quantidade qᵐ", v=fmt(r["qm"]), key=True, s="concorrência: " + fmt(r["qc"])), dict(k="Preço pᵐ", v=fmt(r["pm"]), key=True, s="concorrência: " + fmt(p["c"])),
                   dict(k="Lucro", v=fmt(r["profit"])),
                   dict(k="Peso morto", v=fmt(r["dwl"]), chip=("−" + fmt(100 * r["dwl"] / (r["dwl"] + r["profit"] + r["cs"]), 1) + "% do excedente", "bad")),
                   dict(k="Índice de Lerner", v=fmt(r["lerner"], 3), s="igual a 1/|ε| no ótimo")])


@page("discriminacao", 26)
def discriminacao():
    mid = "disc"
    header(26, CHAPTERS[26], "Discriminação de preços",
           "Se pode separar os mercados, o monopolista iguala a receita marginal de cada um ao custo marginal e cobra mais caro onde a demanda é menos elástica. "
           "Com discriminação perfeita, captura todo o excedente.",
           [("3º grau", r"RMg_1=RMg_2=CMg"), ("Markup", r"p_i\left(1-\frac{1}{|\varepsilon_i|}\right)=c"), ("Duas partes", r"p=c,\ \ T=EC(c)")])
    left, right = cols()
    with left:
        group("Mercado 1")
        p = dict(a1=sl(mid, "a1", "Intercepto (a₁)", 20, 150, 100, 1), b1=sl(mid, "b1", "Inclinação (b₁)", 0.1, 5.0, 1.0, 0.1))
        group("Custo")
        p["c"] = sl(mid, "c", "Custo marginal (c)", 0, 60, 20, 1)
    with right:
        t1, t2 = st.tabs(["3º grau: dois mercados", "1º grau e tarifa em duas partes"])
        with t1:
            c1, c2 = st.columns(2)
            with c1:
                p["a2"] = sl(mid, "a2", "Mercado 2: intercepto (a₂)", 20, 150, 60, 1)
            with c2:
                p["b2"] = sl(mid, "b2", "Mercado 2: inclinação (b₂)", 0.1, 5.0, 0.5, 0.1)
            r = C.discrimination(p)
            qx = max(p["a1"] / p["b1"], p["a2"] / p["b2"])
            chart(fig2d([ln([0, p["a1"] / p["b1"]], [p["a1"], 0], "Demanda 1", COL["navy"], width=3), ln([0, p["a1"] / (2 * p["b1"])], [p["a1"], 0], "RMg 1", COL["navy"], dash="dash", width=1.8),
                         ln([0, p["a2"] / p["b2"]], [p["a2"], 0], "Demanda 2", COL["teal"], width=3), ln([0, p["a2"] / (2 * p["b2"])], [p["a2"], 0], "RMg 2", COL["teal"], dash="dash", width=1.8),
                         ln([0, qx], [p["c"], p["c"]], "Custo marginal", COL["coral"], width=2.4),
                         ln([0, qx], [r["Pu"], r["Pu"]], "Preço único (sem discriminar)", COL["muted"], dash="dot", width=1.8),
                         dot(r["m1"]["q"], r["m1"]["p"], "Mercado 1", COL["yellow"], size=13), dot(r["m2"]["q"], r["m2"]["p"], "Mercado 2", COL["yellow"], size=13, symbol="diamond")],
                        "Quantidade (q)", "Preço", [0, qx * 1.02], [0, max(p["a1"], p["a2"]) * 1.05]), key=f"{mid}-1")
            gain = 100 * (r["profDisc"] / r["profUni"] - 1) if r["profUni"] > 0 else None
            tiles([dict(k="Preço no mercado 1", v=fmt(r["m1"]["p"]), key=True, s=f"|ε₁| = {fmt(r['e1'])} · q₁ = {fmt(r['m1']['q'])}"),
                   dict(k="Preço no mercado 2", v=fmt(r["m2"]["p"]), key=True, s=f"|ε₂| = {fmt(r['e2'])} · q₂ = {fmt(r['m2']['q'])}"),
                   dict(k="Lucro discriminando", v=fmt(r["profDisc"]), chip=("+" + fmt(gain, 1) + "% sobre o preço único", "good") if gain is not None else None),
                   dict(k="Preço único ótimo", v=fmt(r["Pu"]), s="lucro: " + fmt(r["profUni"]))])
        with t2:
            qx = p["a1"] / p["b1"]
            tr = []
            if r["Qc"] > 0:
                tr += [area([0, 0, r["Qc"]], [p["a1"], p["c"], p["c"]], "Lucro com discriminação perfeita (todo o excedente)", "rgba(242,194,0,.38)"),
                       rect(0, r["m1"]["q"], p["c"], r["m1"]["p"], "Lucro do monopólio simples", "rgba(10,30,87,.18)")]
            tr += [ln([0, qx], [p["a1"], 0], "Demanda", COL["navy"], width=3), ln([0, p["a1"] / (2 * p["b1"])], [p["a1"], 0], "Receita marginal", COL["royal"], dash="dash", width=2.2),
                   ln([0, qx], [p["c"], p["c"]], "Custo marginal", COL["coral"], width=2.4)]
            if r["Qc"] > 0:
                tr += [dot(r["m1"]["q"], r["m1"]["p"], "Monopólio simples", COL["navy"], size=10, edge="#fff"), dot(r["Qc"], p["c"], "Discriminação perfeita", COL["yellow"], size=14)]
            chart(fig2d(tr, "Quantidade (q)", "Preço", [0, qx * 1.02], [0, p["a1"] * 1.05]), key=f"{mid}-2")
            tiles([dict(k="Lucro do monopólio simples", v=fmt(r["simpleProfit"]), s="preço " + fmt(r["m1"]["p"])),
                   dict(k="Lucro com discriminação perfeita", v=fmt(r["perfect"]), key=True, s="produz até P = CMg: q = " + fmt(r["Qc"])),
                   dict(k="Tarifa em duas partes", v=f"p = {fmt(p['c'])} ; T = {fmt(r['perfect'])}", key=True, s="taxa fixa = excedente a p = c"),
                   dict(k="Peso morto eliminado", v=fmt(r["perfect"] - r["simpleProfit"] - r["simpleCS"]), chip=("Eficiente", "good"))])


@page("monopsonio", 27)
def monopsonio():
    mid = "monops"
    header(27, CHAPTERS[27], "Monopsônio com oferta linear",
           "Um único comprador de trabalho percebe que contratar mais eleva o salário de todos. Ele contrata onde o custo marginal do fator iguala o valor do produto marginal.",
           [("Oferta", r"w(q)=a+bq"), ("CMg do fator", r"CMgF=a+2bq"), ("Ótimo", r"CMgF=VPMg\Rightarrow q^*=\frac{VPMg-a}{2b}")])
    left, right = cols()
    with left:
        p = dict(a=sl(mid, "a", "Intercepto da oferta (a)", 1, 50, 10, 1), b=sl(mid, "b", "Inclinação da oferta (b)", 0.1, 5.0, 1.0, 0.1),
                 vmp=sl(mid, "vmp", "Valor do produto marginal (VPMg)", 10, 100, 50, 1))
    r = C.monopsony(p)
    with right:
        qx = 1.2 * r["qc"] if r["ok"] else 10
        tr = []
        if r["ok"]:
            tr += [rect(0, r["qm"], r["wm"], p["vmp"], "Ganho do monopsonista", "rgba(242,194,0,.42)"),
                   area([r["qm"], r["qc"], r["qm"]], [p["vmp"], p["vmp"], r["wm"]], "Peso morto", "rgba(210,85,58,.42)")]
        else:
            st.warning("O VPMg precisa ficar acima do intercepto da oferta (VPMg > a) para valer a pena contratar.")
        tr += [ln([0, qx], [p["a"], p["a"] + p["b"] * qx], "Oferta de trabalho", COL["navy"], width=3),
               ln([0, qx], [p["a"], p["a"] + 2 * p["b"] * qx], "Custo marginal do fator", COL["royal"], dash="dash", width=2.4),
               ln([0, qx], [p["vmp"], p["vmp"]], "VPMg", COL["coral"], width=2.4)]
        if r["ok"]:
            tr += [dot(r["qm"], r["wm"], "Monopsônio (q*, w*)", COL["yellow"], size=14), dot(r["qc"], p["vmp"], "Concorrência", COL["coral"], size=10, edge="#fff")]
        chart(fig2d(tr, "Quantidade de trabalho (q)", "Salário e valor", [0, qx], [0, max(p["vmp"] * 1.25, p["a"] * 1.2)]))
        if r["ok"]:
            tiles([dict(k="Emprego q*", v=fmt(r["qm"]), key=True, s="concorrência: " + fmt(r["qc"])), dict(k="Salário w*", v=fmt(r["wm"]), key=True, s="concorrência: " + fmt(r["wc"])),
                   dict(k="Peso morto", v=fmt(r["dwl"])), dict(k="Taxa de exploração (VPMg − w)/w", v=fmt(100 * r["exploit"], 1) + "%")])


@page("oligopolio", 28)
def oligopolio():
    mid = "olig"
    header(28, CHAPTERS[28], "Oligopólio: Cournot, Stackelberg, Bertrand e cartel",
           "Duas empresas com produto homogêneo e demanda linear. A forma de competir (quantidade simultânea, liderança, preço ou conluio) muda preço, quantidade e lucros.",
           [("Demanda", r"P=a-b(q_1+q_2)"), ("Reação", r"q_1=\frac{a-c_1-bq_2}{2b}"), ("Cournot com n", r"P=\frac{a+nc}{n+1}\to c")])
    left, right = cols()
    with left:
        p = dict(a=sl(mid, "a", "Intercepto da demanda (a)", 40, 150, 100, 1), b=sl(mid, "b", "Inclinação da demanda (b)", 0.2, 3.0, 1.0, 0.1),
                 c1=sl(mid, "c1", "Custo marginal da empresa 1 (c₁)", 0, 40, 10, 1), c2=sl(mid, "c2", "Custo marginal da empresa 2 (c₂)", 0, 40, 10, 1))
    r = C.oligopoly(p)
    regs = [(r["cart"], "Cartel", COL["coral"], "triangle-up"), (r["stack"], "Stackelberg (1 lidera)", COL["teal"], "diamond"),
            (r["cournot"], "Cournot", COL["yellow"], "circle"), (r["bert"], "Bertrand", COL["navy"], "square")]
    with right:
        t1, t2, t3 = st.tabs(["Funções de reação", "Comparação na demanda", "Cournot com n empresas"])
        with t1:
            lim = (p["a"] - min(p["c1"], p["c2"])) / p["b"]
            qs = C.lin(0, lim, 300)

            def iso(q1):
                if q1 <= 0:
                    return None
                v = (p["a"] - p["c1"] - p["b"] * q1 - r["stack"]["pi1"] / q1) / p["b"]
                return v if v >= 0 else None
            tr = [ln([r["R1"](q) for q in qs], qs, "Reação da empresa 1", COL["navy"], width=3), ln(qs, [r["R2"](q) for q in qs], "Reação da empresa 2", COL["royal"], width=3),
                  ln([0, r["cart"]["Q"]], [r["cart"]["Q"], 0], "Produção do cartel", COL["coral"], dash="dot", width=1.6),
                  ln(qs, [iso(q) for q in qs], "Isolucro da líder em Stackelberg", COL["teal"], dash="dash", width=1.8)]
            tr += [dot(g["q1"], g["q2"], n, c, symbol=s, size=13, edge=COL["navy"] if c == COL["yellow"] else "#fff") for g, n, c, s in regs]
            chart(fig2d(tr, "Produção da empresa 1 (q₁)", "Produção da empresa 2 (q₂)", [0, lim * 1.02], [0, lim * 1.02], square=True), key=f"{mid}-1")
        with t2:
            qx = p["a"] / p["b"]
            tr = [ln([0, qx], [p["a"], 0], "Demanda", COL["navy"], width=3), ln([0, qx], [p["c1"], p["c1"]], "c₁", COL["coral"], dash="dash", width=1.8)]
            if abs(p["c1"] - p["c2"]) > 1e-9:
                tr.append(ln([0, qx], [p["c2"], p["c2"]], "c₂", COL["coral"], dash="dot", width=1.8))
            tr += [dot(g["Q"], g["P"], n, c, symbol=s, size=13, edge=COL["navy"] if c == COL["yellow"] else "#fff") for g, n, c, s in regs]
            chart(fig2d(tr, "Quantidade total (Q)", "Preço (P)", [0, qx], [0, p["a"] * 1.05]), key=f"{mid}-2")
        rows = [(r["cournot"], "Cournot"), (r["stack"], "Stackelberg"), (r["bert"], "Bertrand"), (r["cart"], "Cartel")]
        with t1:
            tiles([dict(k=n, v="P = " + fmt(g["P"]), key=i == 0, s=f"q₁ = {fmt(g['q1'])} · q₂ = {fmt(g['q2'])}<br>π₁ = {fmt(g['pi1'])} · π₂ = {fmt(g['pi2'])}") for i, (g, n) in enumerate(rows)])
        with t2:
            tiles([dict(k=n, v="P = " + fmt(g["P"]), key=i == 0, s=f"Q = {fmt(g['Q'])} · π total = {fmt(g['pi1'] + g['pi2'])}") for i, (g, n) in enumerate(rows)])
        with t3:
            n = sl(mid, "n", "Número de empresas (n), todas com custo c₁", 1, 30, 3, 1)
            ns = list(range(1, 31))
            fig = fig2d([ln([0, 31], [p["c1"]] * 2, "Custo marginal (concorrência)", COL["coral"], dash="dash", width=2),
                         ln([0, 31], [(p["a"] + p["c1"]) / 2] * 2, "Preço de monopólio", COL["muted"], dash="dot", width=1.6),
                         ln(ns, [r["nP"](k) for k in ns], "Preço de Cournot", COL["navy"], width=2.4),
                         dot(n, r["nP"](n), "n atual", COL["yellow"], size=14)],
                        "Número de empresas (n)", "Preço de equilíbrio", [0, 31], [0, (p["a"] + p["c1"]) / 2 * 1.1])
            fig.data[2].mode = "lines+markers"
            chart(fig, key=f"{mid}-3")
            qi = max(0.0, (p["a"] - p["c1"]) / ((n + 1) * p["b"]))
            P = r["nP"](n)
            tiles([dict(k=f"Preço com n = {n}", v=fmt(P), key=True, s=f"monopólio: {fmt((p['a'] + p['c1']) / 2)} · concorrência: {fmt(p['c1'])}"),
                   dict(k="Quantidade total", v=fmt(r["nQ"](n))), dict(k="Lucro de cada empresa", v=fmt((P - p["c1"]) * qi)),
                   dict(k="Índice de Lerner (P − c)/P", v=fmt((P - p["c1"]) / P, 3) if P > 0 else "—", s="cai como 1/(n·|ε|)")])


GAME_PRESETS = {
    "Batalha dos sexos": dict(A11=2, B11=1, A12=0, B12=0, A21=0, B21=0, A22=1, B22=2),
    "Dilema dos prisioneiros": dict(A11=3, B11=3, A12=0, B12=4, A21=4, B21=0, A22=1, B22=1),
    "Coordenação": dict(A11=4, B11=4, A12=0, B12=1, A21=1, B21=0, A22=2, B22=2),
    "Galinha": dict(A11=0, B11=0, A12=-1, B12=1, A21=1, B21=-1, A22=-10, B22=-10),
    "Cara ou coroa": dict(A11=1, B11=-1, A12=-1, B12=1, A21=-1, B21=1, A22=1, B22=-1),
}
ROWS, COLS = ["Alto", "Baixo"], ["Esquerda", "Direita"]


def _load_preset(mid):
    for k, v in GAME_PRESETS[st.session_state[f"{mid}-preset"]].items():
        st.session_state[f"{mid}-{k}"] = v


@page("jogos", 29)
def jogos():
    mid = "jogos"
    header(29, CHAPTERS[29], "Teoria dos jogos: jogos 2×2",
           "Edite os payoffs ou escolha um exemplo. O app encontra equilíbrios de Nash em estratégias puras e mistas, estratégias dominantes e a solução por indução retroativa quando A joga primeiro.",
           [("Nash", r"u_A(s_A^*,s_B^*)\ge u_A(s_A,s_B^*),\ u_B(s_A^*,s_B^*)\ge u_B(s_A^*,s_B)"), ("Misto", r"q^*:\ A\ \text{indiferente};\ p^*:\ B\ \text{indiferente}")])
    for k, v in GAME_PRESETS["Batalha dos sexos"].items():
        st.session_state.setdefault(f"{mid}-{k}", v)
    left, right = cols(0)
    with left:
        st.selectbox("Exemplo", list(GAME_PRESETS), key=f"{mid}-preset", on_change=_load_preset, args=(mid,))
        group("Payoffs (A, B)")
        p = {}
        for i, rw in enumerate(ROWS):
            st.markdown(f"**A joga {rw}**")
            cs = st.columns(4)
            for j, cl in enumerate(COLS):
                with cs[2 * j]:
                    p[f"A{i + 1}{j + 1}"] = st.number_input(f"A em {cl}", min_value=-100, max_value=100, step=1, key=f"{mid}-A{i + 1}{j + 1}")
                with cs[2 * j + 1]:
                    p[f"B{i + 1}{j + 1}"] = st.number_input(f"B em {cl}", min_value=-100, max_value=100, step=1, key=f"{mid}-B{i + 1}{j + 1}")
    r = C.game(p)
    name = lambda c: f"({ROWS[c[0]]}, {COLS[c[1]]})"

    def table(hits):
        h = '<table class="gtable"><tr><th></th>' + "".join(f"<th>B: {c}</th>" for c in COLS) + "</tr>"
        for i in range(2):
            h += f"<tr><th>A: {ROWS[i]}</th>" + "".join(
                f'<td class="{"hit" if (i, j) in hits else ""}"><span class="a">{fmt(r["A"][i][j], 0)}</span> , <span class="b">{fmt(r["B"][i][j], 0)}</span></td>' for j in range(2)) + "</tr>"
        st.markdown(h + "</table>", unsafe_allow_html=True)

    with right:
        t1, t2 = st.tabs(["Jogo simultâneo", "Jogo sequencial (A joga primeiro)"])
        with t1:
            table(set(r["pure"]))

            def path(dlt, flip):
                d0, d1 = dlt(0), dlt(1)
                if abs(d0) < 1e-12 and abs(d1) < 1e-12:
                    return None
                if d0 * d1 > 0:
                    v = 1 if d0 > 0 else 0
                    pts = ([v, v], [0, 1])
                else:
                    s = 0 if d0 == d1 else d0 / (d0 - d1)
                    before = (1 if d0 > 0 else 0) if abs(d0) > 1e-12 else (0 if d1 > 0 else 1)
                    pts = ([before, before, 1 - before, 1 - before], [0, s, s, 1])
                return (pts[1], pts[0]) if flip else pts
            tr = []
            pa, pb = path(r["dltA"], False), path(r["dltB"], True)
            if pa:
                tr.append(ln(*pa, "Melhor resposta de A", COL["navy"], width=4))
            if pb:
                tr.append(ln(*pb, "Melhor resposta de B", COL["coral"], width=4, dash="dash"))
            tr += [dot(1 if i == 0 else 0, 1 if j == 0 else 0, "Nash em estratégias puras", COL["yellow"], size=16, legend=k == 0) for k, (i, j) in enumerate(r["pure"])]
            if r["mixed"]:
                tr.append(dot(r["mixed"]["p"], r["mixed"]["q"], "Nash em estratégias mistas", COL["teal"], size=14, symbol="diamond", edge="#fff"))
            fig = fig2d(tr, "Prob. de A jogar Alto (p)", "Prob. de B jogar Esquerda (q)", [0, 1], [0, 1], square=True)
            fig.update_xaxes(zeroline=False, dtick=0.25); fig.update_yaxes(zeroline=False, dtick=0.25)
            chart(fig, key=f"{mid}-1")
            ineff = [c for c in r["pure"] if r["pareto_dominated"](c)]
            dom = lambda d, L: "nenhuma" if d is None else L[d]
            tiles([dict(k="Nash em estratégias puras", v="<br>".join(map(name, r["pure"])) or "nenhum", key=True),
                   dict(k="Nash em estratégias mistas", v=f"p = {fmt(r['mixed']['p'], 3)} ; q = {fmt(r['mixed']['q'], 3)}" if r["mixed"] else "nenhum",
                        s="p: prob. de Alto · q: prob. de Esquerda"),
                   dict(k="Estratégias dominantes", v=f"A: {dom(r['domA'], ROWS)} · B: {dom(r['domB'], COLS)}"),
                   dict(k="Eficiência de Pareto", v="Há equilíbrio ineficiente" if ineff else ("Equilíbrios eficientes" if r["pure"] else "—"),
                        chip=(name(ineff[0]) + " é dominado no sentido de Pareto", "bad") if ineff else None)])
        with t2:
            i, j = r["seq"]
            table({(i, j)})
            nodes = {"A": (0.5, 2), 0: (0.25, 1), 1: (0.75, 1)}
            leaf = lambda a, b: (0.125 + 0.5 * a + 0.25 * b, 0)
            tr, ann = [], []

            def edge(fr, to, label, on, path_):
                tr.append(ln([fr[0], to[0]], [fr[1], to[1]], label, COL["gold"] if path_ else (COL["navy"] if on else COL["faint"]),
                             width=6 if path_ else (3 if on else 2), legend=False))
                ann.append(dict(x=(fr[0] + to[0]) / 2, y=(fr[1] + to[1]) / 2, text=label, showarrow=False, xshift=-30 if to[0] < fr[0] else 30,
                                font=dict(size=12.5, color=COL["navy"])))
            for a in range(2):
                edge(nodes["A"], nodes[a], ROWS[a], i == a, i == a)
                for b in range(2):
                    edge(nodes[a], leaf(a, b), COLS[b], r["b_resp"](a) == b, i == a and r["b_resp"](a) == b)
            for t, xy in (("A", nodes["A"]), ("B", nodes[0]), ("B", nodes[1])):
                tr.append(dot(*xy, "Nó de " + t, COL["navy"] if t == "A" else COL["royal"], size=26, edge="#fff", legend=False))
                ann.append(dict(x=xy[0], y=xy[1], text=f"<b>{t}</b>", showarrow=False, font=dict(color="#fff", size=13)))
            for a in range(2):
                for b in range(2):
                    x, y = leaf(a, b)
                    ann.append(dict(x=x, y=y, text=f"({fmt(r['A'][a][b], 0)}, {fmt(r['B'][a][b], 0)})", showarrow=False, yshift=-20,
                                    font=dict(size=14, color=COL["navy"] if (a, b) == (i, j) else COL["muted"])))
            fig = fig2d(tr, "", "", [0, 1], [-0.45, 2.25], legend=False, annotations=ann)
            fig.update_xaxes(visible=False); fig.update_yaxes(visible=False)
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=20, b=40))
            chart(fig, key=f"{mid}-2")
            same = (i, j) in r["pure"]
            tiles([dict(k="Resultado por indução retroativa", v=name(r["seq"]), key=True, s=f"payoffs: ({fmt(r['A'][i][j], 0)}, {fmt(r['B'][i][j], 0)})"),
                   dict(k="Estratégia de B", v=f"Alto → {COLS[r['b_resp'](0)]}; Baixo → {COLS[r['b_resp'](1)]}"),
                   dict(k="Comparação com o jogo simultâneo", v="Coincide com um Nash" if same else "Difere",
                        chip=("Mesmo resultado", "info") if same else ("Jogar primeiro muda o resultado", "warn"))])
