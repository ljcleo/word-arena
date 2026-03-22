# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**WordArena** is a game arena where humans and LLMs play word-based games. It supports 10 games (Wordle, Contexto, ContextoHint, Letroso, Conexo, Numberle, Connections, Strands, Turing Machine, Redactle) with both manual human players and AI agents powered by multiple LLM providers (Anthropic, OpenAI, Google, or a pseudo/mock implementation).

## Commands

```bash
# Install dependencies (uses uv)
uv sync

# Play games manually (human input)
python scripts/play_manual.py

# Play games with an LLM agent
python scripts/play_agent.py
```

There are no tests, linting, or build steps configured.

## Architecture

The codebase has three layers: a generic game framework, player implementations, and game-specific implementations.

### Generic Framework (`word_arena/common/`)

- **`config/`** — Config loading system (shared across all games)
  - `BaseConfigLoader[MT, UT, CT]` — loads deterministic or random configs from a pool
  - `BaseConfigReader[MT, CT]` / `BaseInputConfigReader` — reads configs, with optional user-input hooks
  - Pattern: **MetaConfig** (immutable, from SQLite DB) + **MutableMetaConfig** (variable params) → **Config** (passed to engine)

- **`game/`** — Core game abstractions using 4 type parameters: `Game[IT, GT, FT, RT]`
  - `IT` = Info type (game setup), `GT` = Guess type, `FT` = Feedback type, `RT` = Result type
  - `BaseGameEngine[CT, IT, GT, FT, RT]` — implements game logic (`start_game`, `process_guess`, `is_over`, `get_final_result`)
  - `BaseGameRenderer` — handles output rendering
  - `GameState` / `GameStateInterface` — internal mutable state and read-only view of it
  - `Game[IT, GT, FT, RT]` — composes engine and renderer; exposes `start()`, `guess()`, `query()`

- **`player/`** — `BasePlayer[IT, GT, FT, RT]` with lifecycle: `prepare → guess → digest` per turn, then `reflect → evolve` post-game

- **`gym/`** — `Gym[MT, UT, CT, IT, GT, FT, RT]` orchestrates sessions: `play()` for a single game or `train()` for multiple loops/trials with `player.evolve()`

- **`llm/`** — `BaseLLM` with overloaded `query()` that returns either a plain string or a Pydantic model for structured output

### Player Implementations (`word_arena/players/`)

- **`manual/`** — `ManualPlayer` reads input from a `BaseInputManualReader`
- **`agent/`** — `AgentPlayer` uses an LLM via `BaseAgentEngine` which provides `create_note`, `analyze_and_guess`, `summarize_and_reflect`, `update_note` hooks

### Game Implementations (`word_arena/games/`)

Each of the 10 games follows the same internal layout:

```text
{game}/
  common.py          # Pydantic types for IT, GT, FT, RT, and Config
  config/            # MetaConfig, MutableMetaConfig, ConfigLoader, InputConfigReader
  game/
    engine.py        # Game-specific BaseGameEngine subclass
    state.py         # Type alias for GameStateInterface with game-specific params
    renderer/        # Game-specific BaseGameRenderer subclass
  players/
    manual/          # Game-specific input reader for ManualPlayer
    agent/           # Game-specific AgentEngine and renderer for AgentPlayer
  preset/
    gym.py           # Factory: assembles Gym (config loader + engine + renderer)
    players/
      manual.py      # Factory: assembles ManualPlayer
      agent.py       # Factory: assembles AgentPlayer
```

### LLM Adapters (`word_arena/llms/`)

`AnthropicLLM`, `OpenaiChatLLM`, `OpenaiResponsesLLM`, `GoogleLLM`, `PseudoLLM` — all implement `BaseLLM`.

### Scripts (`scripts/`)

- **`common.py`** — `log(key, value)` helper and `make_cls_prefix(key)` utility (converts `"game_name"` → `"GameName"`)
- **`utils.py`** — CLI input prompts; enumerates available game/LLM keys by scanning `config/games/` and `config/llms/`
- **`build_llm.py`** — `LLM_CONFIG_PATH` and `build_llm()` factory; reads `config/llms/{key}.json`, dynamically imports engine and renderer classes
- **`build_gym.py`** — `GAME_CONFIG_PATH` and `build_gym()` factory; reads `config/games/{key}.json`, dynamically imports `{Game}MetaConfig` / `{Game}MutableMetaConfig` and the preset callable
- **`build_manual_player.py`** — `build_player()` factory for manual play
- **`build_agent_player.py`** — `build_player()` factory for agent play
- **`play_manual.py`** — CLI entry point: prompts for game, runs `gym.play(player)`
- **`play_agent.py`** — CLI entry point: prompts for game and LLM, optionally runs `gym.train()`

### Configuration

- LLM configs live in `config/llms/*.json`. `manual_input.json` and `pseudo.json` are committed; real API configs are gitignored. Format: `{"type": "<provider>", "config": {...}}`.
- Game preset configs live in `config/games/*.json`. Format: `{"meta_config": {...}, "mutable_meta_config_pool": [...]}`. Fields match the corresponding `{Game}MetaConfig` and `{Game}MutableMetaConfig` Pydantic models.
- Game data is stored as SQLite databases in `data/{game_name}/games.db`.

### Data Flow

```text
scripts/play_*.py
  → Gym.play/train(player)
    → ConfigLoader.load_config() → CT (game config)
    → Game.start() → Engine.start_game() → IT (game info)
    → Player.prepare(IT)
    → loop: Player.guess() → Game.guess(GT) → FT feedback → Player.digest(FT)
    → Game.query() → RT (final result)
    → Player.reflect(RT) [→ Player.evolve() if training]
```

### Adding a New Game

1. Create `word_arena/games/{name}/common.py` with Pydantic types for Config, IT, GT, FT, RT
2. Add `config/` with MetaConfig, MutableMetaConfig, ConfigLoader, and InputConfigReader
3. Implement engine, state type alias, and renderer in `game/`
4. Implement manual input reader and agent engine/renderer in `players/`
5. Add factory functions in `preset/gym.py` and `preset/players/{manual,agent}.py`
6. Add `config/games/{name}.json` with `meta_config` (fields for `{Game}MetaConfig`) and `mutable_meta_config_pool` (list of `{Game}MutableMetaConfig` dicts, or plain ints if there is no `MutableMetaConfig`); no script registration needed

### Adding a New LLM Provider

Subclass `BaseLLM` in `word_arena/llms/`, add a corresponding JSON config format under `config/llm/`, and register in `scripts/build_llm.py`.
