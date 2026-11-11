"""Capítulos 1, 2, 3, 4, 11, 17, 30, 31 e 36."""
import math
import plotly.graph_objects as go
import streamlit as st
from . import core as C
from .registry import page, CHAPTERS
from .ui import (split, group, rd, COL, SCALE, header, sl, tiles, fmt, sgn, chart, fig2d, fig3d, ln, dot, area, rect, arrow, budget,
                 pref_controls, pref_eqs, u_text)


def cols(n=3):
    return split(n)


def pick(label, options, key):
    """Radio com rótulos legíveis que devolve a chave interna."""
    return options[rd(label, list(options), key)]


def scatter(x, y, name, color):
    return go.Scatter(mode="markers", x=list(x), y=list(y), name=name, marker=dict(size=6, color=color, opacity=0.55),
                      hovertemplate=f"%{{x:.2f}} · %{{y:.2f}}<extra>{name}</extra>")


@page("mercado", 1)
def mercado():
    mid = "merc"
    header(1, CHAPTERS[1], "O mercado de apartamentos",
           "O exemplo de abertura do livro: inquilinos com preços de reserva diferentes disputam um número fixo de apartamentos. O preço de equilíbrio é o "
           "preço de reserva do primeiro que fica de fora. Compare concorrência, monopólio, discriminação perfeita e controle de aluguel.",
           [("Equilíbrio competitivo", r"p^*=r_{S+1}"), ("Monopolista", r"\max_{q\le S}\ q\cdot r_q"),
            ("Eficiência de Pareto", r"\text{os } S \text{ apartamentos vão para os } S \text{ maiores } r_i")])
    left, right = cols()
    with left:
        regime = pick("Forma de alocação", {"Concorrência": "comp", "Monopólio": "monop", "Discriminador perfeito": "discr", "Teto de aluguel": "teto"}, f"{mid}-regime")
        p = dict(regime=regime, N=sl(mid, "N", "Número de inquilinos interessados", 10, 60, 40, 1), S=sl(mid, "S", "Apartamentos disponíveis (S)", 1, 59, 20, 1),
                 Rmax=sl(mid, "Rmax", "Maior preço de reserva", 400, 2000, 1000, 50), Rmin=sl(mid, "Rmin", "Menor preço de reserva", 50, 390, 200, 10), ceil=400)
        if regime == "teto":
            p["ceil"] = sl(mid, "ceil", "Teto de aluguel", 50, 2000, 400, 10)
    r = C.apartments(p)
    with right:
        if p["S"] >= p["N"]:
            st.warning("Há mais apartamentos que inquilinos; o modelo usa S = N − 1.")
        if regime == "teto" and p["ceil"] >= r["pc"]:
            st.info("O teto está acima do preço de equilíbrio, então não tem efeito.")
        N = len(r["r"])
        tr = [ln(list(range(N + 1)), [*r["r"], r["r"][-1]], "Demanda (preços de reserva)", COL["navy"], width=3, shape="hv"),
              ln([r["S"], r["S"]], [0, p["Rmax"] * 1.08], "Oferta fixa (S)", COL["teal"], width=3)]
        if regime == "discr":
            xs, ys = [0], [0]
            for i in range(r["S"]):
                xs += [i, i + 1]
                ys += [r["r"][i], r["r"][i]]
            tr.append(area([*xs, r["S"]], [*ys, 0], "Cada um paga seu preço de reserva", "rgba(242,194,0,.38)"))
        elif r["price"] is not None:
            tr += [rect(0, r["rented"], 0, r["price"], "Receita dos proprietários", "rgba(242,194,0,.38)"),
                   ln([0, N], [r["price"]] * 2, "Teto de aluguel" if regime == "teto" else "Aluguel cobrado", COL["coral"], width=2.4, dash="dash")]
            if regime == "monop" and r["rented"] < r["S"]:
                tr.append(rect(r["rented"], r["S"], 0, p["Rmax"] * 0.04, "Apartamentos vazios", "rgba(210,85,58,.55)"))
            tr.append(dot(r["rented"], r["price"], "Escolha do monopolista" if regime == "monop" else "Equilíbrio", COL["yellow"], size=14))
        chart(fig2d(tr, "Número de apartamentos", "Aluguel", [0, N], [0, p["Rmax"] * 1.08]))
        tiles([dict(k="Aluguel", v="um por inquilino" if r["price"] is None else fmt(r["price"], 0), key=True, s="competitivo: " + fmt(r["pc"], 0)),
               dict(k="Apartamentos alugados", v=str(r["rented"]), s=f"de {r['S']}" + (f" · {r['demanders']} querem alugar" if r.get("demanders") else "")),
               dict(k="Excedente dos inquilinos · receita", v=f"{fmt(r['cs'], 0)} · {fmt(r['revenue'], 0)}"),
               dict(k="Eficiência de Pareto", v="Eficiente" if r["loss"] < 1e-6 else "Ineficiente",
                    chip=("Os que mais valorizam ficam com os apartamentos", "good") if r["loss"] < 1e-6 else ("Perda de " + fmt(r["loss"], 0), "bad"))])


