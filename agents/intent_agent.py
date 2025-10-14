import logging
from livekit.plugins import openai
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class IntentAgent(BaseAgent):
    """
    Classifies user query into: form, knowledge or navigation.
    """
    
    def __init__(self):
        super().__init__(
            instructions = (
                "You are an intent classifier for Karnataka Govt. Chatbot."
                "Given a user query, classify it into one of: "
                "1. form_intent (contact form, felling form),"
                "2. knowledge_intent (general_info, Q&A),"
                "3. navigation_intent (user wants a specific webpage)."
                "Respond with ony one of these labels"
            ),
            llm = openai.LLM(model="gpt-4o-mini")
        )
    async def classify(self, user_query:str) -> str:
        result = await self.session.ask(user_query)
        intent = result.lower().strip()
        logger.info(f"Detected Intent: {intent}")
        return intent