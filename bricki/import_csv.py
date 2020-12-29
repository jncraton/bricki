import csv
import sqlite3
import helpers

conn = sqlite3.connect("dist/bricks.db")
cursor = conn.cursor()

for row in csv.DictReader(
    open("/dropbox/LEGO/inventory/inventory.tsv"), dialect="excel-tab"
):
    cursor.execute(
        "insert into part_transactions (part_num, color_id, quantity) values (?, (select id from colors where name=?), ?)",
        (row["id"], row["color"], row["quantity"]),
    )
conn.commit()
conn.close()

original_total_parts = helpers.query("select sum(quantity) from my_parts")[0][0]

for row in csv.DictReader(open("rebrickable-sets.csv")):
    total_parts = helpers.query("select sum(quantity) from my_parts")[0][0]

    print(row, total_parts)
    assert total_parts == original_total_parts
    # Add set to set list and remove the parts from inventory
    # This is the inverse of parting out a set from inventory
    helpers.part_out(row["Set Number"], -int(row["Quantity"]))

# (old, new)
part_replacements = [
    ("203", "32474"),
    ("2453", "2453a"),
    ("2476", "2476a"),
    ("30237", "30237a"),
    ("30350", "30350b"),
    ("3048", "3062c"),
    ("3062", "3062b"),
    ("3063", "3063b"),
    ("32064", "32064b"),
    ("3678", "3678a"),
    ("3709b", "3709"),
    ("3747", "3747b"),
    ("3794", "3794b"),
    ("4032", "4032a"),
    ("4073", "6141"),
    ("4460", "4460b"),
    ("4856", "4856a"),
    ("551", "32086"),
    ("60475", "60475b"),
    ("60583", "60583b"),
    ("895", "58176"),
]

for part in part_replacements:
    helpers.query(
        "update part_transactions set part_num=? where part_num=?", (part[1], part[0])
    )