@page("orcamento", 2)
def orcamento():
    mid = "orc"
    header(2, CHAPTERS[2], "Restrição orçamentária e políticas",
           "O conjunto orçamentário reúne as cestas que o consumidor pode pagar. Impostos, subsídios e racionamento mudam a inclinação, deslocam ou dobram a reta.",
           [("Reta orçamentária", r"p_1x_1+p_2x_2=m"), ("Inclinação", r"\frac{\Delta x_2}{\Delta x_1}=-\frac{p_1}{p_2}"), ("Imposto por unidade em x₁", r"(p_1+t)x_1+p_2x_2=m")])
    left, right = cols()
    with left:
        pol = pick("Política", {"Imposto por unidade": "unid", "Imposto ad valorem": "advalorem", "Subsídio por unidade": "subsidio", "Imposto fixo": "fixo",
                                "Racionamento de x₁": "racion", "Imposto só acima de x̄": "acima", "Nenhuma": "nenhuma"}, f"{mid}-pol")
        p = dict(pol=pol, p1=sl(mid, "p1", "Preço do bem 1 (p₁)", 0.5, 10.0, 2.0, 0.5), p2=sl(mid, "p2", "Preço do bem 2 (p₂)", 0.5, 10.0, 1.0, 0.5),
                 m=sl(mid, "m", "Renda (m)", 5, 100, 20, 1), t=2.0, tau=50, T=6, xbar=5.0)
        if pol in ("unid", "subsidio", "acima"):
            p["t"] = sl(mid, "t", "Valor por unidade (t)", 0.0, 10.0, 2.0, 0.5)
        if pol == "advalorem":
            p["tau"] = sl(mid, "tau", "Alíquota ad valorem (%)", 0, 200, 50, 5)
        if pol == "fixo":
            p["T"] = sl(mid, "T", "Imposto fixo (T)", 0, 100, 6, 1)
        if pol in ("racion", "acima"):
            p["xbar"] = sl(mid, "xbar", "Limite x̄", 0.5, 30.0, 5.0, 0.5)
    r = C.budget_set(p)
    with right:
        xm, ym = 1.12 * max(r["base"][1][0], r["x1max"]), 1.12 * max(r["base"][0][1], r["x2max"])
        poly = [(0, 0), *r["pts"], (r["pts"][-1][0], 0)]
        chart(fig2d([area([q[0] for q in poly], [q[1] for q in poly], "Novo conjunto orçamentário", "rgba(242,194,0,.32)"),
                     ln([q[0] for q in r["base"]], [q[1] for q in r["base"]], "Reta original", COL["muted"], dash="dash", width=2),
                     ln([q[0] for q in r["pts"]], [q[1] for q in r["pts"]], "Nova reta orçamentária", COL["navy"], width=3.2)],
                    "Bem 1 (x₁)", "Bem 2 (x₂)", [0, xm], [0, ym]))
        lost = r["lost"]
        tiles([dict(k="Máximo de x₁", v=fmt(r["x1max"]), key=True, s="antes: " + fmt(p["m"] / p["p1"])), dict(k="Máximo de x₂", v=fmt(r["x2max"]), key=True, s="antes: " + fmt(p["m"] / p["p2"])),
               dict(k="Inclinação (primeiro trecho)", v=fmt(r["slope0"]), s="antes: " + fmt(-p["p1"] / p["p2"])),
               dict(k="Cestas que deixaram de caber", v=fmt(100 * lost, 1) + "%",
                    chip=("Sem efeito", "info") if abs(lost) < 1e-9 else ("Conjunto encolheu", "warn") if lost > 0 else ("Conjunto cresceu", "good"))])


PREF_TEXT = {
    "cd": "Cobb-Douglas: bem-comportadas (monótonas e convexas). A TMS cai à medida que x₁ aumenta.",
    "sub": "Substitutos perfeitos: o consumidor troca os bens a uma taxa constante δ/(1−δ).",
    "comp": "Complementares perfeitos: só importa a combinação na proporção x₂ = k·x₁; o excesso de um bem não vale nada.",
    "ces": "CES: o grau de substituição ρ vai de complementares (ρ → −∞) a Cobb-Douglas (ρ = 0) e substitutos (ρ = 1).",
    "ql": "Quase-linear: as curvas são cópias umas das outras deslocadas na vertical; a TMS só depende de x₁.",
    "mal": "x₂ é um mal: para aceitar mais x₂, o consumidor exige mais x₁, então as curvas sobem.",
    "neutro": "x₂ é neutro: o consumidor não se importa com ele, e as curvas são verticais.",
    "saciedade": "Saciedade: existe um ponto de satisfação máxima em (5, 5); longe dele, mais pode ser pior.",
    "concava": "Preferências côncavas: o consumidor prefere os extremos às médias.",
}


PREF_FORMULA = {"cd": lambda a: f"u = x₁^{fmt(a)} · x₂^{fmt(1 - a)}", "sub": lambda a: f"u = {fmt(a)}·x₁ + x₂", "comp": lambda a: f"u = min({fmt(a)}·x₁, x₂)",
                "mal": lambda a: f"u = x₁ − {fmt(a)}·x₂", "neutro": lambda a: "u = x₁", "saciedade": lambda a: "u = −[(x₁ − 5)² + (x₂ − 5)²]", "concava": lambda a: "u = x₁² + x₂²"}


