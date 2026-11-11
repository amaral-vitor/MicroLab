"""Capítulos 5 a 14: o consumidor."""
import streamlit as st
from . import core as C
from .registry import page, CHAPTERS
from .ui import (split, group, cb, rd, COL, header, sl, tiles, fmt, sgn, chart, fig2d, ln, dot, area, rect, arrow, budget,
                 ic_traces, KIND, sigma_text, pref_controls, pref_eqs)


def cols(n=3):
    return split(n)


@page("escolha", 5)
def escolha():
    mid = "escolha"
    header(5, CHAPTERS[5], "Escolha ótima",
           "O consumidor escolhe a cesta mais alta que cabe no orçamento. Calibre a CES pelo ρ (com atalhos para complementares perfeitos, "
           "Cobb-Douglas e substitutos perfeitos) ou troque para quase-linear e veja como a escolha muda.",
           [("Orçamento", r"p_1x_1+p_2x_2=m")])
    left, right = cols()
    with left:
        p = pref_controls(mid, value="ces", a=(1, 20, 0.5, 5))
        pref_eqs(p, demand=True)
        group("Preços e renda")
        p["w"] = sl(mid, "w", "Renda (m)", 10, 300, 100, 5)
        p["p1"] = sl(mid, "p1", "Preço do bem 1 (p₁)", 1.0, 30.0, 10.0, 0.5)
        p["p2"] = sl(mid, "p2", "Preço do bem 2 (p₂)", 1.0, 30.0, 10.0, 0.5)
    r = C.choice(p)
    with right:
        xm, ym = 1.3 * p["w"] / p["p1"], 1.3 * p["w"] / p["p2"]
        chart(fig2d([*ic_traces(r["U"], p["delta"], p["rho"], p["mode"], xm, ym, C.ces_level),
                     budget(p["w"], p["p1"], p["p2"], "Reta orçamentária", COL["navy"], width=3),
                     dot(r["x1"], r["x2"], "Uma das cestas ótimas" if r["kind"] == "tie" else "Cesta ótima", COL["yellow"], size=14)],
                    "Bem 1 (x₁)", "Bem 2 (x₂)", [0, xm], [0, ym]))
        tiles([dict(k="x₁*", v=fmt(r["x1"]), key=True), dict(k="x₂*", v=fmt(r["x2"]), key=True), dict(k="Utilidade U*", v=fmt(r["U"], 3)),
               dict(k="Elasticidade de substituição σ", v=sigma_text(p["rho"], p["mode"]), s="na quase-linear, σ muda ao longo da curva" if p["form"] == "ql" else "σ = 1/(1−ρ)",
                    chip=KIND[r["kind"]])])


