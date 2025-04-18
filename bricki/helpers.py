import csv
import sqlite3
import code
import re


def norm_part(s):
    """
    >>> norm_part('BrIck 1x4')
    'Brick 1 x 4'
    >>> norm_part('Brick 1 x 4')
    'Brick 1 x 4'
    >>> norm_part(' Brick 1 x 4')
    'Brick 1 x 4'
    >>> norm_part('Brick 1x2x2')
    'Brick 1 x 2 x 2'
    >>> norm_part('b 1x2x2')
    'Brick 1 x 2 x 2'
    >>> norm_part('t 1x1')
    'Tile 1 x 1'
    >>> norm_part('s 2x1')
    'Slope 2 x 1'
    >>> norm_part('si 2x1')
    'Slope Inverted 2 x 1'
    >>> norm_part('4444pr0003')
    '4444Pr0003'
    """
    s = str(s).strip().title()
    s = re.sub(r"(\d+) *x *", "\\1 x ", s, flags=re.I)

    first_word = s.split(" ")[0]

    shortcuts = {
        "B": "Brick",
        "P": "Plate",
        "T": "Tile",
        "S": "Slope",
        "Si": "Slope Inverted",
    }

    if first_word in shortcuts.keys():
        s = " ".join([shortcuts[first_word]] + s.split(" ")[1:])

    return s


def norm_color(s):
    """
    >>> norm_color('red')
    'Red'
    >>> norm_color('Dark red')
    'Dark Red'
    >>> norm_color('dkred')
    'Dark Red'
    >>> norm_color('trred')
    'Trans-Red'
    >>> norm_color('trdkblue')
    'Trans-Dark Blue'
    >>> norm_color('rb')
    'Reddish Brown'
    >>> norm_color(' trdkblue')
    'Trans-Dark Blue'
    >>> norm_color('bley')
    'Light Bluish Gray'
    >>> norm_color('light grey')
    'Light Gray'
    >>> norm_color('Trans-Black')
    'Trans-Black'
    """
    s = str(s).lower().strip()

    shortcuts = [
        ("bley", "light bluish gray"),
        ("dbley", "dark bluish gray"),
        ("bg", "light bluish gray"),
        ("dbg", "dark bluish gray"),
        ("dkbley", "dark bluish gray"),
        ("rb", "reddish brown"),
    ]

    for original, new in shortcuts:
        if s == original:
            return new.title()

    ret = ""

    if s[0:2] == "tr" and s[0:5] != "trans":
        ret += "trans-"
        s = s[2:]

    if s[0:2] == "dk":
        ret += "dark "
        s = s[2:]

    s = s.replace("grey", "gray")
    ret += s
    ret = ret.title()
    return ret


def query(*args, as_dict=False, **kwargs):
    """
    >>> query("select id from colors limit 3")
    [(-1,), (0,), (1,)]
    """
    conn = sqlite3.connect("bricks.db")
    if as_dict:
        conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(*args, **kwargs)
    ret = list(cursor.fetchall())

    conn.commit()
    conn.close()

    return ret


def part_keywords(part):
    """
    >>> part_keywords('brick 1x4')
    ['Brick', '1 x 4']
    >>> part_keywords('slope curved 3x1')
    ['Slope', 'Curved', '3 x 1']
    >>> part_keywords('slope 1x1x2/3')
    ['Slope', '1 x 1 x 2/3']
    """
    part = norm_part(part)

    kws = []
    accumulator = []

    for kw in part.split(" "):
        if kw == "x" or re.match(r"\d", kw[0]):
            accumulator.append(kw)
        else:
            if accumulator:
                kws.append(" ".join(accumulator))
                accumulator = []
            kws.append(kw)

    if accumulator:
        kws.append(" ".join(accumulator))
        accumulator = []

    return kws


