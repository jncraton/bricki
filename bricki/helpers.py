import csv
import sqlite3
import code
import re

def norm_name(s):
  """
  >>> norm_name('BrIck 1x4')
  'Brick 1 x 4'
  >>> norm_name('Brick 1 x 4')
  'Brick 1 x 4'
  >>> norm_name('Brick 1x2x2')
  'Brick 1 x 2 x 2'
  """
  s = s.title()
  s = re.sub('(\d+) *x *', '\\1 x ', s, flags=re.I)
  return s

def query(*args, **kwargs):
  """
  >>> query("select id from colors limit 3")
  [(-1,), (0,), (1,)]
  """
  conn = sqlite3.connect("dist/bricks.db")
  cursor = conn.cursor()

  cursor.execute(*args, **kwargs)
  ret = list(cursor.fetchall())

  conn.commit()
  conn.close()

  return ret

def search_part(needle, printed=False):
  """
  >>> search_part("3010")
  [('3010', 'Brick 1 x 4')]
  """
  needle = norm_name(needle)
  needle_like = '%%%s%%' % needle

  filter = ''

  if not printed:
    filter += " and name not like '%%print%%' and part_num not like '%%pr%%'"

  parts = query("select part_num, name from parts where (name like ? or part_num = ?) %s order by length(name) asc" % filter, (needle_like, needle))

  return parts

def search_color(needle):
  """
  >>> search_color("Dark Blue")[0]
  (272, 'Dark Blue')
  """
  needle = norm_name(needle)
  needle_like = '%%%s%%' % needle

  return query("select id, name from colors where (name like ? or id = ?) order by length(name) asc", (needle_like, needle))

def add_part(part, color, quantity=1, notes=''):
  """ Adds part by inserting a new transation into the part_transactions table """
  parts = search_part(part)[0][0]
  color = search_color(color)[0][0]
  
  query("insert into part_transactions (part_num, color_id, quantity, notes) values (?, ?, ?, ?)", (part, color, quantity, notes))

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