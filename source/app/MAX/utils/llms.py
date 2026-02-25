from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()


class LLMs:
    @staticmethod
    def get_openai_model(model="gpt-4o-mini", temperature=0.9):
        """
        Get OpenAI model instance for MAX
        - gpt-4o-mini: Fast, cost-effective, great for conversations
        - gpt-4o: Most capable, best reasoning, use for complex analysis
        - temperature 0.9: Very natural, human-like, ChatGPT-style responses
        
        Higher temperature = More creative, conversational, less robotic
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "❌ OPENAI_API_KEY not found in environment variables! "
                "MAX needs this to provide intelligent responses. "
                "Please add OPENAI_API_KEY='your-key-here' to your .env file"
            )
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            openai_api_key=api_key,
        )