@page("slutsky", 8)
def slutsky():
    mid = "slutsky"
    header(8, CHAPTERS[8], "Equação de Slutsky",
           "Uma mudança em p₁ se divide em efeito substituição (girar o orçamento mantendo o poder de compra, ou a utilidade) "
           "e efeito renda (deslocar o orçamento paralelamente).",
           [("Slutsky", r"\Delta x_1=\Delta x_1^{s}+\Delta x_1^{n}"), ("Renda compensada", r"m'=m+x_1\,\Delta p_1\ \ \text{(Slutsky)}"),
            ("", r"m'=e(p_1',p_2,u_0)\ \ \text{(Hicks)}")])
    left, right = cols()
    with left:
        method = rd("Compensação", ["Slutsky", "Hicks"], f"{mid}-method")
        p = dict(method=method.lower(), **pref_controls(mid, value="ces", a=(1, 20, 0.5, 5)))
        pref_eqs(p)
        group("Preços e renda")
        p["w"] = sl(mid, "w", "Renda (m)", 10, 300, 100, 5)
        p["p1"] = sl(mid, "p1", "p₁ inicial", 1.0, 30.0, 10.0, 0.5)
        p["p1n"] = sl(mid, "p1n", "p₁ novo", 1.0, 30.0, 6.0, 0.5)
        p["p2"] = sl(mid, "p2", "Preço do bem 2 (p₂)", 1.0, 30.0, 10.0, 0.5)
    r = C.slutsky(p)
    with right:
        xm = 1.12 * max(p["w"] / p["p1"], p["w"] / p["p1n"], r["wc"] / p["p1n"])
        ym = 1.12 * max(p["w"] / p["p2"], r["wc"] / p["p2"])
        ic = lambda U, name, color: ln(*C.ces_level(U, p["delta"], p["rho"], p["mode"], xm, ym), name, color, width=2)
        A, B, Z = r["A"], r["B"], r["C"]
        ann = []
        if ((B["x1"] - A["x1"]) ** 2 + (B["x2"] - A["x2"]) ** 2) ** 0.5 > xm * 0.04:
            ann.append(arrow(A["x1"], A["x2"], B["x1"], B["x2"], COL["gold"]))
        if ((Z["x1"] - B["x1"]) ** 2 + (Z["x2"] - B["x2"]) ** 2) ** 0.5 > xm * 0.04:
            ann.append(arrow(B["x1"], B["x2"], Z["x1"], Z["x2"], COL["coral"]))
        chart(fig2d([ic(r["U0"], "Indiferença inicial", COL["royal"]), ic(r["UC"], "Indiferença final", COL["faint"]),
                     budget(p["w"], p["p1"], p["p2"], "Orçamento inicial", COL["navy"], width=2.8),
                     budget(r["wc"], p["p1n"], p["p2"], "Orçamento compensado", COL["gold"], dash="dash"),
                     budget(p["w"], p["p1n"], p["p2"], "Orçamento final", COL["coral"], width=2.8),
                     dot(A["x1"], A["x2"], "X: inicial", COL["navy"], size=11, edge="#fff", text="X", tp="top left"),
                     dot(B["x1"], B["x2"], "Y: compensada", COL["yellow"], size=12, text="Y", tp="bottom left"),
                     dot(Z["x1"], Z["x2"], "Z: final", COL["coral"], size=11, edge="#fff", text="Z")],
                    "Bem 1 (x₁)", "Bem 2 (x₂)", [0, xm], [0, ym], annotations=ann))
        tiles([dict(k="Efeito substituição Δx₁ˢ", v=sgn(r["sub1"]), s="Δx₂ˢ = " + sgn(r["sub2"]), key=True),
               dict(k="Efeito renda Δx₁ⁿ", v=sgn(r["inc1"]), s="Δx₂ⁿ = " + sgn(r["inc2"]), key=True),
               dict(k="Efeito total Δx₁", v=sgn(r["tot1"]), s="Δx₂ = " + sgn(r["tot2"])),
               dict(k="Renda compensada m'", v=fmt(r["wc"]), s="mantém u₀ = " + fmt(r["U0"], 3) if p["method"] == "hicks" else "cesta X ainda cabe no orçamento")])


