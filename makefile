db = bricks.db
sqldump = dist/bricks.sql

all: $(db)

.PHONY: clean dumps export rollback www

$(sqldump): $(db)
	sqlite3 $(db) .dump > $(sqldump)

$(db):
	cd rebrickable-import-dumps && make clean && make DB=../$(db)
	sqlite3 $(db) < scripts/schema.sql
	sqlite3 $(db) < scripts/reset_transactions.sql

export:
	sqlite3 $(db) < scripts/export.sql

dumps:
	sqlite3 $(db) < scripts/dump.sql
	sqlite3 $(db) < scripts/dumpbynotes.sql
	sqlite3 $(db) < scripts/dumprecentparts.sql

rollback:
	@echo Resetting transactions to last committed dump
	git checkout transactions/part_transactions.csv
	git checkout transactions/set_transactions.csv
	sqlite3 $(db) < scripts/reset_transactions.sql

test:
	python3 -m doctest bricki/helpers.py
	python3 -m doctest bricki/cli.py

www: $(db)
	python3 bricki/gen_html.py www

run:
	python3 bricki/cli.py

web:
	FLASK_APP=bricki/web.py python3 -m flask run

clean:
	rm -f bricks.db
	rm -f $(sqldump)
	rm -f dumps/*
	rm -rf bricki/__pycache__
	rm -rf src/__pycache__
	rm -f www/clean.html
	cd rebrickable-import-dumps && make clean
