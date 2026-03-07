#!/bin/bash
cd ~/ai-agents
source venv/bin/activate
cd web_ui
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
