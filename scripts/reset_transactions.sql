.timer on
.mode csv

pragma foreign_keys = 0;

delete from part_transactions;
delete from set_transactions;
delete from locations;

.import transactions/part_transactions.csv part_transactions
.import transactions/set_transactions.csv set_transactions
.import transactions/locations.csv locations

update part_transactions set from_set_num = null where from_set_num = '';
update part_transactions set notes = null where notes = '';
update set_transactions set notes = null where notes = '';