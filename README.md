# WordArena

A game arena where humans and LLMs compete at word-based puzzles. Play manually, or pit AI agents against 10 different games and see how they think.

## Requirements

- Python 3.13+
- (Recommended) [uv](https://github.com/astral-sh/uv) for dependency management

## Games

| Game | Source | Description |
|------|--------|-------------|
| **Wordle** | [nytimes.com](https://www.nytimes.com/games/wordle) | Guess the hidden 5-letter word in 6 tries |
| **Letroso** | [letroso.com](https://letroso.com) | Guess the hidden word with variant lengths |
| **Contexto** | [contexto.me](https://contexto.me) | Find the secret word by semantic similarity — no letter hints |
| **ContextoHint** | [contexto.me](https://contexto.me) | Contexto with periodic hints to guide the search |
| **Conexo** | [conexo.ws](https://conexo.ws) | Group 16 words into 4 hidden categories |
| **Connections** | [nytimes.com](https://www.nytimes.com/games/connections) | NYT-style: find 4 groups of 4 related words |
| **Numberle** | [numberle.wordleday.org](https://numberle.wordleday.org) | Guess a hidden arithmetic equation |
| **Strands** | [nytimes.com](https://www.nytimes.com/games/strands) | Find themed word clusters hidden in a letter grid |
| **Turing Machine** | [turingmachine.info](https://turingmachine.info/) | Deduce a secret code by querying logical verifier cards |
| **Redactle** | [redactle.net](https://redactle.net) | Identify a Wikipedia article from its redacted text |

## Quick Start

```bash
# Install dependencies (use `--group crawl` for crawl scripts)
uv sync --group game --group llm

# Play any game manually
python scripts/play_manual.py

# Let an LLM agent play
python scripts/play_agent.py
```

## LLM Providers

Supports **Anthropic**, **OpenAI** (Chat & Responses API), **Google Gemini**, and a **pseudo** mock for testing. Add API credentials under `config/llm/`:

```json
{
  "provider": "anthropic",
  "api_key": "sk-...",
  "model": "claude-opus-4-6"
}
```

The `pseudo.json` and `manual.json` configs are committed and work out of the box.

## Architecture

The framework is built around five generic abstractions:

```
Gym → Game (Engine + Renderer) → Player (Manual | Agent)
         ↑                              ↑
    ConfigLoader                    BaseLLM
```

Each game is parameterized over `IT` (info), `GT` (guess), `FT` (feedback), and `RT` (result) types. Adding a new game means implementing these types plus an engine, renderer, and player adapter — the orchestration layer stays unchanged.

LLM agents follow a structured turn cycle: `prepare → [analyze_and_guess → digest] → reflect`, with an optional `evolve()` hook for multi-game training runs.

## Project Structure

```
word_arena/
  common/       # Generic framework: config, game, player, gym, llm
  games/        # 10 game implementations
  players/      # ManualPlayer and AgentPlayer
  llms/         # Provider adapters
scripts/
  play_manual.py
  play_agent.py
config/llm/     # LLM configs (API keys gitignored)
data/           # SQLite game databases + crawl scripts
```

## Roadmap

#### Evaluation
- [ ] Per-game benchmark reports: win rate, average guesses, token cost per LLM
- [ ] Elo-style leaderboard across providers and models
- [ ] Prompt variant grid search via `TrainingConfig`

#### Performance
- [ ] Async parallel game execution for faster training runs
- [ ] Response caching for online games (Contexto)

#### Agent Intelligence
- [ ] Cross-session memory: persist strategy notes between runs

#### Interface
- [ ] TUI with `textual`: rich terminal UI by swapping the renderer and input reader, no core changes needed
- [ ] Web UI: FastAPI + WebSocket backend streaming game state to a browser frontend
- [ ] Agent replay viewer: watch recorded LLM sessions without re-running inference

#### Developer Experience
- [ ] Structured CLI with subcommands (`play`, `train`, `bench`) via `typer`
- [ ] Unit tests for game engines and config loaders
