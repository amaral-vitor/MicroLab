"""Modelos prioritários: subitens dos capítulos 6, 8, 10, 24, 25, 26, 32, 33, 35 e 38."""
import math
import streamlit as st
from . import core as C
from .registry import page, CHAPTERS, PAGES
from .ui import (split, group, rd, COL, header, sl, tiles, fmt, sgn, chart, fig2d, ln, dot, area, rect, arrow, budget, ic_traces,
                 pref_controls, pref2_controls, pref_eqs, AGENT_EQ, cached, box_ic, contract_trace)

# rótulos de navegação dos modelos que já existiam nesses capítulos
NAV = {"demanda": "Renda-consumo, Engel e preço-consumo", "slutsky": "Decomposição de Slutsky e Hicks", "intertemporal": "Escolha intertemporal",
       "oferta-industria": "Entrada e saída", "monopolio": "Monopólio com demanda linear", "discriminacao": "1º e 3º graus",
       "edgeworth": "Primeiro Teorema do Bem-Estar", "crusoe": "Robinson Crusoé", "externalidades": "Pigou e tragédia dos comuns",
       "informacao-assimetrica": "Limões e sinalização"}
for _e in PAGES:
    if _e["id"] in NAV:
        _e["nav"] = NAV[_e["id"]]


def cols(n=3):
    return split(n)


def pick(label, options, key):
    return options[rd(label, list(options), key)]


def cost_params(mid):
    return dict(a=sl(mid, "a", "Custo variável: termo linear (a)", 2.0, 20.0, 10.0, 0.5, hint="Custo variável c(y) = a·y − b·y² + c·y³: o CVMe tem formato de U, com mínimo em y = b/(2c)."),
                b=sl(mid, "b", "Custo variável: termo quadrático (b)", 0.5, 4.0, 2.0, 0.1), c=sl(mid, "c", "Custo variável: termo cúbico (c)", 0.05, 1.0, 0.2, 0.01),
                F=sl(mid, "F", "Custo fixo (F)", 0, 100, 20, 1))


def slutsky_figure(S, p1, p1n, p2, e1, e2, xlab, ylab, utility):
    """Gráfico de Slutsky com dotação (A → B → C → D), usado no cap. 10."""
    A, B, Cc, D = S["A"], S["B"], S["C"], S["D"]
    xm = 1.12 * max(S["m0"] / min(p1, p1n), S["m1"] / p1n, S["mS"] / p1n, e1)
    ym = 1.12 * max(S["m0"], S["m1"], S["mS"]) / p2
    ic = lambda z, name, color: ln(*C.ces_level(utility(z), *utility.params, xm, ym), name, color, width=2)
    far = lambda u, v: math.hypot(u["x1"] - v["x1"], u["x2"] - v["x2"]) > xm * 0.03
    ann = []
    for u, v, c in ((A, B, COL["gold"]), (B, Cc, COL["muted"]), (Cc, D, COL["coral"])):
        if far(u, v):
            ann.append(arrow(u["x1"], u["x2"], v["x1"], v["x2"], c))
    return fig2d([ic(A, "Indiferença inicial", COL["royal"]), ic(D, "Indiferença final", COL["faint"]),
                  budget(S["m0"], p1, p2, "Orçamento inicial", COL["navy"], width=2.8), budget(S["mS"], p1n, p2, "Girado em torno de A (substituição)", COL["gold"], dash="dash", width=2.2),
                  budget(S["m0"], p1n, p2, "Preço novo, riqueza antiga", COL["muted"], dash="dot", width=2), budget(S["m1"], p1n, p2, "Orçamento final", COL["coral"], width=2.8),
                  dot(e1, e2, "Dotação", COL["ink"], symbol="square", size=11, edge="#fff", text="ω", tp="bottom left"),
                  dot(A["x1"], A["x2"], "A: inicial", COL["navy"], size=11, edge="#fff", text="A", tp="top left"),
                  dot(B["x1"], B["x2"], "B: após substituição", COL["yellow"], size=12, text="B", tp="bottom left"),
                  dot(Cc["x1"], Cc["x2"], "C: após efeito renda comum", COL["muted"], size=11, edge="#fff", text="C", tp="bottom right"),
                  dot(D["x1"], D["x2"], "D: final", COL["coral"], size=12, edge="#fff", text="D", tp="top right")],
                 xlab, ylab, [0, xm], [0, ym], annotations=ann)


