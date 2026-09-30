import streamlit as st

DARK_CSS = """
<style>
    html, body, .stApp { background-color: #0E1116 !important; }
    [data-testid="stAppViewContainer"] { background-color: #0E1116 !important; }
    section.main, section.main .block-container { background-color: #0E1116 !important; }
    [data-testid="stSidebar"] > div { background-color: #16191F !important; }
    [data-testid="stHeader"] { background-color: transparent !important; }

    /* Tous les textes en clair */
    h1, h2, h3, h4, p, span, label, li, strong, em, b, i, code, td, th {
        color: #FAFAFA !important;
    }
    [data-testid="stCaptionContainer"] p { color: #9CA3AF !important; }

    /* Champs de saisie */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea {
        background-color: #262730 !important;
        color: #FAFAFA !important;
        border-color: #3a3d46 !important;
    }
    [data-baseweb="select"] > div {
        background-color: #262730 !important;
        border-color: #3a3d46 !important;
    }
    [data-baseweb="select"] span { color: #FAFAFA !important; }

    /* Métriques */
    .metric-card { background: #262730 !important; }
    [data-testid="stMetric"] { background: #262730 !important; border-radius: 10px; padding: 10px; }

    /* Éléments qui restent CLAIRS même en dark */
    .keyword-tag { color: #EAF1FB !important; }
    .main-header h1, .main-header p, .hbadge { color: #FFFFFF !important; }
    .stButton > button p, .stDownloadButton > button p { color: #FFFFFF !important; }

    [data-testid="stTabs"] button { color: #FAFAFA !important; }
    hr { border-color: #3a3d46 !important; }
    
    .stMarkdown code {
        background: #262730 !important;
        color: #EAF1FB !important;
        border: 1px solid rgba(255,255,255,.15);
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 700;
    }
    
    .note-card { background:#141B2B !important; border-color:rgba(255,255,255,.1); }
    .note-text { color:#F5F7FB !important; }
    .q-item { color:#F5F7FB !important; }
    
    
</style>
"""

LIGHT_CSS = """
<style>
    html, body, .stApp { background-color: #F4F6FB !important; }
    [data-testid="stAppViewContainer"] { background-color: #F4F6FB !important; }
    section.main, section.main .block-container { background-color: #F4F6FB !important; }
    [data-testid="stSidebar"] > div { background-color: #FFFFFF !important; }
    [data-testid="stHeader"] { background-color: transparent !important; }
    
    
    
    /* Puces Technologies lisibles */
    .stMarkdown code {
        background: #E8EDF7 !important;
        color: #1B3B6F !important;
        border: 1px solid rgba(27,59,111,.25);
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 700;
    }
    

    /* Tous les textes en foncé */
    h1, h2, h3, h4, p, span, label, li, strong, em, b, i, code, td, th {
        color: #0F1A2E !important;
    }
    [data-testid="stCaptionContainer"] p { color: #6B7280 !important; }

    /* Champs de saisie */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea {
        background-color: #FFFFFF !important;
        color: #0F1A2E !important;
        border-color: #D0D7E2 !important;
    }
    [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border-color: #D0D7E2 !important;
    }
    [data-baseweb="select"] span { color: #0F1A2E !important; }

    /* Métriques */
    .metric-card { background: #FFFFFF !important; }
    [data-testid="stMetric"] { background: #FFFFFF !important; border-radius: 10px; padding: 10px; }

    .keyword-tag { color: #1B3B6F !important; }

    /* ✅ Le hero reste bleu foncé → textes BLANCS dans les deux thèmes */
    .main-header h1, .main-header p, .hbadge { color: #FFFFFF !important; }

    /* ✅ Boutons dégradés → texte blanc */
    .stButton > button p, .stDownloadButton > button p { color: #FFFFFF !important; }

    [data-testid="stTabs"] button { color: #0F1A2E !important; }
    hr { border-color: #D0D7E2 !important; }
    
    .note-card { background:#FFFFFF !important; border-color:#E1E7F0; }
    .note-text { color:#0F1A2E !important; }
    .q-item { color:#0F1A2E !important; }
    
</style>
"""

def apply_theme(theme):
    """Injecte le CSS correspondant au thème choisi."""
    st.markdown(DARK_CSS if theme == "dark" else LIGHT_CSS, unsafe_allow_html=True)