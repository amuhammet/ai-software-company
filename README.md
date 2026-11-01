# 🚀 AI Software Factory

An autonomous, self-improving AI software company powered by a multi-agent system. This system doesn't just generate code; it architectures, develops, tests, and learns from its own failures using a stateful cyclic workflow.

## 🛠 Architecture
The system operates as a state machine with the following agent roles:
- **CEO/Orchestrator**: Manages the overall goal and routes tasks.
- **Researcher**: Gathers technical requirements and API documentation.
- **Architect**: Designs the system structure and blueprints.
- **Developer**: Implements the code based on the blueprint.
- **QA/Reviewer**: Validates code in a hardened sandbox.
- **PostMortem**: Analyzes failures to generate "Semantic Lessons."
- **SelfUpdater**: Optimizes agent prompts based on historical data.

## 📦 Key Features
- **State-Based Workflow**: Uses cyclic routing (Fix Loops) instead of linear sequences.
- **Hardened Sandbox**: Secure code execution using isolated Docker containers (No network, resource limits).
- **Hybrid Memory**: Redis for session state and ChromaDB for long-term semantic learning (RAG).
- **CI/CD Integration**: Automated release pipeline via GitHub Actions.
- **Local LLM Support**: Integration via Ollama for privacy and cost-efficiency.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (for the secure sandbox)
- Ollama (for local LLM execution)

### Installation
```bash
git clone <your-repo-url>
cd ai-software-factory
pip install -r requirements.txt