@page("giffen", 6, nav="Bens inferiores e de Giffen")
def giffen():
    mid = "giff"
    header(6, CHAPTERS[6], "Bens inferiores e de Giffen",
           "Um bem é inferior quando a demanda cai com a renda. Se o efeito renda for forte o bastante para superar o efeito substituição, o bem é de Giffen: "
           "a demanda sobe quando o preço sobe. Este exemplo usa a função de utilidade de Haagsma (2012), uma das poucas com demanda de Giffen em forma fechada.",
           [("Utilidade", r"u=\ln(x_1-\gamma_1)-\beta\ln(\gamma_2-x_2),\ \ \beta>1"), ("Demanda", r"x_1=\frac{(p_2\gamma_2-m)+\beta p_1\gamma_1}{(\beta-1)p_1}"),
            ("Giffen", r"\frac{\partial x_1}{\partial p_1}>0\iff m>p_2\gamma_2")])
    left, right = cols()
    with left:
        p = dict(be=sl(mid, "be", "Força da aversão a se aproximar do limite de x₂ (β)", 1.5, 4.0, 2.0, 0.1, hint="Com β > 1, x₁ é sempre um bem inferior nesta função."),
                 g1=sl(mid, "g1", "Consumo mínimo de x₁ (γ₁)", 0.5, 5.0, 3.0, 0.1), g2=sl(mid, "g2", "Limite de x₂ (γ₂)", 6.0, 20.0, 10.0, 0.5))
        group("Preços e renda")
        p.update(m=sl(mid, "m", "Renda (m)", 5.0, 30.0, 12.0, 0.5), p1=sl(mid, "p1", "Preço do bem 1 (p₁)", 0.5, 3.0, 1.0, 0.05),
                 p2=sl(mid, "p2", "Preço do bem 2 (p₂)", 0.5, 3.0, 1.0, 0.05))
    r = C.giffen_stats(p)
    with right:
        if not r["ok"]:
            st.warning("Com esses valores não há solução interior: a função só vale com x₁ > γ₁ e 0 ≤ x₂ < γ₂. Ajuste a renda ou os preços.")
        t1, t2 = st.tabs(["Curva de renda-consumo", "Curva de demanda"])
        with t1:
            ms = [p["m"] * f for f in (0.85, 1, 1.15)]
            xm, ym = 1.1 * max(ms) / p["p1"], min(p["g2"] * 1.15, 1.1 * max(ms) / p["p2"])
            tr = [ln([0, xm], [p["g2"]] * 2, "Limite de x₂ (γ₂)", COL["muted"], dash="dot", width=1.4),
                  ln([p["g1"]] * 2, [0, ym], "Consumo mínimo de x₁ (γ₁)", COL["muted"], dash="dot", width=1.4, legend=False)]
            for i, m in enumerate(ms):
                d = C.giffen(p, m=m)
                tr.append(budget(m, p["p1"], p["p2"], "Orçamento atual" if i == 1 else "Renda 15% menor ou maior", COL["navy"] if i == 1 else COL["muted"],
                                 width=3 if i == 1 else 1.8, dash="solid" if i == 1 else "dash", legend=i < 2))
                if d["ok"]:
                    U = C.u_giffen(d["x1"], d["x2"], p)
                    xs = C.lin(p["g1"] + 1e-3, xm, 300)
                    tr.append(ln(xs, [p["g2"] - math.exp((math.log(x - p["g1"]) - U) / p["be"]) for x in xs], "Curva de indiferença" if i == 1 else "Outras curvas",
                                 COL["royal"] if i == 1 else COL["faint"], width=2.4 if i == 1 else 1.5, legend=i < 2))
                    tr.append(dot(d["x1"], d["x2"], "Cestas ótimas", COL["yellow"] if i == 1 else "#fff", size=14 if i == 1 else 10, legend=i == 1))
            path = [C.giffen(p, m=m) for m in C.lin(p["m"] * 0.5, p["m"] * 1.6, 200)]
            tr.append(ln([d["x1"] if d["ok"] else None for d in path], [d["x2"] if d["ok"] else None for d in path], "Curva de renda-consumo", COL["coral"], width=3))
            chart(fig2d(tr, "Bem 1 (x₁)", "Bem 2 (x₂)", [0, xm], [0, ym]), key=f"{mid}-1")
        with t2:
            ps = C.lin(0.3, 3, 300)
            pts = [C.giffen(p, p1=q) for q in ps]
            xs = [d["x1"] if d["ok"] else None for d in pts]
            valid = [v for v in xs if v is not None]
            tr = [ln(xs, ps, "Curva de demanda", COL["navy"], width=3, hover="x₁ %{x:.2f} · p₁ %{y:.2f}")]
            if r["ok"]:
                tr.append(dot(r["x1"], p["p1"], "Preço atual", COL["yellow"], size=14))
            chart(fig2d(tr, "Quantidade do bem 1 (x₁)", "Preço do bem 1 (p₁)", [0, 1.15 * max(valid + [r["x1"] if r["ok"] else 1])], [0, 3]), key=f"{mid}-2")
        if r["ok"]:
            tiles([dict(k="x₁* ; x₂*", v=f"{fmt(r['x1'])} ; {fmt(r['x2'])}", key=True), dict(k="Elasticidade-renda de x₁", v=fmt(r["em"]), key=True, chip=("Bem inferior", "bad")),
                   dict(k="Elasticidade-preço de x₁", v=fmt(r["ep"]), key=True, chip=("Giffen: a lei da demanda falha", "bad") if r["ep"] > 0 else ("Comum", "good")),
                   dict(k="Limiar de Giffen", v="m > " + fmt(r["mStar"]), s="abaixo dessa renda, x₁ é inferior mas comum")])


@page("demanda-compensada", 8, nav="Demanda comum × compensada")
def demanda_compensada():
    mid = "dcomp"
    header(8, CHAPTERS[8], "Demanda comum × demanda compensada",
           "A demanda comum (marshalliana) mantém a renda fixa; a compensada (hicksiana) ajusta a renda para manter a utilidade inicial. A diferença entre as duas "
           "inclinações é o efeito renda. Para um bem normal, a curva comum é mais achatada.",
           [("Comum", r"x_1(p_1,p_2,m)"), ("Compensada", r"h_1(p_1,p_2,\bar u)=x_1\big(p_1,p_2,e(p_1,p_2,\bar u)\big)"),
            ("Slutsky", r"\frac{\partial x_1}{\partial p_1}=\frac{\partial h_1}{\partial p_1}-x_1\frac{\partial x_1}{\partial m}")])
    left, right = cols()
    with left:
        p = pref_controls(mid, value="ces", a=(1, 20, 0.5, 5))
        pref_eqs(p)
        group("Preços e renda")
        group("Preços e renda")
        p.update(w=sl(mid, "w", "Renda (m)", 10, 300, 100, 5), p1=sl(mid, "p1", "Preço do bem 1 (p₁)", 1.0, 30.0, 10.0, 0.5), p2=sl(mid, "p2", "Preço do bem 2 (p₂)", 1.0, 30.0, 10.0, 0.5))
    r = C.compensated(p)
    with right:
        ps = C.lin(0.3 * p["p1"], 3 * p["p1"], 300)
        xm, xh = [r["mar"](q) for q in ps], [r["hic"](q) for q in ps]
        mx = max([v for v in xm + xh if v == v and abs(v) != math.inf] + [0])
        chart(fig2d([ln(xm, ps, "Demanda comum (renda fixa)", COL["navy"], width=3, hover="x₁ %{x:.2f} · p₁ %{y:.2f}"),
                     ln(xh, ps, "Demanda compensada (utilidade fixa)", COL["coral"], width=3, dash="dash", hover="x₁ %{x:.2f} · p₁ %{y:.2f}"),
                     dot(r["A"]["x1"], p["p1"], "Cesta atual", COL["yellow"], size=14)],
                    "Quantidade do bem 1 (x₁)", "Preço do bem 1 (p₁)", [0, 1.1 * mx if mx > 1e-9 else p["w"] / p["p1"]], [0, 3 * p["p1"]]))
        d = r["eM"] - r["eH"]
        chip = ("Bem normal: a comum é mais elástica", "good") if r["eM"] < r["eH"] - 1e-6 else ("Sem efeito renda", "info") if abs(d) < 1e-6 else ("Bem inferior", "warn")
        tiles([dict(k="x₁ ao preço atual", v=fmt(r["A"]["x1"]), key=True), dict(k="Elasticidade comum", v=fmt(r["eM"], 3), key=True),
               dict(k="Elasticidade compensada", v=fmt(r["eH"], 3), key=True, s="só efeito substituição"),
               dict(k="Efeito renda na elasticidade", v=fmt(d, 3), chip=chip if d == d else None)])


