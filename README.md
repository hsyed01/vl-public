# Verified Listens

**Objective:**  
Build an API that, given a set of podcast-related inputs (podcast show, episode, genre, content duration, etc.), returns the **probability** that a user will listen up to a specific ad placement time (in seconds).

---

## Features

- Trains an ML model using podcast engagement data  
- Predicts the probability of a user listening up to a given timestamp  
- Provides both `GET` and `POST` API endpoints  
- Includes unit tests with `pytest` + `httpx`  
- Easy-to-run model training with CSV data  

---

## Requirements

- **Python 3.13.5+** (recommended)
- **Minimum Python 3.9+** (for compatibility)

---

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/hsyed01/vl-public.git
cd vl-public

# Create virtual environment with Python 3.13 (recommended)
python3.13 -m venv venv
# OR use default Python 3 if 3.13+ is your system default
# python3 -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### requirements.txt

```txt
fastapi==0.115.12
pydantic==2.11.6
pydantic_core==2.33.2
uvicorn==0.34.3
httpx==0.27.0
pytest==8.2.1
pytest-asyncio==0.23.6
scikit-learn==1.7.1
pandas==2.2.2
joblib==1.4.2
```

---

## Model Training

### Dataset

Sample training data: `app/podcast_engagement_data.csv`  
Expected CSV columns:

| Podcast RSS Feed | Enclosure URL | UUID | User Agent | State | Duration of Listen (seconds) | Genre |
|------------------|---------------|------|------------|-------|------------------------------|-------|

### Run the Training Script

```bash
python3 app/model.py
```

This will:
- Load data from `app/podcast_engagement_data.csv`
- Train a classifier (e.g., Random Forest)
- Save the trained model to `app/model.joblib`

---

## Running the API

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

---

## Example API Calls

### GET `/will-listen-to`

```http
GET /will-listen-to?feed=https://feeds.megaphone.fm/stuffyoushouldknow&seconds=600
```

### POST `/will-listen-to`

```json
POST /will-listen-to
Content-Type: application/json

{
  "feed": "https://feeds.megaphone.fm/conan-obrien-needs-a-friend",
  "enclosure": "https://feeds.megaphone.fm/episodes/episode-1056-20241128.m4a",
  "seconds": 600,
  "ua": "Google Podcasts/1.0.0.12345 (Linux; U; Android 13; Pixel 7)",
  "state": "Connecticut"
}
```

### GET `/health`

Health check endpoint to verify API and model status:

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "/path/to/model.joblib",
  "prediction_working": true,
  "api_version": "1.0.0",
  "test_prediction": 0.8234
}
```

### Responses

| Status | Meaning                                    |
|--------|--------------------------------------------|
| 200    | Probability score (e.g., `0.85`)           |
| 400    | `{"detail": "seconds not provided or is malformed"}` |
| 404    | `{"detail": "enclosure not found or prediction failed"}` |
| 422    | Validation error (e.g., missing required fields) |
| 500    | `{"detail": "Health check failed: ..."}` |

---

## Testing the API

### Manual API Testing

#### Test Basic Functionality
```bash
# Test GET endpoint (original requirement)
curl "http://127.0.0.1:8000/will-listen-to?feed=https://feeds.megaphone.fm/stuffyoushouldknow&seconds=600"
# Expected: 0.97 (probability score)

# Test POST endpoint with full parameters
curl -X POST "http://127.0.0.1:8000/will-listen-to" \
  -H "Content-Type: application/json" \
  -d '{
    "feed": "https://feeds.megaphone.fm/conan-obrien-needs-a-friend",
    "enclosure": "https://feeds.megaphone.fm/episodes/episode-1056-20241128.m4a",
    "seconds": 600,
    "ua": "Google Podcasts/1.0.0.12345 (Linux; U; Android 13; Pixel 7)",
    "state": "Connecticut"
  }'
# Expected: 0.96 (probability score)
```

#### Test Health Check
```bash
# Check API and model status
curl "http://127.0.0.1:8000/health" | python3 -m json.tool
# Expected: {"status": "healthy", "model_loaded": true, ...}
```

#### Test Error Handling
```bash
# Missing required parameter
curl "http://127.0.0.1:8000/will-listen-to?feed=https://feeds.megaphone.fm/stuffyoushouldknow"
# Expected: {"detail": "seconds not provided or is malformed"}

# Invalid seconds range
curl "http://127.0.0.1:8000/will-listen-to?feed=https://feeds.megaphone.fm/stuffyoushouldknow&seconds=-1"
# Expected: {"detail": "seconds must be between 1 and 7200"}

