"""Capítulos 6, 7, 15, 18 e 34."""
import streamlit as st
from . import core as C
from .registry import page, CHAPTERS
from .ui import (split, group, rd, COL, header, sl, tiles, fmt, chart, fig2d, ln, dot, area, rect, budget, pref_controls, pref2_controls, pref_eqs,
                 AGENT_EQ, cached, box_ic, contract_trace)


def cols(n=3):
    return split(n)


@page("demanda", 6)
def demanda():
    mid = "dem"
    header(6, CHAPTERS[6], "Demanda: curvas de renda-consumo, Engel e preço-consumo",
           "Como a cesta ótima muda quando a renda ou o preço mudam. Complementares, Cobb-Douglas, substitutos e CES são homotéticas "
           "(a renda-consumo é uma reta pela origem); com preferências quase-lineares, toda renda extra vai para o bem 2.",
           [("Elasticidades", r"\varepsilon_m=\frac{\partial x_1}{\partial m}\frac{m}{x_1},\quad \varepsilon_p=\frac{\partial x_1}{\partial p_1}\frac{p_1}{x_1}")])
    left, right = cols()
    with left:
        p = pref_controls(mid, value="ces", a=(1, 20, 0.5, 4))
        pref_eqs(p, demand=True)
        group("Preços e renda")
        p["m"] = sl(mid, "m", "Renda (m)", 10, 300, 100, 5)
        p["p1"] = sl(mid, "p1", "Preço do bem 1 (p₁)", 1.0, 30.0, 10.0, 0.5)
        p["p2"] = sl(mid, "p2", "Preço do bem 2 (p₂)", 1.0, 30.0, 10.0, 0.5)
    r = C.demand_stats(p)

    def ic(d, xm, ym, main):
        xs, ys = C.level6(C.util6(max(d["x1"], 1e-9), d["x2"], p), p, xm, ym)
        return ln(xs, ys, "Curvas de indiferença", COL["royal"] if main else COL["faint"], width=2.4 if main else 1.6, legend=main)

    def goods(kind, key):
        fs = [0.5, 1, 1.5] if kind == "renda" else [2, 1, 0.5]
        pts = [dict(m=p["m"] * f, p1=p["p1"]) if kind == "renda" else dict(m=p["m"], p1=p["p1"] * f) for f in fs]
        for o in pts:
            o["d"] = C.demand6(p, o["m"], o["p1"])
        xm, ym = 1.1 * max(o["m"] / o["p1"] for o in pts), 1.15 * max(o["m"] / p["p2"] for o in pts)
        ts = C.lin(0.02, 1, 160)
        path = [C.demand6(p, 2 * p["m"] * t, p["p1"]) if kind == "renda" else C.demand6(p, p["m"], p["p1"] * (0.25 + 3.75 * t)) for t in ts]
        tr = []
        for i, o in enumerate(pts):
            tr.append(ic(o["d"], xm, ym, i == 1))
            tr.append(budget(o["m"], o["p1"], p["p2"], "Orçamento atual" if i == 1 else "Outros orçamentos", COL["navy"] if i == 1 else COL["muted"],
                             width=3 if i == 1 else 1.8, legend=i < 2, dash="solid" if i == 1 else "dash"))
        tr.append(ln([d["x1"] for d in path], [d["x2"] for d in path], "Curva de renda-consumo" if kind == "renda" else "Curva de preço-consumo", COL["coral"], width=3))
        tr += [dot(o["d"]["x1"], o["d"]["x2"], "Cestas ótimas", COL["yellow"] if i == 1 else "#fff", size=14 if i == 1 else 10, legend=i == 1) for i, o in enumerate(pts)]
        chart(fig2d(tr, "Bem 1 (x₁)", "Bem 2 (x₂)", [0, xm], [0, ym]), key=key)

    with right:
        t1, t2, t3, t4 = st.tabs(["Curva de renda-consumo", "Curva de Engel", "Curva de preço-consumo", "Curva de demanda"])
        with t1:
            goods("renda", f"{mid}-1")
        with t2:
            ms = C.lin(1, 2 * p["m"], 200)
            xs = [C.demand6(p, m, p["p1"])["x1"] for m in ms]
            chart(fig2d([ln(xs, ms, "Curva de Engel", COL["navy"], width=3, hover="x₁ %{x:.2f} · m %{y:.2f}"), dot(r["x1"], p["m"], "Renda atual", COL["yellow"], size=14)],
                        "Quantidade do bem 1 (x₁)", "Renda (m)", [0, max(max(xs), 1e-6) * 1.15], [0, 2 * p["m"]]), key=f"{mid}-2")
        with t3:
            goods("preco", f"{mid}-3")
        with t4:
            ps = C.lin(0.25 * p["p1"], 3 * p["p1"], 200)
            xs = [C.demand6(p, p["m"], q)["x1"] for q in ps]
            chart(fig2d([ln(xs, ps, "Curva de demanda", COL["navy"], width=3, hover="x₁ %{x:.2f} · p₁ %{y:.2f}"), dot(r["x1"], p["p1"], "Preço atual", COL["yellow"], size=14)],
                        "Quantidade do bem 1 (x₁)", "Preço do bem 1 (p₁)", [0, max(max(xs), 1e-6) * 1.08], [0, 3 * p["p1"]]), key=f"{mid}-4")
        em, ep = r["em"], r["ep"]
        cm = None if em != em else ("Renda não afeta x₁", "info") if abs(em) < 1e-3 else ("Homotética: ε = 1", "info") if abs(em - 1) < 1e-3 else ("Bem de luxo", "warn") if em > 1 else ("Bem necessário", "good") if em > 0 else ("Bem inferior", "bad")
        cp = None if ep != ep else ("Unitária", "info") if abs(ep + 1) < 1e-3 else ("Elástica", "warn") if ep < -1 else ("Inelástica", "good")
        tiles([dict(k="x₁*", v=fmt(r["x1"]), key=True), dict(k="x₂*", v=fmt(r["x2"]), key=True),
               dict(k="Elasticidade-renda de x₁", v=fmt(em), chip=cm), dict(k="Elasticidade-preço de x₁", v=fmt(ep), chip=cp)])