@page("dotacao", 9, nav="Escolha com dotação e Slutsky")
def dotacao():
    mid = "dotacao"
    header(9, CHAPTERS[9], "Comprar e vender: escolha com dotação",
           "O consumidor parte de uma dotação (ω₁, ω₂) e pode vender parte de um bem para comprar o outro. O orçamento sempre passa pela dotação. "
           "Quando p₁ muda, o valor da dotação também muda, e isso cria um terceiro efeito na equação de Slutsky: o efeito renda dotação.",
           [("Orçamento", r"p_1x_1+p_2x_2=p_1\omega_1+p_2\omega_2"), ("Demanda líquida", r"x_i-\omega_i"),
            ("Slutsky com dotação", r"\frac{\Delta x_1}{\Delta p_1}=\frac{\Delta x_1^{s}}{\Delta p_1}+(\omega_1-x_1)\frac{\Delta x_1^{m}}{\Delta m}")])
    left, right = cols()
    with left:
        p = pref_controls(mid, value="ces", a=(0.5, 15, 0.5, 4))
        pref_eqs(p)
        group("Dotação e preços")
        p["e1"] = sl(mid, "e1", "Dotação do bem 1 (ω₁)", 0.0, 20.0, 8.0, 0.5)
        p["e2"] = sl(mid, "e2", "Dotação do bem 2 (ω₂)", 0.0, 20.0, 2.0, 0.5)
        p["p1"] = sl(mid, "p1", "Preço do bem 1 (p₁)", 1.0, 30.0, 10.0, 0.5)
        p["p2"] = sl(mid, "p2", "Preço do bem 2 (p₂)", 1.0, 30.0, 10.0, 0.5)
    if p["e1"] + p["e2"] == 0:
        st.warning("Com dotação zero de tudo, o consumidor não tem o que trocar. Aumente ω₁ ou ω₂.")
        return
    r = C.endowment(p)
    with right:
        t1, t2 = st.tabs(["Escolha com dotação", "Slutsky com dotação"])
        with t1:
            xm, ym = 1.3 * r["m"] / p["p1"], 1.3 * r["m"] / p["p2"]
            ann = [arrow(p["e1"], p["e2"], r["x1"], r["x2"], COL["gold"])] if ((r["x1"] - p["e1"]) ** 2 + (r["x2"] - p["e2"]) ** 2) ** 0.5 > xm * 0.05 else []
            chart(fig2d([*ic_traces(r["U"], p["delta"], p["rho"], p["mode"], xm, ym, C.ces_level),
                         budget(r["m"], p["p1"], p["p2"], "Reta orçamentária", COL["navy"], width=3),
                         dot(p["e1"], p["e2"], "Dotação ω", COL["ink"], symbol="square", size=11, edge="#fff", text="ω", tp="bottom left"),
                         dot(r["x1"], r["x2"], "Cesta ótima", COL["yellow"], size=14)],
                        "Bem 1 (x₁)", "Bem 2 (x₂)", [0, xm], [0, ym], annotations=ann), key=f"{mid}-1")
            role = lambda n: ("Autossuficiente", "info") if abs(n) < 1e-3 else (("Demandante líquido", "good") if n > 0 else ("Ofertante líquido", "warn"))
            tiles([dict(k="x₁*", v=fmt(r["x1"]), key=True, chip=role(r["net1"])), dict(k="x₂*", v=fmt(r["x2"]), key=True, chip=role(r["net2"])),
                   dict(k="Demanda líquida (x₁ − ω₁ ; x₂ − ω₂)", v=sgn(r["net1"]) + " ; " + sgn(r["net2"])),
                   dict(k="Valor da dotação m", v=fmt(r["m"]), chip=KIND[r["kind"]])])
        with t2:
            p["p1n"] = sl(mid, "p1n", "Novo preço do bem 1 (p₁′)", 1.0, 30.0, 14.0, 0.5)
            S = C.endowment_slutsky(p)
            A, B, Cc, D = S["A"], S["B"], S["C"], S["D"]
            xm = 1.12 * max(S["m0"] / min(p["p1"], p["p1n"]), S["m1"] / p["p1n"], S["mS"] / p["p1n"], p["e1"])
            ym = 1.12 * max(S["m0"], S["m1"], S["mS"]) / p["p2"]
            ic = lambda z, name, color: ln(*C.ces_level(C.ces(z["x1"], z["x2"], p["delta"], p["rho"], p["mode"]), p["delta"], p["rho"], p["mode"], xm, ym), name, color, width=2)
            far = lambda u, v: ((u["x1"] - v["x1"]) ** 2 + (u["x2"] - v["x2"]) ** 2) ** 0.5 > xm * 0.03
            ann = []
            if far(A, B):
                ann.append(arrow(A["x1"], A["x2"], B["x1"], B["x2"], COL["gold"]))
            if far(B, Cc):
                ann.append(arrow(B["x1"], B["x2"], Cc["x1"], Cc["x2"], COL["muted"]))
            if far(Cc, D):
                ann.append(arrow(Cc["x1"], Cc["x2"], D["x1"], D["x2"], COL["coral"]))
            chart(fig2d([ic(A, "Indiferença inicial", COL["royal"]), ic(D, "Indiferença final", COL["faint"]),
                         budget(S["m0"], p["p1"], p["p2"], "Orçamento inicial (passa por ω)", COL["navy"], width=2.8),
                         budget(S["mS"], p["p1n"], p["p2"], "Girado em torno de A (substituição)", COL["gold"], dash="dash", width=2.2),
                         budget(S["m0"], p["p1n"], p["p2"], "Preço novo, renda monetária antiga", COL["muted"], dash="dot", width=2),
                         budget(S["m1"], p["p1n"], p["p2"], "Orçamento final (passa por ω)", COL["coral"], width=2.8),
                         dot(p["e1"], p["e2"], "Dotação ω", COL["ink"], symbol="square", size=11, edge="#fff", text="ω", tp="bottom left"),
                         dot(A["x1"], A["x2"], "A: inicial", COL["navy"], size=11, edge="#fff", text="A", tp="top left"),
                         dot(B["x1"], B["x2"], "B: após substituição", COL["yellow"], size=12, text="B", tp="bottom left"),
                         dot(Cc["x1"], Cc["x2"], "C: após efeito renda comum", COL["muted"], size=11, edge="#fff", text="C", tp="bottom right"),
                         dot(D["x1"], D["x2"], "D: final", COL["coral"], size=12, edge="#fff", text="D", tp="top right")],
                        "Bem 1 (x₁)", "Bem 2 (x₂)", [0, xm], [0, ym], annotations=ann), key=f"{mid}-2")
            seller, buyer = S["net0"] > 1e-3, S["net0"] < -1e-3
            tiles([dict(k="Efeito substituição (A → B)", v=sgn(S["sub"]), key=True, s="Δx₂ = " + sgn(S["sub2"])),
                   dict(k="Efeito renda comum (B → C)", v=sgn(S["inc"]), key=True, s="Δx₂ = " + sgn(S["inc2"])),
                   dict(k="Efeito renda dotação (C → D)", v=sgn(S["endow"]), key=True, s="Δx₂ = " + sgn(S["endow2"]),
                        chip=("Vendedor líquido de x₁: a dotação vale mais", "good") if seller else ("Comprador líquido de x₁: a dotação vale menos", "warn") if buyer
                        else ("Autossuficiente: sem efeito dotação", "info")),
                   dict(k="Efeito total sobre x₁ (A → D)", v=sgn(S["tot"]), s="renda comum + dotação = (ω₁ − x₁) × efeito de renda: " + sgn(S["inc"] + S["endow"]))])


