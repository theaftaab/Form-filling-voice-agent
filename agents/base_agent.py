# agents/base_agent.py
"""
Base classes for all conversational agents.
Provides common lifecycle hooks, transfer logic, and form scaffolding.
"""

import logging
from abc import ABC, abstractmethod
from typing import Tuple

from livekit.agents.voice import Agent, RunContext
from livekit.agents.llm import function_tool

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# BaseAgent
# -------------------------------------------------------------------

class BaseAgent(Agent, ABC):
    """
    Core base class for all agents.
    Handles lifecycle (on_enter), context stitching, and agent transfer.
    """

    async def on_enter(self, context: RunContext) -> None:
        """
        Called whenever this agent becomes active.
        Default: logs entry, restores conversation continuity if needed.
        """
        agent_name = self.__class__.__name__
        logger.info(f"🔄 Entering {agent_name}")

        userdata = context.userdata
        prev_agent = getattr(userdata, "prev_agent", None)

        if prev_agent:
            logger.debug(f"🪢 Stitching context from {prev_agent.__class__.__name__}")
            # Re-inject last user message if needed
            if prev_agent.ctx and prev_agent.ctx.chat_ctx:
                last_msg = prev_agent.ctx.chat_ctx.last_user_message
                if last_msg:
                    context.chat_ctx.add_message(last_msg)

    async def _transfer_to_agent(
        self, agent_name: str, context: RunContext
    ) -> Tuple[Agent, str]:
        """
        Utility to transfer control to another agent by name.
        """
        userdata = context.userdata
        current_agent = context.session.current_agent
        next_agent = userdata.agents.get(agent_name)

        if not next_agent:
            logger.error(f"❌ Attempted transfer to unknown agent: {agent_name}")
            return current_agent, f"Agent {agent_name} not found."

        userdata.prev_agent = current_agent
        logger.info(f"➡️ Transferring from {current_agent.__class__.__name__} to {agent_name}")
        return next_agent, f"Transferring to {agent_name}."

    # ----------------------------------------------------------------
    # Default Tool: Go back to greeter
    # ----------------------------------------------------------------
    @function_tool()
    async def to_greeter(self, context: RunContext) -> Tuple[Agent, str]:
        """
        Return to greeter agent.
        Can be invoked by LLM when user says "go back" / "main menu".
        """
        return await self._transfer_to_agent("greeter", context)


# -------------------------------------------------------------------
# BaseFormAgent
# -------------------------------------------------------------------

class BaseFormAgent(BaseAgent, ABC):
    """
    Base class for form-filling agents (e.g. contact form, felling form).
    Adds scaffolding for collecting fields, asking confirmation, and submission.
    """

    @abstractmethod
    async def _start_form_collection(self, context: RunContext) -> str:
        """
        Kick off form collection flow (implemented by subclass).
        Example: ask for applicant name, or first field.
        """
        ...

    async def on_enter(self, context: RunContext) -> None:
        """
        Extended lifecycle: after base enter, begin form collection.
        """
        await super().on_enter(context)

        userdata = context.userdata
        if not getattr(userdata, "language_selected", False):
            logger.debug("🌐 No language selected yet, waiting for language agent/logic.")
            return

        # Start the actual form filling
        prompt = await self._start_form_collection(context)
        if prompt:
            await context.send(prompt)

    async def _ask_for_confirmation(self, context: RunContext) -> str:
        """
        Standard confirmation before form submission.
        """
        userdata = context.userdata
        userdata.awaiting_confirmation = True

        if getattr(userdata, "preferred_language", "english") == "kannada":
            return "ಧನ್ಯವಾದಗಳು. ನೀವು ಫಾರ್ಮ್ ಸಲ್ಲಿಸಲು ಬಯಸುವಿರಾ?"
        else:
            return "Thank you. Would you like to submit the form now?"

    async def _finalize_submission(self, context: RunContext) -> str:
        """
        Default finalize logic: can be overridden per form.
        """
        userdata = context.userdata
        userdata.should_submit = True
        logger.info(f"📨 Form submission flagged for {self.__class__.__name__}")
        return "Your form has been submitted successfully."