const express = require("express");
const mysql = require("mysql2/promise");

const app = express();
app.use(express.json());

const MYSQL_HOST = process.env.MYSQL_HOST || "mysql";
const MYSQL_USER = process.env.MYSQL_USER || "root";
const MYSQL_PASSWORD = process.env.MYSQL_PASSWORD || "rootpass";
const MYSQL_DB = process.env.MYSQL_DB || "datadb";

async function getConn() {
  return mysql.createConnection({
    host: MYSQL_HOST,
    user: MYSQL_USER,
    password: MYSQL_PASSWORD,
    database: MYSQL_DB
  });
}

app.post("/auth", async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ ok: false, message: "Missing username/password" });
  }

  try {
    const conn = await getConn();
    const [rows] = await conn.execute(
      "SELECT * FROM users WHERE username=? AND password=?",
      [username, password]
    );
    await conn.end();

    if (rows.length === 1) return res.json({ ok: true });

    return res.status(401).json({ ok: false, message: "Invalid credentials" });
  } catch (err) {
    return res.status(500).json({ ok: false, message: err.message });
  }
});

app.get("/health", (req, res) => res.json({ ok: true }));

app.listen(3000, () => console.log("auth-service running on port 3000"));
