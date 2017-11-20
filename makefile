db = dist/bricks.db
sqldump = dist/bricks.sql

all: $(db)
.PHONY: clean dumps

$(sqldump): $(db)
	sqlite3 $(db) .dump > $(sqldump)

$(db): tables/themes.csv tables/colors.csv tables/part_categories.csv tables/parts.csv tables/inventories.csv tables/sets.csv tables/inventory_parts.csv tables/inventory_sets.csv tables/part_relationships.csv src/rb_import/schema.sql src/rb_import/import.sql src/schema.sql
	sqlite3 $(db) < src/rb_import/schema.sql
	sqlite3 $(db) < src/rb_import/import.sql
	sqlite3 $(db) < src/schema.sql
	sqlite3 $(db) < src/rb_import/indices.sql
	#python3 src/insert_part_details.py
	python3 src/import_csv.py

tables/%.csv:
	curl --silent https://m.rebrickable.com/media/downloads/$(subst tables/,,$@) | tail -n +2 > $@

indices: $(db)
	sqlite3 $(db) < src/rb_import/indices.sql

dumps:
	sqlite3 $(db) < src/dump.sql

clean:
	rm -f $(db)
	rm -f $(sqldump)
	#rm -f tables/*