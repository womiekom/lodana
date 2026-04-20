# LODANA - Solar Energy Prediction & Distribution System

LODANA is a data-driven system to predict solar energy potential in Sumba and optimize energy distribution across districts.

## Project Structure

- `backend/`: FastAPI application.
- `frontend/`: Vanilla HTML, CSS, and JavaScript dashboard.
- `data/`: Data storage for population and energy metrics.

## Setup

### Backend

1. Navigate to the project root.
2. (Optional) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install fastapi uvicorn
   ```
4. Run the server:
   ```bash
   uvicorn backend.main:app --reload
   ```

### Frontend

Open `frontend/index.html` in your browser.

## API Documentation

Once the backend is running, you can access the interactive API documentation at:
`http://127.0.0.1:8000/docs`
