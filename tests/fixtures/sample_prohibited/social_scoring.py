# regula-ignore
"""Fixture: Article 5 prohibited practice — social scoring system.

This file intentionally contains prohibited patterns for testing.
It should trigger PROHIBITED tier with confidence >= 75.
"""
import tensorflow as tf

# Social credit scoring system for citizen behaviour evaluation
social_scoring_model = tf.keras.Sequential()

def evaluate_citizen_score(behaviour_data):
    """Rate citizens based on social credit scoring of their behaviour."""
    prediction = social_scoring_model.predict(behaviour_data)
    return {"citizen_score": float(prediction[0])}