@page("oferta-trabalho", 9, nav="Oferta de trabalho")
def oferta_trabalho():
    mid = "trab"
    header(9, CHAPTERS[9], "Oferta de trabalho",
           "O trabalhador vende tempo: cada hora de lazer custa o salário w. A oferta de trabalho é a dotação de tempo menos o lazer demandado.",
           [("Orçamento", r"pc+w\ell=M+wT,\quad N=T-\ell"), ("Oferta", r"N^*(w)=T-\ell^*(w,\ M+wT)")])
    left, right = cols()
    with left:
        p = pref_controls(mid, w="sigma", wl="Peso do lazer (σ)", x1="lazer ℓ", x2="consumo c", value="cd", a=(10, 600, 10, 200), k=(1, 40, 1, 10))
        pref_eqs(p, v1=r"\ell", v2="c", w=r"\sigma")
        group("Salário, preço e tempo")
        p.update(w=sl(mid, "w", "Salário (w)", 1, 100, 20, 1),
                 p=sl(mid, "p", "Preço do consumo (p)", 0.5, 5.0, 1.0, 0.1), M=sl(mid, "M", "Renda não salarial (M)", 0, 500, 100, 10),
                 T=sl(mid, "T", "Tempo total (T)", 8, 24, 24, 1))
    r = C.labor_supply(p)
    with right:
        t1, t2 = st.tabs(["Lazer × consumo", "Curva de oferta de trabalho"])
        with t1:
            cTop, ls = 1.15 * (p["M"] + p["w"] * p["T"]) / p["p"], C.lin(0, p["T"], 200)
            chart(fig2d([*ic_traces(r["U"], p["sigma"], p["rho"], p["mode"], p["T"] * 1.05, cTop, C.ces_level), ln(ls, [(p["M"] + p["w"] * (p["T"] - l)) / p["p"] for l in ls], "Reta orçamentária", COL["navy"], width=3),
                         ln([p["T"], p["T"]], [0, p["M"] / p["p"]], "Limite de tempo", COL["navy"], width=1.5, dash="dot", legend=False),
                         dot(p["T"], p["M"] / p["p"], "Dotação (T, M/p)", COL["ink"], symbol="square", size=11, edge="#fff"),
                         dot(r["l"], r["c"], "Escolha ótima", COL["yellow"], size=14)],
                        "Lazer (ℓ)", "Consumo (c)", [0, p["T"] * 1.05], [0, cTop]), key=f"{mid}-1")
        with t2:
            okres = r["wRes"] == r["wRes"]
            wTop = max(2.2 * p["w"], 3 * r["wRes"] if okres else 0, 10)
            ws = C.lin(0.2, wTop, 300)
            tr = [ln([C.labor_N(p, w) for w in ws], ws, "Oferta de trabalho", COL["navy"], width=3, hover="N %{x:.2f} · w %{y:.2f}")]
            if okres:
                tr.append(ln([0, p["T"]], [r["wRes"], r["wRes"]], "Salário de reserva", COL["coral"], dash="dot", width=2))
            if p["mode"]["form"] == "cd":
                tr.append(ln([(1 - p["sigma"]) * p["T"]] * 2, [0, wTop], "Assíntota (1−σ)T", COL["faint"], dash="dash", width=1.6))
            chart(fig2d(tr + [dot(r["N"], p["w"], "Salário atual", COL["yellow"], size=14)],
                        "Horas trabalhadas (N*)", "Salário (w)", [0, p["T"]], [0, wTop]), key=f"{mid}-2")
        tiles([dict(k="Lazer ℓ*", v=fmt(r["l"]), key=True),
               dict(k="Horas trabalhadas N*", v=fmt(r["N"]), key=True, chip=("Não participa", "warn") if r["corner"] else ("Participa", "good")),
               dict(k="Consumo c*", v=fmt(r["c"])), dict(k="Salário de reserva", v=fmt(r["wRes"]) if r["wRes"] == r["wRes"] else "acima de 1.000", s="abaixo dele, N* = 0")])


