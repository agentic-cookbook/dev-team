# Name-Craft

A whimsical web-based character name generator for children's books using Claude AI, sound symbolism, and genre-specific templates.

## Purpose

An interactive web app that creates silly, genre-specific character names for children's books through a 9-question questionnaire. Uses Claude AI (with mock mode fallback) to generate names based on sound symbolism, alliteration, and genre templates, combined with a deterministic word-builder system.

## Key Features

- Interactive 9-question questionnaire for name generation
- Claude AI integration for creative name generation
- Sound symbolism and alliteration-based name building
- Genre-specific templates (fantasy, sci-fi, adventure, etc.)
- Server-Sent Events for real-time streaming name generation
- Mock mode fallback for offline development
- SQLite word persistence

## Tech Stack

- **Backend:** Python 3, Flask
- **Frontend:** HTML/CSS/JavaScript (static, served via Flask)
- **AI:** Anthropic Claude API
- **Database:** SQLite3 (WAL mode)
- **Streaming:** Server-Sent Events (SSE)

## Status

Planning / early development.
