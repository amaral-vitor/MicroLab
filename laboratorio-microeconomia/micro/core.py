"""Núcleo matemático dos modelos do Laboratório de Microeconomia (Varian, 9ª ed.)."""
import math

EPS = 1e-9
INF = float("inf")
NAN = float("nan")


def pw(x, e):
    """Potência segura: 0^(−) = ∞, base negativa com expoente fracionário = nan."""
    if x == 0:
        return INF if e < 0 else (0.0 if e > 0 else 1.0)
    if x < 0 and e != int(e):
        return NAN
    try:
        return x ** e
    except OverflowError:
        return INF


def lin(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def bisect(f, lo, hi, n=200):
    flo = f(lo)
    for _ in range(n):
        mid = (lo + hi) / 2
        fm = f(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return (lo + hi) / 2


def argmax(f, lo, hi, n=400):
    bi, bv = 0, -INF
    for i in range(n + 1):
        v = f(lo + (hi - lo) * i / n)
        if v > bv:
            bv, bi = v, i
    a = lo + (hi - lo) * max(0, bi - 1) / n
    b = lo + (hi - lo) * min(n, bi + 1) / n
    g = (math.sqrt(5) - 1) / 2
    for _ in range(80):
        c, d = b - g * (b - a), a + g * (b - a)
        if f(c) > f(d):
            b = d
        else:
            a = c
    return (a + b) / 2


# ---------------------------------------------------------------- formas funcionais
# mode: None → CES com ρ · "leo" → min(x1, x2) (produção)
# ou um dict {form, k, a} com form = "comp" | "cd" | "sub" | "ces" | "ql":
#   comp: U = min{k·x1, x2}     cd: U = x1^δ x2^(1−δ)     sub: U = δx1 + (1−δ)x2
#   ces:  U = [δx1^ρ + (1−δ)x2^ρ]^(1/ρ)                   ql:  U = a·ln x1 + x2
def form_of(mode):
    if isinstance(mode, dict):
        return mode["form"]
    return "leo" if mode == "leo" else "ces"


def _rho(rho, f):
    return 0.0 if f == "cd" else 1.0 if f == "sub" else rho


def ces(x1, x2, d, rho, mode=None):
    f = form_of(mode)
    if f == "leo":
        return min(x1, x2)
    if f == "comp":
        return min(mode["k"] * x1, x2)
    if f == "ql":
        return mode["a"] * math.log(max(x1, 1e-300)) + x2
    rho = _rho(rho, f)
    if abs(rho) < EPS:
        return pw(x1, d) * pw(x2, 1 - d)
    return pw(d * pw(x1, rho) + (1 - d) * pw(x2, rho), 1 / rho)


def ces_demand(d, rho, mode, p1, p2, w):
    f = form_of(mode)
    if f == "leo":
        x = w / (p1 + p2)
        return dict(x1=x, x2=x, kind="leo")
    if f == "comp":
        x = w / (p1 + mode["k"] * p2)
        return dict(x1=x, x2=mode["k"] * x, kind="leo")
    if f == "ql":
        if w >= mode["a"] * p2:
            return dict(x1=mode["a"] * p2 / p1, x2=(w - mode["a"] * p2) / p2, kind="interior")
        return dict(x1=w / p1, x2=0.0, kind="corner1")
    rho = _rho(rho, f)
    if rho >= 1 - EPS:
        u1, u2 = ces(w / p1, 0, d, rho), ces(0, w / p2, d, rho)
        if abs(u1 - u2) <= 1e-9 * max(u1, u2):
            return dict(x1=w / (2 * p1), x2=w / (2 * p2), kind="tie")
        return dict(x1=w / p1, x2=0.0, kind="corner1") if u1 > u2 else dict(x1=0.0, x2=w / p2, kind="corner2")
    k = pw((p1 * (1 - d)) / (p2 * d), 1 / (1 - rho))
    x1 = w / (p1 + p2 * k)
    return dict(x1=x1, x2=k * x1, kind="interior")


def ces_V(d, rho, mode, p1, p2, w):
    """Utilidade indireta V(p, w)."""
    x = ces_demand(d, rho, mode, p1, p2, w)
    return ces(x["x1"], x["x2"], d, rho, mode)


def ces_E(d, rho, mode, p1, p2, U):
    """Função dispêndio: menor renda que alcança U (V é crescente em w)."""
    lo, hi = 1e-9, 1.0
    for _ in range(200):
        if ces_V(d, rho, mode, p1, p2, hi) >= U:
            break
        hi *= 2
    for _ in range(80):
        mid = (lo + hi) / 2
        if ces_V(d, rho, mode, p1, p2, mid) < U:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def mrs(x1, x2, d, rho, mode):
    """TMS = UMg1/UMg2 (None no bico dos complementares perfeitos)."""
    f = form_of(mode)
    if f in ("leo", "comp"):
        k = mode["k"] if f == "comp" else 1
        return INF if k * x1 < x2 - 1e-12 else 0.0 if k * x1 > x2 + 1e-12 else None
    if f == "ql":
        return mode["a"] / x1
    rho = _rho(rho, f)
    return (d / (1 - d)) * pw(x1 / x2, rho - 1)


def ces_level(U, d, rho, mode, xmax, ymax, n=360):
    """Curva de nível U = const (indiferença ou isoquanta)."""
    f = form_of(mode)
    if f == "leo":
        return [U, U, xmax], [ymax, U, U]
    if f == "comp":
        return [U / mode["k"], U / mode["k"], xmax], [ymax, U, U]
    xs, ys = [], []
    if f == "ql":
        for i in range(1, n + 1):
            x = xmax * (i / n) ** 2
            y = U - mode["a"] * math.log(x)
            if y < 0:
                xs.append(math.exp(U / mode["a"])); ys.append(0.0)
                break
            xs.append(x); ys.append(y if y <= ymax * 4 else None)
        return xs, ys
    rho = _rho(rho, f)
    for i in range(1, n + 1):
        t = i / n
        x = xmax * t * t
        if abs(rho) < EPS:
            y = pw(U / pw(x, d), 1 / (1 - d))
        else:
            inner = (pw(U, rho) - d * pw(x, rho)) / (1 - d)
            if rho > 0 and inner <= 0:
                xs.append(U * pw(d, -1 / rho))
                ys.append(0.0)
                break
            y = pw(inner, 1 / rho) if inner > 0 else NAN
        xs.append(x)
        ys.append(y if (y == y and abs(y) != INF and y <= ymax * 4) else None)
    return xs, ys


def choice(p):
    dm = ces_demand(p["delta"], p["rho"], p["mode"], p["p1"], p["p2"], p["w"])
    return {**dm, "U": ces(dm["x1"], dm["x2"], p["delta"], p["rho"], p["mode"])}


def slutsky(p):
    f = lambda p1, w: ces_demand(p["delta"], p["rho"], p["mode"], p1, p["p2"], w)
    A = f(p["p1"], p["w"])
    U0 = ces(A["x1"], A["x2"], p["delta"], p["rho"], p["mode"])
    if p["method"] == "hicks":
        wc = ces_E(p["delta"], p["rho"], p["mode"], p["p1n"], p["p2"], U0)
    else:
        wc = p["w"] + A["x1"] * (p["p1n"] - p["p1"])
    B, Cc = f(p["p1n"], wc), f(p["p1n"], p["w"])
    u = lambda z: ces(z["x1"], z["x2"], p["delta"], p["rho"], p["mode"])
    return dict(A=A, B=B, C=Cc, wc=wc, U0=U0, UB=u(B), UC=u(Cc),
                sub1=B["x1"] - A["x1"], inc1=Cc["x1"] - B["x1"], tot1=Cc["x1"] - A["x1"],
                sub2=B["x2"] - A["x2"], inc2=Cc["x2"] - B["x2"], tot2=Cc["x2"] - A["x2"])


def endowment(p):
    m = p["p1"] * p["e1"] + p["p2"] * p["e2"]
    dm = ces_demand(p["delta"], p["rho"], p["mode"], p["p1"], p["p2"], m)
    return {**dm, "m": m, "U": ces(dm["x1"], dm["x2"], p["delta"], p["rho"], p["mode"]),
            "net1": dm["x1"] - p["e1"], "net2": dm["x2"] - p["e2"]}


def leisure(p, w):
    """Lazer (bem 1, preço w) e consumo (bem 2, preço p), com ℓ ≤ T."""
    full = p["M"] + w * p["T"]
    d = ces_demand(p["sigma"], p["rho"], p["mode"], w, p["p"], full)
    if d["x1"] <= p["T"] + 1e-12:
        return dict(l=d["x1"], c=d["x2"])
    uT = ces(p["T"], p["M"] / p["p"], p["sigma"], p["rho"], p["mode"])
    u0 = ces(0.0, full / p["p"], p["sigma"], p["rho"], p["mode"])
    return dict(l=p["T"], c=p["M"] / p["p"]) if uT >= u0 else dict(l=0.0, c=full / p["p"])


def labor_N(p, w):
    return max(0.0, p["T"] - leisure(p, w)["l"])


def labor_supply(p):
    q = leisure(p, p["w"])
    N = p["T"] - q["l"]
    wRes = NAN
    ws = [0.01 * 1e5 ** (i / 399) for i in range(400)]
    for i, w in enumerate(ws):
        if labor_N(p, w) > 1e-9:
            if i == 0:
                wRes = 0.0
                break
            lo, hi = ws[i - 1], w
            for _ in range(60):
                mid = (lo + hi) / 2
                if labor_N(p, mid) > 1e-9:
                    hi = mid
                else:
                    lo = mid
            wRes = hi
            break
    return dict(l=q["l"], N=N, c=q["c"], U=ces(q["l"], q["c"], p["sigma"], p["rho"], p["mode"]), corner=N < 1e-9, wRes=wRes)


def intertemporal(p):
    W = p["m1"] + p["m2"] / (1 + p["r"])
    dm = ces_demand(p["beta"], p["rho"], p["mode"], 1, 1 / (1 + p["r"]), W)
    return dict(c1=dm["x1"], c2=dm["x2"], kind=dm["kind"], W=W,
                U=ces(dm["x1"], dm["x2"], p["beta"], p["rho"], p["mode"]), s=p["m1"] - dm["x1"])


def welfare(p):
    """Excedente, VC e VE para qualquer forma funcional (muda p1)."""
    D = lambda p1, m: ces_demand(p["delta"], p["rho"], p["mode"], p1, p["p2"], m)
    V = lambda p1, m: ces_V(p["delta"], p["rho"], p["mode"], p1, p["p2"], m)
    E = lambda p1, u: ces_E(p["delta"], p["rho"], p["mode"], p1, p["p2"], u)
    u0, u1 = V(p["p1"], p["m"]), V(p["p1n"], p["m"])
    mCV, mEV = E(p["p1n"], u0), E(p["p1"], u1)
    n, lo, hi = 400, min(p["p1"], p["p1n"]), max(p["p1"], p["p1n"])
    h = (hi - lo) / n
    area = sum((1 if i in (0, n) else 4 if i % 2 else 2) * D(lo + i * h, p["m"])["x1"] for i in range(n + 1)) * h / 3
    x0, x1 = D(p["p1"], p["m"]), D(p["p1n"], p["m"])
    return dict(u0=u0, u1=u1, mCV=mCV, mEV=mEV, x0=(x0["x1"], x0["x2"]), x1=(x1["x1"], x1["x2"]),
                CV=p["m"] - mCV, EV=mEV - p["m"], dCS=area if p["p1n"] < p["p1"] else -area, xd=lambda q: D(q, p["m"])["x1"])


def ces_prod(K, L, p):
    return ces(K, L, p["delta"], p["rho"], p["mode"])


def profit_max(p):
    s = p["alpha"] + p["beta"]
    if s >= 1 - 1e-9:
        return dict(ok=False, s=s)
    e = 1 / (1 - s)
    y = pw(p["A"] * pw(p["P"] * p["alpha"] / p["r"], p["alpha"]) * pw(p["P"] * p["beta"] / p["w"], p["beta"]), e)
    K, L = p["P"] * p["alpha"] * y / p["r"], p["P"] * p["beta"] * y / p["w"]
    return dict(ok=True, s=s, y=y, K=K, L=L, pi=p["P"] * y - p["r"] * K - p["w"] * L)


def profit_at(K, L, p):
    return p["P"] * p["A"] * pw(K, p["alpha"]) * pw(L, p["beta"]) - p["r"] * K - p["w"] * L


def cost_lr(y, p):
    ratio = p["alpha"] * p["w"] / (p["beta"] * p["r"])
    L = pw(y / (p["A"] * pw(ratio, p["alpha"])), 1 / (p["alpha"] + p["beta"]))
    K = ratio * L
    C = p["w"] * L + p["r"] * K
    return dict(L=L, K=K, C=C, MC=C / ((p["alpha"] + p["beta"]) * y), AC=C / y)


def cost_sr(y, Kf, p):
    L = pw(y / (p["A"] * pw(Kf, p["alpha"])), 1 / p["beta"])
    VC, FC = p["w"] * L, p["r"] * Kf
    return dict(L=L, K=Kf, C=VC + FC, VC=VC, FC=FC, MC=VC / (p["beta"] * y), AC=(VC + FC) / y, AVC=VC / y, AFC=FC / y)


def monopoly(p):
    a, b, c = p["a"], p["b"], p["c"]
    if c >= a:
        return dict(ok=False)
    qm = (a - c) / (2 * b)
    pm = a - b * qm
    qc = (a - c) / b
    return dict(ok=True, qm=qm, pm=pm, qc=qc, profit=(pm - c) * qm, dwl=0.5 * (qc - qm) * (pm - c),
                cs=0.5 * qm * (a - pm), lerner=(pm - c) / pm)


def monopsony(p):
    a, b, v = p["a"], p["b"], p["vmp"]
    if v <= a:
        return dict(ok=False)
    qm = (v - a) / (2 * b)
    wm = a + b * qm
    qc = (v - a) / b
    return dict(ok=True, qm=qm, wm=wm, qc=qc, wc=v, dwl=0.5 * (qc - qm) * (v - wm), exploit=(v - wm) / wm)


# ---------------------------------------------------------------- caixa de Edgeworth (p2 = 1), mesma forma para A e B
def agents(p):
    m = p.get("mode")
    f = ({"ql": "ql", "comp": "comp"}.get(m["form"], "ces")) if isinstance(m, dict) else p.get("form", "cd")
    return [dict(d=p["aA"], rho=p.get("rho", 0.0), mode=dict(form=f, k=p.get("kA", 1), a=p.get("vA", 1))),
            dict(d=p["aB"], rho=p.get("rho", 0.0), mode=dict(form=f, k=p.get("kB", 1), a=p.get("vB", 1)))]


def u_ag(g, x1, x2):
    return ces(max(x1, 0.0), max(x2, 0.0), g["d"], g["rho"], g["mode"])


def d_ag(g, p1, m):
    return ces_demand(g["d"], g["rho"], g["mode"], p1, 1, m)


def equilibrium(p):
    gA, gB = agents(p)
    eB1, eB2 = 10 - p["eA1"], 10 - p["eA2"]

    def at(q):
        mA, mB = q * p["eA1"] + p["eA2"], q * eB1 + eB2
        A, B = d_ag(gA, q, mA), d_ag(gB, q, mB)
        return dict(A=A, B=B, mA=mA, mB=mB, z=A["x1"] + B["x1"] - 10)
    qs = [10 ** (-3 + 6 * i / 480) for i in range(481)]
    best = None
    for i in range(1, len(qs)):
        z0, z1 = at(qs[i - 1])["z"], at(qs[i])["z"]
        if abs(z0) < 1e-9:
            best = qs[i - 1]
            break
        if (z0 > 0 and z1 <= 0) or (z0 < 0 and z1 >= 0):
            lo, hi, s0 = qs[i - 1], qs[i], z0 > 0
            for _ in range(80):
                mid = math.sqrt(lo * hi)
                if (at(mid)["z"] > 0) == s0:
                    lo = mid
                else:
                    hi = mid
            best = math.sqrt(lo * hi)
            break
    if best is None:
        return dict(pStar=NAN, ok=False, free=1 if at(1.0)["z"] < 0 else 2)
    e = at(best)
    A, B = dict(e["A"]), dict(e["B"])
    if abs(e["z"]) > 1e-4:
        # quem está indiferente ao longo da reta fica com o que sobra, se couber no orçamento
        def fix(mX, other):
            x1 = 10 - other["x1"]
            return dict(x1=max(0.0, x1), x2=mX - best * max(0.0, x1)) if x1 >= -1e-9 and best * x1 <= mX + 1e-9 else None
        tryA = fix(e["mA"], B) if e["A"]["kind"] in ("tie", "leo", "corner1", "corner2") else None
        tryB = None if tryA else fix(e["mB"], A)
        if tryA:
            A = tryA
        elif tryB:
            B = tryB
        else:
            return dict(pStar=NAN, ok=False, free=None)
        cA, cB = u_ag(gA, A["x1"], A["x2"]), u_ag(gB, B["x1"], B["x2"])
        vA, vB = u_ag(gA, e["A"]["x1"], e["A"]["x2"]), u_ag(gB, e["B"]["x1"], e["B"]["x2"])
        if cA < vA - 1e-6 * abs(vA) - 1e-9 or cB < vB - 1e-6 * abs(vB) - 1e-9:
            return dict(pStar=NAN, ok=False, free=None)
    return dict(pStar=best, ok=True, A=A, B=B, free=None)


def edgeworth(p):
    gA, gB = agents(p)
    eB1, eB2, p1 = 10 - p["eA1"], 10 - p["eA2"], p["p1"]
    mA, mB = p1 * p["eA1"] + p["eA2"], p1 * eB1 + eB2
    A, B = d_ag(gA, p1, mA), d_ag(gB, p1, mB)
    E = equilibrium(p)
    at_star = E["ok"] and abs(p1 - E["pStar"]) <= 1e-6 * E["pStar"]
    if at_star:
        A, B = E["A"], E["B"]
    z1, z2 = A["x1"] + B["x1"] - 10, A["x2"] + B["x2"] - 10
    return dict(A=(A["x1"], A["x2"]), B=(B["x1"], B["x2"]), z1=z1, z2=z2, walras=p1 * z1 + z2, pStar=E["pStar"],
                uA=u_ag(gA, A["x1"], A["x2"]), uB=u_ag(gB, B["x1"], B["x2"]),
                eq=at_star or (abs(z1) < 1e-3 and abs(z2) < 1e-3), noEq=not E["ok"], free=E["free"])


def _densify(xs, ys, xmax, ymax):
    out = []
    for x, y in zip(xs, ys):
        if y is None or y != y or abs(y) == INF:
            continue
        if out:
            px, py = out[-1]
            n = math.ceil(math.hypot(x - px, y - py) / 0.04)
            out += [(px + (x - px) * j / n, py + (y - py) * j / n) for j in range(1, n)]
        out.append((x, y))
    return [(x, y) for x, y in out if -1e-9 <= x <= xmax + 1e-9 and -1e-9 <= y <= ymax + 1e-9]


def contract_point(u_level, p, G=None):
    """Ponto da curva de indiferença de A (nível u) que dá mais utilidade a B."""
    gA, gB = G or agents(p)
    pts = _densify(*ces_level(u_level, gA["d"], gA["rho"], gA["mode"], 10, 10), 10, 10)
    best, bi = None, -1
    for i, (x, y) in enumerate(pts):
        ub = u_ag(gB, 10 - x, 10 - y)
        if best is None or ub > best["uB"] + 1e-12:
            best, bi = dict(x=x, y=y, uA=u_level, uB=ub), i
    if best and len(pts) > 2:
        a_, m_, b_ = pts[max(0, bi - 1)], pts[bi], pts[min(len(pts) - 1, bi + 1)]
        at = lambda t: ((m_[0] + (a_[0] - m_[0]) * -t, m_[1] + (a_[1] - m_[1]) * -t) if t < 0 else (m_[0] + (b_[0] - m_[0]) * t, m_[1] + (b_[1] - m_[1]) * t))
        t = argmax(lambda t: u_ag(gB, 10 - at(t)[0], 10 - at(t)[1]), -1, 1, 40)
        x, y = at(t)
        ub = u_ag(gB, 10 - x, 10 - y)
        if ub > best["uB"]:
            best = dict(x=x, y=y, uA=u_level, uB=ub)
    return best


def contract_curve(p, n=90):
    G = agents(p)
    out = []
    for i in range(n + 1):
        t = 0.002 + 0.996 * i / n
        q = contract_point(u_ag(G[0], 10 * t, 10 * t), p, G)
        if q:
            out.append(q)
    return out


def support_price(x, y, p):
    """Preço que sustenta a alocação (x, y) de A: cada um escolhe o próprio ponto com o orçamento que passa por ele."""
    gA, gB = agents(p)

    def dev(q):
        d = 0.0
        for g, a_, b_ in ((gA, x, y), (gB, 10 - x, 10 - y)):
            D = d_ag(g, q, q * a_ + b_)
            if D["kind"] != "tie":
                d += abs(D["x1"] - a_) + abs(D["x2"] - b_)
        return d
    qs = [10 ** (-3 + 6 * i / 600) for i in range(601)]
    ds = [dev(q) for q in qs]
    mn = min(ds)
    ok = [q for q, d in zip(qs, ds) if d <= mn + 1e-3]
    q = math.sqrt(ok[0] * ok[-1])
    if len(ok) == 1:
        i = qs.index(ok[0])
        q = argmax(lambda v: -dev(v), qs[max(0, i - 1)], qs[min(len(qs) - 1, i + 1)], 200)
    return dict(price=q, range=(ok[0], ok[-1]))


def crusoe(p):
    """U(C, ℓ), com ℓ = 24 − L e C = A·L^β."""
    U = lambda L: ces(p["A"] * pw(L, p["beta"]), 24 - L, p["alpha"], p["rho"], p["mode"])
    L = argmax(U, 1e-6, 24 - 1e-6, 2000)
    C = p["A"] * pw(L, p["beta"])
    w = p["A"] * p["beta"] * pw(L, p["beta"] - 1)
    return dict(L=L, C=C, w=w, pi=C - w * L, U=U(L))


# ---------------------------------------------------------------- incerteza
def u_crra(c, g):
    if c <= 0:
        return -INF if g >= 1 else (0.0 if g < 1 else NAN)
    return math.log(c) if abs(g - 1) < 1e-9 else (pw(c, 1 - g) - 1) / (1 - g)


def u_inv(v, g):
    if abs(g - 1) < 1e-9:
        return math.exp(v) if v < 700 else INF
    return pw(1 + (1 - g) * v, 1 / (1 - g))


def lottery(p):
    lo, hi = p["w"] - p["L"], p["w"]
    EU = p["pi"] * u_crra(lo, p["g"]) + (1 - p["pi"]) * u_crra(hi, p["g"])
    Ec = p["pi"] * lo + (1 - p["pi"]) * hi
    CE = u_inv(EU, p["g"])
    return dict(lo=lo, hi=hi, EU=EU, Ec=Ec, CE=CE, rp=Ec - CE)


def insurance(p):
    gm = p["prem"]
    cb = lambda K: p["w"] - p["L"] + (1 - gm) * K
    cg = lambda K: p["w"] - gm * K
    Kmax = min(p["w"] / gm - 1e-6, 3 * p["L"])
    EU = lambda K: p["pi"] * u_crra(cb(K), p["g"]) + (1 - p["pi"]) * u_crra(cg(K), p["g"])
    dEU = lambda K: p["pi"] * (1 - gm) * pw(cb(K), -p["g"]) - (1 - p["pi"]) * gm * pw(cg(K), -p["g"])
    if dEU(0) <= 0:
        K = 0.0
    elif dEU(Kmax) >= 0:
        K = Kmax
    else:
        K = bisect(dEU, 0, Kmax)
    return dict(K=K, cb=cb(K), cg=cg(K), EU=EU(K), fair=abs(gm - p["pi"]) < 1e-9, Kmax=Kmax)


def portfolio(p):
    price = (p["rm"] - p["rf"]) / p["sm"]
    x = (p["rm"] - p["rf"]) / (p["A"] * p["sm"] ** 2)
    mu, sd = p["rf"] + x * (p["rm"] - p["rf"]), x * p["sm"]
    return dict(x=x, mu=mu, sd=sd, price=price, U=mu - p["A"] / 2 * sd * sd)


# ---------------------------------------------------------------- oferta (custo cúbico)
class FirmCost:
    def __init__(self, p):
        self.a, self.b, self.c, self.F = p["a"], p["b"], p["c"], p["F"]

    def VC(self, y): return self.a * y - self.b * y * y + self.c * y ** 3
    def MC(self, y): return self.a - 2 * self.b * y + 3 * self.c * y * y
    def AVC(self, y): return self.a - self.b * y + self.c * y * y
    def AC(self, y): return self.F / y + self.AVC(y)


def firm_supply(p, price):
    minAVC = p["a"] - p["b"] ** 2 / (4 * p["c"])
    if price < minAVC:
        return 0.0
    disc = 4 * p["b"] ** 2 - 12 * p["c"] * (p["a"] - price)
    return (2 * p["b"] + math.sqrt(max(0.0, disc))) / (6 * p["c"])


def firm(p):
    f = FirmCost(p)
    yAVC = p["b"] / (2 * p["c"])
    minAVC = f.AVC(yAVC)
    yAC = argmax(lambda y: -f.AC(y), 1e-3, 20 * yAVC + 10)
    y = firm_supply(p, p.get("P", 0))
    profit = p.get("P", 0) * y - p["F"] - f.VC(y) if y > 0 else -p["F"]
    return dict(f=f, yAVC=yAVC, minAVC=minAVC, yAC=yAC, minAC=f.AC(yAC), y=y, profit=profit, ok=minAVC > 0)


def industry(p):
    fr = firm(p)
    D = lambda P: max(0.0, p["Dmax"] - p["d"] * P)
    S = lambda P: p["n"] * firm_supply(p, P)
    Pmax = p["Dmax"] / p["d"]
    if D(fr["minAVC"]) <= S(fr["minAVC"]):
        P = Pmax if D(fr["minAVC"]) <= 0 else fr["minAVC"]
    else:
        P = bisect(lambda x: D(x) - S(x), fr["minAVC"], max(Pmax, fr["minAVC"] + 1))
    Q = D(P)
    yi = Q / p["n"] if p["n"] > 0 else 0.0
    profit_each = P * yi - p["F"] - fr["f"].VC(yi) if yi > 0 else -p["F"]
    QLR = D(fr["minAC"])
    return {**fr, "D": D, "S": S, "P": P, "Q": Q, "yi": yi, "profitEach": profit_each,
            "PLR": fr["minAC"], "QLR": QLR, "nLR": QLR / fr["yAC"], "Pmax": Pmax}


def tax_eq(p):
    a, b, s0, s1, t = p["a"], p["b"], p["s0"], p["s1"], p["t"]
    Q0 = (a - s0) / (b + s1)
    P0 = a - b * Q0
    Qt = max(0.0, (a - s0 - t) / (b + s1))
    Pd = a - b * Qt
    Ps = Pd - t
    return dict(Q0=Q0, P0=P0, Qt=Qt, Pd=Pd, Ps=Ps, rev=t * Qt, dwl=0.5 * t * (Q0 - Qt),
                cons=(Pd - P0) / t if t != 0 else s1 / (b + s1), ok=Q0 > 0)


# ---------------------------------------------------------------- oligopólio
def oligopoly(p):
    a, b, c1, c2 = p["a"], p["b"], p["c1"], p["c2"]
    P = lambda Q: max(0.0, a - b * Q)
    R1 = lambda q2: max(0.0, (a - c1 - b * q2) / (2 * b))
    R2 = lambda q1: max(0.0, (a - c2 - b * q1) / (2 * b))
    pi1 = lambda q1, q2: (P(q1 + q2) - c1) * q1
    pi2 = lambda q1, q2: (P(q1 + q2) - c2) * q2
    pack = lambda q1, q2: dict(q1=q1, q2=q2, Q=q1 + q2, P=P(q1 + q2), pi1=pi1(q1, q2), pi2=pi2(q1, q2))
    x1 = x2 = 0.0
    for _ in range(300):
        x1 = R1(x2)
        x2 = R2(x1)
    s1 = argmax(lambda q1: pi1(q1, R2(q1)), 0, a / b, 800)
    if abs(c1 - c2) < 1e-9:
        bert = pack((a - c1) / (2 * b), (a - c1) / (2 * b))
    else:
        cl, ch = min(c1, c2), max(c1, c2)
        price = min(ch, (a + cl) / 2)
        Q = max(0.0, (a - price) / b)
        bert = pack(Q, 0.0) if c1 < c2 else pack(0.0, Q)
    cl = min(c1, c2)
    Qm = max(0.0, (a - cl) / (2 * b))
    if abs(c1 - c2) < 1e-9:
        cart = pack(Qm / 2, Qm / 2)
    else:
        cart = pack(Qm, 0.0) if c1 < c2 else pack(0.0, Qm)
    return dict(cournot=pack(x1, x2), stack=pack(s1, R2(s1)), bert=bert, cart=cart, R1=R1, R2=R2,
                nP=lambda n: (a + n * c1) / (n + 1), nQ=lambda n: n * (a - c1) / ((n + 1) * b))


def discrimination(p):
    c = p["c"]
    mk = lambda a, b: dict(q=(a - c) / (2 * b), p=(a + c) / 2) if a > c else dict(q=0.0, p=a)
    m1, m2 = mk(p["a1"], p["b1"]), mk(p["a2"], p["b2"])
    Qtot = lambda P: max(0.0, (p["a1"] - P) / p["b1"]) + max(0.0, (p["a2"] - P) / p["b2"])
    Pu = argmax(lambda P: (P - c) * Qtot(P), c, max(p["a1"], p["a2"]), 2000)
    Qc = max(0.0, (p["a1"] - c) / p["b1"])
    el = lambda P, a: P / (a - P) if a > P else INF
    return dict(m1=m1, m2=m2, Pu=Pu, profDisc=(m1["p"] - c) * m1["q"] + (m2["p"] - c) * m2["q"],
                profUni=(Pu - c) * Qtot(Pu), e1=el(m1["p"], p["a1"]), e2=el(m2["p"], p["a2"]), Qc=Qc,
                perfect=0.5 * (p["a1"] - c) * Qc, simpleProfit=(m1["p"] - c) * m1["q"],
                simpleCS=0.5 * m1["q"] * (p["a1"] - m1["p"]))


def pigou(p):
    a, b, c0, c1, e0, e1 = p["a"], p["b"], p["c0"], p["c1"], p["e0"], p["e1"]
    Qm = max(0.0, (a - c0) / (b + c1))
    Qs = max(0.0, (a - c0 - e0) / (b + c1 + e1))
    tax = e0 + e1 * Qs
    gap = (c0 + (c1 + e1) * Qm + e0) - (a - b * Qm)
    return dict(Qm=Qm, Pm=a - b * Qm, Qs=Qs, Ps=a - b * Qs, tax=tax, dwl=0.5 * (Qm - Qs) * gap)


def commons(p):
    cOpen = max(0.0, (p["A"] - p["k"]) / p["B"])
    cOpt = max(0.0, (p["A"] - p["k"]) / (2 * p["B"]))
    return dict(cOpen=cOpen, cOpt=cOpt, rent=(p["A"] - p["B"] * cOpt) * cOpt - p["k"] * cOpt)


def public_good(p):
    m1 = lambda G: max(0.0, p["al1"] - p["be1"] * G)
    m2 = lambda G: max(0.0, p["al2"] - p["be2"] * G)
    s = lambda G: m1(G) + m2(G)
    top = max(p["al1"] / p["be1"], p["al2"] / p["be2"])
    Gs = 0.0 if s(0) <= p["c"] else bisect(lambda G: s(G) - p["c"], 0, top)
    G1 = max(0.0, (p["al1"] - p["c"]) / p["be1"])
    G2 = max(0.0, (p["al2"] - p["c"]) / p["be2"])
    return dict(m1=m1, m2=m2, sum=s, Gs=Gs, G1=G1, G2=G2, Gn=max(G1, G2), t1=m1(Gs), t2=m2(Gs), top=top)


# ---------------------------------------------------------------- jogos 2×2
def game(p):
    A = [[p["A11"], p["A12"]], [p["A21"], p["A22"]]]
    B = [[p["B11"], p["B12"]], [p["B21"], p["B22"]]]
    pure = [(i, j) for i in range(2) for j in range(2) if A[i][j] >= A[1 - i][j] and B[i][j] >= B[i][1 - j]]
    domA = 0 if A[0][0] > A[1][0] and A[0][1] > A[1][1] else (1 if A[1][0] > A[0][0] and A[1][1] > A[0][1] else None)
    domB = 0 if B[0][0] > B[0][1] and B[1][0] > B[1][1] else (1 if B[0][1] > B[0][0] and B[1][1] > B[1][0] else None)
    dA = A[0][0] - A[0][1] - A[1][0] + A[1][1]
    dB = B[0][0] - B[1][0] - B[0][1] + B[1][1]
    q = (A[1][1] - A[0][1]) / dA if dA != 0 else NAN
    pr = (B[1][1] - B[1][0]) / dB if dB != 0 else NAN
    mixed = dict(p=pr, q=q) if (1e-9 < pr < 1 - 1e-9 and 1e-9 < q < 1 - 1e-9) else None

    def pareto_dominated(cell):
        i, j = cell
        return any(A[k][l] >= A[i][j] and B[k][l] >= B[i][j] and (A[k][l] > A[i][j] or B[k][l] > B[i][j])
                   for k in range(2) for l in range(2))

    dltA = lambda qq: (A[0][0] * qq + A[0][1] * (1 - qq)) - (A[1][0] * qq + A[1][1] * (1 - qq))
    dltB = lambda pp: (B[0][0] * pp + B[1][0] * (1 - pp)) - (B[0][1] * pp + B[1][1] * (1 - pp))
    b_resp = lambda i: 0 if B[i][0] >= B[i][1] else 1
    seqA = 0 if A[0][b_resp(0)] >= A[1][b_resp(1)] else 1
    return dict(A=A, B=B, pure=pure, domA=domA, domB=domB, mixed=mixed, pareto_dominated=pareto_dominated,
                dltA=dltA, dltB=dltB, b_resp=b_resp, seq=(seqA, b_resp(seqA)))


def lemons(p):
    EV = p["q"] * p["VH"] + (1 - p["q"]) * p["VL"]
    return dict(EV=EV, qStar=(p["RH"] - p["VL"]) / (p["VH"] - p["VL"]), pooling=EV >= p["RH"])


def signaling(p):
    lo, hi = (p["a2"] - p["a1"]) / p["c1"], (p["a2"] - p["a1"]) / p["c2"]
    return dict(lo=lo, hi=hi, sep=lo - 1e-9 <= p["es"] <= hi + 1e-9,
                low_none=p["a1"], low_mimic=p["a2"] - p["c1"] * p["es"],
                high_none=p["a1"], high_sig=p["a2"] - p["c2"] * p["es"])


# ---------------------------------------------------------------- cap. 6: demanda
def demand6(p, m=None, p1=None):
    m = p["m"] if m is None else m
    p1 = p["p1"] if p1 is None else p1
    return ces_demand(p["delta"], p["rho"], p["mode"], p1, p["p2"], m)


def util6(x1, x2, p):
    return ces(x1, x2, p["delta"], p["rho"], p["mode"])


def level6(U, p, xmax, ymax):
    return ces_level(U, p["delta"], p["rho"], p["mode"], xmax, ymax)


def demand_stats(p):
    d, h = demand6(p), 1e-4
    if d["x1"] <= 0:
        em = ep = NAN
    else:
        em = (demand6(p, p["m"] * (1 + h))["x1"] - demand6(p, p["m"] * (1 - h))["x1"]) / (2 * h * d["x1"])
        ep = (demand6(p, p1=p["p1"] * (1 + h))["x1"] - demand6(p, p1=p["p1"] * (1 - h))["x1"]) / (2 * h * d["x1"])
    return {**d, "em": em, "ep": ep}


# ---------------------------------------------------------------- cap. 7: preferência revelada
def revealed(p):
    px, py = p["p1"] * p["x1"] + p["p2"] * p["x2"], p["p1"] * p["y1"] + p["p2"] * p["y2"]
    qy, qx = p["q1"] * p["y1"] + p["q2"] * p["y2"], p["q1"] * p["x1"] + p["q2"] * p["x2"]
    same = abs(p["x1"] - p["y1"]) < 1e-9 and abs(p["x2"] - p["y2"]) < 1e-9
    xRPy, yRPx = (not same) and px >= py - 1e-9, (not same) and qy >= qx - 1e-9
    return dict(px=px, py=py, qy=qy, qx=qx, xRPy=xRPy, yRPx=yRPx, violates=xRPy and yRPx, Lq=py / px, Pq=qy / qx)


# ---------------------------------------------------------------- cap. 15: demanda de mercado
def market_demand(p):
    A, B, P = p["A"], p["B"], p["P"]
    Q = max(0.0, (A - P) / B)
    return dict(Q=Q, eps=-INF if P >= A else -P / (A - P), R=P * Q, MR=A - 2 * B * Q, Pu=A / 2, Qu=A / (2 * B), Rmax=A * A / (4 * B))


def agg_q(p, P):
    return max(0.0, (p["a1"] - P) / p["b1"]) + max(0.0, (p["a2"] - P) / p["b2"])


# ---------------------------------------------------------------- cap. 18: leilões (valores U[0, 1])
def bid1(v, n, r):
    return None if v < r else v - (v ** n - r ** n) / (n * v ** (n - 1))


def exp_rev(n, r):
    return (n - 1) / (n + 1) + r ** n - 2 * n * r ** (n + 1) / (n + 1)


def simulate_auctions(n, r, K=4000, seed=7):
    import random
    rng = random.Random(seed)
    r1, r2 = [], []
    for _ in range(K):
        vs = sorted(rng.random() for _ in range(n))
        hi, se = vs[-1], vs[-2]
        if hi < r:
            r1.append(0.0)
            r2.append(0.0)
        else:
            r1.append(bid1(hi, n, r))
            r2.append(max(se, r))
    mean = lambda a: sum(a) / len(a)
    sd = lambda a: math.sqrt(sum((x - mean(a)) ** 2 for x in a) / len(a))
    return dict(r1=r1, r2=r2, m1=mean(r1), m2=mean(r2), sd1=sd(r1), sd2=sd(r2))


# ---------------------------------------------------------------- cap. 34: bem-estar
def welfare34(p):
    G = agents(p)

    def W(uA, uB):
        s_ = p["swf"]
        return uA + uB if s_ == "util" else p["w"] * uA + (1 - p["w"]) * uB if s_ == "peso" else min(uA, uB) if s_ == "rawls" else max(uA, 0) * max(uB, 0)
    pt = lambda t: contract_point(u_ag(G[0], 10 * t, 10 * t), p, G)
    ts = [0.002 + 0.996 * i / 120 for i in range(121)]
    frontier = [pt(t) for t in ts]
    k = max(range(len(frontier)), key=lambda i: W(frontier[i]["uA"], frontier[i]["uB"]))
    tb = argmax(lambda t: W(pt(t)["uA"], pt(t)["uB"]), ts[max(0, k - 1)], ts[min(len(ts) - 1, k + 1)], 30)
    o = pt(tb)
    if W(o["uA"], o["uB"]) < W(frontier[k]["uA"], frontier[k]["uB"]):
        o = frontier[k]
    return dict(frontier=frontier, opt={**o, "W": W(o["uA"], o["uB"])})


# ================================================================ capítulos restantes
import random as _random


def apartments(p):
    N = int(p["N"])
    r = [p["Rmax"] - (p["Rmax"] - p["Rmin"]) * i / (N - 1) for i in range(N)]
    S = min(int(p["S"]), N - 1)
    eff, pc = sum(r[:S]), r[S]
    out = None
    if p["regime"] == "monop":
        q = max(range(1, S + 1), key=lambda k: (k * r[k - 1], -k))
        out = dict(price=r[q - 1], rented=q, revenue=q * r[q - 1], cs=sum(r[:q]) - q * r[q - 1], total=sum(r[:q]))
    elif p["regime"] == "discr":
        out = dict(price=None, rented=S, revenue=eff, cs=0.0, total=eff)
    elif p["regime"] == "teto" and p["ceil"] < pc:
        D = sum(1 for v in r if v >= p["ceil"])
        mean = sum(r[:D]) / D
        out = dict(price=p["ceil"], rented=S, revenue=S * p["ceil"], cs=S * (mean - p["ceil"]), total=S * mean, demanders=D)
    if out is None:
        out = dict(price=pc, rented=S, revenue=S * pc, cs=eff - S * pc, total=eff)
    return dict(r=r, S=S, pc=pc, eff=eff, loss=eff - out["total"], **out)


def budget_set(p):
    p1, p2, m, pol = p["p1"], p["p2"], p["m"], p["pol"]
    base = [(0, m / p2), (m / p1, 0)]
    if pol == "unid":
        pts = [(0, m / p2), (m / (p1 + p["t"]), 0)]
    elif pol == "advalorem":
        pts = [(0, m / p2), (m / (p1 * (1 + p["tau"] / 100)), 0)]
    elif pol == "subsidio":
        pts = [(0, m / p2), (m / max(p1 - p["t"], 0.01), 0)]
    elif pol == "fixo":
        m2 = max(m - p["T"], 0)
        pts = [(0, m2 / p2), (m2 / p1, 0)]
    elif pol == "racion":
        xb = min(p["xbar"], m / p1)
        pts = [(0, m / p2), (xb, (m - p1 * xb) / p2), (xb, 0)]
    elif pol == "acima":
        xb = min(p["xbar"], m / p1)
        rest = m - p1 * xb
        pts = [(0, m / p2), (xb, rest / p2), (xb + rest / (p1 + p["t"]), 0)]
    else:
        pts = base

    def area(q):
        poly = [(0, 0), *q, (q[-1][0], 0)]
        return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))) / 2
    a0 = area(base)
    slope = -(pts[0][1] - pts[1][1]) / (pts[1][0] - pts[0][0]) if pts[1][0] > 0 else -p1 / p2
    return dict(base=base, pts=pts, x1max=max(q[0] for q in pts), x2max=pts[0][1], lost=1 - area(pts) / a0 if a0 > 0 else 0.0, slope0=slope)


