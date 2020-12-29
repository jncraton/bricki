import sqlite3

conn = sqlite3.connect("dist/bricks.db")
cursor = conn.cursor()

cursor.execute(
    """
  select part_transactions.part_num
  from part_transactions
  left outer join part_details on
    part_details.part_num = part_transactions.part_num
  where part_details.part_num is null
  group by part_transactions.part_num
"""
)

for part in list(cursor.fetchall()):
    cursor.execute(
        "select part_num from part_details where part_num=? or bricklink_id=? or ldraw_id=? or lego_id=?",
        (part[0], part[0], part[0], part[0]),
    )
    try:
        new_part_num = cursor.fetchall()[-1][0]
        print("Updating %s to %s" % (part[0], new_part_num))
        cursor.execute(
            "update part_transactions set part_num=? where part_num=?",
            (new_part_num, part[0]),
        )
    except IndexError:
        print("No ID for %s" % part[0])

conn.commit()
conn.close()