@page("preferencia-revelada", 7)
def preferencia_revelada():
    mid = "pr"
    header(7, CHAPTERS[7], "Preferência revelada",
           "Duas escolhas observadas, cada uma com seus preços. Se a cesta Y cabia no orçamento quando X foi escolhida, X é revelada preferida a Y. "
           "O Axioma Fraco proíbe que as duas cestas sejam reveladas preferidas uma à outra.",
           [("X revelada preferida a Y", r"p_1x_1+p_2x_2\ \ge\ p_1y_1+p_2y_2"), ("Índices de quantidade", r"L_q=\frac{p\cdot y}{p\cdot x},\quad P_q=\frac{q\cdot y}{q\cdot x}")])
    left, right = cols(4)
    with left:
        group("Observação 1: preços p, cesta X")
        p = dict(p1=sl(mid, "p1", "p₁", 0.5, 5.0, 2.0, 0.5), p2=sl(mid, "p2", "p₂", 0.5, 5.0, 1.0, 0.5), x1=sl(mid, "x1", "x₁", 0.5, 10.0, 3.0, 0.5), x2=sl(mid, "x2", "x₂", 0.5, 10.0, 4.0, 0.5))
        group("Observação 2: preços q, cesta Y")
        p.update(q1=sl(mid, "q1", "q₁", 0.5, 5.0, 1.0, 0.5), q2=sl(mid, "q2", "q₂", 0.5, 5.0, 2.0, 0.5), y1=sl(mid, "y1", "y₁", 0.5, 10.0, 4.0, 0.5), y2=sl(mid, "y2", "y₂", 0.5, 10.0, 2.0, 0.5))
    r = C.revealed(p)
    with right:
        if r["violates"]:
            st.error("Violação do Axioma Fraco: X foi escolhida quando Y cabia no orçamento, e Y foi escolhida quando X cabia. "
                     "Nenhum consumidor maximizador com preferências estáveis faria as duas escolhas.")
        else:
            st.success("Escolhas consistentes com o Axioma Fraco: " + ("X é revelada preferida a Y." if r["xRPy"] else "Y é revelada preferida a X." if r["yRPx"]
                       else "nenhuma cesta cabia no orçamento da outra, então nada é revelado."))
        st.caption("Para ver uma violação, use p = (1, 2), X = (1, 2), q = (2, 1), Y = (2, 1).")
        xm = 1.1 * max(r["px"] / p["p1"], r["qy"] / p["q1"], p["x1"], p["y1"])
        ym = 1.1 * max(r["px"] / p["p2"], r["qy"] / p["q2"], p["x2"], p["y2"])
        chart(fig2d([area([0, r["px"] / p["p1"], 0], [0, 0, r["px"] / p["p2"]], "Cabia no orçamento 1", "rgba(42,100,184,.13)"),
                     area([0, r["qy"] / p["q1"], 0], [0, 0, r["qy"] / p["q2"]], "Cabia no orçamento 2", "rgba(210,85,58,.13)"),
                     budget(r["px"], p["p1"], p["p2"], "Orçamento 1 (preços p)", COL["royal"], width=3), budget(r["qy"], p["q1"], p["q2"], "Orçamento 2 (preços q)", COL["coral"], width=3),
                     dot(p["x1"], p["x2"], "X: escolhida aos preços p", COL["royal"], size=14, edge="#fff", text="X"),
                     dot(p["y1"], p["y2"], "Y: escolhida aos preços q", COL["coral"], size=14, edge="#fff", text="Y")],
                    "Bem 1", "Bem 2", [0, xm], [0, ym]))
        tiles([dict(k="Aos preços p: gasto em X · custo de Y", v=f"{fmt(r['px'])} · {fmt(r['py'])}", key=True, chip=("Y cabia: X é revelada preferida", "info") if r["xRPy"] else ("Y não cabia", "warn")),
               dict(k="Aos preços q: gasto em Y · custo de X", v=f"{fmt(r['qy'])} · {fmt(r['qx'])}", key=True, chip=("X cabia: Y é revelada preferida", "info") if r["yRPx"] else ("X não cabia", "warn")),
               dict(k="Axioma Fraco", v="Violado" if r["violates"] else "Satisfeito", chip=("Inconsistente", "bad") if r["violates"] else ("Consistente", "good")),
               dict(k="Índices de quantidade (de X para Y)", v=f"L = {fmt(r['Lq'], 3)} ; P = {fmt(r['Pq'], 3)}",
                    s="Paasche > 1: melhorou com certeza" if r["Pq"] > 1 else "Laspeyres < 1: piorou com certeza" if r["Lq"] < 1 else "os índices não decidem")])


