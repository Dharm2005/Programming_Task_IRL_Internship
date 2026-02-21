# 🤖 Career Advisor AI — Production-Ready GenAI Chatbot

## 📌 Project Title

**Building a Production-Ready Domain-Specific Chatbot using Google Gemini GenAI API**

---

## 📖 Project Overview

This project implements a **production-ready Career Advisor Chatbot** powered by the **Google Gemini GenAI API**.

The chatbot provides domain-specific career guidance through intelligent conversations.
It follows real-world AI engineering practices including modular architecture, secure API handling, session memory, prompt engineering, and cloud deployment.

The objective of this project is to move beyond a basic AI demo and develop a **scalable, secure, and deployable GenAI application**.

---

## 🎯 Selected Domain

**Career Advisor Chatbot**

The chatbot assists users with:

* Career path suggestions
* Skill development guidance
* Learning roadmap recommendations
* Technology and industry insights
* Personalized career advice through multi-turn conversations

---

## ⚙️ Technical Implementation

### 1. Gemini API Integration

* Integrated **Google Gemini GenAI API**
* Secure API key management using environment variables
* Modular API client (`services/gemini_client.py`)
* Structured request & response handling
* Exception handling and fallback responses
* API logging and monitoring
* Token-efficient prompt usage

---

### 2. Multi-Turn Conversation Memory

* Session-based chat memory
* Context preserved across conversation turns
* Structured history management
* Memory reset on page refresh

Module:

```
memory/session_memory.py
```

---

### 3. Advanced Prompt Engineering

* Role-based system prompting
* Domain-specific career advisor instructions
* Controlled response behavior
* Reusable and configurable prompts

Module:

```
prompts/career_prompt.py
```

---

### 4. Backend Architecture

The application follows **clean architecture principles**:

* Separation of concerns
* Modular design
* Configuration-driven setup
* No hardcoded credentials

Project Modules:

```
config/     → application settings
services/   → Gemini API integration
memory/     → conversation memory
prompts/    → prompt engineering
utils/      → logging utilities
```

---

### 5. User Interface

Built using **Streamlit**

Features:

* Chat-style conversational UI
* Real-time response streaming
* Conversation history display
* Loading indicator
* Light theme interface
* Simple and user-friendly design

Entry File:

```
app.py
```

---

### 6. Cloud Deployment (AWS EC2)

The chatbot is deployed on an **AWS EC2 instance**.

Deployment includes:

* Public IP accessibility
* Environment variable configuration
* Secure API key handling
* Open port configuration
* Background execution of Streamlit app

---

## 🏗️ System Architecture

```
User
   ↓
Streamlit UI
   ↓
Backend Layer
   ↓
Prompt Engineering Module
   ↓
Gemini GenAI API
   ↓
Response Processing
   ↓
UI Rendering
```

---

## 📂 Project Structure

```
career-advisor-chatbot/
│
├── .streamlit/
│   └── config.toml
├── config/
├── memory/
├── prompts/
├── services/
├── utils/
├── app.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_api_key_here
```

⚠️ `.env` is excluded from version control for security.

---

## 💻 Local Setup Instructions

### 1. Clone Repository

```
git clone <your-repo-url>
cd career-advisor-chatbot
```

### 2. Create Virtual Environment

```
python -m venv venv
```

Activate environment:

**Windows**

```
venv\Scripts\activate
```

**Linux / Mac**

```
source venv/bin/activate
```

### 3. Install Dependencies

```
pip install -r requirements.txt
```

### 4. Add Environment Variable

Create `.env` file and add Gemini API key.

### 5. Run Application

```
streamlit run app.py
```

---

## ☁️ AWS EC2 Deployment (Summary)

1. Launch EC2 instance
2. Connect via SSH
3. Clone GitHub repository
4. Install Python & dependencies
5. Configure `.env` variables
6. Open port **8501** in security group
7. Run Streamlit application

---

## 📦 Expected Deliverables

* ✅ Fully functional GenAI chatbot
* ✅ Modular production-ready codebase
* ✅ GitHub repository
* ✅ AWS EC2 deployment
* ✅ Public access link
* ✅ Documentation & architecture explanation

---

## 🧰 Tech Stack

* Python
* Streamlit
* Google Gemini GenAI API
* AWS EC2
* Environment Variables (.env)
* Modular Backend Architecture

---

## 🚀 Future Improvements

* Persistent database memory
* User authentication
* Conversation analytics
* Docker containerization
* CI/CD automation

---

## 👨‍💻 Author

Internship Project — Production-Ready GenAI Chatbot
Career Advisor AI System


Dharm Dobariya
📧 My E-mail : dharmdobariya7016@gmail.com
🔗 [My LinkedIn](https://www.linkedin.com/in/dharm-dobariya-42408134b)