@page("preferencias", 3)
def preferencias():
    mid = "pref"
    header(3, CHAPTERS[3], "Preferências e curvas de indiferença",
           "Uma galeria dos formatos de preferência do capítulo: a CES (que inclui complementares perfeitos, Cobb-Douglas e substitutos perfeitos "
           "como casos especiais), a quase-linear e quatro casos atípicos. A seta aponta para as cestas preferidas, e a TMS mede quanto de x₂ o consumidor aceita "
           "trocar por uma unidade a mais de x₁.",
           [("Taxa marginal de substituição", r"TMS=\left.\frac{\Delta x_2}{\Delta x_1}\right|_{U}"), ("Monotonicidade", r"\text{mais é melhor}"),
            ("Convexidade", r"\text{médias são preferidas aos extremos}")])
    left, right = cols()
    with left:
        p = pref_controls(mid, value="cd", a=(0.5, 10, 0.1, 3), k=(0.2, 3, 0.1, 1), label="Tipo de preferência",
                          extra={"Um mal": "mal", "Bem neutro": "neutro", "Saciedade": "saciedade", "Côncavas": "concava"})
        p["am"] = 1.0
        if p["form"] == "mal":
            p["am"] = sl(mid, "am", "Incômodo de cada unidade de x₂ (a)", 0.2, 3.0, 1.0, 0.1, hint="u = x₁ − a·x₂. Cada unidade a mais de x₂ precisa ser compensada por a unidades de x₁.")
    std = p["form"] in ("ces", "ql")
    if std:
        u = lambda x, y: C.ces(x, y, p["delta"], p["rho"], p["mode"])
        mono, conv = True, not (p["mode"]["form"] == "ces" and p["rho"] > 1)
    else:
        f0, mono, conv = C.PREFS[p["form"]]
        u = lambda x, y: f0(x, y, p["am"])
    h, x0_, y0_ = 1e-5, 3.0, 5.5
    u1, u2 = (u(x0_ + h, y0_) - u(x0_ - h, y0_)) / (2 * h), (u(x0_, y0_ + h) - u(x0_, y0_ - h)) / (2 * h)
    r = dict(ref=(x0_, y0_), u1=u1, u2=u2, mono=mono, conv=conv, mrs=-C.INF if abs(u2) < 1e-9 else -u1 / u2)
    key = p["mode"]["form"] if std else p["form"]
    with right:
        ax = C.lin(0.05, 10, 90)
        z = [[u(x, y) for x in ax] for y in ax]
        x0, y0 = r["ref"]
        g = math.hypot(r["u1"], r["u2"]) or 1
        tip = (x0 + 1.6 * r["u1"] / g, y0 + 1.6 * r["u2"] / g)
        ann = [arrow(x0, y0, *tip, COL["coral"]), dict(x=tip[0], y=tip[1], text="preferidas", showarrow=False, yshift=12, font=dict(color=COL["coral"]))]
        chart(fig2d([go.Contour(x=ax, y=ax, z=z, colorscale=SCALE, ncontours=14, showscale=False, contours=dict(coloring="lines"), line=dict(width=2.2),
                                hovertemplate="x₁ %{x:.2f} · x₂ %{y:.2f}<br>U %{z:.2f}<extra></extra>"), dot(x0, y0, "Cesta de referência", COL["yellow"], size=12)],
                    "Bem 1 (x₁)", "Bem 2 (x₂)", [0, 10], [0, 10], square=True, legend=False, annotations=ann), height=580)
        tiles([dict(k="TMS na cesta de referência (3 ; 5,5)", v=fmt(r["mrs"]), key=True, s="positiva: um dos bens é um mal" if r["mrs"] > 0 else ""),
               dict(k="Monótonas?", v="Sim" if r["mono"] else "Não", chip=("Mais é melhor", "good") if r["mono"] else ("Mais nem sempre é melhor", "warn")),
               dict(k="Convexas?", v="Sim" if r["conv"] else "Não", chip=("Médias são preferidas", "good") if r["conv"] else ("Extremos são preferidos", "warn")),
               dict(k="Função de utilidade", v=u_text(key, p) if std else PREF_FORMULA[p["form"]](p["am"]), s=PREF_TEXT[key], small=True)])


