import os
import json
import time
import streamlit as st
from openai import OpenAI
from tavily import TavilyClient

# Initialize API clients
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
tavily_client = TavilyClient(api_key="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")

# Define assistant behavior
assistant_prompt_instruction = """
You are a legal expert. Your goal is to provide answers based on information from the internet.
You must use the provided Tavily search API function to find relevant online information.
Please include relevant URL sources at the end of your answers.
Output responses in markdown format.
"""

# Create Streamlit interface
st.title("AI Legal Assistant")
user_input = st.text_input("Enter your legal query:")

if user_input:
    with st.spinner('Processing...'):
        # Search function
        def tavily_search(query):
            return tavily_client.get_search_context(
                query,
                search_depth="advanced",
                max_tokens=8000
            )

        # Create OpenAI assistant
        assistant = client.assistants.create(
            name="Legal Expert Assistant",
            instructions=assistant_prompt_instruction,
            model="gpt-4o",
            tools=[{
                "type": "function",
                "function": {
                    "name": "tavily_search",
                    "description": "Retrieve information on recent events from the web.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to use"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }]
        )

        # Create thread and message
        thread = client.threads.create()
        message = client.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input,
        )
        run = client.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        # Helper functions
        def wait_for_run_completion(thread_id, run_id):
            while True:
                time.sleep(1)
                run_status = client.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run_id
                )
                if run_status.status in ['completed', 'failed', 'requires_action']:
                    return run_status

        def submit_tool_outputs(thread_id, run_id, tools_to_call):
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
                        "output": output
                    })
            return client.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=tool_output_array
            )

        # Process run and handle outputs
        run = wait_for_run_completion(thread.id, run.id)
        if run.status == 'failed':
            st.error(run.error)
        elif run.status == 'requires_action':
            run = submit_tool_outputs(
                thread.id,
                run.id,
                run.required_action.submit_tool_outputs.tool_calls
            )
            run = wait_for_run_completion(thread.id, run.id)

        # Display results
        def get_messages_from_thread(thread_id):
            messages = client.threads.messages.list(thread_id=thread_id)
            return "\n".join([
                f"{msg.role}: {msg.content[0].text.value}"
                for msg in messages
            ])

        response_text = get_messages_from_thread(thread.id)
        st.text_area("Response", value=response_text, height=500)
