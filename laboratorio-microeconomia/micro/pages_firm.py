"""Capítulos 16 a 24: equilíbrio, tecnologia, custos e oferta."""
import plotly.graph_objects as go
import streamlit as st
from . import core as C
from .registry import page, CHAPTERS
from .ui import (split, group, cb, COL, SCALE, header, sl, ces_controls, tiles, fmt, sgn, chart, fig2d, fig3d, ln, dot, area, rect, sigma_text)


def cols(n=3):
    return split(n)


@page("impostos", 16)
def impostos():
    mid = "imp"
    header(16, CHAPTERS[16], "Equilíbrio e incidência de impostos",
           "Um imposto por unidade abre uma cunha entre o preço pago pelo consumidor e o recebido pelo produtor. Quem arca com mais "
           "imposto é o lado menos elástico. Valores negativos de t viram subsídio.",
           [("Demanda e oferta", r"P_d=a-bQ,\ \ P_s=s_0+s_1Q"), ("Com imposto", r"P_d-P_s=t"), ("Parcela do consumidor", r"\frac{\Delta P_d}{t}=\frac{s_1}{b+s_1}")])
    left, right = cols()
    with left:
        p = dict(a=sl(mid, "a", "Intercepto da demanda (a)", 20, 150, 100, 1), b=sl(mid, "b", "Inclinação da demanda (b)", 0.1, 5.0, 1.0, 0.1),
                 s0=sl(mid, "s0", "Intercepto da oferta (s₀)", 0, 60, 10, 1), s1=sl(mid, "s1", "Inclinação da oferta (s₁)", 0.1, 5.0, 1.0, 0.1),
                 t=sl(mid, "t", "Imposto por unidade (t)", -30, 60, 20, 1))
    r = C.tax_eq(p)
    with right:
        if not r["ok"]:
            st.warning("A oferta começa acima da demanda (s₀ ≥ a): não há comércio nem sem imposto.")
            return
        if r["Qt"] <= 0:
            st.warning("O imposto é tão alto que elimina o mercado.")
        X = min(max(p["a"] / p["b"], r["Q0"] * 1.3), 1.6 * max(r["Q0"], r["Qt"]) + 1)
        tr = []
        if r["Qt"] > 0 and p["t"] != 0:
            tr += [rect(0, r["Qt"], min(r["Ps"], r["Pd"]), max(r["Ps"], r["Pd"]), "Arrecadação" if p["t"] > 0 else "Custo do subsídio", "rgba(242,194,0,.42)"),
                   area([r["Qt"], r["Qt"], r["Q0"]], [r["Pd"], r["Ps"], r["P0"]], "Peso morto", "rgba(210,85,58,.42)")]
        tr += [ln([0, X], [p["a"], p["a"] - p["b"] * X], "Demanda", COL["navy"], width=3), ln([0, X], [p["s0"], p["s0"] + p["s1"] * X], "Oferta", COL["teal"], width=3)]
        if p["t"] != 0:
            tr.append(ln([0, X], [p["s0"] + p["t"], p["s0"] + p["t"] + p["s1"] * X], "Oferta + imposto" if p["t"] > 0 else "Oferta − subsídio", COL["teal"], dash="dash", width=2))
        tr.append(dot(r["Q0"], r["P0"], "Sem imposto", COL["ink"], size=10, edge="#fff"))
        if r["Qt"] > 0:
            tr += [dot(r["Qt"], r["Pd"], "Preço do consumidor P_d", COL["yellow"], size=13), dot(r["Qt"], r["Ps"], "Preço do produtor P_s", COL["coral"], size=11, edge="#fff")]
        chart(fig2d(tr, "Quantidade (Q)", "Preço (P)", [0, X], [0, p["a"] * 1.05]))
        tiles([dict(k="Preço do consumidor P_d", v=fmt(r["Pd"]), key=True, s="sem imposto: " + fmt(r["P0"])), dict(k="Preço do produtor P_s", v=fmt(r["Ps"]), key=True),
               dict(k="Quantidade", v=fmt(r["Qt"]), s="sem imposto: " + fmt(r["Q0"])),
               dict(k="Arrecadação" if p["t"] >= 0 else "Custo do subsídio", v=fmt(abs(r["rev"]))), dict(k="Peso morto", v=fmt(r["dwl"])),
               dict(k="Parcela paga pelo consumidor", v=fmt(100 * r["cons"], 1) + "%",
                    chip=("Demanda menos elástica", "info") if r["cons"] > 0.5 else ("Oferta menos elástica", "info") if r["cons"] < 0.5 else ("Divisão igual", "info"))])