@page("utilidade", 4)
def utilidade():
    mid = "util"
    header(4, CHAPTERS[4], "Utilidade e transformações monotônicas",
           "A utilidade é só um jeito de numerar as curvas de indiferença. Qualquer transformação crescente preserva as curvas e a TMS, mas muda a altura "
           "da superfície e as utilidades marginais.",
           [("Transformação monotônica", r"v=f(u),\ \ f'>0"), ("TMS", r"TMS=-\frac{UMg_1}{UMg_2}=-\frac{f'(u)\,u_1}{f'(u)\,u_2}")])
    left, right = cols()
    with left:
        p = pref_controls(mid, value="cd", a=(0.5, 5, 0.1, 1), k=(0.2, 3, 0.1, 1))
        pref_eqs(p, U="u")
        group("Transformação")
        f = pick("Transformação v = f(u)", {"u": "id", "2u + 1": "lin", "u³": "cubo", "e^(u/3)": "exp"}, f"{mid}-f")
        group("Cesta de referência")
        p["x1"] = sl(mid, "x1", "x₁", 0.5, 9.5, 3.0, 0.5)
        p["x2"] = sl(mid, "x2", "x₂", 0.5, 9.5, 5.0, 0.5)
    T = C.TRANSF[f]
    base_u = lambda x, y: C.ces(x, y, p["delta"], p["rho"], p["mode"])
    Uf = lambda x, y: T(base_u(x, y))
    h = 1e-5
    mu1 = (Uf(p["x1"] + h, p["x2"]) - Uf(p["x1"] - h, p["x2"])) / (2 * h)
    mu2 = (Uf(p["x1"], p["x2"] + h) - Uf(p["x1"], p["x2"] - h)) / (2 * h)
    r = dict(U=Uf, u=base_u(p["x1"], p["x2"]), fu=Uf(p["x1"], p["x2"]), mu1=mu1, mu2=mu2, mrs=-C.INF if abs(mu2) < 1e-12 else -mu1 / mu2)
    with right:
        t1, t2, t3 = st.tabs(["Superfície de utilidade", "Curvas de nível", "Utilidade marginal"])
        with t1:
            ax = C.lin(0.2, 10, 45)
            chart(fig3d([go.Surface(x=ax, y=ax, z=[[r["U"](x, y) for x in ax] for y in ax], colorscale=SCALE, showscale=False,
                                    contours=dict(z=dict(show=True, usecolormap=True, project=dict(z=True), width=2)),
                                    hovertemplate="x₁ %{x:.2f} · x₂ %{y:.2f}<br>v %{z:.2f}<extra></extra>")], "x₁", "x₂", "v = f(u)"), key=f"{mid}-1")
        with t2:
            ax = C.lin(0.2, 10, 90)
            chart(fig2d([go.Contour(x=ax, y=ax, z=[[r["U"](x, y) for x in ax] for y in ax], colorscale=SCALE, ncontours=14, showscale=False, line=dict(width=2),
                                    contours=dict(coloring="lines", showlabels=True, labelfont=dict(size=10, color=COL["navy"]))),
                         dot(p["x1"], p["x2"], "Cesta de referência", COL["yellow"], size=12)],
                        "Bem 1 (x₁)", "Bem 2 (x₂)", [0, 10], [0, 10], square=True, legend=False), height=580, key=f"{mid}-2")
        with t3:
            xs, h = C.lin(0.2, 10, 200), 1e-5
            mu = [(r["U"](x + h, p["x2"]) - r["U"](x - h, p["x2"])) / (2 * h) for x in xs]
            chart(fig2d([ln(xs, mu, "UMg₁ com a transformação escolhida", COL["navy"], width=3), dot(p["x1"], r["mu1"], "Cesta de referência", COL["yellow"], size=13)],
                        "Bem 1 (x₁), com x₂ fixo", "Utilidade marginal de x₁", [0, 10]), key=f"{mid}-3")
        tiles([dict(k="Função escolhida", small=True, v=u_text(p["mode"]["form"], p),
                    s="transformada: v = " + {"id": "u", "lin": "2u + 1", "cubo": "u³", "exp": "e^(u/3)"}[f]),
               dict(k="u na cesta · v = f(u)", v=f"{fmt(r['u'], 3)} · {fmt(r['fu'], 3)}", key=True),
               dict(k="Utilidades marginais UMg₁ ; UMg₂", v=f"{fmt(r['mu1'], 3)} ; {fmt(r['mu2'], 3)}", s="mudam com a transformação"),
               dict(k="TMS", v=fmt(r["mrs"], 3), key=True, chip=("Igual para qualquer transformação", "good"))])


