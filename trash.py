import sqlite3
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute(
  """
  SELECT
  COUNT(*)
  FROM models
  GROUP BY publisher
  """
)
rows = cursor.fetchall()

for row in rows:
  print(row)