# Data Entry & Analytics Microservices

A small microservices app built with **Docker Compose**. Users log in and submit numeric values through one web app. An analytics service then calculates statistics on those values, and a second web app shows the results. Each part runs in its own container and talks to the others over the Docker network.

## Architecture

```
            ┌──────────────────┐
            │   auth-service   │  Node.js / Express  :3000
            │  (checks login)  │
            └───────▲───▲──────┘
                    │   │
   ┌────────────────┘   └─────────────────┐
   │                                      │
┌──┴───────────────┐                ┌─────┴────────────┐
│  enter-data-web  │                │ show-results-web │
│ Node.js / EJS    │                │ Python / Flask   │
│ :4000            │                │ :7000            │
└──────┬───────────┘                └─────▲────────────┘
       │ writes values                    │ reads stats
       ▼                                  │
┌──────────────┐   reads values   ┌───────┴──────────┐   writes stats   ┌──────────────┐
│  MySQL 8     │ ───────────────▶ │ analytics-service│ ───────────────▶ │  MongoDB 7   │
│  :3306       │                  │ Python / Flask   │                  │  :27017      │
└──────────────┘                  │ :5000            │                  └──────────────┘
                                  └──────────────────┘
```

| Service | Tech | Port | What it does |
|---|---|---|---|
| `auth-service` | Node.js, Express | 3000 | `POST /auth` checks a username and password against MySQL |
| `enter-data-web` | Node.js, Express, EJS | 4000 | Form to log in and submit a value, saved to MySQL |
| `analytics-service` | Python, Flask | 5000 | `GET /run` reads all values from MySQL, calculates count, min, max and average, and stores the result in MongoDB |
| `show-results-web` | Python, Flask | 7000 | Log in to view the latest statistics from MongoDB |
| `mysql` | MySQL 8.0 | 3306 | Stores users and submitted values (schema in `mysql/init.sql`) |
| `mongo` | MongoDB 7 | 27017 | Stores the calculated statistics |

Each service also has a `GET /health` endpoint, except the two web apps.

## Run it

Requires Docker and Docker Compose.

```bash
docker compose up --build
```

Then:

1. Open **http://localhost:4000** and submit a few values. Demo login: `student` / `pass123`.
2. Run the analytics: **http://localhost:5000/run**
3. Open **http://localhost:7000** and log in to see the results.

Stop everything with `docker compose down`.

## What this project shows

- Splitting an app into separate services with one job each
- Containerizing Node.js and Python services with Dockerfiles
- Connecting containers by service name over a Docker Compose network
- Using both a relational database (MySQL) and a document database (MongoDB)
- Configuring services with environment variables
- Parameterized SQL queries to prevent SQL injection

## Known limitations

This is a learning project, so some shortcuts were taken on purpose:

- Passwords are stored in plain text and the demo database password is in `docker-compose.yml`. A production version would hash passwords (for example with bcrypt) and load secrets from an `.env` file or Docker secrets.
- The analytics run is triggered manually. It could run on a schedule instead.
- `depends_on` only waits for containers to start, not for databases to be ready. Health checks would make startup more reliable.
