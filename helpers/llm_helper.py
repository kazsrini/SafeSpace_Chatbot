import ollama
from config import Config

system_prompt = Config.SYSTEM_PROMPT

def chat(user_prompt, model, conversation_history):
    messages = [{'role': 'assistant', 'content': system_prompt}] + conversation_history + [{'role': 'user', 'content': user_prompt}]
    stream = ollama.chat(
        model=model,
        messages=messages,
        stream=True,
    )
    
    # Fallback response for non-relevant questions
    fallback_message = "I'm here to help with medical or mental health-related questions. Please ask a relevant question."
    for chunk in stream:
        content = chunk.get('message', {}).get('content', '')
        if content.strip() == '':
            return [{"message": {"content": fallback_message}}]  # Fallback response
        return stream


# handles stream response back from LLM
def stream_parser(stream):
    """Parse and concatenate all chunks of the response."""
    response = ""  # Initialize an empty string to store the response
    for chunk in stream:
        content = chunk.get('message', {}).get('content', '')
        response += content  # Concatenate all chunks
    return response.strip()  # Return the complete response with no leading/trailing spaces

