import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

QG_SERVICE_URL = "http://localhost:8001/generate_question/"

def generate_question(passage, question_type="SAQ"):
    """
    Calls the external Question Generation microservice with the required fields.
    Logs request details and response.
    """
    try:
        payload = {
            "passage": passage,
            "question_type": question_type  # Default to "SAQ"
        }

        # Log request payload
        logging.info(f"Sending request to QG API: {payload}")

        response = requests.post(QG_SERVICE_URL, json=payload)
        response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)

        # Log full response JSON for debugging
        response_json = response.json()
        logging.info(f"Full QG API response: {response_json}")

        # Extract the correct key
        generated_question = response_json.get("generated_question", "No question generated")

        # Handle missing or empty responses
        if not generated_question or generated_question.strip() == "No question generated":
            logging.error(f"QG API returned an invalid question. Full response: {response_json}")
            raise RuntimeError("Question Generation failed: No valid question received from QG API.")

        logging.info(f"Received question from QG API: {generated_question}")

        return generated_question

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling QG service: {str(e)} - Response: {response.text if response else 'No response'}")
        raise RuntimeError(f"Error calling QG service: {str(e)}")
