""" Imports Rebrickable parts list """

import sys
import csv
import sqlite3
import helpers

file = sys.argv[1]
notes = sys.argv[2]

conn = sqlite3.connect("dist/bricks.db")
cursor = conn.cursor()

for row in csv.DictReader(open(file)):
  print(row)
  cursor.execute("insert into part_transactions (part_num, color_id, quantity, notes) values (?, ?, ?, ?)", (row['Part'], row['Color'], row['Quantity'], notes))
conn.commit()
conn.close()
