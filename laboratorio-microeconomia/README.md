# Laboratório de Microeconomia (Streamlit)

Modelos interativos de *Microeconomia: uma abordagem moderna*, de Hal R. Varian (9ª edição), organizados por capítulo: os 38 capítulos do livro, em ordem.
Feito com base no repositório [amaral-vitor/Hal-Varian-s-models-from-Intermediate-Microeconomics-](https://github.com/amaral-vitor/Hal-Varian-s-models-from-Intermediate-Microeconomics-/tree/master).

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

O menu lateral precisa do Streamlit 1.46 ou mais novo. Se você já tinha uma versão anterior instalada, atualize com `pip install -U streamlit`.

## Publicar no Streamlit Community Cloud

1. Suba esta pasta para um repositório no GitHub.
2. Em https://share.streamlit.io, clique em **Create app**, escolha o repositório e indique `app.py` como arquivo principal.

## Estrutura

- `app.py` — menu lateral por capítulo: os subtópicos de cada capítulo aparecem ao clicar nele.
- `micro/core.py` — toda a matemática dos modelos, sem dependências.
- `micro/pages_*.py` — uma função por modelo.
- `micro/ui.py` — estilo, gráficos Plotly e painéis de resultado.
- `.streamlit/config.toml` — tema com as cores do app.
