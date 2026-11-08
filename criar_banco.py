import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS conhecimento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    marca TEXT,
    categoria TEXT NOT NULL,
    pergunta TEXT NOT NULL,
    resposta TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pergunta TEXT NOT NULL,
    resposta TEXT NOT NULL,
    encontrou_na_base INTEGER NOT NULL,
    util INTEGER,
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

conn = sqlite3.connect("pontal.db")
conn.executescript(SCHEMA)
conn.commit()
conn.close()
print("Banco criado.")