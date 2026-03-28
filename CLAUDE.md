# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**WordArena** is a game arena where humans and LLMs play word-based games. It supports 10 games (Wordle, Contexto, ContextoHint, Letroso, Conexo, Numberle, Connections, Strands, Turing Machine, Redactle) with both manual human players and AI agents powered by multiple LLM providers (Anthropic, OpenAI, Google, or a pseudo/mock implementation).

## Commands

```bash
# Install dependencies (uses uv)
uv sync

# Play any game (manual or agent, with optional training)
python scripts/main.py
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

- **`player/`** — `Player[NT, IT, AT, GT, FT, RT, ST]` with lifecycle: `setup()` once, then per-game `play()` (loops `analyze_and_guess → add_turn`), then `evolve()` for training
  - `NT` = Note type, `AT` = Analysis type, `ST` = Summary/reflection type (in addition to IT/GT/FT/RT)
  - `BasePlayerEngine[NT, IT, AT, GT, FT, RT, ST]` — abstract engine with `create_note`, `analyze_and_guess`, `summarize_and_reflect`, `update_note` hooks

- **`gym/`** — `Gym[MT, UT, CT, IT, GT, FT, RT]` orchestrates sessions: `play()` for a single game or `train()` for multiple loops/trials with `player.evolve()`

- **`llm/`** — `LLM` wraps a `BaseLLMEngine` with a renderer; `query()` returns either a plain string or a Pydantic model for structured output

### Player Implementations (`word_arena/players/`)

- **`manual/`** — `ManualPlayerEngine` reads input from a `BaseInputManualReader`; `ManualLogPlayerRenderer` handles output
- **`agent/`** — `AgentPlayerEngine` uses an LLM plus a game-specific `BaseAgentPrompter` for all prompt construction; `AgentLogPlayerRenderer` handles output

Both player types use the common `Player` class from `word_arena/common/player/`.

### Game Implementations (`word_arena/games/`)

Each of the 10 games follows the same internal layout:

```text
{game}/
  common.py          # Pydantic types for IT, GT, FT, RT, and Config
  config/
    common.py        # MetaConfig, MutableMetaConfig
    generator.py     # ConfigGenerator (BaseConfigGenerator subclass)
    reader/
      input.py       # InputConfigReader (BaseInputConfigReader subclass)
  game/
    engine.py        # Game-specific BaseGameEngine subclass
    renderer/        # Game-specific BaseLogGameRenderer subclass
  players/
    manual/
      reader/        # Game-specific BaseInputManualReader subclass
    agent/
      prompter.py    # Game-specific BaseAgentPrompter subclass
```

### LLM Adapters (`word_arena/llms/`)

Each provider exposes `{Provider}LLMConfig` and `{Provider}LLMEngine` (implements `BaseLLMEngine`). The shared `LLM` class wraps any engine with a `LogLLMRenderer`.

Available providers: `anthropic`, `openai_chat`, `openai_responses`, `google`, `pseudo`, `manual_input`.

### Scripts (`scripts/`)

- **`common.py`** — `GAME_CONFIG_PATH`, `LLM_CONFIG_PATH`, `log(key, value)` helper, and `make_cls_prefix(key)` utility (converts `"game_name"` → `"GameName"`)
- **`utils.py`** — CLI input prompts; enumerates available game/LLM keys by scanning `config/games/` and `config/llms/`
- **`build_llm.py`** — `build_llm()` factory; reads `config/llms/{key}.json`, dynamically imports `{Provider}LLMConfig` and `{Provider}LLMEngine`, constructs an `LLM`
- **`build_gym.py`** — `build_gym()` factory; reads `config/games/{key}/meta_config.json` and `config/games/{key}/renderer.json`, dynamically imports `{Game}MetaConfig` / `{Game}MutableMetaConfig`, `{Game}InputConfigReader`, `{Game}ConfigGenerator`, `{Game}GameEngine`, `{Game}LogGameRenderer` to construct a `Gym`
- **`build_manual_player.py`** — `build_manual_player()` factory; reads `config/games/{key}/players/manual.json`, imports `{Game}InputManualReader`, constructs a `Player` with `ManualPlayerEngine` and `ManualLogPlayerRenderer`
- **`build_agent_player.py`** — `build_agent_player()` factory; imports `{Game}AgentPrompter`, constructs a `Player` with `AgentPlayerEngine` and `AgentLogPlayerRenderer`
- **`main.py`** — CLI entry point: prompts for game and player type (manual or agent); optionally runs `gym.train()` before `gym.play(player)` for agent players

### Configuration

- LLM configs live in `config/llms/*.json`. `manual_input.json` and `pseudo.json` are committed; real API configs are gitignored. Format: `{"type": "<provider>", "config": {...}}`.
- Game configs live in per-game directories under `config/games/{key}/`:
  - `meta_config.json` — `{"meta_config": {...}, "mutable_meta_config_pool": [...]}` (fields match `{Game}MetaConfig` / `{Game}MutableMetaConfig`)
  - `renderer.json` — `{"log_prompt": {...}}` (fields match `{Game}LogPromptConfig` if defined, else passed as-is)
  - `players/manual.json` — `{"input_prompt": {...}}` (fields match `{Game}InputPromptConfig` if defined, else passed as-is)
- Game data is stored as SQLite databases in `data/{game_name}/games.db`.

### Data Flow

```text
scripts/main.py
  → player.setup()                          # create_note → NT
  → [gym.train(player, training_config)]    # optional: multiple play+evolve loops
  → gym.play(player)
      → ConfigGenerator/Reader → CT (game config)
      → Game.start() → Engine.start_game() → IT (game info)
      → loop: player.analyze_and_guess() → Game.guess(GT) → FT feedback
      → Game.query() → RT (final result)
      → player.summarize_and_reflect() → ST
      [→ player.evolve() after each training loop: update_note → NT]
```

### Adding a New Game

1. Create `word_arena/games/{name}/common.py` with Pydantic types for Config, IT, GT, FT, RT
2. Add `config/common.py` with MetaConfig and MutableMetaConfig; `config/generator.py` with ConfigGenerator; `config/reader/input.py` with InputConfigReader
3. Implement engine and log renderer in `game/`
4. Implement manual input reader in `players/manual/reader/input.py` and agent prompter in `players/agent/prompter.py`
5. Add `config/games/{name}/meta_config.json` (with `meta_config` and `mutable_meta_config_pool`), `config/games/{name}/renderer.json` (with `log_prompt`), and `config/games/{name}/players/manual.json` (with `input_prompt`); no script registration needed

### Adding a New LLM Provider

Implement `{Provider}LLMConfig` and `{Provider}LLMEngine` (subclass `BaseLLMEngine`) in `word_arena/llms/`, add a corresponding JSON config under `config/llms/`, and register in `scripts/build_llm.py`.
