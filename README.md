# ChatGPT-like Chat App Using Assistants API

This project is a Streamlit web application that simulates a ChatGPT-like chat interface using OpenAI's Assistants API. It includes features such as web scraping, converting text to PDF, and uploading files to OpenAI.

## Features

- Set up a Streamlit page with a custom title and icon.
- Scrape text from a website URL.
- Convert text content to a PDF file.
- Upload files to OpenAI and manage file IDs.
- Start a chat session with OpenAI's Assistants API.
- Process messages with citations and format them as footnotes.

## Prerequisites

- Python 3.6 or higher
- Streamlit
- BeautifulSoup4
- Requests
- pdfkit
- OpenAI Python client

## Installation

To install the required libraries, run the following command:

```bash
pip install streamlit beautifulsoup4 requests pdfkit openai
```

# Usage

1. Set your OpenAI API key in the Streamlit app sidebar.
2. Optionally, enter a website URL in the sidebar to scrape and organize into a PDF.
3. Use the sidebar to upload files to OpenAI embeddings.
4. Click 'Start Chat' to begin the conversation with the assistant.

# Configuration

Before running the application, ensure to set the following:

- OpenAI Assistant ID
- Path to wkhtmltopdf for PDF conversion

# Running the App

To start the Streamlit app, navigate to the project directory and run the following command:

```bash
streamlit run app.py
```

> Note: Replace app.py with the actual name of your Python script.
> 

# Contributing

Contributions to this project are welcome. Please fork the repository, make your changes, and submit a pull request.

# License

This project is open-source and available under the MIT License.
