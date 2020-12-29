import json
import sqlite3
import http.client

conn = sqlite3.connect("dist/bricks.db")
cursor = conn.cursor()

http = http.client.HTTPSConnection("rebrickable.com")

for page in range(1, 290):
    print("Getting page %d..." % page)
    http.request(
        "GET",
        "/api/v3/lego/parts/?page=%d&page_size=100" % page,
        headers={"Authorization": "key QAfRgbiakP"},
    )

    res = http.getresponse()

    print("HTTP Status %s" % res.status)

    part_details = json.loads(res.read().decode("utf8"))

    for part in part_details["results"]:
        bricklink_id = part["external_ids"].get("BrickLink", [None])[0]
        brickowl_id = part["external_ids"].get("BrickOwl", [None])[0]
        ldraw_id = part["external_ids"].get("LDraw", [None])[0]
        lego_id = part["external_ids"].get("LEGO", [None])[0]

        cursor.execute(
            """
      insert or replace into part_details (
        part_num,
        bricklink_id,
        brickowl_id,
        ldraw_id,
        lego_id,
        part_url,
        part_img_url
      ) values (?, ?, ?, ?, ?, ?, ?)""",
            (
                part["part_num"],
                bricklink_id,
                brickowl_id,
                ldraw_id,
                lego_id,
                part["part_url"],
                part["part_img_url"],
            ),
        )

conn.commit()
conn.close()
