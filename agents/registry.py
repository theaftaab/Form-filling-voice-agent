from .greeter_agent import GreeterAgent
from .contact_agent import ContactFormAgent
from .felling_agent import FellingFormAgent

# Central registry of available agent classes
# Each agent is instantiated per-session in main.py
AGENT_REGISTRY = {
    "greeter": GreeterAgent,
    "contact": ContactFormAgent,
    "felling": FellingFormAgent,
}