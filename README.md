# 🌌 OneLastAI - Enterprise AI Agent Network Platform

<div align="center">

![OneLastAI Logo](https://img.shields.io/badge/OneLastAI-Enterprise%20Platform-blue?style=for-the-badge&logo=robot)
[![Python Version](https://img.shields.io/badge/Python-3.12+-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/Django-5.2+-green?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen?style=flat-square)](https://github.com/1-ManArmy/Django)

**The Ultimate AI Agent Network - 27 Specialized AI Agents in One Powerful Platform**

[🚀 Live Demo](https://onelastai.com) • [📖 Documentation](docs/) • [🛠️ API Reference](docs/api.md) • [💬 Community](https://github.com/1-ManArmy/Django/discussions)

</div>

---

## ✨ **Platform Overview**

OneLastAI is an enterprise-grade AI agent network that brings together 27 specialized AI agents, each designed for specific use cases. From creative content generation to business intelligence, our platform provides everything you need for AI-powered productivity.

### 🎯 **Key Features**

- **27 Specialized AI Agents** - Each with unique capabilities and personalities
- **Django REST Framework** - Robust API architecture with JWT authentication
- **Multi-AI Provider Support** - OpenAI, Anthropic Claude, Google AI integration
- **WebSocket Real-time Chat** - Live agent interactions with Django Channels
- **Multi-Payment Gateway** - Stripe and PayPal integration
- **Creative AI Integration** - RunwayML for video/image generation
- **Enterprise Authentication** - Django Allauth with social login support
- **Production Infrastructure** - PostgreSQL, Redis, Docker orchestration
- **Real-time Monitoring** - Celery task queue, comprehensive logging
- **API-First Design** - RESTful APIs with OpenAPI documentation

---

## 🌌 **AI Agent Network**

<table>
  <tr>
    <td align="center"><strong>🌌 Conversation</strong></td>
    <td align="center"><strong>💻 Technical</strong></td>
    <td align="center"><strong>🎨 Creative</strong></td>
    <td align="center"><strong>📊 Business</strong></td>
  </tr>
  <tr>
    <td>
      • 🔥 <strong>NeoChat</strong> - Advanced conversational AI<br>
      • 👥 <strong>PersonaX</strong> - Personality-driven chat<br>
      • 💕 <strong>Girlfriend</strong> - Emotional companion<br>
      • 🧘 <strong>EmotiSense</strong> - Emotion analysis<br>
      • 📞 <strong>CallGhost</strong> - Voice interactions<br>
      • 🌌 <strong>Memora</strong> - Memory-enhanced AI
    </td>
    <td>
      • 💻 <strong>ConfigAI</strong> - Technical configuration<br>
      • 🔍 <strong>InfoSeek</strong> - Research & analysis<br>
      • 📚 <strong>DocuMind</strong> - Document processing<br>
      • 🌐 <strong>NetScope</strong> - Network analysis<br>
      • 🔒 <strong>AuthWise</strong> - Security consulting<br>
      • 🕵️ <strong>SpyLens</strong> - Data investigation
    </td>
    <td>
      • 🎬 <strong>CineGen</strong> - Video production<br>
      • 🌌 <strong>ContentCrafter</strong> - Content creation<br>
      • 🌟 <strong>DreamWeaver</strong> - Creative ideation<br>
      • 💡 <strong>IdeaForge</strong> - Innovation catalyst<br>
      • 📝 <strong>AIBlogster</strong> - Blog generation<br>
      • 🗣️ <strong>VocaMind</strong> - Voice synthesis
    </td>
    <td>
      • 📊 <strong>DataSphere</strong> - Data analytics<br>
      • 📈 <strong>DataVision</strong> - Business intelligence<br>
      • 📋 <strong>TaskMaster</strong> - Project management<br>
      • 📑 <strong>Reportly</strong> - Report generation<br>
      • 🧬 <strong>DNAForge</strong> - Growth optimization<br>
      • ⚕️ <strong>CareBot</strong> - Health insights
    </td>
  </tr>
</table>

---

## 🚀 **Quick Start**

### **Prerequisites**

- Python 3.12+
- PostgreSQL 13+ or SQLite (for development)
- Redis 6+ (for caching and Celery)
- Node.js 18+ (for frontend assets)

### **1. Clone & Setup**

```bash
# Clone the repository
git clone https://github.com/1-ManArmy/Django.git
cd Django

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements/development.txt
```

### **2. Environment Configuration**

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

**Required Configuration:**
```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL for production, SQLite for development)
DATABASE_URL=postgresql://user:password@localhost:5432/onelastai
# or for SQLite: DATABASE_URL=sqlite:///db.sqlite3

# AI Services (choose at least one)
OPENAI_API_KEY=sk-...                    # OpenAI GPT models
ANTHROPIC_API_KEY=sk-ant-...             # Claude models
GOOGLE_AI_API_KEY=...                    # Google AI models
RUNWAYML_API_KEY=...                     # Creative AI

# Redis (for caching and Celery)
REDIS_URL=redis://localhost:6379/0

# Payment Processing (optional)
STRIPE_SECRET_KEY=sk_test_...            # Stripe payments
STRIPE_PUBLISHABLE_KEY=pk_test_...       # Stripe frontend
PAYPAL_CLIENT_ID=...                     # PayPal payments
PAYPAL_CLIENT_SECRET=...                 # PayPal payments

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### **3. Database & Migration Setup**

```bash
# Run database migrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser

# Load initial data (optional)
python manage.py loaddata fixtures/initial_data.json
```

### **4. Launch Application**

```bash
# Development mode
python manage.py runserver

# With Celery worker (separate terminal)
celery -A config worker -l info

# With Celery beat scheduler (separate terminal)
celery -A config beat -l info

# Docker deployment
docker-compose up -d
```

🎉 **Your platform is now running at http://localhost:8000**

---

## 🏗️ **Enterprise Infrastructure**

### **Cloud Architecture**

- **Database**: PostgreSQL with automatic backups (SQLite for development)
- **Compute**: Docker containers with horizontal scaling
- **Storage**: Local media storage (S3-compatible for production)
- **Caching**: Redis for sessions, caching, and message broker
- **Task Queue**: Celery with Redis broker
- **Monitoring**: Django logging, error tracking
- **Security**: Django Allauth with social authentication

### **Payment Processing**

```python
# Multi-provider payment support
from payments.services import PaymentService

payment_service = PaymentService(provider='stripe')
result = payment_service.process_payment(29.99, currency='usd')

# Subscription management
subscription = payment_service.create_subscription(customer_id, plan_id)
```

### **AI Service Integration**

```python
# Universal AI service
from ai_services.services import AIServiceFactory

ai_service = AIServiceFactory.create_service(provider='openai', model='gpt-4')
response = ai_service.complete("Analyze this business data...")

# Creative AI with RunwayML
runway_service = AIServiceFactory.create_service(provider='runwayml')
video_url = runway_service.generate_video("A sunset over mountains", duration=10)
```

---

## 📊 **API Documentation**

### **Authentication**

All API requests can be protected via Keycloak-backed sessions or JWTs:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.onelastai.com/v1/agents
```

### **Core Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/agents` | GET | List all available agents |
| `/api/v1/agents/{id}/chat` | POST | Chat with specific agent |
| `/api/v1/users/profile` | GET | Get user profile |
| `/api/v1/health` | GET | System health check |

### **Agent Interaction**

```bash
# Chat with NeoChat agent
curl -X POST https://api.onelastai.com/v1/agents/neochat/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me plan a marketing strategy",
    "context": "SaaS startup, B2B focus"
  }'
```

---

## 🔧 **Development**

### **Project Structure**

```
├── app/
│   ├── controllers/         # Agent controllers
│   ├── services/           # AI service integrations
│   │   ├── agents/         # Individual agent engines
│   │   ├── payment_service.rb
│   │   └── passage_auth_service.rb
│   └── views/              # Agent interfaces
├── config/
│   ├── mongoid.yml         # MongoDB configuration
│   ├── routes.rb           # Application routes
│   └── nginx/              # Production web server
├── docker-compose.yml      # Multi-service orchestration
├── setup.sh               # Automated setup script
└── DEPLOYMENT.md          # Deployment guide
```

### Agent configuration (per-agent models & behavior)

The file `config/agents.yml` controls per-agent defaults without changing code. Each agent can define:

- `model` one of: `llama32`, `gemma3`, `phi4`, `deepseek`, `gpt_oss` (mapped by `AiModelService`)
- `temperature`, `max_tokens`, `top_p` generation settings
- `system_prompt` text that is prepended to the agent’s personality

If an agent is not listed, it inherits from the `default` section. The `AiAgentEngine` reads this file on boot and applies overrides automatically.

Quick example:

```
default:
  model: llama32
  temperature: 0.7
agents:
  codemaster:
    model: phi4
    temperature: 0.3
    max_tokens: 3500
    system_prompt: |
      You are CodeMaster. Return runnable, secure code with tests.
```

Tip: ensure the selected `model` is available in your Ollama service and listed by `/ai/status`.

### **Adding New Agents**

1. **Create Agent Engine**:
```python
# agents/engines/your_agent_engine.py
from agents.engines.base import BaseAgentEngine

class YourAgentEngine(BaseAgentEngine):
    def __init__(self):
        super().__init__(
            name="YourAgent",
            description="Your agent description",
            capabilities=["capability1", "capability2"]
        )

        # Your agent logic here
        if context is None:
            context = {}
        return {"response": "Your agent response"}
```

2. **Create Views**:
```python
# agents/views.py
from django.shortcuts import render
from agents.engines.your_agent_engine import YourAgentEngine

def your_agent_view(request):
    agent = YourAgentEngine()
    return render(request, 'agents/your_agent.html', {'agent': agent})
3. **Add URLs**:
```python
# agents/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('your-agent/', views.your_agent_view, name='your_agent'),
]
```ruby
# config/routes.rb
get '/your-agent', to: 'your_agent#index'
```

### **Testing**

```bash
# Run test suite
python manage.py test

# Run specific agent tests
python manage.py test agents.tests

# Integration tests
python manage.py test api.tests
```

---

## 🚀 **Deployment**

### **Docker Deployment (Recommended)**

```bash
# Build and deploy with Docker Compose
docker-compose up -d

# Scale services
docker-compose up -d --scale web=3
```

### **Production Deployment**

```bash
# Production setup script
./setup.sh --production

# Manual deployment
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py migrate
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py collectstatic --noinput
DJANGO_SETTINGS_MODULE=config.settings.production gunicorn config.wsgi:application
```

### **Heroku Deployment**

```bash
# Deploy to Heroku
heroku create your-onelastai-app
git push heroku main
heroku run python manage.py migrate
```

---

## 📈 **Monitoring & Analytics**

### **Health Monitoring**

- **System Health**: `/health` endpoint
- **Database**: `/health/database`
- **AI Services**: `/health/ai_services`
- **Redis**: `/health/redis`

### **Performance Metrics**

- **Response Times**: New Relic integration
- **Error Tracking**: Sentry monitoring
- **User Analytics**: Built-in dashboard
- **API Usage**: Rate limiting and tracking

---

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### **Development Setup**

```bash
# Fork the repository
git clone https://github.com/your-username/fluffy-space-garbanzo.git

# Create feature branch
git checkout -b feature/amazing-new-agent

# Make your changes and test
python manage.py test

# Submit pull request
git push origin feature/amazing-new-agent
```

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **OpenAI** - GPT model integration
- **Anthropic** - Claude model support
- **RunwayML** - Creative AI capabilities
- **Passage** - Authentication infrastructure
- **MongoDB** - Database platform
- **Render** - Cloud deployment platform

---

## 📞 **Support**

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/1-ManArmy/fluffy-space-garbanzo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/1-ManArmy/fluffy-space-garbanzo/discussions)
- **Email**: mail@onelastai.com

---

<div align="center">

**Built with ❤️ by the OneLastAI Team**

[⭐ Star this repository](https://github.com/1-ManArmy/fluffy-space-garbanzo) if you find it helpful!

</div>b Codespaces ♥️ Ruby on Rails

Welcome to your shiny new Codespace running Rails! We've got everything fired up and running for you to explore Rails.

You've got a blank canvas to work on from a git perspective as well. There's a single initial commit with the what you're seeing right now - where you go from here is up to you!

Everything you do here is contained within this one codespace. There is no repository on GitHub yet. If and when you’re ready you can click "Publish Branch" and we’ll create your repository and push up your project. If you were just exploring then and have no further need for this code then you can simply delete your codespace and it's gone forever.
