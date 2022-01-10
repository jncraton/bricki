import helpers
import urllib.request 
import os
from os.path import exists

# This script will overwrite existing images
# Images should be converted to 16 color 96x96 thumbnails after download

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
      join part_bins on canonical_part_num=part_bins.part_num and part_bins.color_id=-1
      left join part_bins as element_bins on canonical_part_num=element_bins.part_num and element_bins.color_id=my_parts.color_id
      where part_bins.bin_id not null
      group by canonical_part_num
      order by part_bins.bin_id, parts.name asc
      """
)

print(f"Downloading {len(parts)} images...")

for p in parts:
    filename = f'www/images/{p[1]}.png'

    try:
        os.mkdir('www/images/new')
    except:
        pass

    if not os.path.exists(filename):
        img = f'https://cdn.rebrickable.com/media/thumbs/parts/ldraw/{p[4] or 71}/{p[1]}.png/250x250p.png'
        try:
            urllib.request.urlretrieve(f'https://cdn.rebrickable.com/media/thumbs/parts/ldraw/71/{p[1]}.png/250x250p.png', f'www/images/new/{p[1]}.png')
        except:
            try:
                urllib.request.urlretrieve(f'https://cdn.rebrickable.com/media/thumbs/parts/ldraw/{p[4]}/{p[1]}.png/250x250p.png', f'www/images/new/{p[1]}.png')
            except:
                print(f'Error with {p[1]} {p[0]}')
