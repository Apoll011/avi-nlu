# Avi NLU API

## Overview
**Avi NLU API** is a high-performance server dedicated to **Natural Language Understanding (NLU)** for the Avi ecosystem. It handles **intent recognition** for voice commands and structured inputs, serving as the computational core for Avi’s voice assistant.

This API is designed to integrate seamlessly with **AECP-enabled devices** such as microphones, smart buttons, and other triggers, providing fast, reliable parsing of user intents.

## Features
- **Intent Recognition Only**: Focused on parsing user queries into structured intents and slots.
- **Multi-language Support**: Supports English and Portuguese out-of-the-box.
- **FastAPI Backend**: Lightweight, modern Python web framework for high-performance endpoints.
- **Containerized Deployment**: Docker-ready for easy setup and distribution.
- **Low Latency**: Optimized for real-time voice command processing.

## Requirements
- Docker Engine (v19.03.0+ recommended)
- 2GB RAM minimum (4GB recommended for training models)
- Network access to the **Avi Core Node** for full integration

## Installation

### Using Docker (Recommended)
Build the Docker image:
```bash
docker build -t avi-nlu-api .
```

### Manual Installation
1. Clone the repository:
```bash
git clone https://github.com/Apoll011/avi-nlu.git
cd Avi-NLU-API
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download language models:
```bash
python -m snips_nlu download-language-entities pt_pt
python -m snips_nlu download-language-entities en
```

## Usage

### Docker Deployment
Run the server:
```bash
docker run -p 1178:1178 avi-nlu-api
```
This will:
- Map port `1178` on the host to port `1178` in the container.
- Start the Avi NLU API server using **uvicorn**.

### Configuration
The server configuration is stored in `config.py`:
- Default host: `0.0.0.0`
- Default port: `1178`
- Model storage paths for intent recognition

## NLU Components

### Intent Recognition
The **IntentKit** handles:
- Parsing text or audio input into structured intents
- Slot extraction for multiple parameters
- Support for multiple languages
- Integration with AECP to receive raw audio or pre-parsed text from triggers
- Persistent storage of trained intent models

## Project Structure
```
├── features/
│   └── intent_recognition/     # Intent models and datasets
│       └── snips/              # Snips NLU models
├── main.py                     # FastAPI application
├── kit.py                      # Core NLU components
├── config.py                   # Server configuration
├── Dockerfile                  # Docker configuration
└── requirements.txt            # Python dependencies
```

## API Endpoints
The server exposes FastAPI endpoints for:
- Receiving text or audio input and returning structured **intents and slots**
- Checking server health and status

## Timezone
The server operates in **Atlantic/Cape Verde timezone (UTC-1)**.

## Docker Image
- Based on **Python 3.8-slim**
- Pre-loaded with Snips NLU utilities
- Includes models for English and Portuguese

## License
This project is licensed under the **MIT License** – see the LICENSE file for details.

## Contact
- GitHub: [@Apoll011](https://github.com/YourUsername)
- Related Project: [Avi Core Node](https://github.com/Apoll011/Avi-Core)
