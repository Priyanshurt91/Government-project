<p align="center">
  <h1 align="center">🏛️ Seva Form AI</h1>
  <p align="center">
    <strong>AI-Powered Seva Kendra Form Filling Assistant</strong>
  </p>
  <p align="center">
    Automating government service form filling using OCR, Voice Recognition & NLP — built for Bharat 🇮🇳
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/Vite-7-646CFF?logo=vite&logoColor=white" />
  <img src="https://img.shields.io/badge/Tesseract-OCR-orange" />
  <img src="https://img.shields.io/badge/Whisper-Speech--to--Text-74aa9c?logo=openai&logoColor=white" />
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [API Endpoints](#-api-endpoints)
- [AI Pipelines](#-ai-pipelines)
- [Internationalization (i18n)](#-internationalization-i18n)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**Seva Form AI** is an intelligent form-filling assistant designed for **Seva Kendra** (Common Service Centers) across India. It leverages AI to automate the tedious process of manually filling government service application forms by:

- **Scanning identity documents** (Aadhaar, PAN cards, birth certificates) using OCR
- **Listening to voice input** in Hindi, English, or other regional languages using OpenAI Whisper
- **Extracting structured data** (name, DOB, address, Aadhaar number, PAN, etc.) using NLP-based entity extraction
- **Auto-filling forms** with intelligent field mapping

This dramatically reduces errors, saves time, and makes government services more accessible — especially for users with limited literacy or digital skills.

---

## ✨ Features

### 📄 Document Intelligence
- **Smart Document Detection** — Automatically classifies uploaded documents as Aadhaar, PAN, or generic
- **Multi-Strategy OCR** — Uses 4 different preprocessing strategies (CLAHE, direct color, sharpened grayscale, Aadhaar-specific) and merges results for maximum accuracy
- **Aadhaar Card Extraction** — Name, DOB/Year of Birth, father's name (S/O, D/O, W/O), gender, address with pincode, Aadhaar number
- **PAN Card Extraction** — PAN number, name, DOB, father's name
- **Address Parsing** — Breaks down Indian addresses into village/city, taluka, district, state, and pincode

### 🎤 Voice Form Filling
- **Speech-to-Text** powered by **OpenAI Whisper** (base model)
- **Multi-language Support** — Hindi, English, Marathi, and more
- **Transcribe or Translate** — Keep original language or auto-translate to English
- **Voice → Entities → Auto-filled Form** pipeline

### 🧠 Smart Entity Extraction
- Regex-based NLP extraction for: name, father's name, mother's name, DOB, gender, Aadhaar, PAN, mobile, email, caste, marital status, address components, registration number, place of birth
- Handles noisy OCR text, mixed languages, and various date formats
- Scoring-based name detection to pick the best candidate from OCR output

### 📝 Form Management
- Dynamic **Seva Kendra service catalog** (JSON-based)
- **Editable auto-filled forms** — users can review and correct AI-extracted data
- **Form submission** with unique ID and timestamp tracking
- **PDF generation** of completed application forms

### 🌐 Multi-language UI
- Full **internationalization (i18n)** with English 🇬🇧 and Hindi 🇮🇳
- Easily extendable to other regional languages

### 🖥️ Additional Pages
- **Admin Dashboard** — View and manage submissions
- **Chat Interface** — Conversational form filling
- **Blog, About & Contact** — Informational pages
- **Login & Register** — User authentication flow

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | REST API framework |
| **Uvicorn** | ASGI server |
| **Tesseract OCR** (pytesseract) | Optical Character Recognition |
| **OpenCV** (cv2) | Image preprocessing & enhancement |
| **Pillow** | Image handling |
| **OpenAI Whisper** | Speech-to-text (voice input) |
| **PyTorch** | Deep learning backend for Whisper |
| **NumPy** | Numerical operations for image processing |

### Frontend
| Technology | Purpose |
|---|---|
| **React 19** | UI framework |
| **Vite 7** | Build tool & dev server |
| **React Router v7** | Client-side routing |
| **react-i18next** | Internationalization |
| **jsPDF** / **html2pdf.js** / **html2canvas** | Client-side PDF export |
| **Tailwind CSS 4** | Utility-first styling |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite)                   │
│                                                                  │
│  Home ─► Service Selector ─► Document Upload ─► Editable Form   │
│                              └─► Voice Form ──┘                  │
│  Chat │ Admin Dashboard │ Blog │ About │ Contact │ Login/Register│
└────────────────────────────┬─────────────────────────────────────┘
                             │  HTTP API (REST)
┌────────────────────────────▼─────────────────────────────────────┐
│                      BACKEND (FastAPI)                            │
│                                                                  │
│  Routes:                                                         │
│  ├── /services          → Service catalog (JSON)                 │
│  ├── /documents/upload  → Document OCR pipeline                  │
│  ├── /api/voice-fill-form → Voice-to-form pipeline               │
│  ├── /api/submit-form   → Save submission                        │
│  └── /api/generate-pdf  → PDF generation                         │
│                                                                  │
│  AI Modules:                                                     │
│  ├── processor.py     → Smart doc detection + routing            │
│  ├── ocr.py           → Multi-strategy Tesseract OCR             │
│  ├── preprocess.py    → Image preprocessing (CLAHE, Otsu, etc.)  │
│  ├── entity_extractor.py → Regex NLP entity extraction           │
│  ├── speech.py        → Whisper speech-to-text                   │
│  ├── nlp.py           → Entity enhancement                      │
│  ├── form_mapper.py   → Entity-to-form field mapping             │
│  └── voice_form_pipeline.py → End-to-end voice pipeline          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
seva-form-ai/
├── backend/
│   ├── ai/                          # AI & ML modules
│   │   ├── ocr.py                   # Multi-strategy OCR (Aadhaar, PAN, generic)
│   │   ├── preprocess.py            # Image preprocessing pipelines
│   │   ├── entity_extractor.py      # NLP entity extraction (468 lines of regex magic)
│   │   ├── processor.py             # Smart document type detection & routing
│   │   ├── speech.py                # OpenAI Whisper speech-to-text
│   │   ├── nlp.py                   # Entity enhancement
│   │   ├── form_mapper.py           # Entity → form field mapping with aliases
│   │   └── voice_form_pipeline.py   # Voice → Text → Entities → Form
│   ├── app/
│   │   ├── main.py                  # FastAPI app setup & CORS config
│   │   ├── api.py                   # Legacy API routes
│   │   ├── routes/
│   │   │   ├── services.py          # GET /services — service catalog
│   │   │   ├── documents.py         # POST /documents/upload & /documents/generate-form
│   │   │   ├── voice.py             # POST /api/voice-fill-form
│   │   │   ├── submit.py            # POST /api/submit-form
│   │   │   └── pdf.py               # POST /api/generate-pdf
│   │   ├── data/
│   │   │   ├── services.json        # Service catalog definitions
│   │   │   ├── forms/               # Form templates (JSON)
│   │   │   ├── uploads/             # Uploaded documents (auto-created)
│   │   │   └── submissions/         # Saved form submissions (JSON)
│   │   ├── schemas/                 # Pydantic schemas
│   │   └── utils/                   # Utility functions
│   └── requirements.txt             # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                  # Route definitions
│   │   ├── main.jsx                 # App entry point
│   │   ├── i18n.js                  # i18next configuration
│   │   ├── api/                     # API client functions
│   │   ├── pages/
│   │   │   ├── Home.jsx             # Landing page with hero section
│   │   │   ├── ServiceSelector.jsx  # Browse available services
│   │   │   ├── DocumentUpload.jsx   # Upload & OCR documents
│   │   │   ├── FormPage.jsx         # Auto-filled editable form
│   │   │   ├── VoiceForm.jsx        # Voice-based form filling
│   │   │   ├── Chat.jsx             # Conversational interface
│   │   │   ├── AdminDashboard.jsx   # Admin panel
│   │   │   ├── Login.jsx            # User login
│   │   │   ├── Register.jsx         # User registration
│   │   │   ├── Blog.jsx             # Blog page
│   │   │   ├── About.jsx            # About page
│   │   │   └── Contact.jsx          # Contact page
│   │   ├── components/
│   │   │   ├── Header.jsx           # Navigation header
│   │   │   ├── Footer.jsx           # Site footer
│   │   │   ├── Layout.jsx           # Page layout wrapper
│   │   │   ├── EditableForm.jsx     # Editable auto-filled form component
│   │   │   ├── AutoFilledForm.jsx   # Read-only form display
│   │   │   ├── MicRecorder.jsx      # Microphone recording component
│   │   │   └── VoiceRecorder.jsx    # Voice recording component
│   │   ├── styles/                  # CSS stylesheets
│   │   └── locales/
│   │       ├── en/translation.json  # English translations
│   │       └── hi/translation.json  # Hindi translations
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** & **npm**
- **Tesseract OCR** installed on your system
  - Windows: Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
  - Linux: `sudo apt install tesseract-ocr`
  - macOS: `brew install tesseract`
- **FFmpeg** (required by OpenAI Whisper for audio processing)
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
  - Linux: `sudo apt install ffmpeg`
  - macOS: `brew install ffmpeg`

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/seva-form-ai.git
cd seva-form-ai
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn app.main:app --reload --port 8000
```

The API will be available at **http://localhost:8000**. Visit **http://localhost:8000/docs** for interactive Swagger documentation.

### 3. Frontend Setup

```bash
# Navigate to frontend (in a new terminal)
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The frontend will be available at **http://localhost:5173**.

---

## 📡 API Endpoints

### Services

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/services` | List all available Seva Kendra services |
| `GET` | `/services/{service_id}` | Get details for a specific service |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/documents/upload` | Upload a document for OCR processing |
| `POST` | `/documents/generate-form` | Generate auto-filled form from extracted entities |

### Voice

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/voice-fill-form` | Upload audio → transcribe → extract entities → fill form |

### Submission

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/submit-form` | Submit a completed form (saved as JSON) |

### PDF

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/generate-pdf` | Generate a PDF from form data |

---

## 🧪 AI Pipelines

### Document Processing Pipeline

```
Image Upload
    │
    ▼
Quick OCR Pass (detect doc type)
    │
    ├── Aadhaar Card ──► Multi-strategy OCR (4 passes) ──► Aadhaar Entity Extractor
    ├── PAN Card ──────► PAN-specific preprocessing ─────► Generic Entity Extractor
    └── Generic ───────► Generic OCR ────────────────────► Generic Entity Extractor
    │
    ▼
Entity-to-Form Mapping (alias-based)
    │
    ▼
Auto-filled Form
```

### Voice Form Filling Pipeline

```
Audio Recording (.m4a / .wav / .webm)
    │
    ▼
OpenAI Whisper (transcribe / translate)
    │
    ▼
Raw Text (Hindi / English / Mixed)
    │
    ▼
Entity Extraction (regex NLP)
    │
    ▼
Entity Enhancement (NLP)
    │
    ▼
Form Mapping
    │
    ▼
Auto-filled Seva Kendra Form
```

---

## 🌍 Internationalization (i18n)

The app supports **English** and **Hindi** out of the box using `react-i18next`.

| Language | File |
|----------|------|
| English 🇬🇧 | `frontend/src/locales/en/translation.json` |
| Hindi 🇮🇳 | `frontend/src/locales/hi/translation.json` |

To add a new language:
1. Create a new folder under `frontend/src/locales/<language-code>/`
2. Add a `translation.json` file with all required keys
3. Register the new language in `frontend/src/i18n.js`

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Built with ❤️ for making government services accessible to all
</p>
