db = bricks.db
sqldump = dist/bricks.sql

all: $(db)

.PHONY: $(db) clean dumps rollback

$(sqldump): $(db)
	sqlite3 $(db) .dump > $(sqldump)

$(db):
	cd rebrickable-import-dumps && make clean && make DB=../$(db)
	sqlite3 $(db) < scripts/schema.sql
	sqlite3 $(db) < scripts/reset_transactions.sql

dumps:
	sqlite3 $(db) < scripts/dump.sql
	sqlite3 $(db) < scripts/dumprecentparts.sql

rollback:
	@echo Resetting transactions to last committed dump
	git checkout dumps/part_transactions.csv
	git checkout dumps/set_transactions.csv
	sqlite3 $(db) < scripts/reset_transactions.sql

test:
	python3 -m doctest bricki/helpers.py
	python3 -m doctest bricki/cli.py

clean:
	rm -f bricks.db
	rm -f $(sqldump)
	rm -f dumps/looseparts.csv
	rm -f dumps/nonsetparts.csv
	rm -f dumps/parts.csv
	rm -f dumps/partsources.csv
	rm -f dumps/recentparts.csv
	rm -f dumps/sets.csv
	rm -f dumps/uploadablelooseparts.csv
	rm -f dumps/uploadablemissingparts.csv
	rm -rf bricki/__pycache__
	rm -rf src/__pycache__
	cd rebrickable-import-dumps && make clean