@page("intertemporal", 10)
def intertemporal():
    mid = "inter"
    header(10, CHAPTERS[10], "Escolha intertemporal",
           "Consumir hoje ou amanhã: a taxa de juros é o preço relativo do consumo presente. Quem consome menos que a renda do período 1 é poupador.",
           [("Orçamento", r"c_1+\frac{c_2}{1+r}=m_1+\frac{m_2}{1+r}"), ("Poupança", r"s=m_1-c_1")])
    left, right = cols()
    with left:
        p = pref_controls(mid, w="beta", wl="Peso do consumo presente (β)", x1="c₁", x2="c₂", value="ces", a=(0.5, 15, 0.5, 4))
        pref_eqs(p, v1="c_1", v2="c_2", w=r"\beta")
        group("Juros e renda")
        p["r"] = sl(mid, "r", "Taxa de juros (r)", 0.0, 1.0, 0.05, 0.01)
        p["m1"] = sl(mid, "m1", "Renda no período 1 (m₁)", 0.0, 20.0, 5.0, 0.5)
        p["m2"] = sl(mid, "m2", "Renda no período 2 (m₂)", 0.0, 20.0, 5.0, 0.5)
    if p["m1"] + p["m2"] == 0:
        st.warning("Com renda zero nos dois períodos não há o que escolher. Aumente m₁ ou m₂.")
        return
    r = C.intertemporal(p)
    with right:
        xm, ym = 1.2 * r["W"], 1.2 * (1 + p["r"]) * r["W"]
        chart(fig2d([*ic_traces(r["U"], p["beta"], p["rho"], p["mode"], xm, ym, C.ces_level),
                     ln([0, r["W"]], [(1 + p["r"]) * r["W"], 0], "Restrição intertemporal", COL["navy"], width=3),
                     dot(p["m1"], p["m2"], "Dotação (m₁, m₂)", COL["ink"], symbol="square", size=11, edge="#fff"),
                     dot(r["c1"], r["c2"], "Consumo ótimo", COL["yellow"], size=14)],
                    "Consumo no período 1 (c₁)", "Consumo no período 2 (c₂)", [0, xm], [0, ym]))
        s = r["s"]
        tiles([dict(k="c₁*", v=fmt(r["c1"]), key=True), dict(k="c₂*", v=fmt(r["c2"]), key=True),
               dict(k="Poupança s = m₁ − c₁", v=sgn(s), chip=("Nem poupa nem toma", "info") if abs(s) < 1e-3 else (("Poupador", "good") if s > 0 else ("Tomador", "warn"))),
               dict(k="Riqueza em valor presente", v=fmt(r["W"]))])