@page("ativos", 11)
def ativos():
    mid = "atv"
    header(11, CHAPTERS[11], "Mercados de ativos",
           "Por arbitragem, ativos sem risco precisam render a taxa de juros. Daí saem o preço de um título, o preço de um recurso esgotável (que sobe à taxa r) "
           "e o momento ótimo de cortar uma floresta.",
           [("Título", r"P=\sum_{t=1}^{T}\frac{c}{(1+r)^t}+\frac{F}{(1+r)^T}"), ("Hotelling", r"p_t=p_0(1+r)^t,\ \ p_0=\frac{C}{(1+r)^{S/D}}"), ("Floresta", r"\frac{F'(T)}{F(T)}=r")])
    left, right = cols(1)
    with left:
        r_ = sl(mid, "r", "Taxa de juros (r)", 0.01, 0.30, 0.05, 0.005)
    t1, t2, t3 = st.tabs(["Preço de um título", "Recurso esgotável (Hotelling)", "Quando cortar a floresta"])
    with t1:
        c1, c2, c3 = st.columns(3)
        with c1:
            c = sl(mid, "c", "Cupom anual (c)", 0.0, 20.0, 5.0, 0.5)
        with c2:
            F = sl(mid, "F", "Valor de face (F)", 50, 200, 100, 10)
        with c3:
            T = sl(mid, "T", "Anos até o vencimento (T)", 1, 40, 10, 1)
        price = C.bond_price(c, F, T, r_)
        rs = C.lin(0.005, 0.3, 200)
        fig = fig2d([ln(rs, [C.bond_price(c, F, T, x) for x in rs], "Preço do título", COL["navy"], width=3, hover="r %{x:.1%} · P %{y:.2f}"),
                     ln([0, 0.3], [F, F], "Valor de face", COL["muted"], dash="dot", width=1.6), dot(r_, price, "Taxa atual", COL["yellow"], size=14)],
                    "Taxa de juros (r)", "Preço do título", [0, 0.3])
        fig.update_xaxes(tickformat=".0%")
        chart(fig, key=f"{mid}-1")
        par = abs(c / F - r_) < 1e-9
        tiles([dict(k="Preço do título", v=fmt(price), key=True, chip=("Ao par: cupom = taxa", "info") if par else ("Acima do par", "good") if price > F else ("Abaixo do par", "warn")),
               dict(k="Perpetuidade com o mesmo cupom", v=fmt(c / r_), s="c / r"), dict(k="Relação", v="Juros ↑ ⇒ preço ↓")])
    with t2:
        c1, c2, c3 = st.columns(3)
        with c1:
            S = sl(mid, "S", "Estoque do recurso (S)", 10, 500, 100, 10)
        with c2:
            D = sl(mid, "D", "Consumo anual (D)", 1, 50, 5, 1)
        with c3:
            Cb = sl(mid, "Cb", "Preço do substituto (C)", 10, 300, 100, 5)
        ho = C.hotelling(S, D, Cb, r_)
        ts = C.lin(0, ho["T"], 200)
        chart(fig2d([ln(ts, [ho["p0"] * (1 + r_) ** t for t in ts], "Trajetória do preço", COL["navy"], width=3), ln([0, ho["T"] * 1.05], [Cb, Cb], "Preço do substituto", COL["coral"], dash="dash", width=2),
                     dot(0, ho["p0"], "Preço hoje", COL["yellow"], size=14), dot(ho["T"], Cb, "Recurso se esgota", COL["coral"], size=11, edge="#fff")],
                    "Anos", "Preço do recurso", [0, ho["T"] * 1.05], [0, Cb * 1.12]), key=f"{mid}-2")
        tiles([dict(k="Preço hoje", v=fmt(ho["p0"]), key=True), dict(k="Anos até esgotar (S/D)", v=fmt(ho["T"], 1)),
               dict(k="Crescimento do preço", v=fmt(100 * r_, 1) + "% ao ano", s="igual à taxa de juros, por arbitragem")])
    with t3:
        k = sl(mid, "k", "Velocidade de crescimento das árvores (k)", 0.02, 0.30, 0.10, 0.01)
        fo = C.forest(100, k, r_)
        Tm = max(3 * fo["Ts"], 30)
        ts = C.lin(0.5, Tm, 300)
        chart(fig2d([ln(ts, [fo["F"](t) for t in ts], "Valor da madeira F(T)", COL["faint"], width=2.2), ln(ts, [fo["PV"](t) for t in ts], "Valor presente F(T)·e^(−rT)", COL["navy"], width=3),
                     dot(fo["Ts"], fo["PV"](fo["Ts"]), "Corte ótimo", COL["yellow"], size=14)],
                    "Idade da floresta (anos)", "Valor", [0, Tm], [0, 105]), key=f"{mid}-3")
        tiles([dict(k="Idade ótima de corte", v=fmt(fo["Ts"], 1) + " anos", key=True), dict(k="Valor presente máximo", v=fmt(fo["PV"](fo["Ts"]))),
               dict(k="Regra", v="F′/F = r", s="corta quando a madeira cresce mais devagar que o dinheiro no banco")])