@page("demanda-mercado", 15)
def demanda_mercado():
    mid = "dm"
    header(15, CHAPTERS[15], "Demanda de mercado, elasticidade e receita",
           "Numa demanda linear a elasticidade muda ao longo da curva: elástica na metade de cima, inelástica na de baixo. A receita é máxima onde a elasticidade é −1. "
           "A demanda de mercado é a soma horizontal das individuais.",
           [("Demanda", r"P=A-BQ"), ("Elasticidade", r"\varepsilon=\frac{dQ}{dP}\frac{P}{Q}=-\frac{P}{A-P}"), ("Receita marginal", r"RMg=P\left(1-\frac{1}{|\varepsilon|}\right)")])
    t1, t2, t3 = st.tabs(["Demanda e elasticidade", "Receita", "Agregação de demandas"])
    with t1:
        left, right = cols()
        with left:
            p = dict(A=sl(mid, "A", "Intercepto (A)", 20, 150, 100, 1), B=sl(mid, "B", "Inclinação (B)", 0.2, 5.0, 1.0, 0.1), P=sl(mid, "P", "Preço (P)", 1, 150, 30, 1))
        r = C.market_demand(p)
        qx = p["A"] / p["B"]
        tr = [rect(0, r["Q"], 0, p["P"], "Receita = P·Q", "rgba(242,194,0,.38)")] if r["Q"] > 0 else []
        tr += [ln([0, r["Qu"]], [p["A"], r["Pu"]], "Trecho elástico (|ε| > 1)", COL["navy"], width=3.4), ln([r["Qu"], qx], [r["Pu"], 0], "Trecho inelástico (|ε| < 1)", COL["teal"], width=3.4),
               ln([0, qx / 2], [p["A"], 0], "Receita marginal", COL["royal"], dash="dash", width=2.2),
               dot(r["Qu"], r["Pu"], "Elasticidade unitária", COL["coral"], size=11, edge="#fff"), dot(r["Q"], min(p["P"], p["A"]), "Preço atual", COL["yellow"], size=14)]
        chart(fig2d(tr, "Quantidade (Q)", "Preço (P)", [0, qx * 1.02], [0, p["A"] * 1.05]), key=f"{mid}-1")
        a = abs(r["eps"])
        chip = ("Sem demanda a esse preço", "bad") if r["Q"] <= 0 else ("Unitária", "info") if abs(a - 1) < 1e-6 else ("Elástica: baixar o preço aumenta a receita", "warn") if a > 1 else ("Inelástica: subir o preço aumenta a receita", "good")
        info = [dict(k="Quantidade demandada", v=fmt(r["Q"]), key=True), dict(k="Elasticidade-preço ε", v=fmt(r["eps"]), key=True, chip=chip),
                dict(k="Receita", v=fmt(r["R"]), s=f"máxima: {fmt(r['Rmax'])} em P = {fmt(r['Pu'])}"), dict(k="Receita marginal", v=fmt(r["MR"]), s="positiva só no trecho elástico")]
        tiles(info)
    with t2:
        st.caption("Usa a mesma demanda e o mesmo preço da primeira aba.")
        qs = C.lin(0, qx, 200)
        chart(fig2d([ln(qs, [(p["A"] - p["B"] * q) * q for q in qs], "Receita total", COL["navy"], width=3),
                     dot(r["Qu"], r["Rmax"], "Receita máxima (|ε| = 1)", COL["coral"], size=11, edge="#fff"), dot(r["Q"], r["R"], "Preço atual", COL["yellow"], size=14)],
                    "Quantidade (Q)", "Receita (P·Q)", [0, qx], [0, r["Rmax"] * 1.12]), key=f"{mid}-2")
        tiles(info)
    with t3:
        left, right = cols(4)
        with left:
            g = dict(a1=sl(mid, "a1", "Consumidor 1: intercepto (a₁)", 10, 100, 80, 1), b1=sl(mid, "b1", "Consumidor 1: inclinação (b₁)", 0.2, 5.0, 2.0, 0.1),
                     a2=sl(mid, "a2", "Consumidor 2: intercepto (a₂)", 10, 100, 40, 1), b2=sl(mid, "b2", "Consumidor 2: inclinação (b₂)", 0.2, 5.0, 1.0, 0.1))
        top, lo = max(g["a1"], g["a2"]), min(g["a1"], g["a2"])
        Ps = C.lin(0, top, 400)
        chart(fig2d([ln([0, g["a1"] / g["b1"]], [g["a1"], 0], "Consumidor 1", COL["royal"], width=2.2, dash="dash"), ln([0, g["a2"] / g["b2"]], [g["a2"], 0], "Consumidor 2", COL["teal"], width=2.2, dash="dash"),
                     ln([C.agg_q(g, P) for P in Ps], Ps, "Demanda de mercado (soma horizontal)", COL["navy"], width=3.4, hover="Q %{x:.2f} · P %{y:.2f}"),
                     dot(C.agg_q(g, lo), lo, "Quebra: o segundo consumidor entra", COL["yellow"], size=12)],
                    "Quantidade", "Preço (P)", None, [0, top * 1.05]), key=f"{mid}-3")
        tiles([dict(k="Preço em que a demanda quebra", v=fmt(lo), key=True, s="acima dele só compra quem tem o maior intercepto"), dict(k="Quantidade a preço zero", v=fmt(C.agg_q(g, 0))),
               dict(k="Inclinação acima · abaixo da quebra", v=f"{fmt(g['b1'] if g['a1'] >= g['a2'] else g['b2'])} · {fmt(1 / (1 / g['b1'] + 1 / g['b2']))}", s="a curva fica mais plana quando os dois compram"),
               dict(k="Preço máximo de mercado", v=fmt(top))])


