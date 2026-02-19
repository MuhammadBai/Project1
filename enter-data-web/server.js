const express = require("express");
const mysql = require("mysql2/promise");

const app = express();
app.set("view engine", "ejs");
app.use(express.urlencoded({ extended: true }));

const AUTH_URL = process.env.AUTH_URL || "http://auth-service:3000/auth";

const MYSQL_HOST = process.env.MYSQL_HOST || "mysql";
const MYSQL_USER = process.env.MYSQL_USER || "root";
const MYSQL_PASSWORD = process.env.MYSQL_PASSWORD || "rootpass";
const MYSQL_DB = process.env.MYSQL_DB || "datadb";

async function authUser(username, password) {
  // Node 20 has fetch, so this works in the container
  const res = await fetch(AUTH_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });
  return res.ok;
}

async function insertValue(username, value) {
  const conn = await mysql.createConnection({
    host: MYSQL_HOST,
    user: MYSQL_USER,
    password: MYSQL_PASSWORD,
    database: MYSQL_DB
  });

  await conn.execute(
    "INSERT INTO entries (username, value) VALUES (?, ?)",
    [username, value]
  );

  await conn.end();
}

app.get("/", (req, res) => {
  res.render("index", { success: "", error: "" });
});

app.post("/submit", async (req, res) => {
  const { username, password, value } = req.body;
  const num = Number(value);

  if (!username || !password || Number.isNaN(num)) {
    return res.render("index", { success: "", error: "Invalid input." });
  }

  try {
    const ok = await authUser(username, password);
    if (!ok) return res.render("index", { success: "", error: "Login failed." });

    await insertValue(username, num);
    return res.render("index", { success: "Saved to MySQL ✅", error: "" });
  } catch (err) {
    return res.render("index", { success: "", error: "Server error: " + err.message });
  }
});

app.listen(4000, () => console.log("enter-data-web running on port 4000"));

