import requests
import logging
from difflib import SequenceMatcher

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

QA_SERVICE_URL = "http://20.193.146.113:8002/qa"

def evaluate_answer(user_answer, context, question):
    """
    Calls the external Question Answering microservice.
    Logs request and response details for debugging.
    """
    try:
        payload = {"question": question, "context": context}

        # Log the API request payload
        logging.info(f"Sending request to QA API: {payload}")

        response = requests.post(QA_SERVICE_URL, json=payload)
        response.raise_for_status()

        gold_answer = response.json().get("answer", "No answer generated")

        # Calculate similarity
        similarity = SequenceMatcher(None, user_answer.lower(), gold_answer.lower()).ratio()

        # Assign reward based on similarity thresholds
        reward = 1.0 if similarity >= 0.7 else (-1.0 if similarity <= 0.3 else 0.0)

        # Log important information
        logging.info(f"User Answer: {user_answer}")
        logging.info(f"Generated Question: {question}")
        logging.info(f"Context: {context}")  # Log full context
        logging.info(f"Gold Answer: {gold_answer}")
        logging.info(f"Similarity Score: {similarity:.2f}")
        logging.info(f"Assigned Reward: {reward}")

        return reward, gold_answer, similarity

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling QA service: {str(e)} - Response: {response.text if response else 'No response'}")
        raise RuntimeError(f"Error calling QA service: {str(e)}")
