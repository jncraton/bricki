import json

from flask import Flask, jsonify, request, redirect

import helpers

app = Flask(__name__, static_folder="static/")


@app.route("/recent")
def recent():
    recent = helpers.query(
        """
    select 
        quantity, 
        colors.name as color, 
        parts.name as part, 
        parts.part_num, 
        colors.id as color_id, 
        notes 
    from part_transactions 
    join colors on colors.id = part_transactions.color_id 
    join parts on parts.part_num = part_transactions.part_num 
    order by date desc limit 20""",
        as_dict=True,
    )
    return jsonify([dict(r) for r in recent])


@app.route("/search_part")
def search_part():
    return jsonify(
        [
            {"part_num": p[0], "part_name": p[1]}
            for p in helpers.search_part(request.args.get("q"))[:10]
        ]
    )


@app.route("/colors")
def colors():
    colors = helpers.query("select colors.name from colors")
    return jsonify([c[0] for c in colors])


@app.route("/add_part", methods=["POST"])
def add_part():
    helpers.add_part(
        request.form["part"],
        request.form["color"],
        request.form["quantity"],
        notes=None,
    )
    return ""


@app.route("/bins")
def bins():
    bins = helpers.query("""
        select colors.name, parts.name, bin_id, part_bins.part_num, part_bins.color_id
            from part_bins 
            join parts on part_bins.part_num = parts.part_num
            join colors on colors.id = part_bins.color_id
            order by colors.name asc, parts.name asc
    """)
    return jsonify(bins)


@app.route("/bins", methods=["POST"])
def update_bin():
    helpers.update_bin(
        request.form["part"],
        request.form["color"],
        request.form["bin_id"],
    )
    return redirect("/bins")


@app.route("/edit-bins")
def edit_bins():
    return open("static/edit-bins.html").read()


@app.route("/")
def static_file():
    return open("static/index.html").read()