@page("inflacao", 10, nav="Inflação e taxa de juros real")
def inflacao():
    mid = "infl"
    header(10, CHAPTERS[10], "Inflação e taxa de juros real",
           "O que importa para a escolha entre hoje e amanhã é a taxa de juros real: quanto consumo futuro se ganha por unidade de consumo de hoje. "
           "Com inflação, a taxa nominal exagera esse ganho.",
           [("Taxa real", r"1+\rho=\frac{1+r}{1+\pi}\ \Rightarrow\ \rho\approx r-\pi"), ("Orçamento real", r"c_1+\frac{c_2}{1+\rho}=m_1+\frac{m_2}{1+\rho}")])
    left, right = cols()
    with left:
        p = pref_controls(mid, w="beta", wl="Peso do consumo presente (β)", x1="c₁", x2="c₂", value="ces", a=(0.5, 15, 0.5, 4))
        pref_eqs(p, v1="c_1", v2="c_2", w=r"\beta")
        group("Juros, inflação e renda (em termos reais)")
        p.update(r=sl(mid, "r", "Taxa de juros nominal (r)", 0.0, 0.5, 0.15, 0.01), pi=sl(mid, "pi", "Inflação (π)", 0.0, 0.5, 0.10, 0.01),
                 m1=sl(mid, "m1", "Renda no período 1 (m₁)", 0.0, 20.0, 5.0, 0.5), m2=sl(mid, "m2", "Renda no período 2 (m₂)", 0.0, 20.0, 5.0, 0.5))
    if p["m1"] + p["m2"] == 0:
        st.warning("Com renda zero nos dois períodos não há o que escolher.")
        return
    r = C.inflation(p)
    with right:
        xm, ym = 1.2 * max(r["W"], r["Wn"]), 1.2 * max((1 + r["real"]) * r["W"], (1 + p["r"]) * r["Wn"])
        chart(fig2d([*ic_traces(r["U"], p["beta"], p["rho"], p["mode"], xm, ym, C.ces_level),
                     ln([0, r["Wn"]], [(1 + p["r"]) * r["Wn"], 0], "Se ignorasse a inflação (taxa r)", COL["muted"], dash="dash", width=2),
                     ln([0, r["W"]], [(1 + r["real"]) * r["W"], 0], "Orçamento real (taxa ρ)", COL["navy"], width=3),
                     dot(p["m1"], p["m2"], "Dotação (m₁, m₂)", COL["ink"], symbol="square", size=11, edge="#fff"), dot(r["c1"], r["c2"], "Consumo ótimo", COL["yellow"], size=14)],
                    "Consumo no período 1 (c₁)", "Consumo no período 2 (c₂)", [0, xm], [0, ym]))
        s = r["s"]
        tiles([dict(k="Taxa de juros real ρ", v=fmt(100 * r["real"]) + "%", key=True, s="aproximação r − π: " + fmt(100 * (p["r"] - p["pi"])) + "%",
                    chip=("Real negativa: poupar encolhe o poder de compra", "warn") if r["real"] < 0 else None),
               dict(k="c₁* ; c₂*", v=f"{fmt(r['c1'])} ; {fmt(r['c2'])}", key=True),
               dict(k="Poupança s = m₁ − c₁", v=sgn(s), chip=("Nem poupa nem toma", "info") if abs(s) < 1e-3 else ("Poupador", "good") if s > 0 else ("Tomador", "warn"))])


class _Util:
    """Utilidade CES para o gráfico de Slutsky intertemporal."""
    def __init__(self, p):
        self.p = p
        self.params = (p["beta"], p["rho"], p["mode"])

    def __call__(self, z):
        return C.ces(z["x1"], z["x2"], self.p["beta"], self.p["rho"], self.p["mode"])


@page("slutsky-intertemporal", 10, nav="Slutsky intertemporal")
def slutsky_intertemporal():
    mid = "slint"
    header(10, CHAPTERS[10], "Slutsky intertemporal: o que acontece quando os juros sobem",
           "A taxa de juros é o preço do consumo presente, e a renda de cada período funciona como uma dotação. Por isso a equação de Slutsky com dotação explica a reação a "
           "uma mudança de juros: um tomador que vê os juros subirem certamente consome menos hoje; para um poupador, o efeito é ambíguo.",
           [("Preço do consumo presente", r"p_1=1+r,\quad p_2=1"), ("Slutsky com dotação", r"\frac{\Delta c_1}{\Delta r}=\frac{\Delta c_1^{s}}{\Delta r}+(m_1-c_1)\frac{\Delta c_1^{m}}{\Delta m}")])
    left, right = cols()
    with left:
        p = pref_controls(mid, w="beta", wl="Peso do consumo presente (β)", x1="c₁", x2="c₂", value="ces", a=(0.5, 15, 0.5, 4))
        pref_eqs(p, v1="c_1", v2="c_2", w=r"\beta")
        group("Juros e renda")
        p.update(r=sl(mid, "r", "Taxa de juros inicial (r)", 0.0, 1.0, 0.05, 0.01), rn=sl(mid, "rn", "Nova taxa de juros (r′)", 0.0, 1.0, 0.5, 0.01),
                 m1=sl(mid, "m1", "Renda no período 1 (m₁)", 0.0, 20.0, 8.0, 0.5), m2=sl(mid, "m2", "Renda no período 2 (m₂)", 0.0, 20.0, 2.0, 0.5))
    if p["m1"] + p["m2"] == 0:
        st.warning("Com renda zero nos dois períodos não há o que escolher.")
        return
    S = C.intertemporal_slutsky(p)
    with right:
        chart(slutsky_figure(S, 1 + p["r"], 1 + p["rn"], 1, p["m1"], p["m2"], "Consumo no período 1 (c₁)", "Consumo no período 2 (c₂)", _Util(p)))
        up, saver, borrower = p["rn"] > p["r"], S["net0"] > 1e-3, S["net0"] < -1e-3
        verdict = ((("Tomador: com juros maiores, certamente consome menos hoje", "bad") if up else ("Tomador: com juros menores, ganha e consome mais hoje", "good")) if borrower
                   else ("Poupador: os efeitos se opõem; o resultado é ambíguo", "info") if saver else ("Nem poupa nem toma", "info"))
        tiles([dict(k="Efeito substituição sobre c₁", v=sgn(S["sub"]), key=True), dict(k="Efeito renda comum", v=sgn(S["inc"]), key=True),
               dict(k="Efeito renda dotação", v=sgn(S["endow"]), key=True), dict(k="Efeito total sobre c₁", v=sgn(S["tot"]), chip=verdict)])


