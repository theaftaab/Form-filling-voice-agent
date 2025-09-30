import pytest
from unittest.mock import AsyncMock, patch
from config.settings import TEST_LLM
from livekit.agents import AgentSession
from agents.greeter_agent import GreeterAgent
from models.userdata import UserData
from utils.frontend import send_to_frontend
from livekit.agents import JobContext, JobProcess, WorkerOptions, cli


@pytest.mark.asyncio
async def test_greeter_agent():
    userdata = UserData()
    userdata.ctx = JobContext(room="test-room")
    userdata.language_selected = False
    async with AgentSession(llm=TEST_LLM,userdata=UserData()) as session:
        agent = GreeterAgent()
        await session.start(agent)

        # # Check the events that happened automatically
        # result = await session.run(user_input="")  # empty input, triggers on_enter messages
        #
        # # Grab the first assistant message
        # greeting_event = result.expect.next_event(type="message").event().item
        #
        # assert greeting_event.role == "assistant"
        # assert "Hello" in greeting_event.content[0]
        # assert "English or Kannada" in greeting_event.content[0]

        # Test Intent Detection for contact
        contact_request = "I want to make a complaint about a department service"
        with patch("utils.frontend.send_to_frontend", new_callable=AsyncMock):
            result2 = await session.run(user_input=contact_request)
            await result2.expect.next_event().is_message(role="assistant").judge(
                TEST_LLM,intent="Greeter detects contact intent and routes to contact form"
            )

        userdata = session.userdata
        assert userdata.requested_route == "/contact-form"

        # Test Intent Detection for felling
        felling_request = "I need a tree cutting permission"
        with patch("utils.frontend.send_to_frontend",new_callable=AsyncMock):
            result3 = await session.run(user_input=felling_request)
            await result3.expect.next_event().is_message(role="assistant").judge(
                TEST_LLM,intent="Greeter detects felling intent and routes to felling form"
            )

        assert userdata.requested_route == "/felling-transit-permission"

        # Test unknown intent
        unknown_request= "Can you tell me the stock price of NVIDIA?"
        result4 = await session.run(user_input=unknown_request)
        await result4.expect.next_event().is_message(role="assistant").judge(
            TEST_LLM, intent = "Greeter replies politely that it can't handle the given request."
        )

        result4.expect.no_more_events()