@page("producao-ces", 19)
def producao_ces():
    mid = "prod"
    header(19, CHAPTERS[19], "Função de produção CES",
           "A mesma família CES do consumidor, agora com capital e trabalho. ρ controla a facilidade de trocar um insumo pelo outro ao longo da isoquanta.",
           [("Produção", r"Y=\left[\delta K^{\rho}+(1-\delta)L^{\rho}\right]^{1/\rho}"), ("Elasticidade de substituição", r"\sigma=\frac{1}{1-\rho}")])
    left, right = cols()
    with left:
        p = dict(delta=sl(mid, "delta", "Peso do capital (δ)", 0.1, 0.9, 0.5, 0.05))
        p["rho"], p["mode"] = ces_controls(mid, hint="ρ = 1: insumos substitutos perfeitos · ρ = 0: Cobb-Douglas · ρ → −∞: complementares perfeitos. Quanto maior ρ, mais fácil trocar capital por trabalho.")
        p["Kmax"] = sl(mid, "Kmax", "Escala dos eixos (K, L máx.)", 2, 50, 10, 1)
        p["Kf"] = sl(mid, "Kf", "Capital fixo no curto prazo (K̄)", 0.5, 50.0, 5.0, 0.5)
    m = p["Kmax"]
    with right:
        t1, t2, t3 = st.tabs(["Superfície de produção", "Mapa de isoquantas", "Curto prazo (K fixo)"])
        with t1:
            ax = C.lin(0, m, 45)
            z = [[C.ces_prod(K, L, p) for L in ax] for K in ax]
            chart(fig3d([go.Surface(x=ax, y=ax, z=z, colorscale=SCALE, showscale=False, name="Y(K, L)",
                                    contours=dict(z=dict(show=True, usecolormap=True, project=dict(z=True), width=2)),
                                    hovertemplate="L %{x:.2f} · K %{y:.2f}<br>Y %{z:.2f}<extra></extra>")],
                        "Trabalho (L)", "Capital (K)", "Produção (Y)"), key=f"{mid}-1")
        with t2:
            ax = C.lin(0, m, 90)
            z = [[C.ces_prod(K, L, p) for L in ax] for K in ax]
            chart(fig2d([go.Contour(x=ax, y=ax, z=z, colorscale=SCALE, ncontours=12, showscale=False, line=dict(width=2.2),
                                    contours=dict(coloring="lines", showlabels=True, labelfont=dict(size=11, color=COL["navy"])),
                                    hovertemplate="L %{x:.2f} · K %{y:.2f}<br>Y %{z:.2f}<extra></extra>")],
                        "Trabalho (L)", "Capital (K)", [0, m], [0, m], square=True, legend=False), key=f"{mid}-2")
        with t3:
            Ls = C.lin(0.01, m, 300)
            Y = [C.ces_prod(p["Kf"], L, p) for L in Ls]
            h = m * 1e-4
            MP = [(C.ces_prod(p["Kf"], L + h, p) - C.ces_prod(p["Kf"], max(L - h, 1e-9), p)) / (L + h - max(L - h, 1e-9)) for L in Ls]
            fig = fig2d([ln(Ls, Y, "Produto total f(K̄, L)", COL["navy"], width=3),
                         ln(Ls, MP, "Produto marginal (eixo direito)", COL["coral"], dash="dash", width=2.2, yaxis="y2")],
                        "Trabalho (L)", "Produção (Y)", [0, m])
            fig.update_layout(yaxis2=dict(title="Produto marginal do trabalho", overlaying="y", side="right", rangemode="tozero", showgrid=False),
                              margin=dict(r=64))
            chart(fig, key=f"{mid}-3")
        kind = (("Complementares perfeitos", "info") if p["mode"] == "leo" else ("Cobb-Douglas", "info") if abs(p["rho"]) < 1e-9
                else ("Substitutos perfeitos", "info") if abs(p["rho"] - 1) < 1e-9 else ("Isoquantas côncavas", "warn") if p["rho"] > 1 else ("CES", "info"))
        tiles([dict(k="Elasticidade de substituição σ", v=sigma_text(p["rho"], p["mode"]), key=True, chip=kind),
               dict(k="TTS em K = L", v="—" if p["mode"] == "leo" else fmt((1 - p["delta"]) / p["delta"]), s="PMg_L / PMg_K = (1 − δ)/δ"),
               dict(k="Retornos de escala", v="Constantes", s="f(tK, tL) = t·f(K, L)"),
               dict(k="Y(K̄, L = K̄)", v=fmt(C.ces_prod(p["Kf"], p["Kf"], p)), s="com K̄ = " + fmt(p["Kf"], 1))])


