.timer on
.mode csv

.output dumps/bynotes.csv
.header on
select part_transactions.part_num as Part, color_id as Color, sum(quantity) as Quantity
from part_transactions
left outer join parts on
  parts.part_num = part_transactions.part_num
left outer join colors on
  colors.id = part_transactions.color_id
left outer join canonical_parts on
  canonical_parts.part_num = part_transactions.part_num
where notes="20180727-garage-sale"
group by canonical_parts.part_num, colors.id
having sum(quantity) > 0;
