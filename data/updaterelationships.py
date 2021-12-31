import csv

with open('stored-together.csv') as f:
    with open('part_relationships.csv', 'w') as out:
        for row in csv.reader(f):
            parent = row[1]

            for child in row[2:]:
                out.write(f"M,{child},{parent}\n")