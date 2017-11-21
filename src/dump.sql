.timer on
.mode csv

.output dumps/looseparts.csv
select colors.name, parts.name, sum(quantity), part_transactions.part_num, color_id, canonical_part_num
from part_transactions
left outer join parts on
  parts.part_num = part_transactions.part_num
left outer join colors on
  colors.id = part_transactions.color_id
left outer join canonical_parts on
  canonical_parts.part_num = part_transactions.part_num
group by canonical_part_num, colors.id
order by colors.name, parts.name;

.output dumps/nonsetparts.csv
select colors.name, parts.name, sum(quantity), part_transactions.part_num, color_id, canonical_part_num
from part_transactions
left outer join parts on
  parts.part_num = part_transactions.part_num
left outer join colors on
  colors.id = part_transactions.color_id
left outer join canonical_parts on
  canonical_parts.part_num = part_transactions.part_num
where from_set_num is null
group by canonical_part_num, colors.id
order by colors.name, parts.name;

.output dumps/parts.csv
select colors.name, parts.name, sum(quantity), my_parts.part_num, color_id, canonical_part_num
from my_parts
left outer join parts on
  parts.part_num = my_parts.part_num
left outer join colors on
  colors.id = my_parts.color_id
left outer join canonical_parts on
  canonical_parts.part_num = my_parts.part_num
group by canonical_part_num, colors.id
order by colors.name, parts.name;

.output dumps/partsources.csv
select colors.name, parts.name, quantity, part_transactions.part_num, color_id, canonical_part_num, from_set_num, notes
from part_transactions
left outer join parts on
  parts.part_num = part_transactions.part_num
left outer join colors on
  colors.id = part_transactions.color_id
left outer join canonical_parts on
  canonical_parts.part_num = part_transactions.part_num
order by colors.name, parts.name;

.output dumps/sets.csv
select year, sets.name, set_transactions.set_num, sum(quantity)
from set_transactions
left outer join sets on
  sets.set_num = set_transactions.set_num
group by sets.set_num
order by year, sets.name;

.output dumps/set_transactions.csv
select * from set_transactions;

.output dumps/part_transactions.csv
select * from part_transactions;