# Form Submission Backend

A FastAPI backend service for handling form submissions and forwarding them to an email notification endpoint.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration:
```bash
API_KEY=your_notification_api_key
NOTIFICATION_ENDPOINT=your_notification_endpoint_url
```

4. Run the server:
```bash
uvicorn main:app --reload
```

## API Endpoints

- `POST /api/submit`: Submit form data
  - Accepts form data
  - Forwards the data to the configured notification endpoint
  - Returns success/error response

## Development

The server will run on `http://localhost:8000` by default.
API documentation is available at `http://localhost:8000/docs` 