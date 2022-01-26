import helpers
import json

path = "www/"

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
    element_bins.bin_id
  from my_parts
  join parts on parts.part_num=my_parts.part_num 
  join colors on colors.id=my_parts.color_id
  join canonical_parts on canonical_parts.part_num = my_parts.part_num
  left join part_bins as element_bins on canonical_parts.canonical_part_num=element_bins.part_num and my_parts.color_id=element_bins.color_id
  left join part_bins on canonical_parts.canonical_part_num=part_bins.part_num and part_bins.color_id=-1
  group by canonical_part_num, colors.id
  having sum(quantity) > 0
  order by sum(quantity) desc
  """
    )

with open(path + "elements.html", "w") as out:
    template = open('bricki/templates/elements.html').read()


    s = template.replace("{{ my_parts }}", json.dumps(my_parts))
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
            count(distinct element_bins.color_id),
            part_bins.section_id,
            part_bins.color_id,
            colors.rgb
          from my_parts
          join canonical_parts on canonical_parts.part_num = my_parts.part_num
          join parts on parts.part_num=canonical_part_num
          join part_bins on canonical_part_num=part_bins.part_num
          left join part_bins as element_bins on canonical_part_num=element_bins.part_num and element_bins.color_id=my_parts.color_id
          left join colors on colors.id = part_bins.color_id
          where part_bins.bin_id not null
          group by canonical_part_num, part_bins.color_id
          having sum(quantity) > 0
          order by part_bins.color_id!=-1, part_bins.bin_id, part_bins.section_id, parts.name asc
          """
    )

    template = open('bricki/templates/part.html').read()

    for part in parts:
        elements = [p for p in my_parts if p[4] == part[1]]

        with open(f"{path}{part[1]}.html", "w") as part_page:
            part_page.write(template.replace("{{ part }}", f"""
                <h1>{part[1]} {part[0]}</h1>
                <img src="images/{part[1]}.png">
                <ul>
                {''.join(["<li><b>" + str(e[2]) + "</b> in <b>" + e[0] + '</b>' + ((' stored in <b>' + str(e[6]) + '</b>') if e[6] else '') for e in elements])} 
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

        if p[7] == -1:
            style = "background: linear-gradient(0deg, rgba(255,0,0,1) 0%, rgba(255,255,0,1) 35%, rgba(0,255,255,1) 50%, rgba(0,0,255,1) 75%, rgba(255,0,255,1) 100%);"
        else:
            style = f"background-color:#{p[8]};"
 
        fig += f'<figure><a href="{p[1]}.html"><img style="{style}" src="images/{p[1]}.png" loading=lazy><figcaption>{p[1]} ({p[5]})</figcaption></a></figure>'

        return fig

    make_fig.in_group = False

    figures = [make_fig(p) for p in parts]

    template = open('bricki/templates/bins.html').read()

    s = template.replace("{{ figures }}", ''.join(figures))

    out.write(s)
