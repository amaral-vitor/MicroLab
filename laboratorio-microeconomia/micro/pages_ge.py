"""Capítulos 32 a 38: equilíbrio geral, falhas de mercado e informação."""
import streamlit as st
from . import core as C
from .registry import page, CHAPTERS
from .ui import (split, group, cb, COL, header, sl, tiles, fmt, sgn, chart, fig2d, ln, dot, area, rect, pref_controls, pref2_controls, pref_eqs,
                 AGENT_EQ, cached, box_ic, contract_trace)


def cols(n=3):
    return split(n)


@page("edgeworth", 32)
def edgeworth():
    mid = "edge"
    header(32, CHAPTERS[32], "Caixa de Edgeworth e o Primeiro Teorema do Bem-Estar",
           "Dois agentes trocam a partir das dotações. A um preço qualquer, as demandas de A e B não se encontram; no preço de equilíbrio, sim, e o ponto cai na curva de contrato.",
           [("Equilíbrio (p₂ = 1)", r"z_1(p_1^*)=x_1^A(p_1^*)+x_1^B(p_1^*)-\bar\omega_1=0"), ("Lei de Walras", r"p_1z_1+p_2z_2\equiv 0")])
    left, right = cols()
    with left:
        p = pref2_controls(mid, aA=0.5, aB=0.3, value="cd")
        pref_eqs(p, **AGENT_EQ)
        group("Dotação de A (total de cada bem = 10)")
        p.update(eA1=sl(mid, "eA1", "Bem 1 de A (ω₁ᴬ)", 0.5, 9.5, 7.0, 0.1), eA2=sl(mid, "eA2", "Bem 2 de A (ω₂ᴬ)", 0.5, 9.5, 2.0, 0.1))
        group("Preço (bem 2 é o numerário)")
        E = cached("equilibrium", p)
        pstar = E["pStar"]
        use_eq = cb("Usar o preço de equilíbrio", f"{mid}-eq") if E["ok"] else False
        p1 = sl(mid, "p1", "Preço relativo p₁/p₂", 0.05, 5.0, 1.0, 0.01) if not use_eq else None
        p["p1"] = pstar if use_eq else p1
        if use_eq:
            st.caption(f"p₁/p₂ = {fmt(pstar, 3)}")
    r = cached("edgeworth", p)
    with right:
        bx = [max(0, p["eA1"] - (10 - p["eA2"]) / p["p1"]), min(10, p["eA1"] + p["eA2"] / p["p1"])]
        tr = [ln([0, 10, 10, 0, 0], [0, 0, 10, 10, 0], "Caixa", COL["navy"], width=1.5, legend=False),
              contract_trace(cached("contract_curve", p)), box_ic(p, "A", r["uA"]), box_ic(p, "B", r["uB"]),
              ln(bx, [p["eA2"] + p["p1"] * (p["eA1"] - x) for x in bx], "Reta de preços", COL["navy"], width=2.6),
              dot(p["eA1"], p["eA2"], "Dotação ω", COL["ink"], symbol="square", size=11, edge="#fff", text="ω", tp="bottom left")]
        if r["eq"]:
            tr.append(dot(*r["A"], "Equilíbrio competitivo", COL["yellow"], symbol="star", size=20))
        else:
            tr += [dot(*r["A"], "Demanda de A", COL["royal"], symbol="x", size=13, edge="#fff"),
                   dot(10 - r["B"][0], 10 - r["B"][1], "Demanda de B", COL["coral"], symbol="x", size=13, edge="#fff")]
        tr.append(dict(type="scatter", x=[10], y=[10], xaxis="x2", yaxis="y2", mode="markers", marker=dict(opacity=0), showlegend=False, hoverinfo="skip"))
        fig = fig2d(tr, "Bem 1 de A →", "Bem 2 de A →", [0, 10], [0, 10], square=True)
        fig.update_xaxes(zeroline=False, rangemode="normal", constrain="domain"); fig.update_yaxes(zeroline=False, rangemode="normal", constrain="domain")
        side = dict(showgrid=False, ticks="outside", tickcolor=COL["coral"], linecolor=COL["coral"], tickfont=dict(color=COL["coral"]))
        fig.update_layout(xaxis2=dict(overlaying="x", side="top", range=[10, 0], title=dict(text="← Bem 1 de B", standoff=4), **side),
                          yaxis2=dict(overlaying="y", side="right", range=[10, 0], title=dict(text="← Bem 2 de B"), **side),
                          margin=dict(l=62, r=62, t=52, b=52))
        chart(fig, height=560)
        if r["eq"]:
            st.success("Equilíbrio: os dois mercados se zeram e a alocação está na curva de contrato. "
                       "Pelo Primeiro Teorema do Bem-Estar, ela é eficiente no sentido de Pareto.")
        elif r["noEq"]:
            st.warning(f"Com essas preferências, o bem {r['free']} sobra a qualquer preço positivo: o equilíbrio só existe com p{'₁' if r['free'] == 1 else '₂'} = 0 (bem livre)."
                       if r["free"] else "Com essas preferências não há preço que zere os dois mercados (as curvas côncavas fazem a demanda saltar).")
        z1 = r["z1"]
        tiles([dict(k="Preço de equilíbrio p₁*", v=fmt(pstar, 3) if pstar == pstar else "—", key=True, chip=("No equilíbrio", "good") if r["eq"] else ("Fora do equilíbrio", "warn")),
               dict(k="Excesso de demanda z₁", v=sgn(z1, 3), s="falta bem 1: p₁ deve subir" if z1 > 1e-3 else "sobra bem 1: p₁ deve cair" if z1 < -1e-3 else "mercado 1 zerado"),
               dict(k="Excesso de demanda z₂", v=sgn(r["z2"], 3)),
               dict(k="Lei de Walras p₁z₁ + p₂z₂", v=fmt(0.0 if abs(r["walras"]) < 1e-12 else r["walras"], 6), s="vale a qualquer preço"),
               dict(k="Utilidades uᴬ ; uᴮ", v=f"{fmt(r['uA'], 3)} ; {fmt(r['uB'], 3)}")])


