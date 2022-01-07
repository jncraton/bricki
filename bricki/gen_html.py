import helpers
import json

path = "www/"

template = open('bricki/templates/elements.html').read()

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

with open(path + "elements.html", "w") as out:
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

    s = template.replace("{{ my_parts }}", json.dumps(my_parts))
    s = s.replace("{{ color_options }}", '\n'.join(color_options))

    out.write(s)