@page("incerteza", 12)
def incerteza():
    mid = "inc"
    header(12, CHAPTERS[12], "Utilidade esperada e seguro",
           "Com perda L de probabilidade π, o consumidor avesso ao risco aceita trocar riqueza esperada por certeza. "
           "Com preço de seguro justo (γ = π), ele se segura por completo.",
           [("Utilidade", r"u(c)=\frac{c^{1-\theta}}{1-\theta}\ \ (\theta=1:\ \ln c)"), ("Utilidade esperada", r"EU=\pi u(c_r)+(1-\pi)u(c_b)"),
            ("Seguro", r"c_r=w-L+(1-\gamma)K,\ \ c_b=w-\gamma K")])
    left, right = cols()
    with left:
        p = dict(w=sl(mid, "w", "Riqueza inicial (w)", 100, 300, 100, 5), L=sl(mid, "L", "Perda no estado ruim (L)", 5, 95, 60, 1),
                 pi=sl(mid, "pi", "Probabilidade da perda (π)", 0.01, 0.99, 0.25, 0.01), g=sl(mid, "g", "Aversão ao risco (θ)", 0.0, 3.0, 1.0, 0.1, hint="θ = 0: neutro ao risco (u linear) · θ = 1: u = ln c. Quanto maior θ, mais curva a utilidade e maior o prêmio de risco."))
    with right:
        t1, t2 = st.tabs(["Utilidade esperada", "Demanda por seguro"])
        with t1:
            lot = C.lottery(p)
            U = lambda c: C.u_crra(c, p["g"])
            hi = lot["hi"] * 1.12
            cs = C.lin(1.0, hi, 300)
            yr = [0, U(hi) * 1.06]
            fig = fig2d([ln(cs, [U(c) for c in cs], "u(c)", COL["navy"], width=3),
                         ln([lot["lo"], lot["hi"]], [U(lot["lo"]), U(lot["hi"])], "Combinações das loterias", COL["faint"], width=2),
                         ln([lot["CE"], lot["Ec"]], [lot["EU"], lot["EU"]], "Prêmio de risco", COL["coral"], width=4),
                         ln([lot["Ec"]] * 2, [yr[0], U(lot["Ec"])], "E[c]", COL["muted"], dash="dot", width=1.4, legend=False),
                         dot(lot["lo"], U(lot["lo"]), "Estado ruim", COL["navy"], size=9, edge="#fff"),
                         dot(lot["hi"], U(lot["hi"]), "Estado bom", COL["navy"], size=9, edge="#fff"),
                         dot(lot["Ec"], lot["EU"], "Utilidade esperada EU", COL["royal"], size=11, edge="#fff"),
                         dot(lot["Ec"], U(lot["Ec"]), "u(E[c])", COL["teal"], size=10, edge="#fff"),
                         dot(lot["CE"], lot["EU"], "Equivalente certo", COL["yellow"], size=13)],
                        "Consumo (c)", "Utilidade u(c)", [0, hi], yr)
            chart(fig, key=f"{mid}-1")
            tiles([dict(k="Consumo esperado E[c]", v=fmt(lot["Ec"]), key=True), dict(k="Equivalente certo", v=fmt(lot["CE"]), key=True),
                   dict(k="Prêmio de risco E[c] − EC", v=fmt(lot["rp"]), chip=("Neutro ao risco", "info") if p["g"] < 1e-9 else ("Avesso ao risco", "good")),
                   dict(k="Utilidade esperada EU", v=fmt(lot["EU"], 3))])
        with t2:
            fair = cb("Usar preço justo (γ = π)", f"{mid}-fair")
            p["prem"] = p["pi"] if fair else sl(mid, "prem", "Preço do seguro por R$ 1 de cobertura (γ)", 0.01, 0.95, 0.30, 0.01)
            ins = C.insurance(p)
            top = p["w"] * 1.08
            xs = C.lin(top * 0.02, top, 300)

            def ic_y(cb):
                y = C.u_inv((ins["EU"] - p["pi"] * C.u_crra(cb, p["g"])) / (1 - p["pi"]), p["g"])
                return y if (y == y and y > 0) else None
            Ks = C.lin(0, ins["Kmax"], 120)
            chart(fig2d([ln([0, top], [0, top], "Linha de certeza (c_r = c_b)", COL["muted"], dash="dot", width=1.6),
                         ln(xs, [ic_y(x) for x in xs], "Curva de indiferença", COL["royal"]),
                         ln([p["w"] - p["L"] + (1 - p["prem"]) * K for K in Ks], [p["w"] - p["prem"] * K for K in Ks], "Restrição do seguro", COL["navy"], width=3),
                         dot(p["w"] - p["L"], p["w"], "Sem seguro (dotação)", COL["ink"], symbol="square", size=11, edge="#fff"),
                         dot(ins["cb"], ins["cg"], "Escolha ótima", COL["yellow"], size=14)],
                        "Consumo no estado ruim (c_r)", "Consumo no estado bom (c_b)", [0, top], [0, top]), key=f"{mid}-2")
            full, none = abs(ins["K"] - p["L"]) < 1e-3 * p["L"], ins["K"] < 1e-6
            chip = ("Seguro completo", "good") if full else ("Não faz seguro", "warn") if none else ("Mais que a perda", "warn") if ins["K"] > p["L"] else ("Seguro parcial", "info")
            tiles([dict(k="Cobertura ótima K*", v=fmt(ins["K"]), key=True, chip=chip), dict(k="Consumo no estado ruim", v=fmt(ins["cb"])),
                   dict(k="Consumo no estado bom", v=fmt(ins["cg"])),
                   dict(k="Prêmio pago γK*", v=fmt(p["prem"] * ins["K"]), s="preço justo: γ = π" if ins["fair"] else "γ − π = " + sgn(p["prem"] - p["pi"]))])