def _crusoe_ic(p, r, yTop):
    cs, ls = C.ces_level(r["U"], p["alpha"], p["rho"], p["mode"], yTop * 1.5, 24)
    return ln([None if (l is None or l > 24) else 24 - l for l in ls], cs, "Curva de indiferença", COL["royal"], width=2.4)


@page("crusoe", 33)
def crusoe():
    mid = "crusoe"
    header(33, CHAPTERS[33], "Economia de Robinson Crusoé",
           "Crusoé é ao mesmo tempo empresa e consumidor. A empresa maximiza lucro ao salário w*; o consumidor escolhe trabalho e consumo. No equilíbrio, as duas decisões coincidem na tangência.",
           [("Lazer", r"\ell=24-L"), ("Produção", r"C=AL^{\beta}"), ("Equilíbrio", r"\max_L\ U\big(AL^{\beta},\,24-L\big)\ \Rightarrow\ w^*=PMg_L")])
    left, right = cols()
    with left:
        p = pref_controls(mid, w="alpha", wl="Peso do consumo (α)", x1="consumo C", x2="lazer ℓ", value="cd", a=(1, 40, 0.5, 10), k=(0.5, 10, 0.1, 2))
        pref_eqs(p, v1="C", v2=r"\ell", w=r"\alpha")
        group("Tecnologia")
        p.update(beta=sl(mid, "beta", "Elasticidade produto-trabalho (β)", 0.1, 0.9, 0.7, 0.01),
                 A=sl(mid, "A", "Produtividade total (A)", 0.5, 2.0, 1.0, 0.1))
    r = C.crusoe(p)
    with right:
        Ls = C.lin(0, 24, 300)
        yTop = 1.25 * max(p["A"] * 24 ** p["beta"], r["C"], r["pi"] + r["w"] * 24 * 0.6)
        chart(fig2d([ln(Ls, [p["A"] * C.pw(l, p["beta"]) for l in Ls], "Função de produção", COL["teal"], width=3),
                     ln(Ls, [r["pi"] + r["w"] * l for l in Ls], "Reta de isolucro C = π* + w*L", COL["navy"], dash="dash", width=2.2),
                     _crusoe_ic(p, r, yTop),
                     dot(r["L"], r["C"], "Equilíbrio (L*, C*)", COL["yellow"], size=14)],
                    "Trabalho (L, horas)", "Consumo (C)", [0, 24], [0, yTop],
                    annotations=[dict(x=0, y=r["pi"], xref="x", yref="y", text="π*", showarrow=True, ax=26, ay=-18, arrowcolor=COL["muted"])]))
        tiles([dict(k="Trabalho L*", v=fmt(r["L"]), key=True, s="lazer: " + fmt(24 - r["L"]) + " h"), dict(k="Consumo C*", v=fmt(r["C"]), key=True),
               dict(k="Salário real w*", v=fmt(r["w"], 3), s="= PMg_L no equilíbrio"), dict(k="Lucro π*", v=fmt(r["pi"], 3)), dict(k="Utilidade U*", v=fmt(r["U"], 3))])


