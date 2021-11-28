.timer on
.headers on
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

.output dumps/uploadablelooseparts.csv
select 'AA_color_name', 'part_name', 'quantity', 'part_num', 'color_id', 'canonical_part'
union
select colors.name, parts.name, sum(quantity), part_transactions.part_num, color_id, canonical_part_num
from part_transactions
left outer join parts on
  parts.part_num = part_transactions.part_num
left outer join colors on
  colors.id = part_transactions.color_id
left outer join canonical_parts on
  canonical_parts.part_num = part_transactions.part_num
group by canonical_part_num, colors.id
having sum(quantity) > 0
order by colors.name, parts.name;

.output dumps/uploadablemissingparts.csv
select 'AA_color_name', 'part_name', 'quantity', 'part_num', 'color_id', 'canonical_part'
union
select colors.name, parts.name, -sum(quantity), part_transactions.part_num, color_id, canonical_part_num
from part_transactions
left outer join parts on
  parts.part_num = part_transactions.part_num
left outer join colors on
  colors.id = part_transactions.color_id
left outer join canonical_parts on
  canonical_parts.part_num = part_transactions.part_num
group by canonical_part_num, colors.id
having sum(quantity) < 0
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

.output dumps/common-elements.csv
select sum(quantity) as quantity, colors.name, parts.name, canonical_part_num
from my_parts
left outer join parts on
  parts.part_num = my_parts.part_num
left outer join colors on
  colors.id = my_parts.color_id
left outer join canonical_parts on
  canonical_parts.part_num = my_parts.part_num
group by canonical_part_num, colors.id
having sum(quantity) > 10
order by colors.name, sum(quantity) desc;

.output dumps/common-parts.csv
select sum(quantity) as quantity, parts.name, canonical_part_num
from my_parts
left outer join parts on
  parts.part_num = my_parts.part_num
left outer join canonical_parts on
  canonical_parts.part_num = my_parts.part_num
group by canonical_part_num
having sum(quantity) > 10
order by sum(quantity) desc;

.output dumps/partsources.csv
select colors.name, parts.name, quantity, part_transactions.part_num, color_id, canonical_part_num, from_set_num, notes
from part_transactions
left outer join parts on
  parts.part_num = part_transactions.part_num
left outer join colors on
  colors.id = part_transactions.color_id
left outer join canonical_parts on
  canonical_parts.part_num = part_transactions.part_num

union all

select 
  colors.name, parts.name, 
  sum(set_parts.quantity * set_transactions.quantity) as quantity,
  parts.part_num, colors.id, canonical_part_num, 'owned sets', ''
from set_transactions
left outer join set_parts on
  set_parts.set_num = set_transactions.set_num
left outer join parts on
  parts.part_num = set_parts.part_num
left outer join colors on
  colors.id = set_parts.color_id
left outer join canonical_parts on
  canonical_parts.part_num = set_parts.part_num
group by set_parts.part_num, set_parts.color_id
order by colors.name, parts.name;

.output dumps/sets.csv
select year, sets.name, set_transactions.set_num, sum(quantity)
from set_transactions
left outer join sets on
  sets.set_num = set_transactions.set_num
group by sets.set_num
order by year, sets.name;
