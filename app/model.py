import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_model():
  """
  Train a machine learning model to predict podcast listening behavior.
  
  Training Strategy:
  - Uses multiple ad placement timestamps (5min, 10min, 15min) to create diverse training data
  - Each original engagement record is expanded to multiple rows with different thresholds
  - Binary classification: will user listen past the ad marker time?
  - This approach allows the model to learn patterns for any timestamp, not just fixed intervals
  """
  logger.info("Starting model training...")
    
  BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  CSV_PATH = os.path.join(BASE_DIR, 'podcast_engagement_data.csv')
  
  if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"Training data not found at {CSV_PATH}. Please run 'python app/generate_mock_data.py' first.")
  
  df = pd.read_csv(CSV_PATH)
  logger.info(f"Loaded {len(df)} records from {CSV_PATH}")

  # Add missing columns if they don't exist
  if 'Genre' not in df.columns:
    df['Genre'] = 'Unknown'
    logger.info("Added default 'Genre' column")

  if 'Content Duration (seconds)' not in df.columns:
    df['Content Duration (seconds)'] = 0
    logger.info("Added default 'Content Duration (seconds)' column")

  # Clean data
  initial_rows = len(df)
  df = df.dropna(subset=[
    'Podcast RSS Feed', 'Enclosure URL', 'UUID',
    'User Agent', 'State', 'Duration of Listen (seconds)'
  ])
  logger.info(f"Cleaned data: {initial_rows} -> {len(df)} rows (removed {initial_rows - len(df)} incomplete records)")
  
  # Create training data for multiple ad placement times
  # This allows the model to learn patterns for different timestamps
  thresholds = [300, 600, 900]  # 5min, 10min, 15min markers
  records = []

  for t in thresholds:
    temp = df.copy()
    temp["ad_marker_seconds"] = t
    # Binary classification: did user listen past this threshold?
    temp["label"] = (temp["Duration of Listen (seconds)"] >= t).astype(int)
    records.append(temp)
    
    # Log class distribution for this threshold
    positive_rate = temp["label"].mean()
    logger.info(f"Threshold {t}s: {positive_rate:.2%} positive examples")

  all_df = pd.concat(records, ignore_index=True)
  logger.info(f"Generated {len(all_df)} training examples from {len(df)} original records")

  # Define features
  features = [
    "Podcast RSS Feed", "Enclosure URL", "User Agent", "State", "Genre",
    "Content Duration (seconds)", "ad_marker_seconds"
  ]
  X = all_df[features]
  y = all_df["label"]

  # Split data for validation
  X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
  )
  logger.info(f"Split: {len(X_train)} train, {len(X_test)} test samples")

  # Define preprocessing pipeline
  categorical = ["Podcast RSS Feed", "Enclosure URL", "User Agent", "State", "Genre"]
  numeric = ["Content Duration (seconds)", "ad_marker_seconds"]

  preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
    ("num", StandardScaler(), numeric)
  ])

  # Build and train model
  model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(n_estimators=100, random_state=42))
  ])

  logger.info("Training model...")
  model.fit(X_train, y_train)

  # Evaluate model performance
  y_pred = model.predict(X_test)
  accuracy = accuracy_score(y_test, y_pred)
  
  logger.info(f"Model Training Complete!")
  logger.info(f"Accuracy: {accuracy:.3f}")
  logger.info("Classification Report:")
  logger.info(f"\n{classification_report(y_test, y_pred)}")

  # Save model
  model_path = os.path.join(BASE_DIR, "model.joblib")
  joblib.dump(model, model_path)
  logger.info(f"Model saved to {model_path}")
  
  return model, accuracy

if __name__ == "__main__":
  train_model()
