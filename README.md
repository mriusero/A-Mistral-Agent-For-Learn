---
title: A Mistral Agent 
emoji: 🤖
colorFrom: white
colorTo: orange
sdk: gradio
sdk_version: 5.26.0
app_file: app.py
pinned: false
hf_oauth: true
hf_oauth_expiration_minutes: 480
short_description: A Mistral Agent for GAIA Benchmark Level 1.
---

# A Mistral Agent For Learn

[![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/)
[![Gradio](https://img.shields.io/badge/Gradio-FFA500?logo=gradio&logoColor=fff)](https://gradio.app/)

## Overview
This project was created as part of the [Agents Course](https://huggingface.co/learn/agents-course) by Hugging Face. 

The purpose of this agent is to demonstrate how to build and deploy a Mistral Agent that can interact with external tools and APIs effectively.
To achieve this, the agent is designed to handle various tasks such as web scraping, data processing, and API interactions.

## Design
The agent is designed to be modular and extensible, allowing for easy integration of new tools and functionalities.
As a learning project, no external libraries are used for agentic workflow, a custom implementation is designed to handle the agent's decision-making process.

## Evaluation
Performances are evaluated based on the GAIA Benchmark Level 1, which tests the agent's ability to perform specific tasks and solve multi-steps problems.
For more information about the GAIA Benchmark, you can refer to the following paper [GAIA: a benchmark for General AI Assistants](https://huggingface.co/papers/2311.12983).

The agent's performance demonstrates a good ability for web searching, multi-steps reasoning, and tool usage but still has room for improvement in terms of robustness and repeatability.

## Usage
The agent has been implemented in a Gradio app template made for specific tasks answering evaluation. 

To use the agent, two possible methods are available:

1. **Hugging Face Space**: You can interact with the agent on the [Hugging Face Space](https://huggingface.co/spaces/mriusero/A-Mistral-Agent) and observe results.
    - Launch the asking/answering process by clicking on `Run Evaluation & Submit All Answers`.
    - Observe the agent's responses and interactions with the tools in logs.


2. **Local Deployment**: You can run the agent locally by cloning the repository.
   - Make sure to have the required dependencies installed.
   - Add a `MISTRAL_API_KEY` and an `AGENT_ID` for inference in the `.env` file. Credentials can be obtained from the [Mistral AI - La Plateforme](https://console.mistral.ai/) website.
   - Run the app using the command:
     ```bash
     gradio app.py
     ```
    - Open your browser and navigate to `http://localhost:7860` to launch the asking/answering process by clicking on `Run Evaluation & Submit All Answers`.
    - Observe the agent's responses and interactions with the tools in logs.
     

