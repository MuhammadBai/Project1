from flask import Flask, render_template, request
import os
import requests
from pymongo import MongoClient

app = Flask(__name__)

AUTH_URL = os.getenv("AUTH_URL", "http://auth-service:3000/auth")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
MONGO_DB = os.getenv("MONGO_DB", "analyticsdb")

def auth_user(username, password):
    r = requests.post(AUTH_URL, json={"username": username, "password": password}, timeout=5)
    return r.status_code == 200

def read_stats():
    client = MongoClient(MONGO_URL)
    db = client[MONGO_DB]
    doc = db.stats.find({}, {"_id": 0}).limit(1)
    docs = list(doc)
    client.close()

    if len(docs) == 0:
        return None
    return docs[0]

@app.get("/")
def home():
    return render_template("index.html", error="")

@app.post("/results")
def results():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return render_template("index.html", error="Missing username/password")

    try:
        if not auth_user(username, password):
            return render_template("index.html", error="Login failed")

        stats = read_stats()
        if not stats:
            stats = {"count": 0, "min": None, "max": None, "avg": None}

        return render_template("results.html", stats=stats)
    except Exception as e:
        return render_template("index.html", error=str(e))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)

