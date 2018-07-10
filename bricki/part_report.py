import helpers

print('<table>')

for part in helpers.query("""
select 
  colors.name as color_name,
  parts.name as part_name,
  "https://m.rebrickable.com/media/parts/ldraw/" || colors.id || "/" ||
      parts.part_num || ".png" as part_img_url,
  parts.part_num,
  sum(quantity) as quantity
from my_parts
join colors on colors.id=my_parts.color_id
join parts on my_parts.part_num=parts.part_num
group by color_name, part_name
order by color_name, part_name 
"""):
  print('<tr><td><img src="%s">%s %s (x%d)<td></tr>' % (part[2],part[0],part[1],part[4]))

print('</table>')