@page("lucro", 20)
def lucro():
    mid = "lucro"
    header(20, CHAPTERS[20], "Maximização de lucro",
           "A empresa competitiva escolhe K e L até o valor do produto marginal de cada insumo igualar seu preço. Só existe ótimo interior com retornos decrescentes (α + β < 1).",
           [("Lucro", r"\pi=P\,AK^{\alpha}L^{\beta}-rK-wL"), ("CPO", r"P\,f_K=r,\ \ P\,f_L=w"),
            ("Produto ótimo", r"y^*=\left[A\left(\tfrac{P\alpha}{r}\right)^{\alpha}\left(\tfrac{P\beta}{w}\right)^{\beta}\right]^{\frac{1}{1-\alpha-\beta}}")])
    left, right = cols()
    with left:
        p = dict(alpha=sl(mid, "alpha", "Elasticidade do capital (α)", 0.05, 0.95, 0.3, 0.01), beta=sl(mid, "beta", "Elasticidade do trabalho (β)", 0.05, 0.95, 0.5, 0.01),
                 A=sl(mid, "A", "Tecnologia (A)", 0.2, 3.0, 1.0, 0.05), P=sl(mid, "P", "Preço do produto (P)", 0.5, 6.0, 3.0, 0.1),
                 r=sl(mid, "r", "Custo do capital (r)", 0.2, 5.0, 1.0, 0.1), w=sl(mid, "w", "Salário (w)", 0.2, 5.0, 1.0, 0.1))
    r = C.profit_max(p)
    with right:
        if not r["ok"]:
            st.warning("Retornos constantes (α + β = 1): o lucro máximo é zero ou infinito e a escala fica indeterminada."
                       if abs(r["s"] - 1) < 1e-9 else "Retornos crescentes (α + β > 1): o lucro cresce sem limite com a escala, então não existe ótimo interior.")
        Km = max(2, 2.2 * r["K"]) if r["ok"] else 10
        Lm = max(2, 2.2 * r["L"]) if r["ok"] else 10
        t1, t2 = st.tabs(["Superfície de lucro", "Curvas de isolucro"])
        with t1:
            Ks, Ls = C.lin(0.001, Km, 45), C.lin(0.001, Lm, 45)
            tr = [go.Surface(x=Ls, y=Ks, z=[[C.profit_at(K, L, p) for L in Ls] for K in Ks], colorscale=SCALE, showscale=False, name="π(K, L)",
                             hovertemplate="L %{x:.2f} · K %{y:.2f}<br>π %{z:.3f}<extra></extra>")]
            if r["ok"]:
                tr.append(go.Scatter3d(mode="markers", x=[r["L"]], y=[r["K"]], z=[r["pi"]], name="Ótimo",
                                       marker=dict(size=7, color=COL["yellow"], line=dict(color=COL["navy"], width=2))))
            chart(fig3d(tr, "Trabalho (L)", "Capital (K)", "Lucro (π)"), key=f"{mid}-1")
        with t2:
            Ks, Ls = C.lin(0.001, Km, 90), C.lin(0.001, Lm, 90)
            z = [[C.profit_at(K, L, p) for L in Ls] for K in Ks]
            if r["ok"]:
                zmax = r["pi"]
                cont = dict(coloring="lines", showlabels=True, start=zmax - 6 * abs(zmax) - 1, end=zmax, size=(6 * abs(zmax) + 1) / 12,
                            labelfont=dict(size=11, color=COL["navy"]))
            else:
                cont = dict(coloring="lines", showlabels=True)
            tr = [go.Contour(x=Ls, y=Ks, z=z, colorscale=SCALE, showscale=False, contours=cont, line=dict(width=2), showlegend=False,
                             hovertemplate="L %{x:.2f} · K %{y:.2f}<br>π %{z:.3f}<extra></extra>")]
            if r["ok"]:
                tr.append(dot(r["L"], r["K"], "Ótimo (K*, L*)", COL["yellow"], size=14))
            chart(fig2d(tr, "Trabalho (L)", "Capital (K)", [0, Lm], [0, Km]), key=f"{mid}-2")
        rts = ("Decrescentes", "good") if r["s"] < 1 - 1e-9 else ("Constantes", "warn") if abs(r["s"] - 1) < 1e-9 else ("Crescentes", "bad")
        g = lambda k, d=3: fmt(r[k], d) if r["ok"] else "—"
        tiles([dict(k="Produto y*", v=g("y"), key=True), dict(k="Capital K*", v=g("K")), dict(k="Trabalho L*", v=g("L")),
               dict(k="Lucro π*", v=g("pi"), key=True),
               dict(k=f"Retornos de escala (α + β = {fmt(r['s'])})", v=rts[0], chip=("Ótimo interior" if r["ok"] else "Sem ótimo interior", rts[1]))])


