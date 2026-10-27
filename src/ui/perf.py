"""
Mini-profiler de rendu — pour trouver ce qui ralentit la navigation.

Activation : ajouter `?perf=1` à l'URL de l'application. Les temps s'affichent en bas de la barre latérale
ET dans les logs (Streamlit Cloud → Manage app → Logs, lignes « [perf] »). Sans `?perf=1`, ne fait rien.

Usage dans app.py :
    from src.ui import perf
    perf.start()                 # tout en haut, juste après `import streamlit as st`
    perf.mark("css")             # après chaque grande étape
    perf.report()                # juste avant le routage des pages
"""
import time
import streamlit as st

_RUN = {"t0": 0.0, "last": 0.0, "marks": []}


def _on() -> bool:
    try:
        return st.query_params.get("perf") == "1"
    except Exception:
        return False


def start() -> None:
    now = time.perf_counter()
    _RUN.update(t0=now, last=now, marks=[])


def mark(label: str) -> None:
    now = time.perf_counter()
    _RUN["marks"].append((label, now - _RUN["last"]))
    _RUN["last"] = now


def report() -> None:
    if not _on():
        return
    total = time.perf_counter() - _RUN["t0"]
    lines = [f"{lbl:<22}{dt * 1000:8.0f} ms" for lbl, dt in _RUN["marks"]] + [f"{'TOTAL script':<22}{total * 1000:8.0f} ms"]
    print("[perf] " + " | ".join(l.replace("  ", " ") for l in lines), flush=True)
    with st.sidebar:
        st.caption("⏱ Temps de rendu du script")
        st.code("\n".join(lines), language=None)