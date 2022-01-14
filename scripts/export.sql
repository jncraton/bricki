.timer on
.mode csv

.output data/set_transactions.csv
select * from set_transactions;

.output data/part_transactions.csv
select * from part_transactions;

update part_bins set section_id=null where section_id='';
.output data/part_bins.csv
select * from part_bins where bin_id != '' order by bin_id, section_id, part_num;
