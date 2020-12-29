import helpers

print("<table>")

for part in helpers.query(
    """
select 
  colors.name as color_name,
  parts.name as part_name,
  "https://m.rebrickable.com/media/parts/ldraw/" || colors.id || "/" ||
      parts.part_num || ".png" as part_img_url,
  parts.part_num,
  count(distinct set_parts.set_num) as num_sets,
  max(year) as year_to 
from set_parts
join sets on sets.set_num = set_parts.set_num
join parts on parts.part_num=set_parts.part_num 
join colors on colors.id=set_parts.color_id
where parts.name not like '%Technic%' and year > 2015 and theme_id=22 and num_parts < 100
group by parts.part_num, colors.id
having year_to=2017
order by num_sets desc 
limit 300
"""
):
    print(
        '<tr><td><img src="%s">%s %s (x%d)<td></tr>'
        % (part[2], part[0], part[1], part[4])
    )

print("</table>")