@page("imposto-longo-prazo", 24, nav="Imposto no curto e no longo prazo")
def imposto_longo_prazo():
    mid = "implp"
    header(24, CHAPTERS[24], "Imposto no curto e no longo prazo",
           "A indústria parte do equilíbrio de longo prazo. Um imposto por unidade é dividido entre consumidores e empresas no curto prazo, quando o número de empresas está fixo. "
           "No longo prazo, empresas saem até o lucro voltar a zero, e o preço sobe exatamente o valor do imposto: o consumidor paga tudo.",
           [("Curto prazo", r"n\,y(P-t)=D(P)"), ("Longo prazo", r"P=\min CMe+t")])
    left, right = cols()
    with left:
        group("Custo de cada empresa")
        p = cost_params(mid)
        group("Mercado e imposto")
        p.update(Dmax=sl(mid, "Dmax", "Demanda a preço zero", 50, 1000, 300, 10), d=sl(mid, "d", "Sensibilidade da demanda ao preço (d)", 1.0, 20.0, 5.0, 0.5),
                 t=sl(mid, "t", "Imposto por unidade (t)", 0.0, 10.0, 2.0, 0.25))
    r = C.tax_runs(p)
    with right:
        if not r["ok"]:
            st.warning("Com esses coeficientes o custo variável fica negativo em algum trecho; aumente o termo linear (a) ou o cúbico (c).")
            return
        Qx, top = p["Dmax"] * 1.02, max(r["Pmax"], r["Plr"]) * 1.05
        P0s, P1s = C.lin(r["minAVC"], top, 200), C.lin(r["minAVC"] + p["t"], top, 200)
        chart(fig2d([ln([0, p["Dmax"]], [r["Pmax"], 0], "Demanda", COL["navy"], width=3),
                     ln([0, *[r["S0"](P) for P in P0s]], [r["minAVC"], *P0s], "Oferta de curto prazo sem imposto", COL["coral"], dash="dash", width=2),
                     ln([0, *[r["S"](P) for P in P1s]], [r["minAVC"] + p["t"], *P1s], "Oferta de curto prazo com imposto", COL["coral"], width=2.8),
                     ln([0, Qx], [r["P0"]] * 2, "Oferta de longo prazo sem imposto", COL["teal"], dash="dash", width=2),
                     ln([0, Qx], [r["Plr"]] * 2, "Oferta de longo prazo com imposto", COL["teal"], width=2.8),
                     dot(r["Q0"], r["P0"], "Equilíbrio inicial", COL["ink"], size=10, edge="#fff"), dot(r["Qsr"], r["Psr"], "Curto prazo com imposto", COL["yellow"], size=14),
                     dot(r["Qlr"], r["Plr"], "Longo prazo com imposto", COL["teal"], size=12, edge="#fff")],
                    "Quantidade da indústria (Q)", "Preço (P)", [0, Qx], [0, top]))
        if p["t"] > 0:
            tiles([dict(k="Alta de preço no curto prazo", v="+" + fmt(r["Psr"] - r["P0"]), key=True, s=fmt(100 * (r["Psr"] - r["P0"]) / p["t"], 1) + "% do imposto"),
                   dict(k="Alta de preço no longo prazo", v="+" + fmt(r["Plr"] - r["P0"]), key=True, chip=("O consumidor paga 100%", "warn")),
                   dict(k="Número de empresas", v=f"{fmt(r['n'], 1)} → {fmt(r['nlr'], 1)}", s="saem até o lucro voltar a zero"),
                   dict(k="Quantidade", v=f"{fmt(r['Q0'])} → {fmt(r['Qsr'])} → {fmt(r['Qlr'])}", s="inicial → curto prazo → longo prazo")])
        else:
            tiles([dict(k="Imposto", v="zero", s="aumente t para ver o efeito", key=True)])