PREFS = {
    "cd": (lambda x, y, a: pw(x, a) * pw(y, 1 - a), True, True),
    "sub": (lambda x, y, a: a * x + y, True, True),
    "comp": (lambda x, y, a: min(a * x, y), True, True),
    "mal": (lambda x, y, a: x - a * y, False, True),
    "neutro": (lambda x, y, a: x, False, True),
    "saciedade": (lambda x, y, a: -((x - 5) ** 2 + (y - 5) ** 2), False, True),
    "concava": (lambda x, y, a: x * x + y * y, True, False),
}


def pref_info(p):
    f, mono, conv = PREFS[p["tipo"]]
    h, x, y = 1e-5, 3.0, 5.5
    u1 = (f(x + h, y, p["a"]) - f(x - h, y, p["a"])) / (2 * h)
    u2 = (f(x, y + h, p["a"]) - f(x, y - h, p["a"])) / (2 * h)
    return dict(u=f, mono=mono, conv=conv, ref=(x, y), u1=u1, u2=u2, mrs=(-INF if abs(u2) < 1e-9 else -u1 / u2))


BASE_U = {"cd": lambda x, y, a: pw(x, a) * pw(y, 1 - a), "ql": lambda x, y, a: math.log(x) + y, "sub": lambda x, y, a: a * x + y}
TRANSF = {"id": lambda v: v, "lin": lambda v: 2 * v + 1, "cubo": lambda v: v ** 3, "exp": lambda v: math.exp(v / 3)}


