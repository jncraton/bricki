import csv
import helpers

with open('dumps/common-parts.csv') as f:
    for b in csv.DictReader(f):
        helpers.query('insert or ignore into part_bins (part_num, bin_id) values (?,?)', (b['canonical_part_num'], b['bin_id']))
        helpers.query('update part_bins set bin_id = ? where part_num = ?', (b['bin_id'], b['canonical_part_num']))