@page("imposto-monopolio", 25, nav="Imposto sobre o monopolista")
def imposto_monopolio():
    mid = "impmon"
    header(25, CHAPTERS[25], "Imposto sobre o monopolista",
           "Um imposto por unidade eleva o custo marginal do monopolista. Com demanda linear, ele repassa metade ao preço; com elasticidade constante, repassa mais do que "
           "o próprio imposto, porque aplica o mesmo markup sobre o custo maior.",
           [("Linear", r"\Delta p=\tfrac{1}{2}\,t"), ("Elasticidade constante", r"p=\frac{\varepsilon}{\varepsilon-1}(c+t)\ \Rightarrow\ \Delta p=\frac{\varepsilon}{\varepsilon-1}\,t")])
    left, right = cols()
    with left:
        kind = pick("Tipo de demanda", {"Linear": "lin", "Elasticidade constante": "ce"}, f"{mid}-kind")
        p = dict(kind=kind, a=100, b=1.0, eps=2.0)
        if kind == "lin":
            p.update(a=sl(mid, "a", "Intercepto da demanda (a)", 20, 150, 100, 1), b=sl(mid, "b", "Inclinação da demanda (b)", 0.2, 5.0, 1.0, 0.1))
        else:
            p["eps"] = sl(mid, "eps", "Elasticidade da demanda (|ε|)", 1.2, 5.0, 2.0, 0.1, hint="Demanda q = 1.000·p^(−ε). Precisa ser maior que 1 para o monopolista ter ótimo.")
        p.update(c=sl(mid, "c", "Custo marginal (c)", 1, 50, 20, 1), t=sl(mid, "t", "Imposto por unidade (t)", 0, 30, 10, 1))
    r = C.mono_tax(p)
    with right:
        if kind == "lin" and r["q1"] <= 0:
            st.warning("O imposto é tão alto que o monopolista deixa de produzir.")
        if kind == "ce":
            qmax = r["q0"] * 2.2
            qs = C.lin(max(1, r["q1"] * 0.3), qmax, 300)
            pq = lambda q: (q / 1000) ** (-1 / p["eps"])
            fig = fig2d([ln(qs, [pq(q) for q in qs], "Demanda", COL["navy"], width=3), ln(qs, [pq(q) * (1 - 1 / p["eps"]) for q in qs], "Receita marginal", COL["royal"], dash="dash", width=2.2),
                         ln([0, qmax], [p["c"]] * 2, "Custo marginal", COL["coral"], dash="dash", width=2), ln([0, qmax], [p["c"] + p["t"]] * 2, "Custo marginal + imposto", COL["coral"], width=2.6),
                         dot(r["q0"], r["p0"], "Sem imposto", COL["ink"], size=10, edge="#fff"), dot(r["q1"], r["p1"], "Com imposto", COL["yellow"], size=14)],
                        "Quantidade (q)", "Preço e custo", [0, qmax], [0, r["p1"] * 1.6])
        else:
            qx = p["a"] / p["b"]
            fig = fig2d([ln([0, qx], [p["a"], 0], "Demanda", COL["navy"], width=3), ln([0, qx / 2], [p["a"], 0], "Receita marginal", COL["royal"], dash="dash", width=2.2),
                         ln([0, qx], [p["c"]] * 2, "Custo marginal", COL["coral"], dash="dash", width=2), ln([0, qx], [p["c"] + p["t"]] * 2, "Custo marginal + imposto", COL["coral"], width=2.6),
                         dot(r["q0"], r["p0"], "Sem imposto", COL["ink"], size=10, edge="#fff"), dot(r["q1"], r["p1"], "Com imposto", COL["yellow"], size=14)],
                        "Quantidade (q)", "Preço e custo", [0, qx * 1.02], [0, p["a"] * 1.05])
        chart(fig)
        tiles([dict(k="Preço sem imposto → com imposto", v=f"{fmt(r['p0'])} → {fmt(r['p1'])}", key=True),
               dict(k="Repasse ao preço", v=fmt(100 * r["pass_"], 1) + "% do imposto", key=True,
                    chip=("Repassa mais que o imposto", "bad") if r["pass_"] > 1 + 1e-9 else ("Repassa uma parte", "info")),
               dict(k="Quantidade", v=f"{fmt(r['q0'])} → {fmt(r['q1'])}")])


@page("monopolio-natural", 25, nav="Monopólio natural")
def monopolio_natural():
    mid = "monnat"
    header(25, CHAPTERS[25], "Monopólio natural e regulação",
           "Com um custo fixo alto e custo marginal constante, o custo médio cai sempre, e uma só empresa atende o mercado mais barato. Cobrar o custo marginal é eficiente, "
           "mas dá prejuízo; cobrar o custo médio cobre os custos, com algum peso morto.",
           [("Custo", r"C(q)=F+cq,\quad CMe=c+\frac{F}{q}"), ("Preço = CMe", r"a-bq=c+\frac{F}{q}")])
    left, right = cols(4)
    with left:
        p = dict(a=sl(mid, "a", "Intercepto da demanda (a)", 20, 150, 100, 1), b=sl(mid, "b", "Inclinação da demanda (b)", 0.2, 5.0, 1.0, 0.1),
                 c=sl(mid, "c", "Custo marginal (c)", 0, 50, 10, 1), F=sl(mid, "F", "Custo fixo (F)", 0, 3000, 1000, 50))
    r = C.natural_mono(p)
    with right:
        if not r["ok"]:
            st.warning("Nenhum preço cobre o custo médio com essa demanda: o serviço só existe com subsídio.")
        qx = p["a"] / p["b"]
        qs = C.lin(qx / 200, qx, 300)
        tr = [ln([0, qx], [p["a"], 0], "Demanda", COL["navy"], width=3), ln([0, qx / 2], [p["a"], 0], "Receita marginal", COL["royal"], dash="dash", width=2),
              ln(qs, [p["c"] + p["F"] / q for q in qs], "Custo médio", COL["teal"]), ln([0, qx], [p["c"]] * 2, "Custo marginal", COL["coral"], width=2.2),
              dot(r["qm"], r["pm"], "Monopólio sem regulação", COL["yellow"], size=14), dot(r["qc"], p["c"], "Preço = custo marginal", COL["coral"], size=11, edge="#fff")]
        if r["ok"]:
            tr.append(dot(r["qac"], r["pac"], "Preço = custo médio", COL["teal"], size=12, edge="#fff"))
        chart(fig2d(tr, "Quantidade (q)", "Preço e custo", [0, qx * 1.02], [0, p["a"] * 1.05]))
        tiles([dict(k="Sem regulação", v="p = " + fmt(r["pm"]), key=True, s=f"q = {fmt(r['qm'])} · lucro {fmt(r['profitM'])} · peso morto {fmt(r['dwlM'])}"),
               dict(k="Preço = custo marginal", v="p = " + fmt(p["c"]), key=True, s=f"q = {fmt(r['qc'])} · prejuízo {fmt(-r['lossMC'])}", chip=("Eficiente, mas precisa de subsídio", "warn")),
               dict(k="Preço = custo médio", v="p = " + fmt(r["pac"]) if r["ok"] else "—", key=True,
                    s=f"q = {fmt(r['qac'])} · lucro zero · peso morto {fmt(r['dwlAC'])}" if r["ok"] else "não existe", chip=("Sem prejuízo, pouca perda", "good") if r["ok"] else None)])


