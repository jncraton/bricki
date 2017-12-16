import csv
import sqlite3
import code

def query(*args, **kwargs):
  conn = sqlite3.connect("dist/bricks.db")
  cursor = conn.cursor()

  cursor.execute(*args, **kwargs)
  ret = list(cursor.fetchall())

  conn.commit()
  conn.close()

  return ret

def search(needle, printed=False):
  needle = '%%%s%%' % needle

  filter = ''

  if not printed:
    filter += " and name not like '%%print%%' and part_num not like '%%pr%%'"

  parts = query("select part_num, name from parts where (name like ? or part_num like ?) %s order by length(name) asc" % filter, (needle, needle))

  parts.sort(key = lambda p: len(p[1]))

  for part in parts:
    print("%s (%s)" % (part[1], part[0]))  

  return None if len(parts) != 1 else parts[0][0]

def part(num):
  part = query("select part_num, name from parts where part_num = ?", (num,))[0]

  print("%s (%s)" % (part[1], part[0]))  

def add_part(part, color, quantity):
  """ TODO """
  query("insert into part_transactions (part_num, color_id, quantity) values (?, ?, ?)", (part, color, quantity)) 

def add_set(set_num, quantity=1):
  query("insert into set_transactions (set_num, quantity) values (?, ?)",
    (str(set_num).strip(), int(quantity)))

def add_set_parts(set_num, quantity=1):
  query("""
      insert into part_transactions (part_num, color_id, quantity, from_set_num)
      select part_num, color_id, quantity * ? as quantity, ? as from_set_num
      from set_parts
      where set_num = ?
    """, (int(quantity), str(set_num).strip(), str(set_num).strip()))

def part_out(set_num, quantity):
  """ Removes quantity sets and adds parts from that many sets """

  add_set(set_num, -int(quantity))
  add_set_parts(set_num, int(quantity))

def scrub_set(set_num):
  """ Removes all traces of set from sets and parts"""
  query("delete from set_transactions where set_num=?", (set_num,))
  query("delete from part_transactions where from_set_num=?", (set_num,))

def clear():
  query("delete from set_transactions")
  query("delete from part_transactions")

if __name__ == '__main__':
  code.interact(banner="Bricki v0.1.0", local=locals())