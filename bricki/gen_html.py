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
<input name=color />
<table id=results></table>

<script>
var my_parts = {{ my_parts }}

function search_part(q, color) {
  re = new RegExp(q.toLowerCase(),'ui')

  results = my_parts.filter((p) => (!color || p[0] == color) && (!q || re.test(p)))

  return results.slice(0,100)
}

document.querySelector('input[name=q]').addEventListener('input', update)
document.querySelector('input[name=color]').addEventListener('input', update)

function update() {
  let q = document.querySelector('input[name=q]').value
  let color = document.querySelector('input[name=color]').value
  results = search_part(q,color)

  let content = ''

  results.forEach((r) => {
    let img_url = 'https://m.rebrickable.com/media/parts/ldraw/' + r[3] + '/' + r[4] + '.png'
    content += `<tr><td><img src="${img_url}"></td><td>${r[2]}</td><td>${r[0]}</td><td>${r[1]}</td></tr>`
  })

  document.querySelector('#results').innerHTML = content
}

update()

</script>
</body>
</html>
"""

with open(path + "search.html", "w") as out:
    my_parts = helpers.query(
        """
  select 
    colors.name,
    parts.name,
    sum(quantity),
    colors.id,
    parts.part_num
  from my_parts
  join parts on parts.part_num=my_parts.part_num 
  join colors on colors.id=my_parts.color_id
  group by parts.part_num, colors.id
  order by quantity desc
  """
    )

    search = search.replace("{{ my_parts }}", json.dumps(my_parts))

    out.write(search)