@page("externalidades", 35)
def externalidades():
    mid = "ext"
    header(35, CHAPTERS[35], "Externalidades",
           "Quando a produção impõe custo a terceiros, o mercado produz demais. O imposto de Pigou, igual ao dano marginal no ótimo social, corrige o excesso. "
           "Num recurso de uso comum, a entrada continua até a renda desaparecer.",
           [("Ótimo social", r"P(Q)=CMg_{priv}(Q)+CMgE(Q)"), ("Pigou", r"t^*=CMgE(Q^s)"), ("Comuns: acesso livre × ótimo", r"\frac{f(c)}{c}=k\quad\text{vs.}\quad f'(c)=k")])
    t1, t2 = st.tabs(["Externalidade negativa e imposto de Pigou", "Tragédia dos comuns"])
    with t1:
        left, right = cols()
        with left:
            p = dict(a=sl(mid, "a", "Intercepto da demanda (a)", 30, 150, 100, 1), b=sl(mid, "b", "Inclinação da demanda (b)", 0.2, 3.0, 1.0, 0.1),
                     c0=sl(mid, "c0", "Custo marginal privado: intercepto", 0, 50, 10, 1), c1=sl(mid, "c1", "Custo marginal privado: inclinação", 0.0, 3.0, 0.5, 0.1),
                     e0=sl(mid, "e0", "Dano a terceiros: fixo por unidade", 0, 50, 15, 1), e1=sl(mid, "e1", "Dano a terceiros: inclinação", 0.0, 2.0, 0.2, 0.05))
        r = C.pigou(p)
        with right:
            qx = min(p["a"] / p["b"], max(r["Qm"] * 1.5, 1))
            smc = lambda q: p["c0"] + p["e0"] + (p["c1"] + p["e1"]) * q
            tr = []
            if r["Qm"] > r["Qs"]:
                tr.append(area([r["Qs"], r["Qm"], r["Qm"]], [smc(r["Qs"]), smc(r["Qm"]), p["a"] - p["b"] * r["Qm"]], "Peso morto do excesso de produção", "rgba(210,85,58,.42)"))
            tr += [ln([0, qx], [p["a"], p["a"] - p["b"] * qx], "Demanda (benefício marginal)", COL["navy"], width=3),
                   ln([0, qx], [p["c0"], p["c0"] + p["c1"] * qx], "Custo marginal privado", COL["teal"]),
                   ln([0, qx], [smc(0), smc(qx)], "Custo marginal social", COL["coral"]),
                   ln([0, qx], [p["c0"] + r["tax"], p["c0"] + p["c1"] * qx + r["tax"]], "Custo privado + imposto de Pigou", COL["gold"], dash="dash", width=2.2),
                   dot(r["Qm"], r["Pm"], "Equilíbrio de mercado", COL["navy"], size=11, edge="#fff"), dot(r["Qs"], r["Ps"], "Ótimo social", COL["yellow"], size=14)]
            chart(fig2d(tr, "Quantidade (Q)", "Preço e custo", [0, qx], [0, p["a"] * 1.05]), key=f"{mid}-1")
            tiles([dict(k="Quantidade de mercado", v=fmt(r["Qm"]), key=True), dict(k="Quantidade socialmente ótima", v=fmt(r["Qs"]), key=True),
                   dict(k="Imposto de Pigou t*", v=fmt(r["tax"]), s="dano marginal no ótimo social"), dict(k="Peso morto sem correção", v=fmt(r["dwl"]))])
    with t2:
        left, right = cols()
        with left:
            q = dict(A=sl(mid, "A", "Produção por animal com pasto livre (A)", 5, 50, 20, 1), B=sl(mid, "B", "Congestionamento (B)", 0.05, 2.0, 0.5, 0.05),
                     k=sl(mid, "k", "Custo por animal (k)", 1.0, 40.0, 8.0, 0.5))
        cm = C.commons(q)
        with right:
            cx = q["A"] / q["B"]
            cs = C.lin(0, cx, 200)
            csm = [c for c in cs if q["A"] - 2 * q["B"] * c >= 0]
            tr = [rect(0, cm["cOpt"], q["k"], q["A"] - q["B"] * cm["cOpt"], "Renda máxima do pasto", "rgba(242,194,0,.42)")] if cm["cOpt"] > 0 else []
            tr += [ln(cs, [q["A"] - q["B"] * c for c in cs], "Produto médio f(c)/c", COL["navy"], width=3),
                   ln(csm, [q["A"] - 2 * q["B"] * c for c in csm], "Produto marginal f′(c)", COL["royal"], dash="dash", width=2.4),
                   ln([0, cx], [q["k"], q["k"]], "Custo por animal k", COL["coral"], width=2.4),
                   dot(cm["cOpen"], q["k"], "Acesso livre", COL["coral"], size=11, edge="#fff"), dot(cm["cOpt"], q["k"], "Ótimo", COL["yellow"], size=14)]
            chart(fig2d(tr, "Número de animais no pasto (c)", "Produção por animal", [0, cx * 1.02], [0, q["A"] * 1.08]), key=f"{mid}-2")
            tiles([dict(k="Animais com acesso livre", v=fmt(cm["cOpen"]), key=True, s="renda: zero (dissipada)"),
                   dict(k="Número ótimo de animais", v=fmt(cm["cOpt"]), key=True), dict(k="Renda máxima do pasto", v=fmt(cm["rent"]), chip=("Perdida com acesso livre", "bad"))])


