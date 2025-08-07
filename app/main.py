from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, HttpUrl
from typing import Optional
import os
import logging
from .predict import predict_probability, MODEL_PATH

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
  title="Verified Listens API",
  description="API for predicting podcast listening probabilities up to ad placement timestamps",
  version="1.0.0"
)

class ListenRequest(BaseModel):
  feed: HttpUrl
  enclosure: HttpUrl
  seconds: int
  ua: str
  state: str
  genre: Optional[str] = "Unknown"
  content_duration: Optional[int] = 0


@app.get("/will-listen-to")
def will_listen_to_get(
  feed: Optional[str] = Query(None),
  enclosure: Optional[str] = Query(None),
  seconds: Optional[int] = Query(None),
  ua: Optional[str] = "",
  state: Optional[str] = "",
  genre: Optional[str] = "Unknown",
  content_duration: Optional[int] = 0
):
  if not seconds:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="seconds not provided or is malformed"
    )

  if seconds <= 0 or seconds > 7200:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="seconds must be between 1 and 7200"
    )
  
  prob = predict_probability(feed, enclosure or "", ua, state, genre, content_duration, seconds)
  if prob is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="enclosure not found or prediction failed"
    )

  return prob


@app.post("/will-listen-to")
def will_listen_to_post(req: ListenRequest):
  
  if not req.enclosure or req.seconds is None:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="enclosure or seconds not provided or is malformed"
    )

  if req.seconds <= 0 or req.seconds > 7200:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="seconds must be between 1 and 7200"
    )

  prob = predict_probability(
    feed=req.feed,
    enclosure=req.enclosure,
    ua=req.ua,
    state=req.state,
    genre=req.genre,
    content_duration=req.content_duration,
    seconds=req.seconds
  )
  if prob is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="enclosure not found or prediction failed"
    )

  return prob


@app.get("/health")
def health_check():
  """
  Health check endpoint to verify API and model availability.
  
  Returns:
    dict: Service status and model information
  """
  try:
    # Check if model file exists
    model_exists = os.path.exists(MODEL_PATH)
    
    # Try a simple prediction to verify model works
    test_prediction = None
    if model_exists:
      try:
        test_prediction = predict_probability(
          feed="https://example.com/feed",
          enclosure="https://example.com/episode.mp3",
          ua="Test Agent",
          state="CA",
          genre="Test",
          content_duration=1800,
          seconds=600
        )
      except Exception as e:
        logger.error(f"Health check prediction failed: {e}")
    
    status_info = {
      "status": "healthy" if model_exists and test_prediction is not None else "unhealthy",
      "model_loaded": model_exists,
      "model_path": MODEL_PATH,
      "prediction_working": test_prediction is not None,
      "api_version": "1.0.0"
    }
    
    if test_prediction is not None:
      status_info["test_prediction"] = test_prediction
    
    return status_info
      
  except Exception as e:
    logger.error(f"Health check failed: {e}")
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Health check failed: {str(e)}"
    )