@page("ativos-risco", 13)
def ativos_risco():
    mid = "ativos"
    header(13, CHAPTERS[13], "Carteira com um ativo de risco",
           "O investidor divide a riqueza entre um ativo sem risco e um de risco. A reta orçamentária no plano (σ, μ) tem inclinação igual ao preço do risco.",
           [("Carteira", r"r_x=x\,r_m+(1-x)\,r_f,\ \ \sigma_x=x\,\sigma_m"), ("Preço do risco", r"p=\frac{r_m-r_f}{\sigma_m}"),
            ("Média-variância", r"U=\mu-\tfrac{A}{2}\sigma^2\Rightarrow x^*=\frac{r_m-r_f}{A\sigma_m^2}")])
    left, right = cols()
    with left:
        p = dict(rf=sl(mid, "rf", "Retorno sem risco (r_f)", 0.0, 0.10, 0.03, 0.005), rm=sl(mid, "rm", "Retorno esperado do ativo de risco (r_m)", 0.02, 0.25, 0.09, 0.005),
                 sm=sl(mid, "sm", "Desvio-padrão do ativo de risco (σ_m)", 0.05, 0.5, 0.2, 0.01), A=sl(mid, "A", "Aversão ao risco (A)", 0.5, 10.0, 3.0, 0.1))
    with right:
        if p["rm"] <= p["rf"]:
            st.warning("O ativo de risco precisa render mais que o sem risco (r_m > r_f); senão ninguém o carrega.")
        r = C.portfolio(p)
        sx = max(1.6 * p["sm"], 1.3 * abs(r["sd"]), 0.1)
        ss = C.lin(0, sx, 200)
        yTop = max(p["rf"] + r["price"] * sx, r["mu"]) * 1.15 + 0.01
        ic = lambda U, name, color, w, leg: ln(ss, [U + p["A"] / 2 * s * s for s in ss], name, color, width=w, legend=leg, hover="σ %{x:.1%} · μ %{y:.2%}")
        tr = [ic(r["U"] - 0.02, "Outras curvas de indiferença", COL["faint"], 1.5, True), ic(r["U"] + 0.02, "", COL["faint"], 1.5, False),
              ic(r["U"], "Curva de indiferença", COL["royal"], 2.6, True),
              ln(ss, [p["rf"] + r["price"] * s for s in ss], "Reta orçamentária", COL["navy"], width=3, hover="σ %{x:.1%} · μ %{y:.2%}"),
              dot(0, p["rf"], "Ativo sem risco", COL["ink"], symbol="square", size=10, edge="#fff"),
              dot(p["sm"], p["rm"], "Ativo de risco", COL["coral"], symbol="diamond", size=12, edge="#fff")]
        if r["x"] > 0:
            tr.append(dot(r["sd"], r["mu"], "Carteira ótima", COL["yellow"], size=14))
        fig = fig2d(tr, "Risco (desvio-padrão σ)", "Retorno esperado (μ)", [0, sx], [0, yTop])
        fig.update_xaxes(tickformat=".0%"); fig.update_yaxes(tickformat=".0%")
        chart(fig)
        x = r["x"]
        tiles([dict(k="Fração no ativo de risco x*", v=fmt(100 * x, 1) + "%", key=True,
                    chip=("Alavancado: toma emprestado a r_f", "warn") if x > 1 else ("Fica fora do ativo de risco", "info") if x <= 0 else ("Parte no ativo sem risco", "good")),
               dict(k="Retorno esperado μ", v=fmt(100 * r["mu"]) + "%"), dict(k="Risco σ", v=fmt(100 * max(0, r["sd"])) + "%"),
               dict(k="Preço do risco", v=fmt(r["price"], 3), s="retorno extra por unidade de σ")])


