---
id: 1
title: Update Groq Model Deprecation
stage: general
date_iso: "2026-01-31"
surface: agent
model: google/gemini-2.0-flash-exp:free
feature: none
branch: 001-todo-console-app
user: irza
command: various
labels: ["groq", "api", "model", "deprecation", "todo-app"]
links_spec: null
links_ticket: null
links_adr: null
links_pr: null
files_yaml: |
  - backend/agents/todo_agent.py
  - .specify/memory/constitution.md
  - specs/1-ai-todo-chatbot/spec.md
tests_yaml: |
  - none
---

# Update Groq Model Deprecation

## Prompt Text
```
Test Groq key locally:
bashcurl https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer gsk_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-70b-versatile",
    "messages": [{"role": "user", "content": "hi"}]
  }'
If this fails, your Groq key is invalid or expired.
```

## Response Text
Successfully identified and fixed the deprecated Groq model issue. The GROQ_API_KEY was valid but the model `llama-3.1-70b-versatile` had been decommissioned. Updated all codebase references to use the new `llama-3.3-70b-versatile` model.

## Outcome Impact
Fixed the deprecated model issue by updating all references from `llama-3.1-70b-versatile` to `llama-3.3-70b-versatile` in the codebase. This ensures the AI chat functionality continues to work with the updated Groq API.

## Tests Summary
- Tested the actual GROQ_API_KEY with curl command
- Verified the key was valid but model was deprecated
- Confirmed new model works with test API call

## Files Summary
- backend/agents/todo_agent.py: Updated two occurrences of deprecated model
- .specify/memory/constitution.md: Updated model reference in constitution
- specs/1-ai-todo-chatbot/spec.md: Updated three occurrences in spec file

## Next Prompts
None needed - issue resolved completely.

## Reflection Note
Groq has deprecated the `llama-3.1-70b-versatile` model and replaced it with `llama-3.3-70b-versatile`. Always check for model deprecation when API calls fail unexpectedly.

## Failure Modes Observed
None - successful resolution of the deprecated model issue.

## Next Experiment to Improve Prompt Quality
N/A