def utility_info(p):
    U = lambda x, y: TRANSF[p["f"]](BASE_U[p["base"]](x, y, p["a"]))
    h = 1e-5
    mu1 = (U(p["x1"] + h, p["x2"]) - U(p["x1"] - h, p["x2"])) / (2 * h)
    mu2 = (U(p["x1"], p["x2"] + h) - U(p["x1"], p["x2"] - h)) / (2 * h)
    return dict(U=U, u=BASE_U[p["base"]](p["x1"], p["x2"], p["a"]), fu=U(p["x1"], p["x2"]), mu1=mu1, mu2=mu2, mrs=-mu1 / mu2)


def bond_price(c, F, T, r):
    return sum(c / (1 + r) ** t for t in range(1, int(T) + 1)) + F / (1 + r) ** T


def hotelling(S, D, C, r):
    T = S / D
    return dict(T=T, p0=C / (1 + r) ** T)


def forest(A, k, r):
    F = lambda T: A * (1 - math.exp(-k * T)) ** 3
    g = lambda T: 3 * k * math.exp(-k * T) / (1 - math.exp(-k * T))
    Ts = math.log((3 * k + r) / r) / k
    return dict(F=F, g=g, Ts=Ts, PV=lambda T: F(T) * math.exp(-r * T))


def identification(N, b, d, sd, ss, seed=11):
    rng = _random.Random(seed)
    a, c = 10.0, 0.0
    Ps, Qs = [], []
    for _ in range(N):
        ud, us = sd * rng.gauss(0, 1), ss * rng.gauss(0, 1)
        P = (a - c + ud - us) / (b + d)
        Ps.append(P)
        Qs.append(c + d * P + us)
    mP, mQ = sum(Ps) / N, sum(Qs) / N
    vP = sum((x - mP) ** 2 for x in Ps)
    beta = sum((x - mP) * (y - mQ) for x, y in zip(Ps, Qs)) / vP if vP > 1e-12 else NAN
    return dict(Ps=Ps, Qs=Qs, beta=beta, alpha=mQ - beta * mP if beta == beta else NAN, a=a, c=c)