# Seconds too large
curl "http://127.0.0.1:8000/will-listen-to?feed=https://feeds.megaphone.fm/stuffyoushouldknow&seconds=10000"
# Expected: {"detail": "seconds must be between 1 and 7200"}
```

#### Test Different Time Intervals
```bash
# Test early ad placement (5 minutes)
curl "http://127.0.0.1:8000/will-listen-to?feed=https://feeds.megaphone.fm/stuffyoushouldknow&seconds=300"

# Test mid-episode ad (15 minutes)
curl "http://127.0.0.1:8000/will-listen-to?feed=https://feeds.megaphone.fm/stuffyoushouldknow&seconds=900"

# Test late ad placement (30 minutes)
curl "http://127.0.0.1:8000/will-listen-to?feed=https://feeds.megaphone.fm/stuffyoushouldknow&seconds=1800"
```

### Running Unit Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run tests with detailed output
pytest tests/ -v --tb=short
```

**Expected Output:**
```
tests/test_main.py::test_get_will_listen_to_success PASSED [ 25%]
tests/test_main.py::test_get_missing_seconds PASSED       [ 50%]
tests/test_main.py::test_post_will_listen_to_success PASSED [ 75%]
tests/test_main.py::test_post_invalid_seconds PASSED      [100%]
4 passed in 1.10s
```

### Testing Model Training

```bash
# Test enhanced model training with logging
source venv/bin/activate
python3 app/model.py
```

**Expected Output:**
```
INFO:__main__:Starting model training...
INFO:__main__:Loaded 1000 records from .../podcast_engagement_data.csv
INFO:__main__:Threshold 300s: 92.40% positive examples
INFO:__main__:Threshold 600s: 85.20% positive examples  
INFO:__main__:Threshold 900s: 75.80% positive examples
INFO:__main__:Model Training Complete!
INFO:__main__:Accuracy: 0.863
```

### Troubleshooting

#### Common Issues and Solutions

**1. Server won't start - "Model file not found"**
```bash
# Solution: Generate data and train model first
python3 app/generate_mock_data.py
python3 app/model.py
```

**2. API returns "prediction failed" errors**
```bash
# Check health status
curl "http://127.0.0.1:8000/health"

# If model_loaded is false, retrain:
python3 app/model.py
```

**3. Tests failing**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Check if all dependencies are installed
pip install -r requirements.txt

# Verify server is running on correct port
curl "http://127.0.0.1:8000/health"
```

**4. Import errors**
```bash
# Make sure you're in the project root directory
cd /path/to/vl-public

# Run from project root
uvicorn app.main:app --reload
```

**5. Python version compatibility issues**
```bash
# Check your Python version
python3 --version

# If using older Python, install compatible scikit-learn version
pip install scikit-learn==1.6.1  # For Python 3.9-3.12

# Recommended: Upgrade to Python 3.13+ for best performance
brew install python@3.13  # macOS with Homebrew
```

#### Expected Behavior
- **Healthy API**: Health check returns `"status": "healthy"`
- **Successful predictions**: Return decimal values between 0 and 1
- **Error responses**: Return JSON with `"detail"` field
- **Model accuracy**: Should be around 85-90% after training
- **Python version**: 3.13.5+ recommended for optimal performance

---

## Generating Mock Data (Optional)

```bash
python3 app/generate_mock_data.py
```

```python
import pandas as pd
import random
import uuid

feeds = [
    "https://feeds.megaphone.fm/conan-obrien-needs-a-friend",
    "https://feeds.megaphone.fm/stuffyoushouldknow"
]
enclosures = [
    "https://feeds.megaphone.fm/episodes/ep-1001.m4a",
    "https://feeds.megaphone.fm/episodes/ep-1056.m4a"
]

states = ["New York", "California", "Texas", "Florida", "Connecticut"]

data = []
for _ in range(1000):
    data.append({
        "feed": random.choice(feeds),
        "enclosure": random.choice(enclosures),
        "uuid": str(uuid.uuid4()),
        "ua": "Google Podcasts/1.0.0.12345 (Linux; Android)",
        "state": random.choice(states),
        "duration": random.randint(10, 3600),
        "genre": random.choice(["comedy", "science", "true crime"])
    })

df = pd.DataFrame(data)
df.to_csv("app/podcast_engagement_data.csv", index=False)
```

---

## Final Notes

This project was built as a challenge to demonstrate end-to-end data pipeline, ML model development, and RESTful API implementation using FastAPI.

Accuracy is not the primary concern—focus is on proper input handling, response formatting, and API reliability.
