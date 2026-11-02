"""Supprime les espaces fantômes en haut de TOUTES les pages.

Chaque st.markdown("<style>…") et chaque iframe de hauteur 0 (components.html)
crée un élément Streamlit vide qui ajoute quand même l'écart (gap) d'un bloc
vertical : empilés, ils forment un grand vide en haut de page.
Appeler apply_tighten() UNE fois, juste après l'injection du CSS global.
"""
import streamlit as st

_CSS = """
<style>
html body .stApp [data-testid="stMainBlockContainer"] [data-testid="stElementContainer"]:has(> [data-testid="stMarkdown"] [data-testid="stMarkdownContainer"] > style:only-child),
html body .stApp [data-testid="stMainBlockContainer"] [data-testid="stElementContainer"]:has(> [data-testid="stMarkdown"] style:only-child):not(:has(p, h1, h2, h3, h4, svg, img, table, ul, ol, a, span)) {
  display:none !important; }
html body .stApp [data-testid="stMainBlockContainer"] [data-testid="stElementContainer"]:has(iframe[height="0"]),
html body .stApp [data-testid="stMainBlockContainer"] [data-testid="stElementContainer"]:has(iframe[style*="height: 0"]) {
  position:absolute !important; width:0 !important; height:0 !important; overflow:hidden !important; margin:0 !important; padding:0 !important; }
html body .stApp [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] { gap:.75rem !important; }
html body .stApp [data-testid="stMainBlockContainer"] { padding-top:1.2rem !important; }
@media (max-width:768px) {
  html body .stApp [data-testid="stMainBlockContainer"] { padding-top:4.6rem !important; }
}
</style>
"""

def apply_tighten():
    st.markdown(_CSS.replace("\n", ""), unsafe_allow_html=True)