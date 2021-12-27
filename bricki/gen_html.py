import helpers
import json

path = "www/"

search = """
<!doctype html>
<html>

<head>
  <meta charset="utf-8">
  <style>
  img {
    height: 64px;
  }
  </style>
<head>

<body>

<input name=q />
<input name=color list=colors />

<datalist id=colors>    
{{ color_options }}
</datalist>

<section><p>Total quantity: <span id=count></span></p></section>

<table id=results></table>

<script>
var my_parts = {{ my_parts }}

function search_part(q, color) {
  re = new RegExp(q.toLowerCase(),'ui')

  results = my_parts.filter((p) => (!color || p[0] == color) && (!q || re.test(p)))

  return results
}

document.querySelector('input[name=q]').addEventListener('input', update)
document.querySelector('input[name=color]').addEventListener('input', update)

function update() {
  let q = document.querySelector('input[name=q]').value
  let color = document.querySelector('input[name=color]').value
  results = search_part(q,color)

  let count = results.reduce((p, c) => {return c[2] + p}, 0)
  document.getElementById('count').textContent = count

  let content = ''

  results.slice(0,100).forEach((r) => {
    let img_url = 'https://m.rebrickable.com/media/parts/ldraw/' + r[3] + '/' + r[4] + '.png'
    content += `<tr><td><img src="${img_url}"></td><td>${r[4]}</td><td>${r[2]}</td><td>${r[0]}</td><td>${r[1]}</td><td>${r[5] || ''} ${r[6] ? '(Also sorted by element)' : ''}</td></tr>`
  })

  document.querySelector('#results').innerHTML = content
}

update()

</script>
</body>
</html>
"""

colors = helpers.query(
"""
select 
colors.name
from colors
"""
)

color_options = [f'<option value="{c[0]}">' for c in colors]

with open(path + "elements.html", "w") as out:
    my_parts = helpers.query(
        """
  select 
    colors.name,
    parts.name,
    sum(quantity),
    colors.id,
    parts.part_num,
    part_bins.bin_id,
    part_bins.size
  from my_parts
  join parts on parts.part_num=my_parts.part_num 
  join colors on colors.id=my_parts.color_id
  left join part_bins on parts.part_num=part_bins.part_num
  group by parts.part_num, colors.id
  having sum(quantity) > 0
  order by sum(quantity) desc
  """
    )

    s = search.replace("{{ my_parts }}", json.dumps(my_parts))
    s = s.replace("{{ color_options }}", '\n'.join(color_options))

    out.write(s)

with open(path + "parts.html", "w") as out:
    my_parts = helpers.query(
        """
  select 
    colors.name,
    parts.name,
    sum(quantity),
    colors.id,
    parts.part_num,
    part_bins.bin_id,
    part_bins.size
  from my_parts
  join parts on parts.part_num=my_parts.part_num 
  join colors on colors.id=my_parts.color_id
  left join part_bins on parts.part_num=part_bins.part_num
  group by parts.part_num
  having sum(quantity) > 0
  order by sum(quantity) desc
  """
    )

    s = search.replace("{{ my_parts }}", json.dumps(my_parts))
    s = s.replace("{{ color_options }}", '\n'.join(color_options))

    out.write(s)