@page("medicao", 17)
def medicao():
    mid = "med"
    header(17, CHAPTERS[17], "Medição: identificação e experimentos",
           "Os dados de preço e quantidade são equilíbrios, não pontos de uma curva só. Uma regressão recupera a demanda apenas quando é a oferta que se desloca. "
           "E comparar quem escolheu um tratamento com quem não escolheu mistura efeito com seleção; o sorteio resolve.",
           [("Demanda e oferta", r"Q=a-bP+u_d,\quad Q=c+dP+u_s"), ("Diferença de médias", r"\bar Y_{trat}-\bar Y_{ctrl}=\tau+\text{viés de seleção}")])
    t1, t2 = st.tabs(["Identificar a demanda", "Experimento × dados observacionais"])
    with t1:
        left, right = cols(4)
        with left:
            b = sl(mid, "b", "Inclinação da demanda (b)", 0.2, 3.0, 1.0, 0.1)
            d = sl(mid, "d", "Inclinação da oferta (d)", 0.2, 3.0, 1.0, 0.1)
            sd = sl(mid, "sd", "Choques de demanda (desvio-padrão)", 0.0, 3.0, 0.3, 0.1)
            ss = sl(mid, "ss", "Choques de oferta (desvio-padrão)", 0.0, 3.0, 1.5, 0.1)
        if sd == 0 and ss == 0:
            st.warning("Sem choques, todos os pontos caem no mesmo equilíbrio e não há o que estimar.")
        idf = C.identification(300, b, d, sd, ss)
        lo, hi = min(idf["Ps"]), max(idf["Ps"])
        pad = 0.15 * ((hi - lo) or 1)
        P0, P1 = lo - pad, hi + pad
        tr = [scatter(idf["Qs"], idf["Ps"], "Equilíbrios observados", COL["royal"]),
              ln([idf["a"] - b * P0, idf["a"] - b * P1], [P0, P1], "Demanda verdadeira", COL["navy"], width=3),
              ln([idf["c"] + d * P0, idf["c"] + d * P1], [P0, P1], "Oferta verdadeira", COL["teal"], width=3)]
        if idf["beta"] == idf["beta"]:
            tr.append(ln([idf["alpha"] + idf["beta"] * P0, idf["alpha"] + idf["beta"] * P1], [P0, P1], "Regressão de Q em P", COL["coral"], width=2.6, dash="dash"))
        fig = fig2d(tr, "Quantidade (Q)", "Preço (P)")
        chart(fig, key=f"{mid}-1")
        beta = idf["beta"]
        near = lambda x, y: abs(x - y) < 0.15
        chip = ("Identifica a demanda", "good") if near(beta, -b) else ("Identifica a oferta", "info") if near(beta, d) else ("Mistura das duas curvas", "bad")
        tiles([dict(k="Inclinação estimada dQ/dP", v=fmt(beta, 3), key=True, chip=chip if beta == beta else None), dict(k="Demanda verdadeira dQ/dP", v=fmt(-b)),
               dict(k="Oferta verdadeira dQ/dP", v=fmt(d)), dict(k="Regra", v="Oferta move, demanda aparece", s="choques de oferta revelam a demanda; choques de demanda revelam a oferta")])
    with t2:
        left, right = cols(2)
        with left:
            tau = sl(mid, "tau", "Efeito verdadeiro do tratamento (τ)", 0.0, 5.0, 2.0, 0.1)
            sel = sl(mid, "sel", "Força da autosseleção", 0.0, 2.0, 1.0, 0.05)
        ex = C.experiment(4000, tau, sel)
        fig = go.Figure([go.Bar(x=["Efeito verdadeiro", "Experimento (sorteio)", "Dados observacionais"], y=[tau, ex["rand"], ex["obs"]],
                                marker=dict(color=[COL["navy"], COL["teal"], COL["coral"]]), text=[fmt(tau), fmt(ex["rand"]), fmt(ex["obs"])], textposition="outside",
                                hovertemplate="%{x}: %{y:.2f}<extra></extra>")])
        fig.update_layout(font=dict(family="Archivo, Helvetica Neue, Arial, sans-serif", size=13, color=COL["ink"]), separators=",.", paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="#FFFFFF", showlegend=False, margin=dict(l=62, r=16, t=30, b=40))
        fig.update_yaxes(title_text="Efeito estimado", range=[0, max(tau, ex["obs"], ex["rand"], 1) * 1.25], gridcolor=COL["grid"])
        chart(fig, height=460, key=f"{mid}-2")
        tiles([dict(k="Efeito verdadeiro τ", v=fmt(tau), key=True), dict(k="Estimativa com sorteio", v=fmt(ex["rand"]), key=True, chip=("Sem viés de seleção", "good")),
               dict(k="Estimativa observacional", v=fmt(ex["obs"]), chip=("Viés pequeno", "info") if abs(ex["bias"]) < 0.15 else ("Viés de " + sgn(ex["bias"]), "bad"),
                    s="quem já teria resultado alto escolhe se tratar"),
               dict(k="Fração que escolheu o tratamento", v=fmt(100 * ex["share"], 1) + "%")])


@page("aplicacoes-jogos", 30)
def aplicacoes_jogos():
    mid = "apj"
    header(30, CHAPTERS[30], "Aplicações da teoria dos jogos",
           "Dois jogos do capítulo. No falcão-pombo, a população se estabiliza numa mistura em que as duas estratégias rendem o mesmo. "
           "Na barganha com ofertas alternadas, quem é mais paciente fica com a maior fatia.",
           [("Falcão-pombo (estratégia evolucionariamente estável)", r"h^*=\frac{V}{C}\ \ (V<C)"), ("Rubinstein", r"x_1^*=\frac{1-\delta_2}{1-\delta_1\delta_2}")])
    t1, t2 = st.tabs(["Coexistência: falcão e pombo", "Barganha de Rubinstein"])
    with t1:
        left, right = cols(2)
        with left:
            V = sl(mid, "V", "Valor do recurso disputado (V)", 1.0, 20.0, 4.0, 0.5)
            Cc = sl(mid, "Cc", "Custo de uma briga (C)", 1.0, 30.0, 10.0, 0.5)
        hd = C.hawk_dove(V, Cc)
        hs = C.lin(0, 1, 200)
        chart(fig2d([ln(hs, [hd["payH"](h) for h in hs], "Payoff de um falcão", COL["coral"], width=3), ln(hs, [hd["payD"](h) for h in hs], "Payoff de um pombo", COL["royal"], width=3),
                     dot(hd["h"], hd["payH"](hd["h"]), "Equilíbrio evolucionário", COL["yellow"], size=14)],
                    "Fração de falcões na população (h)", "Payoff esperado", [0, 1]), key=f"{mid}-1")
        tiles([dict(k="Fração de falcões", v=fmt(100 * hd["h"], 1) + "%", key=True, chip=("Só falcões: brigar compensa", "warn") if V >= Cc else ("Mistura estável", "good")),
               dict(k="Payoff médio", v=fmt(hd["avg"]), s="se todos fossem pombos: " + fmt(V / 2)), dict(k="Regra", v="h* = V / C", s="brigas caras mantêm os falcões raros")])
    with t2:
        left, right = cols(2)
        with left:
            d1 = sl(mid, "d1", "Paciência de quem propõe primeiro (δ₁)", 0.0, 0.99, 0.9, 0.01)
            d2 = sl(mid, "d2", "Paciência do outro jogador (δ₂)", 0.0, 0.99, 0.9, 0.01)
        x1 = C.rubinstein(d1, d2)
        ds = C.lin(0, 0.99, 200)
        chart(fig2d([ln(ds, [C.rubinstein(d1, d) for d in ds], "Fatia x₁* com δ₁ fixo", COL["navy"], width=3), ln([0, 1], [0.5, 0.5], "Divisão igual", COL["muted"], dash="dot", width=1.6),
                     dot(d2, x1, "Situação atual", COL["yellow"], size=14)],
                    "Paciência do outro jogador (δ₂)", "Fatia de quem propõe primeiro", [0, 1], [0, 1.05]), key=f"{mid}-2")
        tiles([dict(k="Fatia de quem propõe primeiro", v=fmt(100 * x1, 1) + "%", key=True), dict(k="Fatia do outro", v=fmt(100 * (1 - x1), 1) + "%"),
               dict(k="Acordo", v="Imediato", chip=("Ninguém perde com atraso", "good"), s="com δ₁ = δ₂ → 1, a divisão tende a 50/50")])