def search_part(needle, printed=False, duplo=False):
    """
    >>> search_part("3010")
    [('3010', 'Brick 1 x 4')]
    >>> search_part("Brick 1x4")[0]
    ('3010', 'Brick 1 x 4')
    >>> search_part("Tile 2x2")[0]
    ('3068b', 'Tile 2 x 2 with Groove')
    >>> search_part("Tile 1x3")[0]
    ('63864', 'Tile 1 x 3')
    >>> search_part("Tile 2x4")[0]
    ('87079', 'Tile 2 x 4 with Groove')
    >>> search_part("cheese slope")[0][0]
    '54200'
    >>> search_part("3794b")[0][0]
    '3794b'
    >>> search_part("Brick 2x6")[0][0]
    '2456'
    >>> search_part("Duplo Brick 2x6",duplo=True)[0][0]
    '2300'
    >>> search_part("3046")[0][0]
    '3046a'
    >>> search_part("erling")[0][0]
    '4070a'
    >>> search_part("slope 2x1")[0][0]
    '3040b'
    >>> search_part("slope 2x1")[1][0] != '3040a'
    True
    >>> search_part("plate 1x1 clip horiz")[0][0]
    '6019'
    >>> search_part("plate 1x2 arm up")[0][0]
    '88072'
    >>> search_part("4444pr0003")[0][0]
    '4444pr0003'
    >>> search_part("")
    []
    """
    if not needle:
        return []

    needle = norm_part(needle)

    shortcuts = {
        "Erling": "4070a",
        "Slope 2 x 1": "Slope 2 x 1 with Bottom Pin",
    }

    if needle in shortcuts.keys():
        needle = shortcuts[needle]

    base_part_num = needle.rstrip("abcdef")

    for part_num in [needle, base_part_num, base_part_num + "a", base_part_num + "b"]:
        exact_id_part = query(
            "select part_num, name from parts where part_num like :part_num",
            (part_num,),
        )

        if exact_id_part:
            return [exact_id_part[0]]

    # Handle common tiles correctly
    if needle in ["Tile 1 x 3"]:
        pass
    elif re.match(r"Tile \d+[ ]*x[ ]*\d+$", needle):
        needle += " with Groove"

    filter = ""

    if not printed:
        filter += "parts.name not like '%%print%%' and parts.part_num not like '%%pr%%' and "
    if not duplo:
        filter += "parts.part_cat_id != 4 and "  # For is the ID for Dulpo parts

    kws = ["%%%s%%" % kw for kw in part_keywords(needle)]

    values = tuple([needle] + kws)

    kw_clause = ("parts.name like ? and " * len(kws))[:-5]

    parts = query(
        """
            select canonical.part_num, canonical.name
            from parts
            join canonical_parts on canonical_parts.part_num = parts.part_num
            join parts as canonical on canonical_parts.canonical_part_num = canonical.part_num
            where %s (parts.part_num like :needle or (%s))
            group by canonical.part_num
            order by length(canonical.name) asc
        """ % (filter, kw_clause),
        values,
    )

    return list(parts)


def search_color(needle):
    """
    >>> search_color("Dark Blue")[0]
    (272, 'Dark Blue')
    >>> search_color("dkblue")[0]
    (272, 'Dark Blue')
    >>> search_color("bley")[0]
    (71, 'Light Bluish Gray')
    >>> search_color("trans-green")[0]
    (34, 'Trans-Green')
    """
    needle = norm_color(needle)
    needle_like = "%%%s%%" % needle

    colors = query(
        "select id, name from colors where (name like ? or id = ?) order by length(name) asc",
        (needle_like, needle),
    )

    return list(colors)


def search_set(needle):
    """
    >>> search_set("10193-1")[0]
    ('10193-1', 'Medieval Market Village')
    >>> search_set("medieval market village")[0]
    ('10193-1', 'Medieval Market Village')
    >>> search_set("31067")[0]
    ('31067-1', 'Modular Poolside Holiday')
    >>> search_set("8042")[0]
    ('8042-1', 'Universal Pneumatic Set')
    """
    needle_like = "%%%s%%" % needle

    if re.match(r"^\d+$", str(needle)):
        needle += "-1"

    sets = query(
        "select set_num, name from sets where (name like ? or set_num = ?) order by length(name) asc",
        (needle_like, needle),
    )

    return list(sets)


def add_part(part, color, quantity=1, notes=None):
    """ Adds part by inserting a new transation into the part_transactions table """
    part = search_part(part)[0][0]
    color = search_color(color)[0][0]

    query(
        "insert into part_transactions (part_num, color_id, quantity, notes) values (?, ?, ?, ?)",
        (part, color, quantity, notes),
    )


def update_bin(part, color, bin_id):
    """ Adds part by inserting a new transation into the part_transactions table """
    part = search_part(part)[0][0]
    color = search_color(color)[0][0]

    query(
        "insert or replace into part_bins (part_num, color_id, bin_id) values (?, ?, ?)",
        (part, color, bin_id),
    )


def get_part_total(part, color):
    """ Gets total element count in inventory """
    part = search_part(part)[0][0]
    color = search_color(color)[0][0]

    res = query(
        "select quantity from my_parts where part_num=? and color_id=?", (part, color)
    )

    return res[0][0]


def add_set(set, quantity=1, notes=None):
    set_num = search_set(set)[0][0]

    query(
        "insert into set_transactions (set_num, quantity, notes) values (?, ?, ?)",
        (str(set_num).strip(), int(quantity), notes),
    )


def add_set_parts(set_num, quantity=1):
    query(
        """
      insert into part_transactions (part_num, color_id, quantity, from_set_num)
      select part_num, color_id, quantity * ? as quantity, ? as from_set_num
      from set_parts
      where set_num = ?
    """,
        (int(quantity), str(set_num).strip(), str(set_num).strip()),
    )


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


if __name__ == "__main__":
    code.interact(banner="Bricki v0.1.0", local=locals())
