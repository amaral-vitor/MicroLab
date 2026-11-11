"""Registro das páginas na ordem dos capítulos do Varian (9ª edição)."""
CHAPTERS = {1: "O mercado", 2: "Restrição orçamentária", 3: "Preferências", 4: "Utilidade", 11: "Mercados de ativos", 17: "Medição", 30: "Aplicações da teoria dos jogos", 31: "Economia comportamental", 36: "Tecnologia da informação", 5: "Escolha", 6: "Demanda", 7: "Preferência revelada", 15: "Demanda de mercado", 18: "Leilões", 34: "Bem-estar", 8: "Equação de Slutsky", 9: "Comprar e vender", 10: "Escolha intertemporal", 12: "Incerteza",
            13: "Ativos de risco", 14: "Excedente do consumidor", 16: "Equilíbrio", 19: "Tecnologia", 20: "Maximização de lucro",
            21: "Minimização de custos", 22: "Curvas de custo", 23: "Oferta da empresa", 24: "Oferta da indústria",
            25: "Monopólio", 26: "Comportamento do monopólio", 27: "Mercados de fatores", 28: "Oligopólio",
            29: "Teoria dos jogos", 32: "Trocas", 33: "Produção", 35: "Externalidades", 37: "Bens públicos",
            38: "Informação assimétrica"}

PAGES = []


def page(pid, ch, nav=None):
    """Registra uma página. `nav` é o rótulo no menu quando o capítulo tem mais de um modelo."""
    def deco(fn):
        PAGES.append(dict(id=pid, ch=ch, nav=nav, fn=fn))
        return fn
    return deco