@page("leiloes", 18)
def leiloes():
    mid = "lei"
    header(18, CHAPTERS[18], "Leilões",
           "Leilões de valor privado, com valores sorteados de uma uniforme entre 0 e 1. No segundo preço (Vickrey), dar o próprio valor como lance é estratégia dominante; "
           "no primeiro preço, cada um sombreia o lance. A receita esperada do vendedor é a mesma nos dois.",
           [("Lance no 1º preço", r"b(v)=v-\frac{v^{n}-r^{n}}{n\,v^{n-1}}"), ("Lance no 2º preço", r"b(v)=v"), ("Receita esperada", r"E[R]=\frac{n-1}{n+1}+r^{n}-\frac{2n}{n+1}\,r^{n+1}")])
    left, right = cols()
    with left:
        n = sl(mid, "n", "Número de participantes (n)", 2, 12, 3, 1)
        r = sl(mid, "r", "Preço de reserva (r)", 0.0, 0.9, 0.0, 0.01)
        v = sl(mid, "v", "Meu valor (v), para a primeira aba", 0.05, 1.0, 0.8, 0.01)
    ER, ER0, ERopt = C.exp_rev(n, r), C.exp_rev(n, 0), C.exp_rev(n, 0.5)
    with right:
        t1, t2, t3 = st.tabs(["Funções de lance", "Receita e preço de reserva", "Simulação"])
        with t1:
            b = C.bid1(v, n, r)
            vs = C.lin(max(r, 0.001), 1, 200)
            tr = [ln([0, 1], [0, 1], "Segundo preço: b = v", COL["coral"], dash="dash"), ln(vs, [C.bid1(x, n, r) for x in vs], "Primeiro preço", COL["navy"], width=3)]
            if r > 0:
                tr.append(ln([r, r], [0, 1], "Preço de reserva", COL["muted"], dash="dot", width=1.6))
            if b is not None:
                tr += [dot(v, v, "Meu lance no 2º preço", COL["coral"], size=11, edge="#fff"), dot(v, b, "Meu lance no 1º preço", COL["yellow"], size=14)]
            chart(fig2d(tr, "Valor do participante (v)", "Lance", [0, 1], [0, 1]), key=f"{mid}-1")
            if b is None:
                tiles([dict(k="Meu lance", v="Não participo", chip=("Valor abaixo da reserva", "warn"))])
            else:
                tiles([dict(k="Meu lance no 1º preço", v=fmt(b, 3), key=True, s=f"sombreamento: {fmt(100 * (1 - b / v), 1)}% do valor"),
                       dict(k="Meu lance no 2º preço", v=fmt(v, 3), key=True, chip=("Estratégia dominante", "good")),
                       dict(k="Probabilidade de ganhar", v=fmt(100 * v ** (n - 1), 1) + "%", s="igual nos dois formatos"), dict(k="Receita esperada do vendedor", v=fmt(ER, 3))])
        with t2:
            rs = C.lin(0, 1, 200)
            ys = [C.exp_rev(n, x) for x in rs]
            chart(fig2d([ln(rs, ys, "Receita esperada", COL["navy"], width=3), dot(0.5, ERopt, "Reserva ótima (r = 0,5)", COL["coral"], size=11, edge="#fff"), dot(r, ER, "Reserva atual", COL["yellow"], size=14)],
                        "Preço de reserva (r)", "Receita esperada", [0, 1], [0, max(ys) * 1.15]), key=f"{mid}-2")
            tiles([dict(k="Receita esperada", v=fmt(ER, 3), key=True, s="sem reserva: " + fmt(ER0, 3)), dict(k="Probabilidade de não vender", v=fmt(100 * r ** n, 1) + "%"),
                   dict(k="Reserva ótima", v="0,50", s=f"receita: {fmt(ERopt, 3)} (vendedor dá valor zero ao bem)"),
                   dict(k="Ganho da reserva ótima", v="+" + fmt(100 * (ERopt / ER0 - 1), 1) + "%", s="encolhe quando n cresce")])
        with t3:
            sim = C.simulate_auctions(n, r)
            nb = 25

            def hist(a):
                h = [0] * nb
                for x in a:
                    h[min(nb - 1, int(x * nb))] += 1
                return [c / len(a) for c in h]
            xs, h1, h2 = C.lin(0, 1, nb + 1), hist(sim["r1"]), hist(sim["r2"])
            top = max(*h1, *h2) * 1.15
            chart(fig2d([ln(xs, [*h1, h1[-1]], "Primeiro preço", COL["navy"], shape="hv"), ln(xs, [*h2, h2[-1]], "Segundo preço", COL["coral"], shape="hv", dash="dash"),
                         ln([ER, ER], [0, top], "Receita esperada teórica", COL["gold"], width=2, dash="dot")],
                        "Receita do vendedor", "Frequência", [0, 1], [0, top]), key=f"{mid}-3")
            tiles([dict(k="Receita média: 1º preço", v=fmt(sim["m1"], 3), key=True, s="desvio-padrão " + fmt(sim["sd1"], 3)),
                   dict(k="Receita média: 2º preço", v=fmt(sim["m2"], 3), key=True, s="desvio-padrão " + fmt(sim["sd2"], 3)),
                   dict(k="Receita esperada teórica", v=fmt(ER, 3), chip=("Equivalência de receita", "info")), dict(k="Leilões simulados", v="4.000", s="o 2º preço tem receita mais dispersa")])


