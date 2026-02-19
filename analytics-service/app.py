from flask import Flask, jsonify
import os
import mysql.connector
from pymongo import MongoClient

app = Flask(__name__)

MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "rootpass")
MYSQL_DB = os.getenv("MYSQL_DB", "datadb")

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
MONGO_DB = os.getenv("MONGO_DB", "analyticsdb")

def get_mysql_values():
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )
    cur = conn.cursor()
    cur.execute("SELECT value FROM entries;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [r[0] for r in rows]

def write_stats_to_mongo(stats):
    # make a clean dict so it can be JSON safely
    clean = dict(stats)
    clean.pop("_id", None)

    client = MongoClient(MONGO_URL)
    db = client[MONGO_DB]
    db.stats.delete_many({})
    db.stats.insert_one(clean)
    client.close()

@app.get("/run")
def run_analytics():
    values = get_mysql_values()

    if len(values) == 0:
        stats = {"count": 0, "min": None, "max": None, "avg": None}
    else:
        stats = {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values)
        }

    write_stats_to_mongo(stats)
    return jsonify({"ok": True, "stats": stats})

@app.get("/health")
def health():
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
