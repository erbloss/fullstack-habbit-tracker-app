# Full‑Stack Habit Tracker App

A full‑stack application to help users log, track, and mark completion of daily habits. Users can log in, create habits, mark them complete each day, and view progress over time.

---

## Features

- User authentication (login)  
- Create, edit, and delete habits  
- Mark habits complete on a daily basis  
- View habit progress over time (history / calendar view)  
- Responsive front‑end UI using React  

---

## Tech Stack

| Layer        | Technology         |
|---------------|---------------------|
| Frontend     | React (JavaScript)  |
| Backend      | Flask (Python)      |
| Database     | SQLite              |

---

## Getting Started

Follow these steps to run the application locally.

### Prerequisites

- Python 3.x installed  
- Node.js & npm (or yarn) installed  
- (Optional) Virtual environment tool for Python (venv or similar)  

### Installation

1. Clone the repo:  
   ```bash
   git clone https://github.com/erbloss/fullstack-habbit-tracker-app.git
   cd fullstack-habbit-tracker-app

2. Backend Setup:
    cd backend
    python -m venv venv
    source venv/bin/activate  # on macOS/Linux or `venv\Scripts\activate` on Windows

    pip install -r requirements.txt

3. Frontend Setup
   cd ../frontend
   npm install

4. Seed database
    cd backend
    python seed_db.py

5. Run the App
   cd backend
   python app.py

   cd frontend
   npm run build
   npm start

