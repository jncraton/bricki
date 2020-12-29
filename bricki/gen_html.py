import helpers
import json

path = "www/"

search = """
<!doctype html>
<html>

<head>
  <meta charset="utf-8">
  <style>
  #results > * {
    height: 60px
  }
  img {
    height: 100%;
  }
  </style>
<head>

<body>

<input name=q />
<div id=results></div>

<script>
var my_parts = {{ my_parts }}

function search_part(q) {
  re = new RegExp(q.toLowerCase(),'ui')
  console.log(q,re)

  results = my_parts.filter((p) => re.test(p))

  return results.slice(0,10)
}

document.querySelector('input[name=q]').addEventListener('input', function(e) {
  results = search_part(e.target.value)

  el = document.querySelector('#results')
  el.innerHTML = ''

  results.forEach((r) => {
    let img_url = 'https://m.rebrickable.com/media/parts/ldraw/' + r[3] + '/' + r[4] + '.png'
    el.innerHTML += '<div><img src="' + img_url + '">' + r + '</div>'
  })
})

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