def _cost_params(mid, extra):
    p = dict(A=sl(mid, "A", "Tecnologia (A)", 0.2, 3.0, 1.0, 0.05), alpha=sl(mid, "alpha", "Elasticidade do capital (α)", 0.05, 0.95, 0.5, 0.01),
             beta=sl(mid, "beta", "Elasticidade do trabalho (β)", 0.05, 0.95, 0.5, 0.01), w=sl(mid, "w", "Salário (w)", 0.2, 5.0, 1.0, 0.1),
             r=sl(mid, "r", "Custo do capital (r)", 0.2, 5.0, 1.0, 0.1))
    for k, args in extra:
        p[k] = sl(mid, k, *args)
    return p


@page("custo-min", 21)
def custo_min():
    mid = "cmin"
    header(21, CHAPTERS[21], "Minimização de custos",
           "Para produzir ŷ, a empresa busca a isocusto mais baixa que toca a isoquanta. No curto prazo, com K fixo, ela não consegue chegar à tangência e paga mais.",
           [("Longo prazo", r"\min_{K,L} wL+rK\ \text{s.a.}\ AK^{\alpha}L^{\beta}=\hat y"), ("Tangência", r"\frac{\alpha L}{\beta K}=\frac{r}{w}"),
            ("Curto prazo", r"L=\left(\frac{\hat y}{A\bar K^{\alpha}}\right)^{1/\beta}")])
    left, right = cols()
    with left:
        p = _cost_params(mid, [("Y", ("Produção desejada (ŷ)", 1.0, 50.0, 10.0, 0.5)), ("Kf", ("Capital fixo no curto prazo (K̄)", 0.5, 50.0, 5.0, 0.5))])
    lr, sr = C.cost_lr(p["Y"], p), C.cost_sr(p["Y"], p["Kf"], p)
    with right:
        t1, t2, t3 = st.tabs(["Isoquanta e isocusto", "Custo total: LP × CP", "Superfície de custo"])
        Lm, Km = max(2.2 * lr["L"], 1.25 * sr["L"]), max(2.2 * lr["K"], 1.4 * p["Kf"])
        with t1:
            Ls = C.lin(0.01, Lm, 300)
            chart(fig2d([ln(Ls, [C.pw(p["Y"] / (p["A"] * C.pw(l, p["beta"])), 1 / p["alpha"]) for l in Ls], "Isoquanta ŷ", COL["royal"], width=3),
                         ln(Ls, [(lr["C"] - p["w"] * l) / p["r"] for l in Ls], "Isocusto mínima (LP)", COL["navy"], width=2.4),
                         ln(Ls, [(sr["C"] - p["w"] * l) / p["r"] for l in Ls], "Isocusto do curto prazo", COL["coral"], dash="dash", width=2.2),
                         ln([0, Lm], [p["Kf"], p["Kf"]], "K = K̄", COL["muted"], dash="dot", width=1.6),
                         dot(lr["L"], lr["K"], "Ótimo de longo prazo", COL["yellow"], size=14), dot(sr["L"], sr["K"], "Escolha de curto prazo", COL["coral"], size=11, edge="#fff")],
                        "Trabalho (L)", "Capital (K)", [0, Lm], [0, Km]), key=f"{mid}-1")
        with t2:
            ys = C.lin(0.05, 2 * p["Y"], 300)
            chart(fig2d([ln(ys, [C.cost_lr(y, p)["C"] for y in ys], "Custo de longo prazo", COL["navy"], width=3),
                         ln(ys, [C.cost_sr(y, p["Kf"], p)["C"] for y in ys], "Custo de curto prazo (K̄ fixo)", COL["coral"], dash="dash"),
                         dot(p["Y"], lr["C"], "LP em ŷ", COL["yellow"], size=12), dot(p["Y"], sr["C"], "CP em ŷ", COL["coral"], size=10, edge="#fff")],
                        "Produção (y)", "Custo total (C)"), key=f"{mid}-2")
        with t3:
            Ls3, Ks3 = C.lin(0, Lm, 40), C.lin(0, Km, 40)
            chart(fig3d([go.Surface(x=Ls3, y=Ks3, z=[[p["w"] * L + p["r"] * K for L in Ls3] for K in Ks3], colorscale=SCALE, opacity=0.85, showscale=False, name="C = wL + rK"),
                         go.Scatter3d(mode="markers", x=[lr["L"]], y=[lr["K"]], z=[lr["C"]], name="Ótimo de longo prazo",
                                      marker=dict(size=7, color=COL["yellow"], line=dict(color=COL["navy"], width=2))),
                         go.Scatter3d(mode="markers", x=[sr["L"]], y=[sr["K"]], z=[sr["C"]], name="Ótimo de curto prazo", marker=dict(size=6, color=COL["coral"]))],
                        "Trabalho (L)", "Capital (K)", "Custo total"), key=f"{mid}-3")
        tiles([dict(k="Longo prazo: L* ; K*", v=fmt(lr["L"]) + " ; " + fmt(lr["K"]), key=True), dict(k="Custo mínimo C*", v=fmt(lr["C"]), key=True),
               dict(k=f"Curto prazo: L com K̄ = {fmt(p['Kf'], 1)}", v=fmt(sr["L"])),
               dict(k="Custo de curto prazo", v=fmt(sr["C"]), chip=("K̄ já é o ótimo", "good") if sr["C"] - lr["C"] < 1e-6 else (f"+{fmt(sr['C'] - lr['C'])} acima do LP", "warn"))])


