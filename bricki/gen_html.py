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
  table {
    border-collapse: collapse;
  }
  td {
    padding: 0px 18px;
    border:1px solid #ddd;
  }
  </style>
</head>

<body>

<label>Search <input name=q /></label>
<label>Part <input name=part /></label>
<label>Color <input name=color list=colors /></label>
<label>Min Quantity <input name=minqty value=0 /></label>
<label>Group by Part <input name=groupcolors type=checkbox /></label>

<datalist id=colors>    
{{ color_options }}
</datalist>

<section><p>Unique: <span id=unique></span> Total quantity: <span id=count></span></p></section>

<table>
<thead>
<tr>
<th></th>
<th>Part</th>
<th>Quantity</th>
<th>Color</th>
<th>Name</th>
<th>Locations</th>
</tr>
</thead>
<tbody id=results>
</tbody>
</table>

<script>
const my_parts = {{ my_parts }}

function search_part(q, color, part, min_qty) {
  const re = new RegExp(q.toLowerCase(),'ui')

  let results = my_parts.filter((p) => (!part || p[4] == part) && (!color || p[0] == color) && (!q || re.test(p[1])))

  if (!color && document.querySelector('[name=groupcolors]').checked) {
      let parts = results.reduce((storage, el) => {
        let group = el[4]
        if (!storage[group]) {
          storage[group] = [...el]
          storage[group][0] = 0
        } else {
          storage[group][2] += el[2]
        }
        storage[group][0] += 1
        storage[group][3] = 71
        return storage
      }, {})

      results = Object.values(parts).reduce((p, c) => {p.push(c); return p}, [])
  }

  results = results.filter((p) => (!min_qty || p[2] >= min_qty))

  results = results.sort((a,b) => {return a[2] < b[2]})

  return results
}

function update() {
  let q = document.querySelector('input[name=q]').value
  let color = document.querySelector('input[name=color]').value
  let part = document.querySelector('input[name=part]').value
  let min_qty = document.querySelector('input[name=minqty]').value

  let results = search_part(q,color,part,min_qty)

  let count = results.reduce((p, c) => {return c[2] + p}, 0)
  document.getElementById('count').textContent = count

  let unique = results.reduce((p, c) => {return 1 + p}, 0)
  document.getElementById('unique').textContent = unique

  let content = ''

  results.slice(0,100).forEach((r) => {
    let img_url = 'https://m.rebrickable.com/media/parts/ldraw/' + r[3] + '/' + r[4] + '.png'
    content += `<tr><td><img src="${img_url}"></td><td>${r[4]}</td><td>${r[2]}</td><td>${r[0]}</td><td>${r[1]}</td><td>${r[5] || ''} ${r[6] ? '(Also sorted by element)' : ''}</td></tr>`
  })

  document.querySelector('#results').innerHTML = content
}

document.querySelector('input[name=q]').addEventListener('input', update)
document.querySelector('input[name=part]').addEventListener('input', update)
document.querySelector('input[name=color]').addEventListener('input', update)
document.querySelector('input[name=minqty]').addEventListener('input', update)
document.querySelector('input[name=groupcolors]').addEventListener('input', update)

update()

</script>
</body>
</html>
"""

colors = helpers.query(
"""
select 
colors.name
from my_parts
join colors on colors.id=my_parts.color_id
group by colors.name
order by colors.name
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