@page("excedente", 14)
def excedente():
    mid = "exc"
    header(14, CHAPTERS[14], "Excedente do consumidor, variação compensatória e equivalente",
           "Três formas de medir em dinheiro o ganho (ou a perda) de uma mudança no preço do bem 1. Se o bem 1 é normal, VC ≤ ΔEC ≤ VE; "
           "com preferências quase-lineares não há efeito renda e as três medidas coincidem.",
           [("VC", r"m-e(p_1',p_2,u_0)"), ("VE", r"e(p_1,p_2,u_1)-m"), ("ΔEC", r"\int_{p_1'}^{p_1}x_1(p,p_2,m)\,dp")])
    left, right = cols()
    with left:
        p = pref_controls(mid, value="cd", a=(2, 80, 1, 30))
        pref_eqs(p)
        group("Renda e preços")
        p.update(m=sl(mid, "m", "Renda (m)", 10, 300, 100, 5),
                 p2=sl(mid, "p2", "Preço do bem 2 (p₂)", 0.5, 10.0, 1.0, 0.1), p1=sl(mid, "p1", "p₁ inicial", 0.5, 10.0, 2.0, 0.1),
                 p1n=sl(mid, "p1n", "p₁ final", 0.5, 10.0, 1.0, 0.1))
    r = C.welfare(p)
    with right:
        t1, t2 = st.tabs(["Cestas e orçamentos", "Curva de demanda"])
        with t1:
            mx = max(p["m"], r["mCV"], r["mEV"])
            xm, ym = 1.15 * mx / min(p["p1"], p["p1n"]), 1.2 * mx / p["p2"]
            cd = lambda U, name, color: ln(*C.ces_level(U, p["delta"], p["rho"], p["mode"], xm, ym), name, color, width=2)
            chart(fig2d([cd(r["u0"], "Indiferença inicial u₀", COL["royal"]), cd(r["u1"], "Indiferença final u₁", COL["faint"]),
                         budget(p["m"], p["p1"], p["p2"], "Orçamento inicial", COL["navy"], width=2.8),
                         budget(p["m"], p["p1n"], p["p2"], "Orçamento final", COL["coral"], width=2.8),
                         budget(r["mCV"], p["p1n"], p["p2"], "Novos preços, renda que mantém u₀ (VC)", COL["gold"], dash="dash", width=2.2),
                         budget(r["mEV"], p["p1"], p["p2"], "Preços antigos, renda que dá u₁ (VE)", COL["teal"], dash="dash", width=2.2),
                         dot(*r["x0"], "Cesta inicial", COL["navy"], size=11, edge="#fff"), dot(*r["x1"], "Cesta final", COL["coral"], size=11, edge="#fff")],
                        "Bem 1 (x₁)", "Bem 2 (x₂)", [0, xm], [0, ym]), key=f"{mid}-1")
        with t2:
            lo, hi = min(p["p1"], p["p1n"]), max(p["p1"], p["p1n"])
            xd = r["xd"]
            ps, band = C.lin(lo * 0.35, hi * 1.6, 300), C.lin(lo, hi, 80)
            gain = p["p1n"] < p["p1"]
            tr = []
            if hi > lo:
                tr.append(area([0, *map(xd, band), 0], [lo, *band, hi], "ΔEC (ganho)" if gain else "ΔEC (perda)",
                               "rgba(242,194,0,.45)" if gain else "rgba(210,85,58,.35)"))
            tr += [ln([xd(q) for q in ps], ps, "Demanda x₁(p₁)", COL["navy"], width=3, hover="x₁ %{x:.2f} · p₁ %{y:.2f}"),
                   dot(xd(p["p1"]), p["p1"], "Inicial", COL["navy"], size=10, edge="#fff"), dot(xd(p["p1n"]), p["p1n"], "Final", COL["coral"], size=10, edge="#fff")]
            chart(fig2d(tr, "Quantidade do bem 1 (x₁)", "Preço do bem 1 (p₁)", [0, 1.1 * max(xd(lo * 0.6), xd(lo), 1e-6)], [0, hi * 1.6]), key=f"{mid}-2")
        tol = 1e-4 * max(1, abs(r["dCS"]))
        ok, same = r["CV"] <= r["dCS"] + tol and r["dCS"] <= r["EV"] + tol, abs(r["CV"] - r["EV"]) <= tol
        tiles([dict(k="Variação compensatória (VC)", v=sgn(r["CV"]), key=True, s="renda que poderia ser retirada após a mudança"),
               dict(k="Variação do excedente (ΔEC)", v=sgn(r["dCS"]), key=True, s="área à esquerda da demanda"),
               dict(k="Variação equivalente (VE)", v=sgn(r["EV"]), key=True, s="renda que equivaleria à mudança"),
               dict(k="Ordem das medidas", v="VC = ΔEC = VE", chip=("Sem efeito renda: as três coincidem", "good")) if same else
               dict(k="Ordem das medidas", v="VC ≤ ΔEC ≤ VE" if r["CV"] <= r["EV"] else "VE ≤ ΔEC ≤ VC",
                    chip=("Bem normal", "good") if ok else ("Bem inferior: a ordem se inverte", "warn"))])
