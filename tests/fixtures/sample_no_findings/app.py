import logging
import openai

logger = logging.getLogger(__name__)

def get_recommendation(data):
    """Get AI recommendation with human oversight."""
    client = openai.Client()
    result = client.chat.completions.create(model="gpt-4", messages=[{"role": "user", "content": str(data)}])
    logger.info("AI recommendation generated", extra={"input_hash": hash(str(data))})
    return result

def human_review(recommendation):
    """Human reviews and approves AI recommendation before action."""
    logger.info("Recommendation sent for human review")
    return {"status": "pending_review", "recommendation": recommendation}