@page("bens-publicos", 37)
def bens_publicos():
    mid = "bp"
    header(37, CHAPTERS[37], "Bens públicos e o problema do carona",
           "Um bem público beneficia todos ao mesmo tempo, então a disposição a pagar se soma na vertical. A provisão eficiente iguala a soma das TMS ao custo marginal; "
           "contribuições voluntárias ficam abaixo disso.",
           [("Samuelson", r"TMS_1(G)+TMS_2(G)=CMg"), ("Voluntária", r"G^N=\max\{G_1,G_2\}"), ("Lindahl", r"t_i=TMS_i(G^*)")])
    left, right = cols()
    with left:
        group("Consumidor 1: TMS₁ = α₁ − β₁G")
        p = dict(al1=sl(mid, "al1", "α₁", 5, 60, 30, 1), be1=sl(mid, "be1", "β₁", 0.1, 3.0, 1.0, 0.05))
        group("Consumidor 2: TMS₂ = α₂ − β₂G")
        p.update(al2=sl(mid, "al2", "α₂", 5, 60, 24, 1), be2=sl(mid, "be2", "β₂", 0.1, 3.0, 0.4, 0.05))
        group("Custo")
        p["c"] = sl(mid, "c", "Custo marginal do bem público", 1, 80, 20, 1)
    r = C.public_good(p)
    with right:
        gx = max(r["top"], r["Gs"] * 1.2)
        gs = C.lin(0, gx, 300)
        tr = []
        if r["Gs"] > r["Gn"]:
            seg = C.lin(r["Gn"], r["Gs"], 60)
            tr.append(area([*seg, *reversed(seg)], [*[r["sum"](g) for g in seg], *[p["c"]] * len(seg)], "Perda por subprovisão", "rgba(210,85,58,.38)"))
        tr += [ln(gs, [r["m1"](g) for g in gs], "TMS do consumidor 1", COL["royal"], width=2.4), ln(gs, [r["m2"](g) for g in gs], "TMS do consumidor 2", COL["teal"], width=2.4),
               ln(gs, [r["sum"](g) for g in gs], "Soma vertical das TMS", COL["navy"], width=3.2), ln([0, gx], [p["c"]] * 2, "Custo marginal", COL["coral"], width=2.4),
               dot(r["Gn"], p["c"], "Contribuição voluntária", COL["coral"], size=11, edge="#fff"), dot(r["Gs"], p["c"], "Provisão eficiente", COL["yellow"], size=14)]
        chart(fig2d(tr, "Quantidade do bem público (G)", "Disposição marginal a pagar", [0, gx], [0, max(p["al1"] + p["al2"], p["c"]) * 1.05]))
        under = r["Gn"] < r["Gs"] - 1e-9
        tiles([dict(k="Provisão eficiente G*", v=fmt(r["Gs"]), key=True),
               dict(k="Provisão voluntária", v=fmt(r["Gn"]), key=True, s="o consumidor 1 paga tudo; o 2 pega carona" if r["G1"] >= r["G2"] else "o consumidor 2 paga tudo; o 1 pega carona",
                    chip=(fmt(100 * (1 - r["Gn"] / r["Gs"]), 1) + "% abaixo do eficiente", "bad" if under else "good") if r["Gs"] > 0 else None),
               dict(k="Preços de Lindahl t₁ ; t₂", v=f"{fmt(r['t1'])} ; {fmt(r['t2'])}", s="somam o custo marginal")])


