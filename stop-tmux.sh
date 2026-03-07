#!/bin/bash
cd ~/ai-agents

# Убиваем старую сессию, если есть
tmux kill-session -t agents 2>/dev/null