@page("comportamental", 31)
def comportamental():
    mid = "comp"
    header(31, CHAPTERS[31], "Economia comportamental",
           "Com desconto hiperbólico, a mesma pessoa prefere esperar quando as duas recompensas estão longe e muda de ideia quando a primeira fica perto. "
           "No ultimato, quem se incomoda com a desigualdade recusa ofertas baixas, mesmo perdendo dinheiro.",
           [("Desconto hiperbólico", r"D(t)=\frac{1}{1+ht}"), ("Desconto exponencial", r"D(t)=e^{-\rho t}"), ("Aversão à desigualdade", r"U_R=x-\alpha\max\{10-2x,0\}")])
    t1, t2 = st.tabs(["Viés do presente", "Jogo do ultimato"])
    with t1:
        left, right = cols()
        with left:
            A = sl(mid, "A", "Recompensa menor e mais cedo (A)", 10, 200, 100, 5)
            B = sl(mid, "B", "Recompensa maior e mais tarde (B)", 20, 400, 120, 5)
            k = sl(mid, "k", "Dias de espera entre A e B (k)", 1, 60, 7, 1)
            h = sl(mid, "h", "Impaciência hiperbólica (h)", 0.01, 2.0, 0.5, 0.01)
            rho = sl(mid, "rho", "Taxa de desconto exponencial (ρ)", 0.0, 0.2, 0.02, 0.005)
        if B <= A:
            st.warning("Escolha B maior que A para haver dilema entre esperar e não esperar.")
        pb = C.present_bias(A, B, k, h, rho)
        tS = pb["tStar"]
        tm = max(90, tS * 1.6 if tS == tS and tS > 0 else 0)
        ts = C.lin(0, tm, 300)
        tr = [ln(ts, [A * pb["H"](t) for t in ts], "A (hiperbólico)", COL["coral"], width=3), ln(ts, [B * pb["H"](t + k) for t in ts], "B (hiperbólico)", COL["navy"], width=3),
              ln(ts, [A * pb["E"](t) for t in ts], "A (exponencial)", COL["coral"], dash="dot", width=1.8), ln(ts, [B * pb["E"](t + k) for t in ts], "B (exponencial)", COL["navy"], dash="dot", width=1.8)]
        if tS == tS and 0 < tS < tm:
            tr.append(dot(tS, A * pb["H"](tS), "Reversão de preferência", COL["yellow"], size=14))
        chart(fig2d(tr, "Dias até a recompensa A", "Valor presente", [0, tm]), key=f"{mid}-1")
        rev = pb["nowH"] != pb["farH"]
        tiles([dict(k="Escolha hoje (hiperbólico)", v=pb["nowH"], key=True),
               dict(k="Escolha daqui a 60 dias (hiperbólico)", v=pb["farH"], key=True, chip=("Inconsistência temporal", "bad") if rev else ("Consistente", "good")),
               dict(k="Dia da reversão", v=fmt(tS, 1) if (rev and tS == tS and tS > 0) else "—", s="antes dele prefere A; depois, B"),
               dict(k="Desconto exponencial", v=f"{pb['nowE']} e {pb['farE']}", chip=("Nunca reverte", "info"))])
    with t2:
        left, right = cols(2)
        with left:
            al = sl(mid, "al", "Inveja do respondente (α)", 0.0, 3.0, 1.0, 0.05)
            bp = sl(mid, "bp", "Culpa do proponente (β)", 0.0, 1.0, 0.2, 0.05)
        ul = C.ultimatum(al, bp)
        xs = C.lin(0, 10, 201)
        fig = fig2d([ln(xs, [ul["uR"](x) for x in xs], "Aceitar", COL["navy"], width=3), ln([0, 10], [0, 0], "Recusar (os dois ficam sem nada)", COL["coral"], dash="dash", width=2),
                     dot(ul["thr"], 0, "Menor oferta aceita", COL["coral"], size=11, edge="#fff"), dot(ul["offer"], ul["uR"](ul["offer"]), "Oferta do proponente", COL["yellow"], size=14)],
                    "Oferta ao respondente (de 10)", "Utilidade do respondente", [0, 10])
        fig.update_yaxes(rangemode="normal")
        chart(fig, key=f"{mid}-2")
        tiles([dict(k="Menor oferta aceita", v=fmt(ul["thr"]), key=True, s="de um total de 10"),
               dict(k="Oferta do proponente", v=fmt(ul["offer"]), key=True, chip=("Divide meio a meio por culpa", "info") if bp >= 0.5 else ("Oferece o mínimo aceitável", "warn")),
               dict(k="Payoffs (proponente ; respondente)", v=f"{fmt(ul['prop'])} ; {fmt(ul['offer'])}", s="sem aversão à desigualdade, a oferta seria quase zero")])


