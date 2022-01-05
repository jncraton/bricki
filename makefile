db = bricks.db
sqldump = dist/bricks.sql

all: $(db)

.PHONY: clean dumps export rollback www

$(sqldump): $(db)
	sqlite3 $(db) .dump > $(sqldump)

$(db):
	cd rebrickable-sqlite && make clean && make DB=../$(db)
	sqlite3 $(db) < scripts/schema.sql
	sqlite3 $(db) < scripts/reset_transactions.sql

export: $(db)
	sqlite3 $(db) < scripts/export.sql

dumps:
	sqlite3 $(db) < scripts/dump.sql
	sqlite3 $(db) < scripts/dumpbynotes.sql
	sqlite3 $(db) < scripts/dumprecentparts.sql

rollback:
	@echo Resetting transactions to last committed dump
	git checkout data/part_transactions.csv
	git checkout data/set_transactions.csv
	sqlite3 $(db) < scripts/reset_transactions.sql

test:
	python3 -m doctest bricki/helpers.py
	python3 -m doctest bricki/cli.py

bins:
	python3 bricki/update_bins_from_common_parts.py

www: $(db)
	python3 bricki/gen_html.py www

run: $(db)
	python3 bricki/cli.py

web: $(db)
	FLASK_APP=bricki/web.py python3 -m flask run

clean:
	rm -f bricks.db
	rm -f $(sqldump)
	rm -f dumps/*
	rm -rf bricki/__pycache__
	rm -rf src/__pycache__
	rm -f www/search.html www/parts.html www/elements.html
	cd rebrickable-sqlite && make clean
