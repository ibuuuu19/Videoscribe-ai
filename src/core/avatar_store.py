"""
Photo de profil PERSISTANTE (cloud + local).

Sur Streamlit Cloud le disque est éphémère : un fichier écrit dans data/avatars disparaît au prochain
redéploiement/redémarrage. On stocke donc l'image (redimensionnée 256×256, ~15 Ko) dans PostgreSQL,
table `user_avatars`, créée automatiquement. Le disque reste un simple secours si la base est indisponible
(et sert aussi à migrer les anciennes photos : lues sur disque, elles sont recopiées en base au 1er affichage).
"""
import base64
import io
from pathlib import Path

try:
    from src.core.config import AVATAR_DIR
except Exception:  # pragma: no cover
    AVATAR_DIR = Path("data/avatars")

_MIME = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp", "gif": "image/gif"}
_table_ready = False


def _cursor():
    from src.core.db import db_cursor
    return db_cursor()


def _ensure_table(cur) -> None:
    global _table_ready
    if _table_ready:
        return
    cur.execute(
        "CREATE TABLE IF NOT EXISTS user_avatars ("
        "username TEXT PRIMARY KEY, mime TEXT NOT NULL, data BYTEA NOT NULL, updated_at TIMESTAMPTZ DEFAULT now())"
    )
    _table_ready = True


def _normalize(raw: bytes, mime: str):
    """Recadre en carré 256×256 et compresse (JPEG). Sans Pillow : octets tels quels."""
    try:
        from PIL import Image, ImageOps
        im = Image.open(io.BytesIO(raw))
        im = ImageOps.exif_transpose(im).convert("RGB")
        im = ImageOps.fit(im, (256, 256), method=Image.LANCZOS)
        out = io.BytesIO()
        im.save(out, format="JPEG", quality=86, optimize=True)
        return out.getvalue(), "image/jpeg"
    except Exception:
        return raw, mime


def _disk_file(user: str):
    try:
        for p in Path(AVATAR_DIR).glob(f"{user}.*"):
            return p
    except Exception:
        pass
    return None


def _uri(data: bytes, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(data).decode()


def save_avatar(user: str, raw: bytes, filename: str = "photo.png") -> bool:
    """Enregistre la photo (base + disque de secours). True si la base l'a acceptée."""
    mime = _MIME.get(filename.rsplit(".", 1)[-1].lower(), "image/png")
    data, mime = _normalize(raw, mime)
    ok = False
    try:
        with _cursor() as cur:
            _ensure_table(cur)
            cur.execute(
                "INSERT INTO user_avatars (username, mime, data, updated_at) VALUES (%s, %s, %s, now()) "
                "ON CONFLICT (username) DO UPDATE SET mime = EXCLUDED.mime, data = EXCLUDED.data, updated_at = now()",
                (user, mime, data),
            )
        ok = True
    except Exception as e:
        print(f"[avatar] écriture base impossible ({type(e).__name__}) → disque seulement")
    try:  # secours local
        d = Path(AVATAR_DIR); d.mkdir(parents=True, exist_ok=True)
        for old in d.glob(f"{user}.*"):
            old.unlink()
        (d / f"{user}.{'jpg' if mime == 'image/jpeg' else mime.split('/')[-1]}").write_bytes(data)
    except Exception:
        pass
    return ok


def get_avatar_b64(user: str) -> str:
    """URI data: de la photo, ou "" s'il n'y en a pas."""
    if not user:
        return ""
    try:
        with _cursor() as cur:
            _ensure_table(cur)
            cur.execute("SELECT mime, data FROM user_avatars WHERE username = %s", (user,))
            row = cur.fetchone()
        if row:
            return _uri(bytes(row[1]), row[0])
    except Exception:
        pass
    # pas en base (ou base indisponible) → ancien fichier disque, recopié en base pour le rendre durable
    f = _disk_file(user)
    if f:
        try:
            raw = f.read_bytes()
            save_avatar(user, raw, f.name)
            return _uri(raw, _MIME.get(f.suffix.lstrip(".").lower(), "image/png"))
        except Exception:
            return ""
    return ""


def delete_avatar(user: str) -> None:
    try:
        with _cursor() as cur:
            _ensure_table(cur)
            cur.execute("DELETE FROM user_avatars WHERE username = %s", (user,))
    except Exception:
        pass
    try:
        for p in Path(AVATAR_DIR).glob(f"{user}.*"):
            p.unlink()
    except Exception:
        pass