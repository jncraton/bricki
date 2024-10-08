import helpers
import urllib.request 
import os
from os.path import exists
from subprocess import run
import sys

# This script will overwrite existing images
# Images should be converted to 16 color 96x96 thumbnails after download

def get_filename(part):
    return f'www/images/{part[1]}.png'

def get_image(p, url=None): 
    if not os.path.exists(get_filename(p)):
        for color in ['71', '7', '72', '4', '8', p[4], 0]:
            try:
                urllib.request.urlretrieve(url or f'https://cdn.rebrickable.com/media/thumbs/parts/ldraw/{color}/{p[1]}.png/250x250p.png', get_filename(p))
                break
            except:
                pass
        else:
            print(f'Error with {p[1]} {p[0]}')
            return

        # Add transparency
        run(['convert',
            get_filename(p),
             '-resize', '96x96^',
             '-colorspace', 'Gray',
             '-auto-gamma',
             '-level', '0.5%,100%',
             '(', 
                '-clone', '0', 
                '-fill', '#999999', 
                '-colorize', '100', 
                '-black-threshold', '80%',
            ')',
             '(', 
                '-clone', '0,1', 
                '-compose', 'difference', 
                '-composite', 
                '-separate', 
                '+channel',
                '-evaluate-sequence', 'max',
            ')',
            '-delete', '1',
            '-alpha', 'off',
            '-compose', 'over',
            '-compose', 'copy_opacity',
            '-composite',
            get_filename(p)])

        # Compress PNG
        run(['pngquant', '--force', '--ext', '.png', '--ordered', '--speed', '1', '16', get_filename(p)])

        run(['advpng', '-z', '-4', get_filename(p)])

if len(sys.argv) == 3:
    # Program [part_id] [image_url]
    get_image(['Unknown', sys.argv[1], '', '', ''], sys.argv[2])
    exit()

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

needed = [p for p in parts if not os.path.exists(get_filename(p))]

print(f"{len(needed)} missing. Attempting download...")

from multiprocessing import Pool

with Pool(8) as pool:
    pool.map(get_image, needed)
