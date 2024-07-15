# Issue Analyzer

This project processes customer support transcripts to identify and file bug reports and feature requests using the Linear API and OpenAI.

## Setup Instructions

### 1. Clone the repository
First, clone the repository to your local machine:

### 2. Install dependencies
This project uses Python and requires some specific libraries. You can install them using:
pip install openai

### 3. Set up environment variables
You need to set up API keys for OpenAI and Linear. Add the following environment variables:

OPENAI_API_KEY: Your OpenAI API key.
LINEAR_API_KEY: Your Linear API key.

export OPENAI_API_KEY="your_openai_api_key"
export LINEAR_API_KEY="your_linear_api_key"

Running the Project
To run the 
 script:
 
```
python main.py
```