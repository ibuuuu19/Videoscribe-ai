"""
Cache de lecture par session — supprime les allers-retours base de données/disque répétés à chaque clic.

Avant : chaque exécution du script refaisait get_tier, unread_count (×2), get_notifications, list_users,
count_today, get_avatar_b64… = autant de requêtes PostgreSQL distantes (souvent une nouvelle connexion
SSL par appel) → plusieurs secondes de page grisée.
Maintenant : les lectures sont mémorisées quelques secondes dans st.session_state ; toute ÉCRITURE
(analyse enregistrée, notification lue, changement de plan, favori…) vide ce cache, donc rien n'est périmé
pour l'utilisateur qui agit.

Usage : `from src.ui.fast import get_tier, unread_count, ...` à la place des imports directs.
"""
import copy
import functools
import time

import streamlit as st

from src import user_manager as _um
from src import notification_manager as _nm
from src import history_manager as _hm
from src.ui import storage as _stor

_KEY = "_fast_cache"


def clear() -> None:
    st.session_state.pop(_KEY, None)


def _cached(fn, ttl: float):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        store = st.session_state.setdefault(_KEY, {})
        ck = (fn.__module__, fn.__name__, args, tuple(sorted(kwargs.items())))
        try:
            hash(ck)
        except TypeError:
            return fn(*args, **kwargs)
        hit = store.get(ck)
        now = time.time()
        if hit and now - hit[0] < ttl:
            return copy.deepcopy(hit[1])
        val = fn(*args, **kwargs)
        store[ck] = (now, copy.deepcopy(val))
        return val
    return wrapper


def _writer(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        finally:
            clear()
    return wrapper


# ── Lectures (mémorisées) ──
get_tier = _cached(_um.get_tier, 30)
get_plan = _cached(_um.get_plan, 30)
list_users = _cached(_um.list_users, 30)
unread_count = _cached(_nm.unread_count, 15)
get_notifications = _cached(_nm.get_notifications, 15)
count_today = _cached(_hm.count_today, 30)
get_history = _cached(_hm.get_history, 30)
load_favs = _cached(_stor.load_favs, 30)
get_avatar_b64 = _cached(_stor.get_avatar_b64, 600)

# ── Écritures (vident le cache) ──
set_plan = _writer(_um.set_plan)
set_active = _writer(_um.set_active)
delete_user = _writer(_um.delete_user)
reset_password = _writer(_um.reset_password)
register_user = _writer(_um.register_user)
notify = _writer(_nm.notify)
mark_all_read = _writer(_nm.mark_all_read)
save_analysis = _writer(_hm.save_analysis)
clear_history = _writer(_hm.clear_history)
trim_history = _writer(_hm.trim_history)
toggle_fav = _writer(_stor.toggle_fav)