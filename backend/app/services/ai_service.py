"""AI-powered anomaly detection service"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle
import json

from app.core.config import settings
from app.models import LoginEvent

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered anomaly detection and feature extraction"""
    
    def __init__(self):
        self.model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None
        self.is_trained = False
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the anomaly detection model"""
        try:
            self.model = IsolationForest(
                contamination=settings.contamination_rate,
                random_state=42,
                n_estimators=100
            )
            self.scaler = StandardScaler()
            logger.info("AI model initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI model: {e}")
            raise
    
    def extract_features(self, event: LoginEvent, historical_data: Dict[str, Any] = None) -> List[float]:
        """Extract features from a login event for anomaly detection"""
        try:
            features = []
            
            # Time-based features
            import datetime
            dt = datetime.datetime.fromtimestamp(event.timestamp)
            features.extend([
                dt.hour,  # Hour of day (0-23)
                dt.weekday(),  # Day of week (0-6)
                dt.day,  # Day of month
            ])
            
            # IP-based features (simplified)
            ip_parts = event.ip.split('.')
            if len(ip_parts) == 4:
                features.extend([
                    int(ip_parts[0]),  # First octet
                    int(ip_parts[1]),  # Second octet
                ])
            else:
                features.extend([0, 0])
            
            # Location-based features (simplified hash)
            location_hash = abs(hash(event.location)) % 1000
            features.append(location_hash)
            
            # Historical features (if available)
            if historical_data:
                features.extend([
                    historical_data.get('login_frequency', 0),
                    historical_data.get('unique_ips_count', 0),
                    historical_data.get('unique_locations_count', 0),
                    historical_data.get('avg_time_between_logins', 0),
                ])
            else:
                features.extend([0, 0, 0, 0])
            
            # Pad or truncate to fixed size
            target_size = 16
            if len(features) < target_size:
                features.extend([0] * (target_size - len(features)))
            else:
                features = features[:target_size]
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to extract features: {e}")
            return [0] * 16  # Return zero vector on error
    
    def generate_behavior_embedding(self, event: LoginEvent, features: List[float] = None) -> List[float]:
        """Generate behavior embedding vector for similarity search"""
        try:
            if features is None:
                features = self.extract_features(event)
            
            # Create a behavior embedding (for demo, we'll use the features directly)
            # In a real implementation, you might use a neural network or more sophisticated method
            embedding = features.copy()
            
            # Normalize to unit vector
            embedding_array = np.array(embedding, dtype=np.float32)
            norm = np.linalg.norm(embedding_array)
            if norm > 0:
                embedding_array = embedding_array / norm
            
            # Ensure fixed dimension
            target_dim = settings.vector_dimension
            if len(embedding_array) < target_dim:
                # Pad with zeros
                padding = np.zeros(target_dim - len(embedding_array), dtype=np.float32)
                embedding_array = np.concatenate([embedding_array, padding])
            elif len(embedding_array) > target_dim:
                # Truncate
                embedding_array = embedding_array[:target_dim]
            
            return embedding_array.tolist()
            
        except Exception as e:
            logger.error(f"Failed to generate behavior embedding: {e}")
            return [0.0] * settings.vector_dimension
    
    def predict_anomaly_score(self, features: List[float]) -> float:
        """Predict anomaly score for given features"""
        try:
            if not self.is_trained:
                # For demo purposes, train with some dummy data
                self._train_with_dummy_data()
            
            # Reshape for single prediction
            features_array = np.array(features).reshape(1, -1)
            
            # Scale features
            features_scaled = self.scaler.transform(features_array)
            
            # Get anomaly score
            # Isolation Forest returns values between -1 and 1
            # We'll convert to 0-1 scale where higher values indicate more anomalous
            raw_score = self.model.decision_function(features_scaled)[0]
            
            # Convert to 0-1 scale (higher = more anomalous)
            # The decision_function returns negative values for anomalies
            anomaly_score = max(0, min(1, (1 - raw_score) / 2))
            
            return float(anomaly_score)
            
        except Exception as e:
            logger.error(f"Failed to predict anomaly score: {e}")
            return 0.5  # Return neutral score on error
    
    def _train_with_dummy_data(self):
        """Train the model with dummy data for demo purposes"""
        try:
            # Generate some dummy training data
            np.random.seed(42)
            
            # Normal patterns
            normal_data = []
            for _ in range(1000):
                features = [
                    np.random.randint(8, 18),  # Normal working hours
                    np.random.randint(0, 5),   # Weekdays
                    np.random.randint(1, 29),  # Day of month
                    np.random.randint(192, 193),  # Common IP range
                    np.random.randint(168, 169),  # Common IP range
                    np.random.randint(0, 100),    # Location hash
                    np.random.poisson(5),         # Login frequency
                    np.random.randint(1, 3),      # Unique IPs
                    np.random.randint(1, 2),      # Unique locations
                    np.random.normal(3600, 600),  # Avg time between logins
                ]
                # Pad to target size
                while len(features) < 16:
                    features.append(0)
                normal_data.append(features[:16])
            
            # Add some anomalous patterns
            anomalous_data = []
            for _ in range(50):
                features = [
                    np.random.randint(0, 24),     # Any hour
                    np.random.randint(0, 7),      # Any day
                    np.random.randint(1, 29),     # Day of month
                    np.random.randint(0, 256),    # Random IP
                    np.random.randint(0, 256),    # Random IP
                    np.random.randint(500, 1000), # Unusual location
                    np.random.poisson(20),        # High frequency
                    np.random.randint(5, 20),     # Many IPs
                    np.random.randint(5, 10),     # Many locations
                    np.random.normal(300, 100),   # Quick succession
                ]
                # Pad to target size
                while len(features) < 16:
                    features.append(0)
                anomalous_data.append(features[:16])
            
            # Combine data
            training_data = normal_data + anomalous_data
            training_array = np.array(training_data)
            
            # Fit scaler and model
            self.scaler.fit(training_array)
            scaled_data = self.scaler.transform(training_array)
            self.model.fit(scaled_data)
            
            self.is_trained = True
            logger.info("AI model trained with dummy data")
            
        except Exception as e:
            logger.error(f"Failed to train model with dummy data: {e}")
            raise
    
    def save_model(self, path: str):
        """Save the trained model to disk"""
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'is_trained': self.is_trained
            }
            
            with open(path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved to {path}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise
    
    def load_model(self, path: str):
        """Load a trained model from disk"""
        try:
            with open(path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.is_trained = model_data['is_trained']
            
            logger.info(f"Model loaded from {path}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise


# Global AI service instance
ai_service = AIService()
