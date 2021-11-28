.timer on
.mode csv

.output data/set_transactions.csv
select * from set_transactions;

.output data/part_transactions.csv
select * from part_transactions;

.output data/part_bins.csv
select * from part_bins where bin_id != '' or size != '' order by bin_id, part_num;
