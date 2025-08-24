# T-Care — Thalassemia Patient Portal

**T-Care** is a prototype patient portal and donor-matching frontend backed by a FastAPI backend.
It includes features such as symptom logging, donor matching, bridge creation (donor relationships), QR code generation for emergency sharing, a simple forum, and an AI assistant (Vivra). The repo contains two main services:

* `backend` — FastAPI server providing REST endpoints for patients, donors, matching, emergency, chat, QR generation, etc.
* `frontend` — Static single-file HTML/Tailwind UI (and a React app scaffold) used to present patient dashboard, donor search, QR, chat, and forum pages.

This README explains how to run the project locally, and where to integrate backend outputs into the frontend pages.

---

## Quick summary

* Backend default base URL: `http://localhost:8000/api/v1`
* Frontend default served on Nginx: `http://localhost:3000` (or `http://localhost:80` depending on how you run it)
* Use Docker Compose to run both services together: `docker compose up --build` 

---

## Prerequisites

* Docker & Docker Compose (for production/dev environment)
* Node.js + npm (only if you want to run the React frontend locally)
* Python 3.10+ (for backend development)
* (Optional) curl / httpie / Postman for testing APIs

---

## Repo structure (high-level)

```
.
├── README.md
├── ai_knowledge
│   ├── blood_compatibility.json
│   └── thalassemia_data.json
├── backend
│   ├── Dockerfile
│   ├── __pycache__
│   ├── alembic
│   ├── app
│   ├── data
│   ├── main.py
│   ├── requirements.txt
│   ├── scripts
│   ├── start_backend.sh
│   └── test.db
├── data
│   └── hackathon_data.csv
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── docker-compose.yml
└── frontend
    ├── Dockerfile
    ├── build
    ├── nginx.conf
    ├── node_modules
    ├── package-lock.json
    ├── package.json
    ├── public
    ├── src
    └── start_frontend.sh
```

> Note: the repo contains both a static `t-care.html` (Tailwind single-file UI) and a React app scaffold. You can use the HTML file as the easiest quick frontend (no build step) but ensure `API_BASE` is pointing to the backend.

---

## Run with Docker Compose (recommended)

From repository root:

```bash
# build and start both services (frontend + backend)
docker compose up --build
```

This will:

* build backend image, start FastAPI app on host port `8000`
* build frontend image (Nginx) and serve the built frontend on host port `3000` (your compose has frontend mapping `3000:80`)

If there is an already-running container with the same name, stop and remove first:

```bash
docker compose down
# or manually remove containers
docker rm -f tcare-backend tcare-frontend || true
```

Then re-run `docker compose up --build`.

---

## Run services separately (dev)

### Backend (development)

From `backend` folder:

```bash
# create venv (optional)
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

# run uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

> If you see `ERROR: Error loading ASGI app. Could not import module "main".` ensure `app/main.py` exists and contains the FastAPI app instance (example `app = FastAPI()` and `include_router(...)`). If your entry file is `app/main.py`, run `uvicorn app.main:app`.

### Frontend (static HTML)

You can serve `public/t-care.html` with any static server. Easiest for quick development:

```bash
# Simple python server in frontend/public
cd frontend/public
python -m http.server 3000
# then visit http://localhost:3000/t-care.html
```

### Frontend (React dev server)

If you want the React app (src) dev server:

```bash
cd frontend
npm install
npm start
# dev server typically runs at http://localhost:3000
```

```bash
npm install react-hot-toast
# or install all deps
npm install
npm run build
```

---

## Important API endpoints (reference)

This is a short summary of the backend endpoints available in the `backend` service (paths are relative to `API_BASE`):

* `GET /patients/{patient_id}` — fetch patient profile
* `PUT /patients/{patient_id}` — update profile
* `POST /patients/{patient_id}/symptoms` — add symptom entry
* `GET /patients/{patient_id}/symptoms` — symptom history
* `POST /patients/{patient_id}/transfusion` — log transfusion
* `GET /donors` — list donors (filters via query params)
* `GET /donors/{donor_id}` — donor details
* `POST /matching/find-donors` — find donor matches (body: `{ patient_id, emergency, limit, distance_km?, blood_group? }`)
* `POST /matching/create-bridge` — create a patient→donor bridge (`{ patient_id, donor_id }`)
* `POST /matching/notify-donors` — notify donor(s) (`{ patient_id, donor_ids, message }`)
* `GET /qrcode/{data}` — generate QR code image (returns PNG stream)
* `POST /qrcode/{patient_id}/regenerate` — regenerate patient QR (if supported)
* `POST /chat/message` — send chat message to Vivra
* `GET /chat/suggestions` — fetch suggested prompts
* `GET /forum`, `POST /forum` — forum posts

> Use `curl` or Postman to test these endpoints. See the Testing section below.

---

## How the HTML frontend uses the backend 

If you are using the single-file `t-care.html` (Tailwind + vanilla JS), here are the places to add or update code so backend outputs are used:

1. **API base constant**

   * Locate the line near top:

     ```js
     const API_BASE = "http://localhost:8000/api/v1";
     ```
   * Change this to your correct backend URL (if different).

2. **Patient profile**

   * Function: `loadPatientProfile()` — call `GET ${API_BASE}/patients/{id}` and render patient fields (name, blood\_group, last\_transfusion, expected\_next\_transfusion, etc.).
   * Place: near the top `<script>`; call from `window.onload`.

3. **Donor matching**

   * Function(s): `loadMatches()` or `loadDonors()` — call `POST ${API_BASE}/matching/find-donors` with payload `{ patient_id, emergency, limit }` and render results into the donor list DOM.
   * Wire "Notify", "Create Bridge" and "Contact" buttons to:

     * `POST ${API_BASE}/matching/create-bridge` to create bridge
     * `POST ${API_BASE}/matching/notify-donors` to send message(s)

4. **QR Code**

   * Replace dummy QR generator UI with actual image source:

     ```html
     <img id="qrImg" src="" alt="QR" />
     ```

     And in JS:

     ```js
     async function loadQRCode(patientId, customMessage) {
       // If backend's QR endpoint encodes the data in path:
       // e.g. GET /api/v1/qrcode/{data} returns PNG image
       const encoded = encodeURIComponent(customMessage || patientId);
       const url = `${API_BASE}/qrcode/${encoded}`;
       document.getElementById('qrImg').src = url;
     }
     ```
   * For download: make a fetch to the PNG endpoint and create an object URL or link `a.download`.

5. **Notify / Bridge flow**

   * Use `fetch()` with `Content-Type: application/json` and handle JSON / HTTP errors.
   * Show success toasts or modal confirmations.

6. **CORS**

   * If frontend is served from a different origin (file://, [http://localhost:3000](http://localhost:3000), or docker-nginx at :3000), ensure FastAPI has CORS configured to allow that origin (or `allow_origins=["*"]` while developing).

---

## Testing endpoints with `curl`

Fetch patient:

```bash
curl -s http://localhost:8000/api/v1/patients/1 | jq
```

Find donors:

```bash
curl -s -X POST http://localhost:8000/api/v1/matching/find-donors \
  -H 'Content-Type: application/json' \
  -d '{"patient_id":"1","emergency":false,"limit":10}' | jq
```

Create bridge:

```bash
curl -s -X POST http://localhost:8000/api/v1/matching/create-bridge \
 -H 'Content-Type: application/json' \
 -d '{"patient_id":"1","donor_id":"donor123"}' | jq
```

Generate QR (returns PNG image):

```bash
# open in browser:
http://localhost:8000/api/v1/qrcode/Patient:1
# or download:
curl http://localhost:8000/api/v1/qrcode/Patient:1 -o qr.png
```


---

## Useful commands 

```bash
# docker compose
docker compose up --build
docker compose down

# remove a named container if conflict
docker rm -f tcare-frontend tcare-backend || true

# manually run backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# serve static HTML quickly
cd frontend/public
python -m http.server 3000

# react dev
cd frontend
npm install
npm start
```