@page("segundo-grau", 26, nav="Discriminação de 2º grau")
def segundo_grau():
    mid = "seg"
    header(26, CHAPTERS[26], "Discriminação de preços de 2º grau",
           "O monopolista sabe que há consumidores de demanda alta e baixa, mas não sabe quem é quem. Ele oferece dois pacotes (quantidade e preço) e deixa cada um escolher. "
           "Para o tipo alto não fingir que é baixo, o pacote pequeno é reduzido e o tipo alto recebe uma renda informacional.",
           [("Pacote pequeno", r"q_L=a_L-\frac{\pi_H}{1-\pi_H}(a_H-a_L)"), ("Renda informacional", r"(a_H-a_L)\,q_L")])
    left, right = cols()
    with left:
        p = dict(aH=sl(mid, "aH", "Demanda alta: P = a_H − q (a_H)", 40, 150, 100, 1), aL=sl(mid, "aL", "Demanda baixa: P = a_L − q (a_L)", 10, 140, 80, 1),
                 pH=sl(mid, "pH", "Fração de consumidores do tipo alto", 0.05, 0.95, 0.5, 0.05, hint="Custo marginal zero, como no exemplo do livro."))
    with right:
        if p["aL"] >= p["aH"]:
            st.warning("A demanda baixa precisa ficar abaixo da alta (a_L < a_H).")
            return
        r = C.second_degree(p)
        q = r["qL"]
        tr = []
        if q > 0:
            tr += [area([0, 0, q, q], [0, p["aL"], p["aL"] - q, 0], "Preço do pacote pequeno", "rgba(242,194,0,.42)"),
                   area([0, 0, q, q], [p["aL"], p["aH"], p["aH"] - q, p["aL"] - q], "Renda informacional do tipo alto", "rgba(210,85,58,.38)")]
        tr += [area([q, q, p["aH"]], [0, p["aH"] - q, 0], "Cobrado a mais no pacote grande", "rgba(42,100,184,.18)"),
               ln([0, p["aH"]], [p["aH"], 0], "Demanda do tipo alto", COL["navy"], width=3), ln([0, p["aL"]], [p["aL"], 0], "Demanda do tipo baixo", COL["teal"], width=3),
               dot(q, max(p["aL"] - q, 0), "Pacote pequeno", COL["yellow"], size=13), dot(p["aH"], 0, "Pacote grande", COL["coral"], size=12, edge="#fff")]
        chart(fig2d(tr, "Quantidade (q)", "Preço", [0, p["aH"] * 1.02], [0, p["aH"] * 1.05]))
        tiles([dict(k="Pacote pequeno (q ; preço)", v=f"{fmt(r['qL'])} ; {fmt(r['TL'])}", key=True, s="eficiente seria q = " + fmt(p["aL"]),
                    chip=("Reduzido para conter o tipo alto", "warn") if r["qL"] < p["aL"] - 1e-9 else None),
               dict(k="Pacote grande (q ; preço)", v=f"{fmt(r['qH'])} ; {fmt(r['TH'])}", key=True, s="quantidade eficiente"),
               dict(k="Renda informacional", v=fmt(r["rent"]), s="o que o tipo alto ganha por poder se passar por baixo"),
               dict(k="Lucro médio por consumidor", v=fmt(r["profit"]), s="com informação completa: " + fmt(r["perfect"]))])


@page("hotelling", 26, nav="Localização de Hotelling")
def hotelling():
    mid = "hot"
    header(26, CHAPTERS[26], "Diferenciação de produto: o modelo de localização",
           "Dois vendedores de sorvete numa praia, com preço fixo; cada banhista vai ao mais próximo. Quem se move para perto do rival rouba fregueses, então os dois acabam "
           "no centro. Para os banhistas, o melhor seria ficarem nos pontos 1/4 e 3/4.",
           [("Fatia de A (x_A < x_B)", r"s_A=\frac{x_A+x_B}{2}"), ("Distância média ótima", r"\tfrac{1}{8}\ \text{com vendedores em } \tfrac14 \text{ e } \tfrac34")])
    left, right = cols()
    with left:
        conf = pick("Posições", {"Escolher posições": "livre", "Equilíbrio de Nash": "nash", "Ótimo social": "otimo"}, f"{mid}-conf")
        if conf == "livre":
            xA, xB = sl(mid, "xA", "Posição do vendedor A", 0.0, 1.0, 0.2, 0.01), sl(mid, "xB", "Posição do vendedor B", 0.0, 1.0, 0.7, 0.01)
        else:
            xA, xB = (0.5, 0.5) if conf == "nash" else (0.25, 0.75)
    r = C.hotelling_loc(xA, xB)
    with right:
        xs = C.lin(0, 1, 401)
        dist = lambda x: min(abs(x - xA), abs(x - xB))
        lo, hi = min(xA, xB), max(xA, xB)
        cut = 0.5 if abs(xA - xB) < 1e-9 else (lo + hi) / 2
        left_x, right_x = [x for x in xs if x <= cut], [x for x in xs if x >= cut]
        a_left = xA <= xB
        cA, cB = "rgba(42,100,184,.28)", "rgba(210,85,58,.28)"
        chart(fig2d([area([0, *left_x, cut], [0, *[dist(x) for x in left_x], 0], "Fregueses de A" if a_left else "Fregueses de B", cA if a_left else cB),
                     area([cut, *right_x, 1], [0, *[dist(x) for x in right_x], 0], "Fregueses de B" if a_left else "Fregueses de A", cB if a_left else cA),
                     ln(xs, [dist(x) for x in xs], "Distância percorrida", COL["navy"]),
                     dot(xA, 0, "Vendedor A", COL["royal"], size=15, edge="#fff", text="A", tp="top center"), dot(xB, 0, "Vendedor B", COL["coral"], size=15, edge="#fff", text="B", tp="top center")],
                    "Posição na praia", "Distância até o vendedor mais próximo", [0, 1], [0, 0.75]))
        tiles([dict(k="Fatia de A ; de B", v=f"{fmt(100 * r['sA'], 0)}% ; {fmt(100 * r['sB'], 0)}%", key=True),
               dict(k="Distância média dos banhistas", v=fmt(r["avg"], 3), key=True, s="mínimo possível: 0,125"),
               dict(k="Estabilidade", v="Equilíbrio" if conf == "nash" else "Não é equilíbrio",
                    chip=("Ninguém ganha mudando de lugar", "good") if conf == "nash" else ("Quem se aproxima do rival rouba fregueses", "warn"))])


