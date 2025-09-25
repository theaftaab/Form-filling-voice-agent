import json
from config.settings import logger
# Session creation is now handled directly in main.py
from handlers.data_handler import register_data_handler
from agents.registry import AGENT_REGISTRY
from models.userdata import UserData
from livekit.agents import JobContext, JobProcess, WorkerOptions, cli
from livekit.agents.voice import AgentSession
from livekit.agents.voice.room_io import RoomInputOptions
from livekit.plugins import openai, silero, soniox
from livekit import rtc


def extract_agent_type_from_room_name(room_name: str) -> str:
    """Extract agent type from room name that contains __agent=type"""
    try:
        if "__agent=" in room_name:
            agent_type = room_name.split("__agent=")[1].split("__")[0]
            # Return the specific agent type if it's valid
            if agent_type in ["contact", "felling"]:
                return agent_type
    except:
        pass
    return "greeter"  # Default to greeter for intent detection


def prewarm(proc: JobProcess):
    """Pre-warm Silero VAD model to avoid TLS issues during runtime"""
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    try:
        logger.info(f"🚀 Starting agent for room: {ctx.room.name}")
        await ctx.connect()
        logger.info("✅ Connected to room")

        # Initialize UserData with context
        userdata = UserData(ctx=ctx)

        # Instantiate all agents from registry
        agents = {name: cls() for name, cls in AGENT_REGISTRY.items()}
        userdata.agents = agents

        # Register data handlers
        register_data_handler(ctx, userdata)

        # Get pre-warmed VAD or load it with custom settings
        vad = ctx.proc.userdata.get("vad") or silero.VAD.load(
            min_silence_duration=1.0,  # Wait 1 second of silence before ending
            min_speech_duration=0.1,   # Minimum speech duration
            speech_pad_ms=300,         # Add padding around speech
        )

        # Configure initial Soniox STT
        initial_soniox_options = soniox.STTOptions(
            language_hints=["en", "kn"],  # Start with English and Kannada
            context=(
                "Karnataka Government voice assistant for language selection. "
                "User will say 'English' or 'Kannada' to select language. "
                "Wait for complete phrases - do not cut off speech early. "
                "Services: Contact Form, Felling Transit Permission."
            )
        )

        # Determine which agent to start with based on room name
        agent_type = extract_agent_type_from_room_name(ctx.room.name)
        logger.info(f"🎯 Detected agent type from room name: {agent_type}")

        # Set up userdata based on agent type
        if agent_type == "contact":
            userdata.agent_type = "contact"
            userdata.language_selected = True  # Skip language selection
            userdata.preferred_language = "english"  # Default to English
            selected_agent = agents["contact"]
        elif agent_type == "felling":
            userdata.agent_type = "felling"
            userdata.language_selected = True  # Skip language selection
            userdata.preferred_language = "english"  # Default to English
            selected_agent = agents["felling"]
        else:
            # Default to greeter for intent detection
            selected_agent = agents["greeter"]

        # Create session with proper configuration
        session = AgentSession[UserData](
            userdata=userdata,
            llm=openai.LLM(model="gpt-4o-mini"),
            stt=soniox.STT(params=initial_soniox_options),
            tts=openai.TTS(voice="alloy"),
            vad=vad,
            turn_detection="vad",
            max_tool_steps=5,
        )

        logger.info(f"🎙️ Starting with agent: {agent_type}")
        await session.start(
            agent=selected_agent,
            room=ctx.room,
            room_input_options=RoomInputOptions(),
        )

    except Exception as e:
        logger.error(f"❌ Error in entrypoint: {e}", exc_info=True)
        raise
    finally:
        logger.info(f"🏁 Session ended for room: {ctx.room.name}")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))