def experiment(N, tau, sel, seed=23):
    rng = _random.Random(seed)
    g = {k: [0.0, 0] for k in ("R1", "R0", "O1", "O0")}
    for _ in range(N):
        y0 = 10 + 2 * rng.gauss(0, 1)
        dR = rng.random() < 0.5
        dO = rng.random() < 1 / (1 + math.exp(-4 * sel * (y0 - 10) / 2))
        for key, d in (("R", dR), ("O", dO)):
            k = key + ("1" if d else "0")
            g[k][0] += y0 + (tau if d else 0)
            g[k][1] += 1
    est = lambda a, b: g[a][0] / g[a][1] - g[b][0] / g[b][1] if g[a][1] and g[b][1] else NAN
    rand, obs = est("R1", "R0"), est("O1", "O0")
    return dict(rand=rand, obs=obs, bias=obs - tau, share=g["O1"][1] / N)


def hawk_dove(V, Cc):
    h = 1.0 if V >= Cc else V / Cc
    payH = lambda s: s * (V - Cc) / 2 + (1 - s) * V
    payD = lambda s: (1 - s) * V / 2
    return dict(h=h, payH=payH, payD=payD, avg=h * payH(h) + (1 - h) * payD(h))


def rubinstein(d1, d2):
    return (1 - d2) / (1 - d1 * d2)


