-- 1. Total dépensé par type de transaction
SELECT
  json_extract(data, '$.TRANSACTION_TYPE') AS transaction_type,
  SUM(json_extract(data, '$.AMOUNT_USD')) AS total_spent_usd
FROM TRANSACTIONS_USD
GROUP BY transaction_type;

-- 2. Classement des utilisateurs les plus dépensiers
SELECT
  json_extract(data, '$.USER_ID_HASHED') AS user,
  SUM(json_extract(data, '$.AMOUNT_USD')) AS total
FROM TRANSACTIONS_USD
GROUP BY user
ORDER BY total DESC
LIMIT 10;

-- 3. Montant moyen par type de transaction
SELECT
  json_extract(data, '$.TRANSACTION_TYPE') AS transaction_type,
  AVG(json_extract(data, '$.AMOUNT_USD')) AS avg_spent
FROM TRANSACTIONS_USD
GROUP BY transaction_type;

-- 4. Analyse des transactions “failed” par pays
SELECT
  json_extract(data, '$.COUNTRY') AS country,
  COUNT(*) AS failed_transactions
FROM TRANSACTIONS_FAILED
GROUP BY country
ORDER BY failed_transactions DESC;
