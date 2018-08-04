.timer on
.mode csv

.output transactions/set_transactions.csv
select * from set_transactions;

.output transactions/part_transactions.csv
select * from part_transactions;

.output transactions/locations.csv
select * from locations;
