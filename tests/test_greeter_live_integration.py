import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from config.settings import TEST_LLM
from livekit.agents import AgentSession
from agents.greeter_agent import GreeterAgent
from models.userdata import UserData
from utils.frontend import send_to_frontend
from livekit.agents import JobContext, JobProcess, WorkerOptions, cli
from agents.registry import AGENT_REGISTRY


@pytest.mark.asyncio
async def test_greeter_agent():
    agents = {name: cls() for name, cls in AGENT_REGISTRY.items()}
    fake_ctx = MagicMock()
    fake_ctx.room.name = "test_room"
    fake_ctx.proc.userdata = {}
    fake_ctx.connect = AsyncMock()
    userdata = UserData()
    userdata.ctx = fake_ctx
    userdata.language_selected = False
    userdata.agents = agents
    async with AgentSession(llm=TEST_LLM,userdata=userdata) as session:
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
        with patch("agents.greeter_agent.send_to_frontend", new_callable=AsyncMock):
            result2 = await session.run(user_input=contact_request)

            # Find the next assistant message, skipping function call events
            chat_event = None
            try:
                while True:
                    e = result2.expect.next_event(type="message")
                    if e:
                        chat_event = e
                        break
            except Exception:
                pass

            assert chat_event is not None
            print("chat_event type:", type(chat_event))
            print("chat_event dir:", dir(chat_event))
            print("chat_event repr:", repr(chat_event))
            print("Has event method:", hasattr(chat_event, "event"))
            print("Is event callable:", callable(getattr(chat_event, "event", None)))
            # Uncomment below to see the actual event if available
            # print("chat_event.event():", chat_event.event() if callable(getattr(chat_event, "event", None)) else chat_event.event)
            assert chat_event.event().role == "assistant"
            # Optionally judge with TEST_LLM
            await chat_event.judge(TEST_LLM, intent="Greeter detects contact intent and routes to contact form")

        userdata = session.userdata
        assert userdata.requested_route == "/contact-form"

        # Test Intent Detection for felling
        felling_request = "I need a tree cutting permission"
        with patch("agents.greeter_agent.send_to_frontend", new_callable=AsyncMock):
            result3 = await session.run(user_input=felling_request)

            # Grab next assistant message
            chat_event3 = None
            try:
                while True:
                    e = result3.expect.next_event(type="message")
                    if e:
                        chat_event3 = e
                        break
            except Exception:
                pass

            assert chat_event3 is not None
            assert chat_event3.event().role == "assistant"
            await chat_event3.judge(TEST_LLM, intent="Greeter detects felling intent and routes to felling form")

        assert userdata.requested_route == "/felling-transit-permission"


        # Unknown intent
        unknown_request = "Can you tell me the stock price of NVIDIA?"
        result4 = await session.run(user_input=unknown_request)

        chat_event4 = None
        try:
            while True:
                e = result4.expect.next_event(type="message")
                if e:
                    chat_event4 = e
                    break
        except Exception:
            pass

        assert chat_event4 is not None
        assert chat_event4.event().role == "assistant"
        await chat_event4.judge(TEST_LLM, intent="Greeter replies politely that it can't handle the given request.")

        result4.expect.no_more_events()