def present_bias(A, B, k, h, rho):
    H = lambda t: 1 / (1 + h * t)
    E = lambda t: math.exp(-rho * t)
    tStar = (A * (1 + h * k) - B) / (h * (B - A)) if B != A else NAN
    pick = lambda D, t: "A" if A * D(t) >= B * D(t + k) else "B"
    return dict(H=H, E=E, tStar=tStar, nowH=pick(H, 0), farH=pick(H, 60), nowE=pick(E, 0), farE=pick(E, 60))


def ultimatum(al, bp):
    thr = 10 * al / (1 + 2 * al)
    offer = 5.0 if bp >= 0.5 else thr
    return dict(thr=thr, offer=offer, uR=lambda x: x - al * max(10 - 2 * x, 0), prop=10 - offer)


def network(p):
    if p > 0.25:
        return dict(ok=False)
    s = math.sqrt(1 - 4 * p)
    return dict(ok=True, nLow=(1 - s) / 2, nHigh=(1 + s) / 2)


def complements(a, c):
    pi, xi = (a + c) / 3, (a - 2 * c) / 3
    Pm, xm = (a + 2 * c) / 2, (a - 2 * c) / 2
    return dict(pi=pi, Pind=2 * pi, xi=xi, profInd=(pi - c) * xi, Pm=Pm, xm=xm, profM=(Pm - 2 * c) * xm, ok=a > 2 * c)


