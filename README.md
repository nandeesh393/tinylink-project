
# TinyLink — URL Shortener


---

## ⚙️ Setup Instructions


```bash
1️⃣ Create virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# OR
.venv\Scripts\activate           # Windows

2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Configure environment variables

Copy .env.example to .env:

cp .env.example .env


Edit .env with your database credentials:

DEBUG=True
SECRET_KEY=replace-me
DATABASE_URL=postgres://postgres:yourPassword@localhost:5432/tinylinkdb
BASE_URL=http://localhost:8000
PORT=8000

4️⃣ Create PostgreSQL Database

If you have PostgreSQL CLI:

psql -U postgres -c "CREATE DATABASE tinylinkdb;"


Or use pgAdmin GUI → Create Database → name it tinylinkdb.

5️⃣ Apply migrations
python manage.py makemigrations
python manage.py migrate

6️⃣ Run server
python manage.py runserver 0.0.0.0:8000


Now open:

http://localhost:8000/healthz


You should see:

{ "ok": true, "version": "1.0" }

🔗 API Endpoints
✔ GET /healthz
200 OK
{ "ok": true, "version": "1.0" }

✔ POST /api/links (Create short link)
Request Body:
{
  "target": "https://google.com",
  "code": "abc123"   // optional
}

Rules:

target → required, must be http/https URL

code → optional, must match ^[A-Za-z0-9]{6,8}$

If no code provided → system generates one via nanoid

Responses:

201 CREATED → success

400 BAD REQUEST → invalid URL/code

409 CONFLICT → code already exists

✔ GET /api/links

Returns all non-deleted links:

[
  {
    "code": "abc123",
    "target": "https://google.com",
    "clicks": 2,
    "created_at": "...",
    "last_clicked": "..."
  }
]

✔ GET /api/links/<code>

Returns stats for a single link.

404 if deleted or not found.

✔ DELETE /api/links/<code>

Soft-deletes the link.

Response:

{ "ok": true }


After deleting → GET /<code> should return 404.

✔ GET /<code> (Redirect Route)

Behavior:

If link exists and not deleted:

Returns 302 Redirect to target URL

Atomically increments clicks

Updates last_clicked

Else → returns 404

🧪 Curl Tests Script (curl_tests.sh)

Make executable:

chmod +x curl_tests.sh


Run:

./curl_tests.sh


Script automatically tests:

Health endpoint

Create link

Fetch stats

Redirect (302)

Click increment

Delete link

Redirect fails after delete

📦 .env.example

DEBUG=True
SECRET_KEY=replace-me-in-production

# Postgres DATABASE_URL; format:
# postgresql://USER:PASSWORD@HOST:PORT/DBNAME
DATABASE_URL=postgres://postgres:yourPassword@localhost:5432/tinylinkdb

BASE_URL=http://localhost:8000
PORT=8000
