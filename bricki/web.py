import json

from flask import Flask, jsonify

import helpers

app = Flask(__name__,static_folder="static/")

@app.route('/recent')
def recent():
    recent = helpers.query("""
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
    order by date desc limit 20""", as_dict=True)
    return jsonify([dict(r) for r in recent])

@app.route('/')
def static_file():
    return open("static/index.html").read()