def endowment_slutsky(p):
    """Decomposição de Slutsky com dotação (Varian, cap. 9): substituição + renda comum + renda dotação."""
    f = lambda p1, m: ces_demand(p["delta"], p["rho"], p["mode"], p1, p["p2"], m)
    m0 = p["p1"] * p["e1"] + p["p2"] * p["e2"]
    m1 = p["p1n"] * p["e1"] + p["p2"] * p["e2"]
    A = f(p["p1"], m0)
    mS = p["p1n"] * A["x1"] + p["p2"] * A["x2"]
    B, Cc, D = f(p["p1n"], mS), f(p["p1n"], m0), f(p["p1n"], m1)
    return dict(A=A, B=B, C=Cc, D=D, m0=m0, m1=m1, mS=mS, sub=B["x1"] - A["x1"], inc=Cc["x1"] - B["x1"], endow=D["x1"] - Cc["x1"],
                tot=D["x1"] - A["x1"], sub2=B["x2"] - A["x2"], inc2=Cc["x2"] - B["x2"], endow2=D["x2"] - Cc["x2"], tot2=D["x2"] - A["x2"],
                net0=p["e1"] - A["x1"])


# ================================================================ modelos prioritários
def giffen(p, m=None, p1=None):
    """Utilidade de Haagsma (2012): u = ln(x1 − γ1) − β ln(γ2 − x2), β > 1 ⇒ x1 inferior; Giffen quando m > p2·γ2."""
    m = p["m"] if m is None else m
    p1 = p["p1"] if p1 is None else p1
    x1 = ((p["p2"] * p["g2"] - m) + p["be"] * p1 * p["g1"]) / ((p["be"] - 1) * p1)
    x2 = (m - p1 * x1) / p["p2"]
    return dict(x1=x1, x2=x2, ok=x1 > p["g1"] + 1e-9 and -1e-9 <= x2 < p["g2"] - 1e-9)


