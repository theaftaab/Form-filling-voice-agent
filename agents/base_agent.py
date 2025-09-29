# agents/base_agent.py
"""
Base classes for all conversational agents.
Provides common lifecycle hooks, transfer logic, and form scaffolding.
"""

import logging
from abc import ABC, abstractmethod
from typing import Tuple, Annotated

from livekit.agents.voice import Agent
from livekit.agents.llm import function_tool
from livekit.plugins import openai
from pydantic import Field

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# BaseAgent
# -------------------------------------------------------------------

class BaseAgent(Agent):
    """
    Core base class for all agents.
    Handles lifecycle (on_enter), context stitching, and agent transfer.
    """

    async def on_enter(self) -> None:
        """
        Called whenever this agent becomes active.
        Default: logs entry, restores conversation continuity if needed.
        """
        agent_name = self.__class__.__name__
        logger.info(f"🔄 Entering {agent_name}")

        userdata = self.session.userdata
        chat_ctx = self.chat_ctx.copy()

        # Add the previous agent's chat history to the current agent
        if isinstance(userdata.prev_agent, Agent):
            truncated_chat_ctx = userdata.prev_agent.chat_ctx.copy(
                exclude_instructions=True, exclude_function_call=False
            ).truncate(max_items=6)
            existing_ids = {item.id for item in chat_ctx.items}
            items_copy = [item for item in truncated_chat_ctx.items if item.id not in existing_ids]
            chat_ctx.items.extend(items_copy)

        # Add an instruction including the user data
        chat_ctx.add_message(
            role="system",
            content=f"You are {agent_name} agent.",
        )
        await self.update_chat_ctx(chat_ctx)

    async def _transfer_to_agent(self, name: str) -> Tuple[Agent, str]:
        """
        Utility to transfer control to another agent by name.
        """
        userdata = self.session.userdata
        current_agent = self.session.current_agent
        next_agent = userdata.agents[name]
        userdata.prev_agent = current_agent
        return next_agent, f"Transferring to {name}."

    @function_tool()
    async def to_greeter(self) -> tuple:
        """Called when user asks any unrelated questions or wants to go back to main menu."""
        return await self._transfer_to_agent("greeter")

    @function_tool()
    async def set_language(
        self,
        language: Annotated[str, Field(description="The user's preferred language: english or kannada")],
    ) -> str:
        """Called when the user selects their preferred language."""
        from utils.language import update_stt_language
        
        userdata = self.session.userdata
        language_lower = language.lower()
        
        if language_lower not in ["english", "kannada"]:
            return "Please choose English or Kannada."
        
        userdata.preferred_language = language_lower
        userdata.language_selected = True
        
        # Update STT language hints based on selected language
        await update_stt_language(self.session, language_lower)
        
        if language_lower == "kannada":
            return "ಧನ್ಯವಾದಗಳು! ನಿಮ್ಮ ಮಾಹಿತಿಯನ್ನು ನಾನು ಸಂಗ್ರಹಿಸುತ್ತೇನೆ."
        else:
            return "Thank you! I'll help you fill out the form."


# -------------------------------------------------------------------
# BaseFormAgent
# -------------------------------------------------------------------

class BaseFormAgent(BaseAgent):
    """
    Base class for form-filling agents (e.g. contact form, felling form).
    Adds scaffolding for collecting fields, asking confirmation, and submission.
    """

    async def on_enter(self) -> None:
        """
        Extended lifecycle: after base enter, begin form collection.
        """
        await super().on_enter()
        agent_name = self.__class__.__name__
        logger.info(f"Entering {agent_name}")
        
        userdata = self.session.userdata
        
        # Form agents should already have language selected from greeter
        if userdata.language_selected:
            await self._start_form_collection()

    async def _start_form_collection(self):
        """Override this method in subclasses to start collecting form data"""
        pass

    async def _ask_for_confirmation(self) -> str:
        """
        Standard confirmation before form submission.
        """
        userdata = self.session.userdata
        userdata.awaiting_confirmation = True

        if userdata.preferred_language == "kannada":
            return "ಧನ್ಯವಾದಗಳು. ನೀವು ಫಾರ್ಮ್ ಸಲ್ಲಿಸಲು ಬಯಸುವಿರಾ?"
        else:
            return "Thank you. Would you like to submit the form now?"