@page("bem-estar", 34)
def bem_estar():
    mid = "bem"
    header(34, CHAPTERS[34], "Bem-estar: fronteira de utilidades e escolha social",
           "Cada ponto da curva de contrato dá um par de utilidades; juntos, eles formam a fronteira de possibilidades de utilidade. "
           "Uma função de bem-estar social escolhe um ponto dela, e critérios diferentes escolhem pontos diferentes. Como Rawls e o utilitarismo "
           "comparam utilidades de pessoas diferentes, o resultado depende da escala de cada forma funcional.",
           [("Utilitarista", r"W=u_A+u_B"), ("Ponderada", r"W=\omega u_A+(1-\omega)u_B"), ("Rawls", r"W=\min\{u_A,u_B\}"), ("Nash", r"W=u_A\cdot u_B")])
    left, right = cols()
    with left:
        names = {"Rawls (mínimo)": "rawls", "Utilitarista (soma)": "util", "Soma ponderada": "peso", "Nash (produto)": "nash"}
        p = dict(swf=names[rd("Função de bem-estar", list(names), f"{mid}-swf")], w=0.6)
        if p["swf"] == "peso":
            p["w"] = sl(mid, "w", "Peso de A (ω)", 0.05, 0.95, 0.6, 0.05)
        p.update(pref2_controls(mid, aA=0.7, aB=0.3, value="cd"))
        pref_eqs(p, **AGENT_EQ)
    r = cached("welfare34", p)
    o = r["opt"]
    with right:
        t1, t2 = st.tabs(["Fronteira de possibilidades de utilidade", "Alocação na caixa de Edgeworth"])
        with t1:
            fa, fb = [q["uA"] for q in r["frontier"]], [q["uB"] for q in r["frontier"]]
            lo = min(0.0, *fa, *fb)
            top = max(*fa, *fb) * 1.06 + 0.01 - lo * 0.06
            us = C.lin(max(lo, 1e-3), top, 200)
            if p["swf"] == "util":
                iso = (us, [o["W"] - u for u in us])
            elif p["swf"] == "peso":
                iso = (us, [(o["W"] - p["w"] * u) / (1 - p["w"]) for u in us])
            elif p["swf"] == "nash":
                iso = (us, [o["W"] / u for u in us])
            else:
                iso = ([o["W"], o["W"], top], [top, o["W"], o["W"]])
            chart(fig2d([area([lo, *fa, lo], [lo, *fb, lo], "Utilidades possíveis", "rgba(42,100,184,.12)"), ln(fa, fb, "Fronteira de utilidades", COL["navy"], width=3.2),
                         ln([lo, top], [lo, top], "Igualdade (u_A = u_B)", COL["muted"], dash="dot", width=1.4),
                         ln(iso[0], [None if (v < lo or v > top * 1.5) else v for v in iso[1]], "Curva de isobem-estar", COL["coral"], width=2.4, dash="dash"),
                         dot(o["uA"], o["uB"], "Ótimo social", COL["yellow"], size=15)],
                        "Utilidade de A (u_A)", "Utilidade de B (u_B)", [lo, top], [lo, top], square=True), height=560, key=f"{mid}-1")
        with t2:
            fig = fig2d([ln([0, 10, 10, 0, 0], [0, 0, 10, 10, 0], "Caixa", COL["navy"], width=1.5, legend=False), contract_trace(r["frontier"]),
                         box_ic(p, "A", o["uA"]), box_ic(p, "B", o["uB"]),
                         dot(o["x"], o["y"], "Alocação escolhida", COL["yellow"], size=16, symbol="star")],
                        "Bem 1 de A →", "Bem 2 de A →", [0, 10], [0, 10], square=True)
            chart(fig, height=560, key=f"{mid}-2")
        tie = p["swf"] in ("util", "peso") and p["mode"]["form"] == "cd" and abs(p["aA"] - p["aB"]) < 1e-9
        chip = ("Fronteira reta: solução de canto ou empate", "warn") if tie else ("Igualitária", "good") if abs(o["uA"] - o["uB"]) < 0.02 else ("Favorece " + ("A" if o["uA"] > o["uB"] else "B"), "info")
        tiles([dict(k="Utilidades u_A ; u_B", v=f"{fmt(o['uA'])} ; {fmt(o['uB'])}", key=True, chip=chip),
               dict(k="Cesta de A (x₁ ; x₂)", v=f"{fmt(o['x'])} ; {fmt(o['y'])}", s=f"B fica com {fmt(10 - o['x'])} ; {fmt(10 - o['y'])}"),
               dict(k="Bem-estar social W", v=fmt(o["W"], 3), key=True), dict(k="Eficiência", v="Pareto-eficiente", s="todo máximo de bem-estar está na curva de contrato")])
