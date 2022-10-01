import helpers
import urllib.request 
import os
from os.path import exists
from subprocess import run

# This script will overwrite existing images
# Images should be converted to 16 color 96x96 thumbnails after download

try:
    os.mkdir('www/images/new')
except:
    pass

parts = helpers.query(
    """
      select 
        parts.name,
        canonical_part_num,
        sum(quantity) as quantity,
        part_bins.bin_id,
        min(my_parts.color_id),
        count(distinct element_bins.color_id)
      from my_parts
      join canonical_parts on canonical_parts.part_num = my_parts.part_num
      join parts on parts.part_num=canonical_part_num
      join part_bins on canonical_part_num=part_bins.part_num
      join bins on part_bins.bin_id = bins.bin_id
      left join part_bins as element_bins on canonical_part_num=element_bins.part_num and element_bins.color_id=my_parts.color_id
      where part_bins.bin_id not null and bins.sort_style != 'unsorted'
      group by canonical_part_num
      order by part_bins.bin_id, parts.name asc
      """
)

print(f"{len(parts)} total images...")

def get_filename(part):
    return f'www/images/{part[1]}.png'

def get_new_filename(part):
    return f'www/images/new/{part[1]}.png'

needed = [p for p in parts if not os.path.exists(get_filename(p))]

print(f"{len(needed)} missing. Attempting download...")

for p in needed:
    if not os.path.exists(get_filename(p)):
        try:
            urllib.request.urlretrieve(f'https://cdn.rebrickable.com/media/thumbs/parts/ldraw/71/{p[1]}.png/250x250p.png', f'www/images/new/{p[1]}.png')
        except:
            try:
                urllib.request.urlretrieve(f'https://cdn.rebrickable.com/media/thumbs/parts/ldraw/{p[4]}/{p[1]}.png/250x250p.png', f'www/images/new/{p[1]}.png')
            except:
                print(f'Error with {p[1]} {p[0]}')
                continue

        # Add transparency
        run(['convert',
            get_new_filename(p),
             '-resize', '96x96^',
             '-colorspace', 'Gray',
             '(', 
                '-clone', '0', 
                '-fill', '#999999', 
                '-colorize', '100', 
            ')',
             '(', 
                '-clone', '0,1', 
                '-compose', 'difference', 
                '-composite', 
                '-separate', 
                '+channel',
                '-evaluate-sequence', 'max',
                '-auto-level',
            ')',
            '-delete', '1',
            '-alpha', 'off',
            '-compose', 'over',
            '-compose', 'copy_opacity',
            '-composite',
            get_new_filename(p)])

        # Compress PNG
        run(['pngquant', '--force', '--ext', '.png', '--ordered', '--speed', '1', '16', get_new_filename(p)])

        run(['advpng', '-z', '-4', get_new_filename(p)])