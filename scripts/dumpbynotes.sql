.timer on
.mode csv

.output dumps/bynotes.csv
select 'part_num' as 'Part', 'color_id' as 'Color', 'quantity' as 'Quantity'
union
select part_transactions.part_num, color_id, sum(quantity)
from part_transactions
left outer join parts on
  parts.part_num = part_transactions.part_num
left outer join colors on
  colors.id = part_transactions.color_id
left outer join canonical_parts on
  canonical_parts.part_num = part_transactions.part_num
where notes="20180528 probricks small"
group by canonical_part_num, colors.id
having sum(quantity) > 0
order by Color, Part;
