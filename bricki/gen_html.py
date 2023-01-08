import helpers
import json

path = "www/"

sets = helpers.query(
"""
select
  year,
  set_transactions.set_num,
  name,
  sum(set_transactions.quantity)
from set_transactions
natural join sets
group by set_transactions.set_num
order by year desc
"""
)

with open(path + "sets.html", "w") as out:
    template = open('bricki/templates/sets.html').read()
    table = ""

    for s in sets:
        table += f"<tr><td>{'</td><td>'.join(map(str,s))}</td></tr>"

    s = template.replace("{{ sets }}", table)

    out.write(s)

colors = helpers.query(
"""
select 
colors.name
from my_parts
join colors on colors.id=my_parts.color_id
group by colors.name
order by colors.name
"""
)

color_options = [f'<option value="{c[0]}">' for c in colors]

my_parts = helpers.query(
        """
  select 
    colors.name,
    parts.name,
    sum(quantity),
    colors.id,
    canonical_part_num,
    part_bins.bin_id,
    element_bins.bin_id,
    part_categories.name
  from my_parts
  join parts on parts.part_num=my_parts.part_num 
  join colors on colors.id=my_parts.color_id
  join canonical_parts on canonical_parts.part_num = my_parts.part_num
  left join part_bins as element_bins on canonical_parts.canonical_part_num=element_bins.part_num and my_parts.color_id=element_bins.color_id
  left join part_bins on canonical_parts.canonical_part_num=part_bins.part_num and part_bins.color_id=-1
  left join part_categories on parts.part_cat_id = part_categories.id
  group by canonical_part_num, colors.id
  having sum(quantity) > 0
  order by sum(quantity) desc
  """
    )

with open(path + "elements.html", "w") as out:
    template = open('bricki/templates/elements.html').read()


    s = template.replace("'{{ my_parts }}'", json.dumps(my_parts))
    s = s.replace("{{ color_options }}", '\n'.join(color_options))

    out.write(s)

with open(path + "bins.html", "w") as out:
    parts = helpers.query(
        """
          select 
            parts.name,
            canonical_part_num,
            sum(quantity) as quantity,
            part_bins.bin_id,
            min(my_parts.color_id),
            count(distinct part_bins.color_id),
            part_bins.section_id,
            part_bins.color_id,
            colors.rgb,
            bins.sort_style
          from my_parts
          join canonical_parts on canonical_parts.part_num = my_parts.part_num
          join parts on parts.part_num=canonical_part_num
          left join part_bins on canonical_part_num=part_bins.part_num and (part_bins.color_id=-1 or part_bins.color_id=my_parts.color_id)
          left join part_bins as element_bins on canonical_part_num=element_bins.part_num and element_bins.color_id=my_parts.color_id
          left join bins on part_bins.bin_id == bins.bin_id
          left join colors on colors.id = part_bins.color_id
          group by canonical_part_num, part_bins.color_id
          having sum(quantity) > 0
          order by bins.sort_style == 'category' asc, bins.sort_style, part_bins.bin_id, part_bins.section_id, parts.name asc
          """
    )

    template = open('bricki/templates/part.html').read()

    part_seen = set()

    for part in parts:
        if not part[1] in part_seen and (part[7] == -1 or part[7] == None):
            part_seen.add(part[1])
        
            elements = [p for p in my_parts if p[4] == part[1]]

            sets = helpers.query("""
                select
                    set_transactions.set_num,
                    sum(set_parts.quantity * set_transactions.quantity) as q from set_transactions
                left outer join set_parts on
                    set_parts.set_num = set_transactions.set_num
                where part_num = :part_num
                group by set_transactions.set_num
                order by q desc""", {"part_num": part[1]})

            with open(f"{path}{part[1]}.html", "w") as part_page:
                part_page.write(template.replace("{{ part }}", f"""
                    <h1>{part[1]} {part[0]}</h1>
                    <img src="images/{part[1]}.png">
                    <h2>Storage</h2>
                    <ul>
                    <li><b>{sum([e[2] for e in elements])}</b> total
                    <li>Stored in <b>{part[3]}</b> if not stored by color
                    {''.join(["<li><b>" + str(e[2]) + "</b> in <b>" + e[0] + '</b>' + ((' stored in <b>' + str(e[6]) + '</b>') if e[6] else f' stored in {str(part[3])}') for e in elements])}
                    </ul>
                    <h2>Sets</h2>
                    <ul>
                    {''.join([f"<li>{s[1]} from {s[0]}" for s in sets])}
                    </ul>
                """))

    seen = set()
    sections = set()

    def make_fig(p):
        fig = ''

        if not p[3] in seen:
            bin = p[3].replace('-', ' ').replace('+',', ').title().replace('Xn','xN').replace('X','x')
            fig = f'</section><h1>{bin}</h1><section>'
            seen.add(p[3])

        if p[6] and not p[6] in sections:
            if make_fig.in_group:
                make_fig.in_group = False
                fig += f'</div>'
            make_fig.in_group = True
            fig += f'<div class=grouped>'
            sections.add(p[6])
            if p[9] == 'category':
                fig += f'<figure><figcaption>{p[6].replace("-"," ").title()}</figcaption></figure>'


        if p[7] == -1:
            style = 'class=multicolor'
        else:
            style = f'style="background-color:#{p[8]};"'

        if p[9] != 'category':
            fig += f'<figure><a href="{p[1]}.html"><img {style} src="images/{p[1]}.png" alt="{p[0]}" loading=lazy><figcaption>{p[1]}<br>{p[2]}  pcs</figcaption></a></figure>'

        return fig

    make_fig.in_group = False

    parts = [p for p in parts if p[3] and p[9] != 'unsorted']

    figures = [make_fig(p) for p in parts]

    template = open('bricki/templates/bins.html').read()

    s = template.replace("{{ figures }}", ''.join(figures))

    out.write(s)