@page("segundo-teorema", 32, nav="Segundo Teorema do Bem-Estar")
def segundo_teorema():
    mid = "seg2"
    header(32, CHAPTERS[32], "Segundo Teorema do Bem-Estar",
           "Qualquer alocação eficiente pode virar um equilíbrio competitivo, desde que se redistribua a dotação antes da troca (e as preferências sejam convexas). "
           "Escolha um ponto da curva de contrato: "
           "o app mostra os preços que o sustentam e a transferência necessária.",
           [("Preço que sustenta o ponto", r"\frac{p_1}{p_2}=TMS_A=TMS_B"), ("Transferência para A", r"T=p_1x_1^A+x_2^A-(p_1\omega_1^A+\omega_2^A)")])
    left, right = cols()
    with left:
        p = dict(tpos=sl(mid, "tpos", "Alocação desejada: posição na curva de contrato", 0.02, 0.98, 0.6, 0.01,
                         hint="Perto de 0, quase tudo fica com B; perto de 1, quase tudo fica com A. O ponto está sempre na curva de contrato."))
        group("Dotação de A (total de cada bem = 10)")
        p.update(eA1=sl(mid, "eA1", "Bem 1 de A (ω₁ᴬ)", 0.5, 9.5, 7.0, 0.1), eA2=sl(mid, "eA2", "Bem 2 de A (ω₂ᴬ)", 0.5, 9.5, 2.0, 0.1))
        p.update(pref2_controls(mid, aA=0.5, aB=0.3, value="cd"))
        pref_eqs(p, **AGENT_EQ)
    r = cached("second_theorem", p)
    with right:
        bx = [max(0, r["x"] - (10 - r["y"]) / r["price"]), min(10, r["x"] + r["y"] / r["price"])]
        y2 = p["eA2"] + r["T"]
        tr = [ln([0, 10, 10, 0, 0], [0, 0, 10, 10, 0], "Caixa", COL["navy"], width=1.5, legend=False), contract_trace(r["curve"]),
              box_ic(p, "A", r["uA"]), box_ic(p, "B", r["uB"]),
              ln(bx, [r["y"] + r["price"] * (r["x"] - x) for x in bx], "Reta de preços que sustenta o ponto", COL["navy"], width=2.6),
              dot(p["eA1"], p["eA2"], "Dotação original ω", COL["ink"], symbol="square", size=11, edge="#fff", text="ω", tp="bottom left")]
        inside = 0 <= y2 <= 10
        if inside:
            tr.append(dot(p["eA1"], y2, "Dotação após a transferência", COL["gold"], symbol="square", size=11, edge="#fff", text="ω′", tp="top left"))
        tr.append(dot(r["x"], r["y"], "Alocação desejada", COL["yellow"], symbol="star", size=20))
        ann = [arrow(p["eA1"], p["eA2"], p["eA1"], y2, COL["gold"])] if inside and abs(r["T"]) > 0.15 else []
        fig = fig2d(tr, "Bem 1 de A →", "Bem 2 de A →", [0, 10], [0, 10], square=True, annotations=ann)
        fig.update_xaxes(zeroline=False, constrain="domain"); fig.update_yaxes(zeroline=False, constrain="domain")
        chart(fig, height=560)
        T = r["T"]
        lo_, hi_ = r["range"]
        tiles([dict(k="Preço que sustenta o ponto (p₁/p₂)", v="≈ 0" if r["price"] < 0.0015 else fmt(r["price"], 3), key=True,
                    s="o bem 1 sobra para quem fica com ele: só um preço zero sustenta o ponto" if r["price"] < 0.0015
                    else f"qualquer preço entre {fmt(lo_, 3)} e {fmt(hi_, 3)} serve (há um bico ou um canto)" if hi_ > lo_ * 1.02 else "igual à TMS de A e de B"),
               dict(k="Transferência", v=fmt(abs(T)) + " do bem 2", key=True, chip=("Nenhuma: já é o equilíbrio", "good") if abs(T) < 0.01 else ("De B para A" if T > 0 else "De A para B", "info"),
                    s="em valor, a preços de equilíbrio" if inside else "grande demais para caber só em bem 2: seria preciso transferir também bem 1"),
               dict(k="Utilidades uᴬ ; uᴮ", v=f"{fmt(r['uA'], 3)} ; {fmt(r['uB'], 3)}")])


@page("vantagem-comparativa", 33, nav="Vantagem comparativa")
def vantagem_comparativa():
    mid = "vc"
    header(33, CHAPTERS[33], "Vantagem comparativa: Robinson e Sexta-feira",
           "Cada um tem 10 horas para colher cocos ou pescar. Mesmo que um seja melhor em tudo, compensa que cada um se especialize onde seu custo de oportunidade é menor. "
           "A fronteira conjunta é dobrada no ponto de especialização completa.",
           [("Custo de oportunidade de 1 coco", r"\frac{\text{peixes por hora}}{\text{cocos por hora}}"), ("Fronteira conjunta", r"\text{quem tem o menor custo colhe cocos primeiro}")])
    left, right = cols(4)
    with left:
        group("Robinson (por hora)")
        p = dict(rc=sl(mid, "rc", "Cocos colhidos por hora", 0.5, 10.0, 4.0, 0.5), rf=sl(mid, "rf", "Peixes pescados por hora", 0.5, 10.0, 2.0, 0.5))
        group("Sexta-feira (por hora)")
        p.update(fc=sl(mid, "fc", "Cocos colhidos por hora", 0.5, 10.0, 1.0, 0.5), ff=sl(mid, "ff", "Peixes pescados por hora", 0.5, 10.0, 2.0, 0.5))
    r = C.comparative(p)
    with right:
        k = r["kink"]
        chart(fig2d([area([0, 0, k["fish"], r["maxFish"]], [0, r["maxCoco"], k["coco"], 0], "Produção possível em conjunto", "rgba(42,100,184,.12)"),
                     ln([0, r["T"] * p["rf"]], [r["T"] * p["rc"], 0], "Fronteira de Robinson", COL["royal"], dash="dash", width=2.2),
                     ln([0, r["T"] * p["ff"]], [r["T"] * p["fc"], 0], "Fronteira de Sexta-feira", COL["teal"], dash="dash", width=2.2),
                     ln([0, k["fish"], r["maxFish"]], [r["maxCoco"], k["coco"], 0], "Fronteira conjunta", COL["navy"], width=3.2),
                     dot(k["fish"], k["coco"], "Especialização completa", COL["yellow"], size=14)],
                    "Peixes", "Cocos", [0, r["maxFish"] * 1.05], [0, r["maxCoco"] * 1.05]))
        same = abs(r["ocR"] - r["ocF"]) < 1e-9
        tiles([dict(k="Custo de 1 coco para Robinson", v=fmt(r["ocR"]) + " peixes", key=True), dict(k="Custo de 1 coco para Sexta-feira", v=fmt(r["ocF"]) + " peixes", key=True),
               dict(k="Especialização", v="Indiferente" if same else ("Robinson: cocos · Sexta-feira: peixes" if r["rCoco"] else "Robinson: peixes · Sexta-feira: cocos"),
                    chip=("Mesmo custo: não há ganho com a troca", "info") if same else ("Cada um onde seu custo é menor", "good")),
               dict(k="Ponto de especialização", v=f"{fmt(k['fish'], 0)} peixes ; {fmt(k['coco'], 0)} cocos")])


