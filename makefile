db = bricks.db
sqldump = dist/bricks.sql

all: $(db)
.PHONY: clean dumps

$(sqldump): $(db)
	sqlite3 $(db) .dump > $(sqldump)

$(db): .PHONY
	cd rebrickable-import-dumps && make clean && make DB=../$(db)

dumps:
	sqlite3 $(db) < scripts/dump.sql

rollback:
	@echo Resetting transactions to last committed dump
	git checkout dumps/part_transactions.csv
	git checkout dumps/set_transactions.csv
	sqlite3 $(db) < scripts/reset_transactions.sql

test:
	python3 -m doctest bricki/helpers.py

clean:
	rm -f $(sqldump)
	rm -f dumps/*
	rm -rf bricki/__pycache__
	rm -rf src/__pycache__
