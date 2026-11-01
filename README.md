<div align="center">

```
███╗   ███╗██████╗ ██╗███████╗
████╗ ████║██╔══██╗██║██╔════╝
██╔████╔██║██████╔╝██║███████╗
██║╚██╔╝██║██╔═══╝ ██║╚════██║
██║ ╚═╝ ██║██║     ██║███████║
╚═╝     ╚═╝╚═╝     ╚═╝╚══════╝
Missing Person Identification System
```

**AI-powered face matching to help bring missing people home.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0097A7?style=flat-square&logo=google&logoColor=white)](https://mediapipe.dev)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)

</div>

---

## 📖 The Problem

Hundreds of people — mostly children — go missing every day in India. When a sighting is reported, officers have to **manually compare photos**, sift through paperwork, and coordinate across stations. By the time a match is confirmed, the trail has often gone cold.

**MPIS automates the hardest part** — face matching — so officers can focus on action, not administration.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **AI Face Matching** | KNN on 1,404-dimensional face vectors with confidence % |
| 📸 **468-Point Face Mesh** | MediaPipe Face Landmarker — no manual tagging needed |
| 🎥 **Video Sightings** | Upload a video — unique faces extracted per frame automatically |
| 🗺️ **Live Case Map** | Dashboard map showing case density across India |
| 📧 **Email Alerts** | Auto-notifies complainant when a face match is confirmed |
| 🔐 **Role-Based Access** | Admin vs Officer permissions out of the box |
| 🌐 **Public Portal** | Mobile-friendly sighting submission — no login required |

---

## 🚀 A Case, Start to Finish

**Step 1 — Officer registers the missing person**

A family reports their child missing. An officer uploads a photo → AI instantly extracts a 468-point face mesh. No manual tagging.

**Step 2 — Dashboard tracks every open case**

Live counts of found vs not-found cases, and a map plotting case concentrations across India.

**Step 3 — Public submits a sighting**

Anyone can submit a photo through the public portal (no login). When an admin clicks **Match Cases**, the KNN model compares all sightings against all open cases. A close enough match → case flipped to **Found** → complainant notified by email.

**Step 4 — City map tells the bigger picture**

Admins see which cities have the most unresolved cases and track resolution rates over time.

---

## 🛠️ Getting Started

### 1. Clone & Install

```bash
git clone https://github.com/gaganmanku96/Finding-missing-person-using-AI.git
cd Finding-missing-person-using-AI
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

> **Gmail users:** Use an [App Password](https://myaccount.google.com/apppasswords), not your regular password.
> Go to: Google Account → Security → 2-Step Verification ON → App Passwords → Generate.

Load it in your email code:

```python
from dotenv import load_dotenv
import os

load_dotenv()

SMTP_HOST     = os.getenv("SMTP_HOST")
SMTP_PORT     = os.getenv("SMTP_PORT")
SMTP_USER     = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
```

### 3. Run the Portals

```bash
# Officer / Admin portal
streamlit run Home.py

# Public sighting submission portal
streamlit run mobile_app.py
```

The SQLite database and face landmarker model (~30 MB, auto-downloaded on first run) are created automatically.

---

## 🔑 Configuring Login Credentials

Credentials live in `login_config.yml` (git-ignored — never commit real credentials).

**Step 1 — Generate a bcrypt hash:**

```python
import bcrypt
print(bcrypt.hashpw(b"your_password", bcrypt.gensalt()).decode())
```

**Step 2 — Add the user to `login_config.yml`:**

```yaml
credentials:
  usernames:
    your_username:
      name: Your Display Name
      email: you@example.com
      city: Delhi
      area: Sector 1
      role: Admin           # Admin or Officer
      password: '$2b$12$...'
```

**Role permissions:**

| Role | Can Do |
|---|---|
| **Admin** | Register cases · View all cases · Trigger matching · Edit/Delete |
| **Officer** | Register cases · View own cases only |

---

## 🌱 Seeding Demo Data

### Step 1 — Download sample images

```bash
# Download ~2 images per celebrity into scripts/bulk_data/reported/
uv run scripts/download_celebrity_images.py --dest reported

# Or split across both folders
uv run scripts/download_celebrity_images.py --dest both
```

You can also drop your own images directly:
```
scripts/bulk_data/reported/       ← missing person cases
scripts/bulk_data/publicly_seen/  ← public sighting submissions
```

### Step 2 — Run the bulk upload

```bash
python scripts/bulk_upload.py
```

This will:
- Extract a face mesh from every image (skips undetectable faces)
- Generate realistic metadata (names, cities, Aadhaar numbers)
- Insert records into the SQLite database
- Copy images to `resources/` for display

```bash
# Custom officer username
python scripts/bulk_upload.py --officer your_username

# Reset and re-seed from scratch
sqlite3 sqlite_database.db "DELETE FROM registeredcases; DELETE FROM publicsubmissions;"
python scripts/bulk_upload.py
```

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| **UI** | Streamlit |
| **Face Detection** | MediaPipe Tasks (468-point 3D face mesh) |
| **Face Matching** | scikit-learn KNN (1,404-dim vectors) |
| **Database** | SQLModel + SQLite |
| **Map** | Folium |
| **Video Processing** | OpenCV |
| **Email** | smtplib + python-dotenv |

---

## ❓ FAQ

<details>
<summary><strong>Can I run this without an internet connection?</strong></summary>

The face landmarker model (~30 MB) is downloaded once on first run and cached locally. After that, both portals work fully offline.
</details>

<details>
<summary><strong>How accurate is the face matching?</strong></summary>

Accuracy depends heavily on photo quality. Front-facing, well-lit photos work best. The confidence score reflects KNN distance — higher means a stronger match.
</details>

<details>
<summary><strong>Can I add multiple officers?</strong></summary>

Yes. Add as many usernames as needed to `login_config.yml`. Each officer sees only their own registered cases; Admins see all.
</details>

<details>
<summary><strong>A city isn't showing on the map.</strong></summary>

The map uses a built-in city → coordinates lookup. If a city is missing, open an issue or add it to the `CITY_COORDS` dict in `Home.py`.
</details>

<details>
<summary><strong>Where is the data stored?</strong></summary>

Everything is in `sqlite_database.db` (git-ignored) in the project root. Images are stored as JPGs in `resources/` (also git-ignored). Nothing is sent to any external server.
</details>

<details>
<summary><strong>How do I reset the database?</strong></summary>

```bash
sqlite3 sqlite_database.db "DELETE FROM registeredcases; DELETE FROM publicsubmissions;"
```
Or simply delete `sqlite_database.db` — it will be recreated on next run.
</details>

<details>
<summary><strong>Can the public portal be hosted separately?</strong></summary>

Yes. `Home.py` and `mobile_app.py` are independent Streamlit apps that share only the SQLite database file. Point both to the same path and they work together.
</details>

---

## ⚠️ Disclaimer

All sample images used for demonstration were sourced from the internet solely for educational purposes. No claim of ownership is made. If you are the rights holder of any image and wish it removed, please open an issue and it will be taken down promptly.

This project does not store, distribute, or commercialise any personal images. Face data (landmark vectors) is used only locally for matching and is never shared with any third party.

---

<div align="center">

**Built with ❤️ to help bring missing people home.**

*Thanks to the [MediaPipe](https://mediapipe.dev/) team for the open-source face landmarker model.*

</div>