@page("curvas-custo", 22)
def curvas_custo():
    mid = "ccurv"
    header(22, CHAPTERS[22], "Curvas de custo",
           "Custo médio, custo variável médio e custo marginal a partir da tecnologia Cobb-Douglas. O CMg corta o CMe no mínimo deste; o CMe de longo prazo envolve os de curto prazo.",
           [("Longo prazo", r"c(y)=c(1)\,y^{\frac{1}{\alpha+\beta}},\ \ CMg=\frac{c(y)}{(\alpha+\beta)y}"), ("Curto prazo", r"c_s(y)=r\bar K+w\left(\frac{y}{A\bar K^{\alpha}}\right)^{1/\beta}")])
    left, right = cols()
    with left:
        p = _cost_params(mid, [("Kf", ("Capital fixo no curto prazo (K̄)", 0.5, 50.0, 5.0, 0.5)), ("Ymax", ("Produção máxima no gráfico", 5, 200, 30, 5))])
    ys = C.lin(p["Ymax"] / 400, p["Ymax"], 400)
    srs = [C.cost_sr(y, p["Kf"], p) for y in ys]
    lrs = [C.cost_lr(y, p) for y in ys]
    i_min = min(range(len(srs)), key=lambda i: srs[i]["AC"])
    s = p["alpha"] + p["beta"]
    with right:
        t1, t2, t3 = st.tabs(["Longo prazo", "Curto prazo", "Envoltória"])
        with t1:
            mid_i = len(ys) // 2
            chart(fig2d([ln(ys, [c["AC"] for c in lrs], "CMe de longo prazo", COL["navy"], width=3), ln(ys, [c["MC"] for c in lrs], "CMg de longo prazo", COL["coral"])],
                        "Produção (y)", "Custo por unidade", [0, p["Ymax"]], [0, 1.6 * max(lrs[mid_i]["MC"], lrs[mid_i]["AC"])]), key=f"{mid}-1")
        with t2:
            m = srs[i_min]
            yTop = max(2.4 * m["AC"], 1.1 * min(srs[-1]["MC"], 4 * m["AC"]))
            chart(fig2d([ln(ys, [c["AC"] for c in srs], "CMe (curto prazo)", COL["navy"], width=3), ln(ys, [c["AVC"] for c in srs], "CVMe", COL["royal"], dash="dash", width=2.4),
                         ln(ys, [c["AFC"] for c in srs], "CFMe", COL["faint"], dash="dot", width=2), ln(ys, [c["MC"] for c in srs], "CMg (curto prazo)", COL["coral"]),
                         dot(ys[i_min], m["AC"], "CMe mínimo", COL["yellow"], size=12)],
                        "Produção (y)", "Custo por unidade", [0, p["Ymax"]], [0, yTop]), key=f"{mid}-2")
        with t3:
            ref = lrs[len(ys) // 2]["AC"]
            tr = [ln(ys, [C.cost_sr(y, K, p)["AC"] for y in ys], "CMe de curto prazo", COL["faint"], width=1.8, legend=i == 0,
                     hover=f"K̄ = {fmt(K, 1)}<br>%{{x:.2f}} · %{{y:.2f}}") for i, K in enumerate(f * p["Kf"] for f in (0.25, 0.5, 1, 2, 4))]
            tr.append(ln(ys, [c["AC"] for c in lrs], "CMe de longo prazo (envoltória)", COL["navy"], width=3.2))
            chart(fig2d(tr, "Produção (y)", "Custo médio", [0, p["Ymax"]], [0, 2.6 * ref]), key=f"{mid}-3")
        rts = ("Decrescentes", "CMe de LP sobe", "warn") if s < 1 - 1e-9 else ("Constantes", "CMe de LP plano", "info") if abs(s - 1) < 1e-9 else ("Crescentes", "CMe de LP cai", "good")
        edge = i_min == len(srs) - 1
        tiles([dict(k=f"Retornos de escala (α + β = {fmt(s)})", v=rts[0], chip=(rts[1], rts[2])),
               dict(k="CMe mínimo de curto prazo", v=fmt(srs[i_min]["AC"]), key=True, s="no limite do gráfico: aumente a produção máxima" if edge else "onde CMg = CMe"),
               dict(k="Produção nesse ponto", v=fmt(ys[i_min])), dict(k="CMe de longo prazo nesse y", v=fmt(lrs[i_min]["AC"]))])


def _cubic_params(mid):
    return dict(a=sl(mid, "a", "Custo variável: termo linear (a)", 2.0, 20.0, 10.0, 0.5, hint="Custo variável c(y) = a·y − b·y² + c·y³: o CVMe tem formato de U, com mínimo em y = b/(2c)."),
                b=sl(mid, "b", "Custo variável: termo quadrático (b)", 0.5, 4.0, 2.0, 0.1),
                c=sl(mid, "c", "Custo variável: termo cúbico (c)", 0.05, 1.0, 0.2, 0.01), F=sl(mid, "F", "Custo fixo (F)", 0, 100, 20, 1))


@page("oferta-empresa", 23)
def oferta_empresa():
    mid = "ofemp"
    header(23, CHAPTERS[23], "Oferta da empresa competitiva",
           "A empresa toma o preço como dado e produz onde P = CMg. Abaixo do mínimo do custo variável médio, ela fecha: a curva de oferta é o trecho do CMg acima do CVMe.",
           [("Custo", r"c(y)=F+ay-by^2+cy^3"), ("Oferta (y = 0 abaixo do mín. CVMe)", r"P=CMg(y),\quad P\ge\min CVMe")])
    left, right = cols()
    with left:
        p = _cubic_params(mid)
        p["P"] = sl(mid, "P", "Preço de mercado (P)", 0.0, 40.0, 12.0, 0.5)
    r = C.firm(p)
    with right:
        if not r["ok"]:
            st.warning("Com esses coeficientes o custo variável fica negativo em algum trecho; aumente o termo linear (a) ou o cúbico (c).")
            return
        f = r["f"]
        yM = max(2.4 * r["yAC"], r["y"] * 1.25, 1)
        ys = C.lin(yM / 300, yM, 300)
        ysS = [y for y in ys if y >= r["yAVC"]]
        tr = []
        if r["y"] > 0:
            tr.append(rect(0, r["y"], f.AC(r["y"]), p["P"], "Lucro" if r["profit"] >= 0 else "Prejuízo",
                           "rgba(23,143,126,.28)" if r["profit"] >= 0 else "rgba(210,85,58,.32)"))
        tr += [ln(ys, [f.AC(y) for y in ys], "CMe", COL["navy"]), ln(ys, [f.AVC(y) for y in ys], "CVMe", COL["royal"], dash="dash", width=2.2),
               ln(ys, [f.MC(y) for y in ys], "CMg", COL["coral"], width=2.4),
               ln([0, 0, *ysS], [0, r["minAVC"], *[f.MC(y) for y in ysS]], "Curva de oferta", COL["gold"], width=6, opacity=0.55),
               ln([0, yM], [p["P"], p["P"]], "Preço P", COL["ink"], dash="dot", width=1.6),
               dot(r["yAVC"], r["minAVC"], "Ponto de fechamento", COL["royal"], size=10, edge="#fff")]
        if r["y"] > 0:
            tr.append(dot(r["y"], p["P"], "Escolha da empresa", COL["yellow"], size=14))
        chart(fig2d(tr, "Produção (y)", "Preço e custo por unidade", [0, yM], [0, max(p["P"] * 1.5, r["minAC"] * 2.2, 5)]))
        chip = ("Fecha (y = 0)", "bad") if r["y"] == 0 else ("Lucro econômico", "good") if r["profit"] >= 0 else ("Prejuízo, mas produz", "warn")
        tiles([dict(k="Produção ótima y*", v=fmt(r["y"]), key=True, chip=chip), dict(k="Lucro", v=fmt(r["profit"]), s="perde só o custo fixo" if r["y"] == 0 else ""),
               dict(k="Preço de fechamento (mín. CVMe)", v=fmt(r["minAVC"]), s="em y = " + fmt(r["yAVC"])),
               dict(k="Mínimo do CMe", v=fmt(r["minAC"]), s="preço de longo prazo, em y = " + fmt(r["yAC"]))])


@page("oferta-industria", 24)
def oferta_industria():
    mid = "ofind"
    header(24, CHAPTERS[24], "Oferta da indústria e entrada",
           "No curto prazo, a oferta da indústria é a soma das ofertas das n empresas. Com lucro positivo, entram empresas até o preço cair ao mínimo do custo médio: a oferta de longo prazo é horizontal.",
           [("Curto prazo", r"S(P)=n\,y(P)=D(P)"), ("Longo prazo", r"P=\min CMe,\ \ n^*=\frac{D(\min CMe)}{y_{CMe}}")])
    left, right = cols()
    with left:
        group("Custo de cada empresa")
        p = _cubic_params(mid)
        group("Mercado")
        p.update(Dmax=sl(mid, "Dmax", "Demanda a preço zero", 50, 1000, 300, 10), d=sl(mid, "d", "Sensibilidade da demanda ao preço (d)", 1.0, 20.0, 5.0, 0.5),
                 n=sl(mid, "n", "Número de empresas (n)", 1, 100, 25, 1))
    r = C.industry(p)
    with right:
        if not r["ok"]:
            st.warning("Com esses coeficientes o custo variável fica negativo em algum trecho; aumente o termo linear (a) ou o cúbico (c).")
            return
        Qx = p["Dmax"] * 1.02
        Ps = C.lin(r["minAVC"], max(r["Pmax"], r["minAVC"] + 1), 200)
        chart(fig2d([ln([0, p["Dmax"]], [r["Pmax"], 0], "Demanda", COL["navy"], width=3),
                     ln([0, *[r["S"](P) for P in Ps]], [r["minAVC"], *Ps], "Oferta de curto prazo (n empresas)", COL["coral"]),
                     ln([0, Qx], [r["PLR"], r["PLR"]], "Oferta de longo prazo (mín. CMe)", COL["teal"], dash="dash", width=2.4),
                     dot(r["Q"], r["P"], "Equilíbrio de curto prazo", COL["yellow"], size=14), dot(r["QLR"], r["PLR"], "Equilíbrio de longo prazo", COL["teal"], size=11, edge="#fff")],
                    "Quantidade da indústria (Q)", "Preço (P)", [0, Qx], [0, max(r["Pmax"], r["P"]) * 1.05]))
        dn = r["nLR"] - p["n"]
        pe = r["profitEach"]
        tiles([dict(k="Preço de curto prazo", v=fmt(r["P"]), key=True, s="quantidade: " + fmt(r["Q"])),
               dict(k="Lucro de cada empresa", v=fmt(pe), chip=("Atrai entrada", "good") if pe > 1e-6 else ("Provoca saída", "bad") if pe < -1e-6 else ("Lucro zero", "info")),
               dict(k="Preço de longo prazo (mín. CMe)", v=fmt(r["PLR"]), key=True, s="quantidade: " + fmt(r["QLR"])),
               dict(k="Empresas no longo prazo", v=fmt(r["nLR"], 1), s=("entram " if dn >= 0 else "saem ") + fmt(abs(dn), 1))])