@page("tecnologia-informacao", 36)
def tecnologia_informacao():
    mid = "ti"
    header(36, CHAPTERS[36], "Tecnologia da informação",
           "Quando o valor de um produto cresce com o número de usuários, há dois equilíbrios com usuários: um pequeno e instável (a massa crítica) e um grande e estável. "
           "E quando dois monopolistas vendem bens complementares, uma fusão reduz o preço total.",
           [("Rede", r"p=n(1-n)\ \Rightarrow\ n=\frac{1\pm\sqrt{1-4p}}{2}"), ("Complementos separados", r"p_A=p_B=\frac{a+c}{3}"), ("Fusão", r"p_A+p_B=\frac{a+2c}{2}")])
    t1, t2 = st.tabs(["Externalidades de rede", "Complementos e fusões"])
    with t1:
        price = sl(mid, "p", "Preço da assinatura (p)", 0.01, 0.35, 0.16, 0.005)
        nw = C.network(price)
        ns = C.lin(0, 1, 200)
        tr = [ln(ns, [n * (1 - n) for n in ns], "Disposição a pagar p = n(1 − n)", COL["navy"], width=3), ln([0, 1], [price, price], "Preço", COL["coral"], dash="dash", width=2)]
        if nw["ok"]:
            tr += [dot(nw["nLow"], price, "Massa crítica (instável)", "#fff", size=12), dot(nw["nHigh"], price, "Equilíbrio estável", COL["yellow"], size=14)]
        tr.append(dot(0, 0, "Ninguém usa (estável)", COL["muted"], size=10, edge="#fff"))
        chart(fig2d(tr, "Fração de usuários (n)", "Disposição a pagar do usuário marginal", [0, 1], [0, 0.38]), key=f"{mid}-1")
        if nw["ok"]:
            tiles([dict(k="Massa crítica", v=fmt(100 * nw["nLow"], 1) + "%", key=True, s="abaixo dela a rede encolhe até sumir"),
                   dict(k="Equilíbrio estável", v=fmt(100 * nw["nHigh"], 1) + "%", key=True),
                   dict(k="Dinâmica", v="Entre os dois, a rede cresce", chip=("Dois equilíbrios estáveis: 0 e o alto", "info"))])
        else:
            tiles([dict(k="Usuários", v="0", key=True, chip=("Preço alto demais: a rede não decola", "bad"), s="preço máximo sustentável: 0,25")])
    with t2:
        left, right = cols(2)
        with left:
            a = sl(mid, "a", "Intercepto da demanda conjunta (a)", 20, 150, 90, 1)
            c = sl(mid, "c", "Custo marginal de cada bem (c)", 0, 20, 0, 1)
        co = C.complements(a, c)
        if not co["ok"]:
            st.warning("Com a ≤ 2c ninguém compra o sistema; aumente a demanda ou reduza o custo.")
        xs = [0, a]
        chart(fig2d([ln(xs, [(a + c - pa) / 2 for pa in xs], "Reação da empresa B", COL["royal"], width=3), ln([(a + c - pb) / 2 for pb in xs], xs, "Reação da empresa A", COL["navy"], width=3),
                     ln([0, co["Pm"]], [co["Pm"], 0], "Preços com fusão (soma ótima)", COL["coral"], dash="dash", width=2.2),
                     dot(co["pi"], co["pi"], "Empresas separadas", COL["yellow"], size=14), dot(co["Pm"] / 2, co["Pm"] / 2, "Empresa fundida", COL["coral"], size=12, edge="#fff")],
                    "Preço do bem A (p_A)", "Preço do bem B (p_B)", [0, a * 0.8], [0, a * 0.8], square=True), height=560, key=f"{mid}-2")
        tiles([dict(k="Preço total separado · fundido", v=f"{fmt(co['Pind'])} · {fmt(co['Pm'])}", key=True, chip=("A fusão baixa o preço", "good")),
               dict(k="Quantidade separada · fundida", v=f"{fmt(co['xi'])} · {fmt(co['xm'])}"),
               dict(k="Lucro total separado · fundido", v=f"{fmt(2 * co['profInd'])} · {fmt(co['profM'])}", s="consumidores e empresas ganham com a fusão")])
