# jobs/permissions_manager.py
import sqlite3

DB_PATH = "data_warehouse.db"

def init_permissions_table():
    """Crée la table des permissions si elle n'existe pas."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            folder TEXT NOT NULL,
            can_read BOOLEAN DEFAULT 1,
            can_write BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    print("✅ Table 'permissions' initialisée.")

def add_permission(user, folder, can_read=True, can_write=False):
    """Ajoute ou met à jour les droits d’un utilisateur."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO permissions (user, folder, can_read, can_write)
        VALUES (?, ?, ?, ?)
    """, (user, folder, can_read, can_write))
    conn.commit()
    conn.close()
    print(f"🔐 Permission ajoutée pour {user} sur {folder}.")

def list_permissions():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM permissions;").fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_permissions_table()
    add_permission("admin", "TRANSACTIONS_SECURE", True, True)
    add_permission("analyst", "TRANSACTIONS_USD", True, False)
    print(list_permissions())
