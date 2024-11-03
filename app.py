import os
import json
import time
import streamlit as st
from openai import OpenAI
from tavily import TavilyClient

# Initialize API clients
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# Define assistant behavior
assistant_prompt_instruction = """
You are a legal expert. Your goal is to provide answers based on information from the internet.
You must use the provided Tavily search API function to find relevant online information.
Please include relevant URL sources at the end of your answers.
Output responses in markdown format.
"""

# Create Streamlit interface
st.title("AI Legal Assistant")

# Initialize session state for assistant ID
if "assistant_id" not in st.session_state:
    st.session_state.assistant_id = None

def get_or_create_assistant():
    """Get existing assistant or create a new one"""
    if st.session_state.assistant_id:
        try:
            return client.beta.assistants.retrieve(st.session_state.assistant_id)
        except:
            pass
    
    assistant = client.beta.assistants.create(
        name="Legal Expert Assistant",
        instructions=assistant_prompt_instruction,
        model="gpt-4-1106-preview",
        tools=[{
            "type": "function",
            "function": {
                "name": "tavily_search",
                "description": "Search function",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        }]
    )
    st.session_state.assistant_id = assistant.id
    return assistant

def tavily_search(query):
    """Perform search using Tavily API"""
    return tavily_client.get_search_context(
        query,
        search_depth="advanced",
        max_tokens=8000
    )

def wait_for_run_completion(thread_id, run_id):
    """Wait for the assistant's run to complete"""
    while True:
        time.sleep(1)
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        if run_status.status in ['completed', 'failed', 'requires_action']:
            return run_status

def submit_tool_outputs(thread_id, run_id, tools_to_call):
    """Submit tool outputs for the assistant"""
    tool_output_array = []
    for tool in tools_to_call:
        output = None
        if tool.function.name == "tavily_search":
            output = tavily_search(
                query=json.loads(tool.function.arguments)["query"]
            )
        if output:
            tool_output_array.append({
                "tool_call_id": tool.id,
                "output": json.dumps(output)
            })
    return client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_output_array
    )

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
user_input = st.chat_input("Enter your legal query:")

if user_input:
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get or create assistant
    assistant = get_or_create_assistant()

    with st.spinner('Processing...'):
        # Create thread and message
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        # Create run
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        # Process run and handle outputs
        run = wait_for_run_completion(thread.id, run.id)
        if run.status == 'failed':
            st.error("An error occurred while processing your request.")
        elif run.status == 'requires_action':
            run = submit_tool_outputs(
                thread.id,
                run.id,
                run.required_action.submit_tool_outputs.tool_calls
            )
            run = wait_for_run_completion(thread.id, run.id)

        # Display assistant response
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        assistant_message = messages.data[0].content[0].text.value
        
        with st.chat_message("assistant"):
            st.markdown(assistant_message)
        st.session_state.messages.append({"role": "assistant", "content": assistant_message})