def u_giffen(x1, x2, p):
    return math.log(x1 - p["g1"]) - p["be"] * math.log(p["g2"] - x2)


def giffen_stats(p):
    d, h = giffen(p), 1e-4
    ep = (giffen(p, p1=p["p1"] * (1 + h))["x1"] - giffen(p, p1=p["p1"] * (1 - h))["x1"]) / (2 * h * d["x1"]) if d["x1"] else NAN
    return {**d, "em": -p["m"] / ((p["be"] - 1) * p["p1"] * d["x1"]) if d["x1"] else NAN, "ep": ep, "mStar": p["p2"] * p["g2"]}


def compensated(p):
    A = ces_demand(p["delta"], p["rho"], p["mode"], p["p1"], p["p2"], p["w"])
    U0 = ces(A["x1"], A["x2"], p["delta"], p["rho"], p["mode"])
    mar = lambda q: ces_demand(p["delta"], p["rho"], p["mode"], q, p["p2"], p["w"])["x1"]
    hic = lambda q: ces_demand(p["delta"], p["rho"], p["mode"], q, p["p2"], ces_E(p["delta"], p["rho"], p["mode"], q, p["p2"], U0))["x1"]
    h = 1e-4 * p["p1"]
    sM, sH = (mar(p["p1"] + h) - mar(p["p1"] - h)) / (2 * h), (hic(p["p1"] + h) - hic(p["p1"] - h)) / (2 * h)
    return dict(A=A, U0=U0, mar=mar, hic=hic, sM=sM, sH=sH, eM=sM * p["p1"] / A["x1"] if A["x1"] else NAN, eH=sH * p["p1"] / A["x1"] if A["x1"] else NAN)


