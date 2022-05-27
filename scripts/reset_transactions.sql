.timer on
.mode csv

pragma foreign_keys = 0;

delete from part_transactions;
delete from set_transactions;

.import data/part_transactions.csv part_transactions
.import data/set_transactions.csv set_transactions

update part_transactions set from_set_num = null where from_set_num = '';
update part_transactions set notes = null where notes = '';
update set_transactions set notes = null where notes = '';

delete from bins;
.import data/bins.csv bins

delete from part_bins;
.import data/part_bins.csv part_bins

delete from part_relationships where rel_type='M';
.import data/part_relationships.csv part_relationships
