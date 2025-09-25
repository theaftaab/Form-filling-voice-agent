#!/usr/bin/env python3
"""
Simple test script to verify the project structure and imports work correctly.
Run this before starting the full agent to catch any import or configuration issues.
"""

import sys
import os
from dotenv import load_dotenv

def test_imports():
    """Test that all imports work correctly"""
    print("🧪 Testing imports...")
    
    try:
        # Test core imports
        from config.settings import logger
        print("✅ Config imports work")
        
        # Test model imports
        from models.userdata import UserData
        from models.contact_form import ContactFormData
        from models.felling_form import FellingFormData
        print("✅ Model imports work")
        
        # Test agent imports
        from agents.registry import AGENT_REGISTRY
        from agents.greeter_agent import GreeterAgent
        from agents.contact_agent import ContactFormAgent
        from agents.felling_agent import FellingFormAgent
        print("✅ Agent imports work")
        
        # Test handler imports
        from handlers.data_handler import register_data_handler
        print("✅ Handler imports work")
        
        # Test utility imports
        from utils.frontend import send_to_frontend
        print("✅ Utility imports work")
        
        # Test LiveKit imports
        from livekit.agents import JobContext, WorkerOptions, cli
        from livekit.agents.voice import AgentSession
        from livekit.plugins import openai, silero, soniox
        print("✅ LiveKit imports work")
        
        print("🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_environment():
    """Test environment variables"""
    print("\n🔧 Testing environment variables...")
    
    load_dotenv()
    
    required_vars = [
        "LIVEKIT_URL",
        "LIVEKIT_API_KEY", 
        "LIVEKIT_API_SECRET",
        "OPENAI_API_KEY",
        "SONIOX_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"✅ {var} is set")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("🎉 All required environment variables are set!")
    return True

def test_agent_registry():
    """Test that agent registry is properly configured"""
    print("\n🤖 Testing agent registry...")
    
    try:
        from agents.registry import AGENT_REGISTRY
        
        expected_agents = ["greeter", "contact", "felling"]
        
        for agent_name in expected_agents:
            if agent_name not in AGENT_REGISTRY:
                print(f"❌ Missing agent: {agent_name}")
                return False
            print(f"✅ Agent '{agent_name}' registered")
        
        # Test instantiation
        agents = {name: cls() for name, cls in AGENT_REGISTRY.items()}
        print(f"✅ Successfully instantiated {len(agents)} agents")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent registry error: {e}")
        return False

def test_form_models():
    """Test form model functionality"""
    print("\n📝 Testing form models...")
    
    try:
        from models.contact_form import ContactFormData
        from models.felling_form import FellingFormData
        
        # Test contact form
        contact_form = ContactFormData()
        missing = contact_form.get_missing_fields()
        print(f"✅ Contact form has {len(missing)} required fields")
        
        # Test field setting
        contact_form.set_field("company", "Test Company")
        assert contact_form.company == "Test Company"
        print("✅ Contact form field setting works")
        
        # Test felling form
        felling_form = FellingFormData()
        missing = felling_form.get_missing_fields()
        print(f"✅ Felling form has {len(missing)} required fields")
        
        # Test field setting
        felling_form.set_field("applicant_name", "Test Name")
        assert felling_form.applicant_name == "Test Name"
        print("✅ Felling form field setting works")
        
        return True
        
    except Exception as e:
        print(f"❌ Form model error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting project tests...\n")
    
    tests = [
        test_imports,
        test_environment,
        test_agent_registry,
        test_form_models
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Your project is ready to run.")
        print("\nTo start the agent, run:")
        print("python main.py dev")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)