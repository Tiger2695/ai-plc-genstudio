# AI PLC-GenStudio

> AI-Powered PLC Programming Assistant for Delta AS228 R/T

## Overview

AI PLC-GenStudio is an AI-assisted engineering application that converts natural language functional requirements into PLC ladder logic for the Delta AS228 R/T platform.

The application integrates AI-assisted code generation, hardware-aware validation, automatic PLC tag allocation, safety auditing, and graphical ladder rendering into a unified engineering workflow.

Designed for internal R&D use, the software assists engineers in reducing repetitive programming effort while improving consistency during PLC application development.

---

## Features

- AI-Assisted Ladder Logic Generation
- Hardware-Aware Validation
- Industrial Safety Audit
- Automatic PLC Tag Allocation
- SVG-Based Ladder Rendering
- Engineering Report Generation
- PDF Export
- PNG Export

---

## Workflow

```text
Natural Language Prompt
        │
        ▼
AI Processing
        │
        ▼
PLC JSON Generation
        │
        ▼
Hardware Validation
        │
        ▼
Safety Audit
        │
        ▼
Tag Allocation
        │
        ▼
Ladder Rendering
        │
        ▼
Engineering Report
```

---

## Technology Stack

Frontend
- Streamlit

Backend
- FastAPI

Language
- Python

AI
- Google Gemini

Rendering
- SVG

Target Hardware
- Delta AS228 R/T

---

## Project Structure

```text
AI-PLC-GenStudio/

├── app.py
├── backend/
├── assets/
├── requirements.txt
├── README.md
├── LICENSE.txt
└── NOTICE.txt
```

---

## Disclaimer

AI PLC-GenStudio is an engineering assistance tool.

All generated PLC programs and engineering reports must be independently reviewed and validated by qualified engineers before deployment to industrial hardware.