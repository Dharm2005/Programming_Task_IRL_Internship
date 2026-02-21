from google import genai

from config.settings import Settings
from utils.logger import get_logger

logger = get_logger()

class GeminiClient:

    def __init__(self):

        if not Settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found")

        self.client = genai.Client(
            api_key=Settings.GEMINI_API_KEY
        )

        # Use supported model from your list
        self.model = "models/gemini-2.5-flash"

        logger.info(f"Gemini Client Initialized with {self.model}")


    def generate(self, prompt):

        try:

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            if not response or not response.text:
                return "No response generated."

            logger.info("Gemini Response Generated")

            return response.text


        except Exception as e:

            logger.error(f"Gemini Error: {str(e)}")

            return "Sorry, I am facing technical issues."