@page("coase", 35, nav="Teorema de Coase")
def coase():
    mid = "coase"
    header(35, CHAPTERS[35], "Teorema de Coase: fumantes e não fumantes",
           "Um fumante e um não fumante dividem um quarto. Com preferências quase-lineares e negociação sem custos, a quantidade de fumaça acordada é a mesma, "
           "não importa quem tem o direito. O direito só decide quem paga a quem.",
           [("Quantidade eficiente", r"BMg_A(s)=DMg_B(s)\Rightarrow s^*=\frac{a}{1+k}"), ("Benefício e dano marginais", r"BMg_A=a-s,\quad DMg_B=k\,s")])
    left, right = cols()
    with left:
        rights = pick("Quem tem o direito", {"Direito do fumante": "fumante", "Direito do não fumante": "naofumante"}, f"{mid}-dir")
        a = sl(mid, "a", "Benefício do fumante com a primeira unidade (a)", 2.0, 20.0, 10.0, 0.5)
        k = sl(mid, "k", "Dano de cada unidade extra para o não fumante (k)", 0.2, 3.0, 1.0, 0.1)
    r = C.coase(a, k)
    with right:
        s, fum = r["s"], rights == "fumante"
        tri = (area([s, a, a], [a - s, 0, k * a], "Ganho de reduzir de a até s*", "rgba(242,194,0,.42)") if fum
               else area([0, 0, s], [0, a, a - s], "Ganho de liberar de 0 até s*", "rgba(242,194,0,.42)"))
        chart(fig2d([tri, ln([0, a], [a, 0], "Benefício marginal do fumante", COL["navy"], width=3), ln([0, a], [0, k * a], "Dano marginal do não fumante", COL["coral"], width=3),
                     dot(a if fum else 0, 0, "Ponto de partida", COL["ink"], symbol="square", size=11, edge="#fff"), dot(s, a - s, "Acordo (s*)", COL["yellow"], size=14)],
                    "Fumaça no quarto (s)", "Valor marginal", [0, a * 1.05], [0, max(a, k * a) * 1.05]))
        d = r["rightsA"] if fum else r["rightsB"]
        tiles([dict(k="Fumaça acordada s*", v=fmt(s), key=True, chip=("Igual com qualquer direito", "good")),
               dict(k="Ponto de partida", v=fmt(d["start"]), s="o fumante fuma o quanto quer" if fum else "ninguém fuma"),
               dict(k="Pagamento", v=fmt(d["pay"]), key=True, s="o não fumante paga para o fumante fumar menos" if fum else "o fumante paga para poder fumar", chip=("Divide o ganho ao meio", "info")),
               dict(k="Ganho total da negociação", v=fmt(d["gain"]))])


@page("incentivos", 38, nav="Risco moral e incentivos")
def incentivos():
    mid = "inc38"
    header(38, CHAPTERS[38], "Risco moral e contratos de incentivo",
           "O dono da terra não observa o esforço do trabalhador (risco moral). O contrato precisa fazer o trabalhador ganhar, na margem, todo o produto do esforço extra. "
           "Aluguel e salário por esforço fazem isso; a parceria (meação) não, e o trabalhador se esforça de menos.",
           [("Produção e custo", r"f(x)=a\,x,\quad c(x)=\tfrac{1}{2}x^2"), ("Esforço eficiente", r"f'(x)=c'(x)\Rightarrow x^*=a"), ("Parceria", r"s\,a=x\Rightarrow x=s\,a<x^*")])
    left, right = cols()
    with left:
        contract = pick("Contrato", {"Parceria": "parceria", "Aluguel": "aluguel", "Salário": "salario"}, f"{mid}-contract")
        p = dict(contract=contract, a=sl(mid, "a", "Produto por unidade de esforço (a)", 1.0, 10.0, 4.0, 0.5),
                 ubar=sl(mid, "ubar", "Utilidade de reserva do trabalhador", 0.0, 20.0, 2.0, 0.5), s=0.5)
        if contract == "parceria":
            p["s"] = sl(mid, "s", "Parte do produto que fica com o trabalhador (s)", 0.05, 0.95, 0.5, 0.05)
    r = C.incentives(p)
    with right:
        if not r["part"]:
            st.warning("Com essa parte, o trabalhador ganha menos que sua utilidade de reserva e recusa o contrato.")
        a, xm = p["a"], 1.4 * p["a"]
        mb = p["s"] * a if contract == "parceria" else a
        tr = [area([r["x"], r["x"], a], [r["x"], a, a], "Perda de eficiência", "rgba(210,85,58,.38)")] if r["loss"] > 1e-9 else []
        tr += [ln([0, xm], [a, a], "Produto marginal do esforço", COL["navy"], width=3), ln([0, xm], [0, xm], "Custo marginal do esforço", COL["teal"], width=3)]
        if contract == "parceria":
            tr.append(ln([0, xm], [mb, mb], "Ganho marginal do trabalhador (s·a)", COL["coral"], dash="dash", width=2.4))
        tr += [dot(a, a, "Esforço eficiente", COL["ink"], size=10, edge="#fff"), dot(r["x"], mb, "Esforço escolhido", COL["yellow"], size=14)]
        chart(fig2d(tr, "Esforço (x)", "Valor e custo marginais", [0, xm], [0, xm]))
        owner_s = ("aluguel fixo cobrado" if contract == "aluguel" else f"paga {fmt(a)} por unidade de esforço" if contract == "salario"
                   else f"fica com {fmt(100 * (1 - p['s']), 0)}% do produto")
        tiles([dict(k="Esforço escolhido", v=fmt(r["x"]), key=True, s="eficiente: " + fmt(r["xe"]), chip=("Esforço de menos", "bad") if r["loss"] > 1e-9 else ("Eficiente", "good")),
               dict(k="Renda do dono", v=fmt(r["owner"]), key=True, s=owner_s), dict(k="Utilidade do trabalhador", v=fmt(r["worker"]), s="reserva: " + fmt(p["ubar"])),
               dict(k="Perda de eficiência", v=fmt(r["loss"]), s="excedente máximo: " + fmt(r["Se"]))])
