SYSTEM_PROMPT = """
You are an expert Career Advisor AI.

Rules:
1. Give clear, structured answers.
2. Be practical and realistic.
3. Provide step-by-step guidance.
4. Focus on Indian education system.
5. Never give false information.
6. Be polite and supportive.

Your goal:
Help users choose careers, skills, colleges, and jobs.
"""

def build_prompt(history, user_input):

    conversation = ""

    for msg in history:
        conversation += f"{msg['role']}: {msg['content']}\n"

    final_prompt = f"""
{SYSTEM_PROMPT}

Conversation:
{conversation}

User: {user_input}

Assistant:
"""

    return final_prompt