-- ═══════════════════════════════════════════════════════════════
-- SCHÉMA PostgreSQL — VideoScribe AI
-- ═══════════════════════════════════════════════════════════════
-- Ce fichier est exécuté par init_db() pour créer les tables.
-- Idempotent : utilise CREATE TABLE IF NOT EXISTS.

-- ═══ UTILISATEURS ═══
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT DEFAULT '',
    salt TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'client',
    active BOOLEAN DEFAULT TRUE,
    plan TEXT DEFAULT 'free',
    premium_expires TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ═══ HISTORIQUE DES ANALYSES ═══
CREATE TABLE IF NOT EXISTS history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    video_id TEXT NOT NULL,
    title TEXT DEFAULT '',
    lang TEXT DEFAULT 'unknown',
    notes JSONB DEFAULT '[]'::jsonb,
    keywords JSONB DEFAULT '[]'::jsonb,
    questions JSONB DEFAULT '[]'::jsonb,
    total_words INTEGER DEFAULT 0,
    num_chunks INTEGER DEFAULT 0,
    processing_time REAL DEFAULT 0,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_history_user ON history(user_id);
CREATE INDEX IF NOT EXISTS idx_history_video ON history(video_id);
CREATE INDEX IF NOT EXISTS idx_history_date ON history(date DESC);

-- ═══ FAVORIS ═══
CREATE TABLE IF NOT EXISTS favorites (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    video_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, video_id)
);

CREATE INDEX IF NOT EXISTS idx_favorites_user ON favorites(user_id);

-- ═══ PARTAGES PUBLICS ═══
CREATE TABLE IF NOT EXISTS shares (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    video_id TEXT NOT NULL,
    notes JSONB DEFAULT '[]'::jsonb,
    keywords JSONB DEFAULT '[]'::jsonb,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_shares_user ON shares(user_id);

-- ═══ PRÉFÉRENCES ═══
CREATE TABLE IF NOT EXISTS prefs (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value TEXT DEFAULT '',
    PRIMARY KEY (user_id, key)
);

-- ═══ NOTIFICATIONS ═══
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    icon TEXT DEFAULT 'info',
    text TEXT NOT NULL,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(user_id, read);

-- ═══ SESSIONS ═══
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);

-- ═══ MESSAGES DE CONTACT ═══
CREATE TABLE IF NOT EXISTS contact_messages (
    id SERIAL PRIMARY KEY,
    sender TEXT DEFAULT 'anonyme',
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    urgency TEXT DEFAULT 'normale',
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_contact_read ON contact_messages(read);

-- ═══ REVENUS ═══
CREATE TABLE IF NOT EXISTS revenues (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan TEXT NOT NULL,
    amount REAL NOT NULL,
    days INTEGER DEFAULT 30,
    method TEXT DEFAULT 'manuel',
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_revenues_user ON revenues(user_id);
CREATE INDEX IF NOT EXISTS idx_revenues_date ON revenues(date DESC);