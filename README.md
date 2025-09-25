# Karnataka Government Voice Assistant Backend

A multilingual voice-powered form filling assistant for Karnataka Government services, built with LiveKit and OpenAI. Supports English and Kannada languages for Contact Forms and Tree Felling Permission applications.

## 🚀 Features

- **Multilingual Support**: English and Kannada voice interaction
- **Multiple Services**: 
  - Contact Form for general inquiries
  - Tree Felling Transit Permission form
- **Voice-First Interface**: Complete form filling through voice commands
- **Real-time Communication**: LiveKit-powered voice streaming
- **Intelligent Routing**: Automatic agent selection based on user intent
- **Form Validation**: Built-in field validation and confirmation

## 🏗️ Architecture

### Agent System
- **Greeter Agent**: Handles language selection and service routing
- **Contact Form Agent**: Collects contact information and inquiries
- **Felling Form Agent**: Processes tree cutting permission applications
- **Base Agent**: Common functionality shared across all agents

### Data Flow
```
User Voice Input → LiveKit → Soniox STT → Agent Processing → OpenAI LLM → OpenAI TTS → LiveKit → User Audio Output
                                    ↓
                            Form Data Collection
                                    ↓
                            Frontend Data Channel
```

## 📋 Prerequisites

- Python 3.11+
- LiveKit Cloud account
- OpenAI API key
- Soniox API key (for STT)

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd voice-formfill-backend
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
Create a `.env` file with the following:
```env
# LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-url
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

# AI Services
OPENAI_API_KEY=your-openai-key
SONIOX_API_KEY=your-soniox-key

# Optional
ELEVEN_API_KEY=your-elevenlabs-key
GROQ_API_KEY=your-groq-key
LOG_LEVEL=INFO
```

## 🚀 Running the Backend

### Development Mode
```bash
# Using the shell script (recommended for macOS)
./run.sh

# Or directly with Python
python main.py dev
```

### Testing
```bash
# Run comprehensive tests
python test_project.py

# Test specific components
python -c "from agents.registry import AGENT_REGISTRY; print('Agents loaded:', list(AGENT_REGISTRY.keys()))"
```

## 🌐 Frontend Integration

### Data Communication
The backend communicates with the frontend through LiveKit's data channel using JSON messages.

#### Outgoing Data (Backend → Frontend)
The backend sends form data updates via `send_to_frontend()` function:

```json
{
  "company": "Example Corp",
  "subject": "Technical Support",
  "message": "Need help with...",
  "phone": "9876543210",
  "should_submit": false,
  "requested_route": "/contact-form"
}
```

#### Incoming Data (Frontend → Backend)
The frontend can send field updates to the backend:

```json
{
  "field": "company",
  "value": "Updated Company Name"
}
```

### Form Data Structures

#### Contact Form
```json
{
  "company": "string",
  "subject": "string", 
  "message": "string",
  "phone": "string",
  "should_submit": "boolean"
}
```

#### Felling Permission Form
```json
{
  "applicant_name": "string",
  "father_name": "string",
  "mobile_number": "string",
  "email_id": "string",
  "address": "string",
  "village": "string",
  "taluk": "string",
  "district": "string",
  "pincode": "string",
  "khata_number": "string",
  "survey_number": "string",
  "total_extent_acres": "string",
  "guntas": "string",
  "anna": "string",
  "tree_species": "string",
  "tree_age": "string",
  "tree_girth": "string",
  "files_uploaded": "object",
  "should_submit": "boolean"
}
```

### Agent Selection
You can direct users to specific agents using room names:

- **Default/Greeter**: `room-name` (language selection + intent detection)
- **Contact Form**: `room-name__agent=contact` (direct to contact form)
- **Felling Form**: `room-name__agent=felling` (direct to felling form)

## 🔧 Configuration

### Language Settings
- **English**: Strict romanization, ASCII-only output
- **Kannada**: Native Kannada script support with English fallback

### STT Configuration
- **Primary**: Soniox with language hints
- **Context**: Government form terminology
- **Endpointing**: Optimized for complete phrases

### TTS Configuration
- **Provider**: OpenAI TTS
- **Voice**: Alloy (configurable)
- **Languages**: English and Kannada support

## 📁 Project Structure

```
├── agents/
│   ├── base_agent.py       # Common agent functionality
│   ├── greeter_agent.py    # Language selection & routing
│   ├── contact_agent.py    # Contact form handling
│   ├── felling_agent.py    # Felling permission form
│   └── registry.py         # Agent registration
├── models/
│   ├── userdata.py         # Session data management
│   ├── contact_form.py     # Contact form data model
│   ├── felling_form.py     # Felling form data model
│   └── base_form.py        # Common form functionality
├── handlers/
│   ├── data_handler.py     # Frontend data communication
│   └── sessions.py         # Session management
├── utils/
│   ├── frontend.py         # Frontend communication utilities
│   └── language.py         # Language processing utilities
├── config/
│   └── settings.py         # Configuration management
├── main.py                 # Application entry point
├── test_project.py         # Comprehensive testing
└── run.sh                  # Startup script
```

## 🔍 Debugging

### Common Issues

1. **No audio in LiveKit playground**
   - Check browser microphone permissions
   - Verify OpenAI API key is valid
   - Ensure TTS service is accessible

2. **Import errors**
   - Run `python test_project.py` to check all imports
   - Verify all dependencies are installed

3. **Agent not responding**
   - Check logs for agent selection: `🎯 Detected agent type`
   - Verify agent enters successfully: `🔄 Entering [AgentName]`

### Logging
Logs are written to both console and files in the `logs/` directory:
- **Level**: Configurable via `LOG_LEVEL` environment variable
- **Format**: `[timestamp] [level] logger: message`
- **Components**: Separate loggers for agents, handlers, and utilities

## 🚦 API Endpoints

The backend doesn't expose traditional REST endpoints but communicates through:

1. **LiveKit Room Connection**: Voice streaming and real-time communication
2. **Data Channel**: JSON message passing for form data
3. **Agent Selection**: Room name-based routing

## 🔐 Security

- **Environment Variables**: Sensitive keys stored in `.env` file
- **SSL/TLS**: All LiveKit communication encrypted
- **Input Validation**: Form data validated before processing
- **Error Handling**: Graceful error handling with user feedback

## 📈 Monitoring

Monitor the application through:
- **Console Logs**: Real-time agent activity
- **LiveKit Dashboard**: Connection and room statistics  
- **Error Tracking**: Exception logging with stack traces

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests: `python test_project.py`
4. Submit a pull request

## 📄 License

[Add your license information here]

## 🆘 Support

For issues and questions:
1. Check the logs for error messages
2. Run the test suite to identify configuration issues
3. Verify all environment variables are set correctly
4. Check LiveKit and OpenAI service status