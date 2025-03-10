import json
import os
import requests

def get_gemini_response(message):
    api_key = os.environ["GEMINI_API_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-002:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": message}]}]}
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

def get_openai_response(message):
    api_key = os.environ["OPENAI_API_KEY"]
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    data = {"model": "gpt-3.5-turbo", "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": message}]}
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def get_claude_response(message):
    api_key = os.environ["CLAUDE_API_KEY"]
    url = "https://api.anthropic.com/v1/messages"
    headers = {"Content-Type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"}
    data = {"model": "claude-3-opus-20240229", "max_tokens": 1024, "messages": [{"role": "user", "content": message}]}
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["content"][0]["text"]


def main():
    # Get inputs from the workflow
    ai_type = os.environ["INPUT_AI_TYPE"]
    user_message = os.environ["INPUT_USER_MESSAGE"]

    # Get conversation history from the previous step
    history_str = os.environ.get("STEPS_GET-HISTORY_OUTPUTS_HISTORY", "[]")  # Default to empty list
    try:
      conversation_history = json.loads(history_str)
    except json.JSONDecodeError:
      conversation_history = []
      print("Warning: Invalid JSON in conversation history.  Starting fresh.")


    # Add user message to history
    conversation_history.append({"role": "user", "content": user_message})

    # Get AI response
    try:
        if ai_type == "gemini":
            ai_response = get_gemini_response(user_message)
        elif ai_type == "openai":
            ai_response = get_openai_response(user_message)
        elif ai_type == "claude":
            ai_response = get_claude_response(user_message)
        else:
            ai_response = "Error: Invalid AI type selected."
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")  # Log the error
        ai_response = f"Error: Could not get a response from the AI. {e}"
    except Exception as e:
        print(f"An unexpected error occurred: {e}") # Log more general errors.
        ai_response = f"Error: An unexpected error occurred. {e}"


    # Add AI response to history
    conversation_history.append({"role": "ai", "content": ai_response})

    # Save updated history to file
    with open("conversation_history.json", "w") as f:
        json.dump(conversation_history, f, indent=2)

    print(f"Conversation history updated.  AI Response: {ai_response}") # For workflow logs


if __name__ == "__main__":
    main()
