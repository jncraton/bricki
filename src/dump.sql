.timer on
.mode csv

.output dumps/looseparts.csv
select colors.name, parts.name, sum(quantity), part_transactions.part_num, color_id
from part_transactions
left outer join parts on
  parts.part_num = part_transactions.part_num
left outer join colors on
  colors.id = part_transactions.color_id
group by part_transactions.part_num, colors.id
order by colors.name, parts.name;

.output dumps/parts.csv
select colors.name, parts.name, sum(quantity), my_parts.part_num, color_id
from my_parts
left outer join parts on
  parts.part_num = my_parts.part_num
left outer join colors on
  colors.id = my_parts.color_id
group by my_parts.part_num, colors.id
order by colors.name, parts.name;

.output dumps/sets.csv
select year, sets.name, set_transactions.set_num, sum(quantity)
from set_transactions
left outer join sets on
  sets.set_num = set_transactions.set_num
group by sets.set_num
order by year, sets.name;