@page("informacao-assimetrica", 38)
def informacao():
    mid = "info"
    header(38, CHAPTERS[38], "Informação assimétrica",
           "Quando só o vendedor conhece a qualidade, os bons produtos podem sumir do mercado. Quem tem qualidade alta pode tentar se distinguir com um sinal caro demais para os outros imitarem.",
           [("Limões", r"qV_H+(1-q)V_L\ge R_H\Leftrightarrow q\ge q^*"), ("Separação", r"\frac{a_2-a_1}{c_1}\le e^*\le\frac{a_2-a_1}{c_2}")])
    t1, t2 = st.tabs(["Mercado de limões", "Sinalização com educação"])
    with t1:
        left, right = cols()
        with left:
            p = dict(q=sl(mid, "q", "Fração de carros bons (q)", 0.0, 1.0, 0.5, 0.01))
            group("Valores (compradores · vendedores)")
            p.update(VH=sl(mid, "VH", "Comprador: carro bom (V_H)", 500, 5000, 2400, 50), VL=sl(mid, "VL", "Comprador: limão (V_L)", 200, 4000, 1200, 50),
                     RH=sl(mid, "RH", "Vendedor: carro bom (R_H)", 200, 5000, 2000, 50), RL=sl(mid, "RL", "Vendedor: limão (R_L)", 100, 4000, 1000, 50))
        with right:
            if p["VH"] <= p["VL"] or p["RH"] <= p["RL"]:
                st.warning("Carros bons precisam valer mais que limões, tanto para compradores quanto para vendedores.")
            else:
                lm = C.lemons(p)
                qs = C.lin(0, 1, 101)
                top = max(p["VH"], p["RH"]) * 1.1
                tr = [rect(max(0, lm["qStar"]), 1, 0, top, "Os dois tipos são vendidos", "rgba(23,143,126,.13)")] if lm["qStar"] < 1 else []
                tr += [ln(qs, [q * p["VH"] + (1 - q) * p["VL"] for q in qs], "Disposição a pagar do comprador", COL["navy"], width=3),
                       ln([0, 1], [p["RH"]] * 2, "Reserva do dono de carro bom", COL["coral"], dash="dash", width=2.2),
                       ln([0, 1], [p["RL"]] * 2, "Reserva do dono de limão", COL["muted"], dash="dot", width=1.8),
                       dot(p["q"], lm["EV"], "Situação atual", COL["yellow"] if lm["pooling"] else COL["coral"], size=14, edge=COL["navy"] if lm["pooling"] else "#fff")]
                chart(fig2d(tr, "Fração de carros bons (q)", "Valor (R$)", [0, 1], [0, top]), key=f"{mid}-1")
                tiles([dict(k="Disposição a pagar média", v=fmt(lm["EV"], 0), key=True),
                       dict(k="Fração crítica q*", v=fmt(lm["qStar"], 3), s="acima dela, os carros bons continuam no mercado"),
                       dict(k="Resultado", v="Os dois tipos são vendidos" if lm["pooling"] else "Só limões são vendidos",
                            chip=(f"Preço entre {fmt(p['RH'], 0)} e {fmt(lm['EV'], 0)}", "good") if lm["pooling"] else ("Seleção adversa", "bad")),
                       dict(k="Ganho de troca perdido por carro bom", v=fmt(0 if lm["pooling"] else p["VH"] - p["RH"], 0))])
    with t2:
        left, right = cols()
        with left:
            group("Produtividade (salário pago)")
            s = dict(a1=sl(mid, "a1", "Baixa produtividade (a₁)", 1, 50, 10, 1), a2=sl(mid, "a2", "Alta produtividade (a₂)", 2, 60, 20, 1))
            group("Custo de cada ano de educação")
            s.update(c1=sl(mid, "c1", "Para o tipo baixo (c₁)", 0.5, 10.0, 4.0, 0.1), c2=sl(mid, "c2", "Para o tipo alto (c₂)", 0.5, 10.0, 2.0, 0.1),
                     es=sl(mid, "es", "Educação exigida para salário alto (e*)", 0.0, 12.0, 3.0, 0.1))
        with right:
            if s["a2"] <= s["a1"] or s["c1"] <= s["c2"]:
                st.warning("A sinalização precisa de a₂ > a₁ e de educação mais cara para o tipo baixo (c₁ > c₂).")
            else:
                sg = C.signaling(s)
                ex = max(12, sg["hi"] * 1.3)
                tr = [rect(max(0, sg["lo"]), sg["hi"], 0, s["a2"] * 1.6, "e* que separa os tipos", "rgba(23,143,126,.13)")] if sg["hi"] > sg["lo"] else []
                tr += [ln([0, s["es"], None, s["es"], ex], [s["a1"], s["a1"], None, s["a2"], s["a2"]], "Salário oferecido", COL["navy"], width=3.4),
                       ln([0, ex], [s["a1"], s["a1"] + s["c1"] * ex], "Indiferença do tipo baixo", COL["coral"], dash="dash", width=2.2),
                       ln([0, ex], [s["a1"], s["a1"] + s["c2"] * ex], "Indiferença do tipo alto", COL["royal"], dash="dash", width=2.2),
                       dot(0, s["a1"], "Tipo baixo: e = 0", COL["coral"], size=11, edge="#fff"),
                       dot(s["es"], s["a2"], "Salário alto com e*", COL["yellow"] if sg["sep"] else COL["faint"], size=14)]
                chart(fig2d(tr, "Anos de educação (e)", "Salário", [0, ex], [0, s["a2"] * 1.6]), key=f"{mid}-2")
                tiles([dict(k="Intervalo de e* que separa", v=f"{fmt(sg['lo'])} a {fmt(sg['hi'])}", key=True, chip=("e* separa os tipos", "good") if sg["sep"] else ("e* não separa", "bad")),
                       dict(k="Tipo baixo: sem educação · imitando", v=f"{fmt(sg['low_none'])} · {fmt(sg['low_mimic'])}",
                            s="compensa imitar" if sg["low_mimic"] > sg["low_none"] else "não compensa imitar"),
                       dict(k="Tipo alto: sem educação · com e*", v=f"{fmt(sg['high_none'])} · {fmt(sg['high_sig'])}",
                            s="compensa sinalizar" if sg["high_sig"] >= sg["high_none"] else "não compensa sinalizar"),
                       dict(k="Custo social do sinal", v=fmt(s["c2"] * s["es"]), s="por trabalhador do tipo alto: a educação aqui não aumenta a produtividade")])
