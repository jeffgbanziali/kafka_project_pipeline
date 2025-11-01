import sqlite3
import pandas as pd

# Connexion à la base SQLite
conn = sqlite3.connect("data_warehouse.db")

queries = {
    "total_by_type": """
        SELECT
          json_extract(data, '$.TRANSACTION_TYPE') AS transaction_type,
          SUM(json_extract(data, '$.AMOUNT_USD')) AS total_spent_usd
        FROM TRANSACTIONS_USD
        GROUP BY transaction_type;
    """,
    "top_users": """
        SELECT
          json_extract(data, '$.USER_ID_HASHED') AS user,
          SUM(json_extract(data, '$.AMOUNT_USD')) AS total
        FROM TRANSACTIONS_USD
        GROUP BY user
        ORDER BY total DESC
        LIMIT 10;
    """,
    "avg_by_type": """
        SELECT
          json_extract(data, '$.TRANSACTION_TYPE') AS transaction_type,
          AVG(json_extract(data, '$.AMOUNT_USD')) AS avg_spent
        FROM TRANSACTIONS_USD
        GROUP BY transaction_type;
    """,
    "failed_by_country": """
        SELECT
          json_extract(data, '$.COUNTRY') AS country,
          COUNT(*) AS failed_transactions
        FROM TRANSACTIONS_FAILED
        GROUP BY country
        ORDER BY failed_transactions DESC;
    """
}

# Exécution des requêtes et affichage
for name, query in queries.items():
    print(f"\n📊 Résultat : {name.upper()}")
    df = pd.read_sql_query(query, conn)
    print(df)

conn.close()
