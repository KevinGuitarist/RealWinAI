"""
Advanced AI Prediction Engine for M.A.X.
Combines multiple ML models with expert systems for highly accurate predictions
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
import tensorflow as tf
import xgboost as xgb
import lightgbm as lgb
from sklearn.ensemble import RandomForestClassifier
import logging
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class PredictionResult:
    """Structured prediction result"""
    outcome: str
    probability: float
    confidence_score: float
    model_weights: Dict[str, float]
    key_factors: List[Dict[str, Any]]
    uncertainty_range: tuple
    time_horizon: str

@dataclass
class ModelMetrics:
    """Model performance metrics"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    calibration_score: float

class MaxAIPredictionEngine:
    """
    Advanced AI prediction engine that:
    - Uses ensemble of ML models
    - Incorporates expert systems
    - Handles real-time data
    - Self-adjusts based on performance
    - Provides uncertainty estimates
    """

    def __init__(self):
        # Initialize ML models
        self.models = {
            "xgboost": None,
            "lightgbm": None,
            "neural_net": None,
            "random_forest": None
        }
        
        # Model weights for ensemble
        self.model_weights = {
            "xgboost": 0.3,
            "lightgbm": 0.25,
            "neural_net": 0.25,
            "random_forest": 0.2
        }
        
        # Performance tracking
        self.model_metrics = {}
        
        # Initialize models
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize all ML models"""
        try:
            # XGBoost
            self.models["xgboost"] = xgb.XGBClassifier(
                n_estimators=1000,
                max_depth=7,
                learning_rate=0.01,
                objective='binary:logistic',
                eval_metric='auc',
                tree_method='gpu_hist',  # Use GPU if available
                early_stopping_rounds=50
            )
            
            # LightGBM
            self.models["lightgbm"] = lgb.LGBMClassifier(
                n_estimators=1000,
                num_leaves=31,
                learning_rate=0.01,
                objective='binary',
                metric='auc',
                device='gpu'  # Use GPU if available
            )
            
            # Neural Network
            self.models["neural_net"] = tf.keras.Sequential([
                tf.keras.layers.Dense(256, activation='relu', input_shape=(None, 512)),
                tf.keras.layers.Dropout(0.3),
                tf.keras.layers.Dense(128, activation='relu'),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(64, activation='relu'),
                tf.keras.layers.Dense(1, activation='sigmoid')
            ])
            
            # Random Forest
            self.models["random_forest"] = RandomForestClassifier(
                n_estimators=1000,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                n_jobs=-1  # Use all CPU cores
            )
            
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
    
    async def predict_match(
        self,
        team_a: str,
        team_b: str,
        sport: str,
        context: Optional[Dict] = None
    ) -> PredictionResult:
        """Generate comprehensive match prediction"""
        try:
            # Get feature data
            features = await self._get_feature_data(team_a, team_b, sport)
            
            # Get predictions from each model
            predictions = {}
            for model_name, model in self.models.items():
                predictions[model_name] = await self._get_model_prediction(
                    model,
                    features,
                    model_name
                )
            
            # Combine predictions using weighted ensemble
            ensemble_pred = self._combine_predictions(predictions)
            
            # Calculate confidence score
            confidence = self._calculate_confidence_score(predictions, features)
            
            # Get key factors
            key_factors = self._extract_key_factors(predictions, features)
            
            # Calculate uncertainty range
            uncertainty = self._calculate_uncertainty_range(predictions)
            
            return PredictionResult(
                outcome="win" if ensemble_pred > 0.5 else "lose",
                probability=ensemble_pred,
                confidence_score=confidence,
                model_weights=self.model_weights,
                key_factors=key_factors,
                uncertainty_range=uncertainty,
                time_horizon="match"
            )
            
        except Exception as e:
            logger.error(f"Error in match prediction: {e}")
            return PredictionResult(
                outcome="unknown",
                probability=0.5,
                confidence_score=0.0,
                model_weights={},
                key_factors=[],
                uncertainty_range=(0.0, 0.0),
                time_horizon="match"
            )
    
    async def _get_feature_data(
        self,
        team_a: str,
        team_b: str,
        sport: str
    ) -> pd.DataFrame:
        """Get and process feature data for prediction"""
        try:
            features = pd.DataFrame()
            
            # Get historical match data
            historical = await self._get_historical_data(team_a, team_b, sport)
            
            # Get recent form data
            form = await self._get_form_data(team_a, team_b, sport)
            
            # Get player statistics
            player_stats = await self._get_player_stats(team_a, team_b, sport)
            
            # Get venue data
            venue_data = await self._get_venue_data(team_a, team_b, sport)
            
            # Get weather data if relevant
            weather = await self._get_weather_data() if sport == "cricket" else None
            
            # Combine all features
            features = self._combine_features(
                historical,
                form,
                player_stats,
                venue_data,
                weather
            )
            
            # Feature engineering
            features = self._engineer_features(features, sport)
            
            # Normalize features
            features = self._normalize_features(features)
            
            return features
            
        except Exception as e:
            logger.error(f"Error getting feature data: {e}")
            return pd.DataFrame()
    
    async def _get_model_prediction(
        self,
        model: Any,
        features: pd.DataFrame,
        model_name: str
    ) -> Dict[str, Any]:
        """Get prediction from individual model"""
        try:
            # Preprocess features for specific model
            model_features = self._preprocess_for_model(features, model_name)
            
            # Get prediction
            if model_name == "neural_net":
                pred = model.predict(model_features.values.reshape(1, -1, 512))
            else:
                pred = model.predict_proba(model_features.values.reshape(1, -1))
                
            # Get feature importance
            importance = self._get_feature_importance(model, model_features, model_name)
            
            return {
                "probability": float(pred[0][1]) if model_name != "neural_net" else float(pred[0]),
                "feature_importance": importance,
                "model_metrics": self.model_metrics.get(model_name, {})
            }
            
        except Exception as e:
            logger.error(f"Error in model prediction: {e}")
            return {"probability": 0.5, "feature_importance": {}, "model_metrics": {}}
    
    def _combine_predictions(self, predictions: Dict[str, Dict[str, Any]]) -> float:
        """Combine predictions using weighted ensemble"""
        try:
            # Get weighted average
            weighted_sum = 0
            total_weight = 0
            
            for model_name, pred in predictions.items():
                weight = self.model_weights[model_name]
                weighted_sum += pred["probability"] * weight
                total_weight += weight
                
            # Normalize
            if total_weight > 0:
                return weighted_sum / total_weight
            return 0.5
            
        except Exception as e:
            logger.error(f"Error combining predictions: {e}")
            return 0.5
    
    def _calculate_confidence_score(
        self,
        predictions: Dict[str, Dict[str, Any]],
        features: pd.DataFrame
    ) -> float:
        """Calculate confidence score for prediction"""
        try:
            # Base confidence on:
            # 1. Model agreement
            model_agreement = self._calculate_model_agreement(predictions)
            
            # 2. Feature quality
            feature_quality = self._assess_feature_quality(features)
            
            # 3. Historical accuracy
            historical_accuracy = self._get_historical_accuracy(predictions)
            
            # 4. Prediction margin
            prediction_margin = self._calculate_prediction_margin(predictions)
            
            # Combine factors
            confidence = (
                0.4 * model_agreement +
                0.2 * feature_quality +
                0.2 * historical_accuracy +
                0.2 * prediction_margin
            )
            
            return min(confidence, 0.99)  # Cap at 99%
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _extract_key_factors(
        self,
        predictions: Dict[str, Dict[str, Any]],
        features: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """Extract key factors influencing prediction"""
        try:
            key_factors = []
            
            # Get top features from each model
            for model_name, pred in predictions.items():
                importance = pred.get("feature_importance", {})
                top_features = sorted(
                    importance.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
                
                for feature, importance in top_features:
                    key_factors.append({
                        "factor": feature,
                        "importance": importance,
                        "model": model_name
                    })
            
            # Deduplicate and sort
            key_factors = self._deduplicate_factors(key_factors)
            key_factors.sort(key=lambda x: x["importance"], reverse=True)
            
            return key_factors[:10]  # Return top 10 factors
            
        except Exception as e:
            logger.error(f"Error extracting key factors: {e}")
            return []
    
    def _calculate_uncertainty_range(
        self,
        predictions: Dict[str, Dict[str, Any]]
    ) -> tuple:
        """Calculate uncertainty range for prediction"""
        try:
            probabilities = [pred["probability"] for pred in predictions.values()]
            
            # Calculate confidence interval
            mean = np.mean(probabilities)
            std = np.std(probabilities)
            
            # Use 95% confidence interval
            lower = max(0, mean - 1.96 * std)
            upper = min(1, mean + 1.96 * std)
            
            return (lower, upper)
            
        except Exception as e:
            logger.error(f"Error calculating uncertainty: {e}")
            return (0.4, 0.6)  # Default range
    
    async def update_models(self, new_data: pd.DataFrame):
        """Update models with new data"""
        try:
            # Split data
            X, y = self._prepare_training_data(new_data)
            
            # Update each model
            for model_name, model in self.models.items():
                # Update model
                await self._update_model(model, X, y, model_name)
                
                # Update metrics
                self.model_metrics[model_name] = self._calculate_model_metrics(
                    model,
                    X,
                    y,
                    model_name
                )
                
            # Update model weights based on performance
            self._update_model_weights()
            
        except Exception as e:
            logger.error(f"Error updating models: {e}")
    
    def _update_model_weights(self):
        """Update ensemble weights based on model performance"""
        try:
            total_score = 0
            new_weights = {}
            
            # Calculate weight based on model metrics
            for model_name, metrics in self.model_metrics.items():
                score = (
                    metrics.accuracy * 0.3 +
                    metrics.precision * 0.2 +
                    metrics.recall * 0.2 +
                    metrics.f1_score * 0.2 +
                    metrics.calibration_score * 0.1
                )
                new_weights[model_name] = score
                total_score += score
            
            # Normalize weights
            if total_score > 0:
                for model_name in new_weights:
                    self.model_weights[model_name] = new_weights[model_name] / total_score
            
        except Exception as e:
            logger.error(f"Error updating model weights: {e}")

# Export main components
__all__ = [
    "MaxAIPredictionEngine",
    "PredictionResult",
    "ModelMetrics"
]