def inflation(p):
    real = (p["r"] - p["pi"]) / (1 + p["pi"])
    W = p["m1"] + p["m2"] / (1 + real)
    d = ces_demand(p["beta"], p["rho"], p["mode"], 1, 1 / (1 + real), W)
    return dict(real=real, W=W, Wn=p["m1"] + p["m2"] / (1 + p["r"]), c1=d["x1"], c2=d["x2"], s=p["m1"] - d["x1"],
                U=ces(d["x1"], d["x2"], p["beta"], p["rho"], p["mode"]))


def intertemporal_slutsky(p):
    return endowment_slutsky(dict(delta=p["beta"], rho=p["rho"], mode=p["mode"], p1=1 + p["r"], p1n=1 + p["rn"], p2=1, e1=p["m1"], e2=p["m2"]))


def tax_runs(p):
    fr = firm({**p, "P": 0})
    D = lambda P: max(0.0, p["Dmax"] - p["d"] * P)
    Pmax = p["Dmax"] / p["d"]
    n = D(fr["minAC"]) / fr["yAC"]
    S = lambda P: n * firm_supply(p, P - p["t"])
    lo = fr["minAVC"] + p["t"]
    if D(lo) <= S(lo):
        Psr = Pmax if D(lo) <= 0 else lo
    else:
        Psr = bisect(lambda x: D(x) - S(x), lo, max(Pmax, lo + 1))
    Plr = fr["minAC"] + p["t"]
    Qlr = D(Plr)
    return {**fr, "n": n, "P0": fr["minAC"], "Q0": D(fr["minAC"]), "Psr": Psr, "Qsr": D(Psr), "Plr": Plr, "Qlr": Qlr, "nlr": Qlr / fr["yAC"],
            "D": D, "S": S, "S0": lambda P: n * firm_supply(p, P), "Pmax": Pmax}


def mono_tax(p):
    if p["kind"] == "ce":
        mk = p["eps"] / (p["eps"] - 1)
        p0, p1 = p["c"] * mk, (p["c"] + p["t"]) * mk
        return dict(p0=p0, p1=p1, q0=1000 * p0 ** -p["eps"], q1=1000 * p1 ** -p["eps"], pass_=(p1 - p0) / p["t"] if p["t"] else mk, mk=mk)
    q0 = max(0.0, (p["a"] - p["c"]) / (2 * p["b"]))
    q1 = max(0.0, (p["a"] - p["c"] - p["t"]) / (2 * p["b"]))
    P0, P1 = p["a"] - p["b"] * q0, p["a"] - p["b"] * q1
    return dict(p0=P0, p1=P1, q0=q0, q1=q1, pass_=(P1 - P0) / p["t"] if p["t"] else 0.5)


def natural_mono(p):
    a, b, c, F = p["a"], p["b"], p["c"], p["F"]
    qm = (a - c) / (2 * b)
    pm = a - b * qm
    qc = (a - c) / b
    disc = (a - c) ** 2 - 4 * b * F
    qac = ((a - c) + math.sqrt(disc)) / (2 * b) if disc >= 0 else NAN
    pac = a - b * qac if disc >= 0 else NAN
    return dict(qm=qm, pm=pm, profitM=(pm - c) * qm - F, qc=qc, lossMC=-F, qac=qac, pac=pac, ok=disc >= 0 and a > c,
                dwlM=0.5 * (qc - qm) * (pm - c), dwlAC=0.5 * (qc - qac) * (pac - c) if disc >= 0 else NAN)


def second_degree(p):
    ratio = p["pH"] / (1 - p["pH"])
    qL = max(0.0, p["aL"] - ratio * (p["aH"] - p["aL"]))
    TL = p["aL"] * qL - qL * qL / 2
    rent = (p["aH"] - p["aL"]) * qL
    TH = p["aH"] ** 2 / 2 - rent
    return dict(qL=qL, qH=p["aH"], TL=TL, TH=TH, rent=rent, profit=p["pH"] * TH + (1 - p["pH"]) * TL,
                perfect=p["pH"] * p["aH"] ** 2 / 2 + (1 - p["pH"]) * p["aL"] ** 2 / 2, lostL=(p["aL"] - qL) ** 2 / 2)


def hotelling_loc(xA, xB):
    a, b = min(xA, xB), max(xA, xB)
    low = 0.5 if abs(xA - xB) < 1e-9 else (a + b) / 2
    sA = low if xA <= xB else 1 - low
    return dict(sA=sA, sB=1 - sA, avg=a * a / 2 + (b - a) ** 2 / 4 + (1 - b) ** 2 / 2, opt=0.125)


def second_theorem(p):
    G, cc = agents(p), contract_curve(p, 120)
    ln_ = [0.0]
    for i in range(1, len(cc)):
        ln_.append(ln_[-1] + math.hypot(cc[i]["x"] - cc[i - 1]["x"], cc[i]["y"] - cc[i - 1]["y"]))
    target = p["tpos"] * ln_[-1]
    i = next((j for j, v in enumerate(ln_) if v >= target), len(ln_) - 1)
    i = max(1, i)
    f = (target - ln_[i - 1]) / (ln_[i] - ln_[i - 1]) if ln_[i] > ln_[i - 1] else 0.0
    x = cc[i - 1]["x"] + f * (cc[i]["x"] - cc[i - 1]["x"])
    y = cc[i - 1]["y"] + f * (cc[i]["y"] - cc[i - 1]["y"])
    S = support_price(x, y, p)
    price = S["price"]
    return dict(x=x, y=y, price=price, range=S["range"], T=price * x + y - (price * p["eA1"] + p["eA2"]),
                uA=u_ag(G[0], x, y), uB=u_ag(G[1], 10 - x, 10 - y), curve=cc)


def comparative(p):
    T = 10
    ocR, ocF = p["rf"] / p["rc"], p["ff"] / p["fc"]
    rCoco = ocR <= ocF
    kink = dict(fish=T * p["ff"], coco=T * p["rc"]) if rCoco else dict(fish=T * p["rf"], coco=T * p["fc"])
    return dict(T=T, ocR=ocR, ocF=ocF, rCoco=rCoco, kink=kink, maxFish=T * (p["rf"] + p["ff"]), maxCoco=T * (p["rc"] + p["fc"]))


def coase(a, k):
    s = a / (1 + k)
    lossA, gainB = (a - s) ** 2 / 2, k * (a * a - s * s) / 2
    gainA, lossB = a * s - s * s / 2, k * s * s / 2
    return dict(s=s, rightsA=dict(start=a, payer="B", pay=(lossA + gainB) / 2, gain=gainB - lossA),
                rightsB=dict(start=0.0, payer="A", pay=(gainA + lossB) / 2, gain=gainA - lossB))


def incentives(p):
    a, ubar = p["a"], p["ubar"]
    xe, Se = a, a * a / 2
    if p["contract"] == "parceria":
        x = p["s"] * a
        owner, worker = (1 - p["s"]) * a * x, p["s"] * a * x - x * x / 2
        return dict(x=x, owner=owner, worker=worker, total=owner + worker, xe=xe, Se=Se, loss=Se - owner - worker, part=worker >= ubar - 1e-9)
    return dict(x=xe, owner=Se - ubar, worker=ubar, total=Se, xe=xe, Se=Se, loss=0.0, part=True,
                fee=Se - ubar if p["contract"] == "aluguel" else ubar - Se, wage=a)
