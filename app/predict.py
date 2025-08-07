import os
import joblib
import pandas as pd
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")

def load_model():
  """Load the trained model with proper error handling."""
  if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Please train the model first using: python app/model.py")
  
  try:
    model = joblib.load(MODEL_PATH)
    logger.info(f"Model loaded successfully from {MODEL_PATH}")
    return model
  except Exception as e:
    logger.error(f"Failed to load model from {MODEL_PATH}: {e}")
    raise

# Load model on module import
model = load_model()

def validate_inputs(feed, enclosure, ua, state, genre, content_duration: int, seconds: int) -> None:
  """Validate prediction inputs."""
  if not isinstance(seconds, int) or seconds <= 0:
    raise ValueError("seconds must be a positive integer")
  
  if not isinstance(content_duration, int) or content_duration < 0:
    raise ValueError("content_duration must be a non-negative integer")
  
  # Convert any URL objects to strings for validation
  # This handles both string inputs and Pydantic HttpUrl types
  if feed and not isinstance(str(feed), str):
    raise ValueError("feed must be a valid URL or string")
  
  if enclosure and not isinstance(str(enclosure), str):
    raise ValueError("enclosure must be a valid URL or string")

def predict_probability(feed: str, enclosure: str, ua: str, state: str, genre: str, content_duration: int, seconds: int) -> Optional[float]:
  """
  Predict the probability of a user listening up to a specific timestamp.
  
  Args:
    feed: Podcast RSS feed URL
    enclosure: Episode enclosure URL
    ua: User agent string
    state: US state
    genre: Podcast genre
    content_duration: Total content duration in seconds
    seconds: Ad placement time in seconds
  
  Returns:
    Float probability between 0 and 1, or None if prediction fails
  """
  try:
    # Validate inputs
    validate_inputs(feed, enclosure, ua, state, genre, content_duration, seconds)
    
    # Prepare data for prediction (convert URLs to strings)
    df = pd.DataFrame([{
      "Podcast RSS Feed": str(feed) if feed else "",
      "Enclosure URL": str(enclosure) if enclosure else "",
      "User Agent": ua or "",
      "State": state or "",
      "Genre": genre or "Unknown",
      "Content Duration (seconds)": content_duration,
      "ad_marker_seconds": seconds
    }])
    
    # Make prediction
    proba = model.predict_proba(df)[0][1]
    result = round(proba, 4)
    
    logger.info(f"Prediction successful: {result} for seconds={seconds}")
    return result
      
  except ValueError as e:
    logger.error(f"Input validation error: {e}")
    return None
  except (KeyError, IndexError) as e:
    logger.error(f"Data structure error: {e}")
    return None
  except Exception as e:
    logger.error(f"Unexpected prediction error: {e}")
    return None

