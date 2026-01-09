# Multi-Page Redesign Implementation Plan

## Overview

Redesign the desktop client from a single-page application to a four-page navigation structure (Home, Game, Settings, Analysis) with supporting backend enhancements for multi-provider LLM support and coach chat functionality.

---

## Architecture Decisions

### Frontend (PyQt6 Desktop Client)
- **Page-based organization** following frontend-architect spec
- **QStackedWidget** for page navigation (no page reload, maintains state)
- **View-state separation**: Each page has a view component and state management module
- **Shared components**: Navigation bar, reusable widgets

### Backend (FastAPI)
- **Hexagonal architecture** with ports/adapters for LLM providers
- **Port interfaces** (ABC) for swappable LLM and chess engine implementations
- **Dependency injection** via `dependencies.py` for adapter selection

### Configuration
- **Local config file**: `~/.chesster/config.json` for LLM keys, provider selection, Chess.com username
- **Account data**: Extended User model in database

---

## Phase 1: Foundation & Navigation Structure

### 1.1 Desktop Client Page Structure
```
desktop_client/
├── pages/
│   ├── __init__.py
│   ├── home/
│   │   ├── __init__.py
│   │   ├── home_page.py          # QWidget view
│   │   └── home_state.py         # Navigation logic
│   ├── game/
│   │   ├── __init__.py
│   │   ├── game_page.py          # QWidget view
│   │   ├── game_state.py         # Game session management
│   │   └── components/
│   │       ├── __init__.py
│   │       ├── chess_board.py    # Extracted from main_api.py
│   │       ├── coach_chat.py     # New: Chat interface
│   │       └── game_controls.py  # New/save/load buttons
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── settings_page.py      # QWidget view
│   │   ├── settings_state.py     # Config management
│   │   └── components/
│   │       ├── __init__.py
│   │       ├── account_form.py   # User profile editing
│   │       ├── llm_config_form.py # Provider & API key config
│   │       └── chesscom_form.py  # Chess.com username
│   └── analysis/
│       ├── __init__.py
│       ├── analysis_page.py      # QWidget view
│       ├── analysis_state.py     # Game list & analysis logic
│       └── components/
│           ├── __init__.py
│           ├── game_list.py      # List of local + imported games
│           ├── game_viewer.py    # Read-only board + move navigation
│           └── analysis_panel.py # LLM analysis display
├── shared/
│   ├── __init__.py
│   ├── components/
│   │   ├── __init__.py
│   │   └── navigation.py         # Sidebar/header navigation
│   └── services/
│       ├── __init__.py
│       ├── api_client.py         # Existing, extend
│       └── config_service.py     # New: Local config file management
└── main.py                       # New entry point with QStackedWidget
```

### 1.2 Main Application Shell
- Create `MainWindow` with `QStackedWidget` containing all pages
- Implement `NavigationWidget` (sidebar or header) for page switching
- Signal-based navigation: pages emit signals, main window handles transitions

### 1.3 Local Config Service
Create `~/.chesster/config.json`:
```json
{
  "llm": {
    "provider": "anthropic",  // anthropic | openai | gemini | local
    "anthropic_api_key": "sk-...",
    "openai_api_key": "sk-...",
    "gemini_api_key": "...",
    "local_endpoint": "http://localhost:11434"
  },
  "chesscom_username": "player123",
  "account_user_id": 1
}
```

---

## Phase 2: Backend Hexagonal Refactoring

### 2.1 Domain Layer Updates

**Extend User Model** (`core_api/models/user.py`):
- Add `preferred_color` (white/black/random)
- Add `skill_level` (beginner/intermediate/advanced)
- Add `chesscom_username` (move from config to account)

**New Domain Ports** (`core_api/domain/ports/`):
```python
# llm_port.py
class LLMProviderPort(ABC):
    @abstractmethod
    async def chat(self, messages: list[Message], system_prompt: str) -> str: ...

    @abstractmethod
    async def chat_stream(self, messages: list[Message], system_prompt: str) -> AsyncIterator[str]: ...

# chess_engine_port.py
class ChessEnginePort(ABC):
    @abstractmethod
    def analyze_position(self, fen: str, depth: int) -> PositionAnalysis: ...

    @abstractmethod
    def get_best_move(self, fen: str, depth: int) -> str: ...

    @abstractmethod
    def evaluate_move(self, fen: str, move: str) -> MoveEvaluation: ...
```

### 2.2 Adapters Layer

**LLM Adapters** (`core_api/adapters/llm/`):
```
├── __init__.py
├── anthropic_adapter.py    # Claude API implementation
├── openai_adapter.py       # OpenAI API implementation
├── gemini_adapter.py       # Google Gemini implementation
└── local_adapter.py        # Ollama/local model implementation
```

**Chess Engine Adapter** (`core_api/adapters/chess_engine/`):
```
├── __init__.py
└── stockfish_adapter.py    # Stockfish binary wrapper
```

### 2.3 New Services

**CoachService** (`core_api/services/coach_service.py`):
- Receives: user message, current FEN, move history, Stockfish evaluation
- Constructs context-aware prompt for LLM
- System prompt: "You are a chess coach helping a student learn..."
- Returns coaching response

**MoveAnalysisService** (`core_api/services/move_analysis_service.py`):
- Input: Full PGN of completed game
- Process:
  1. Parse PGN for existing annotations (NAGs like $2=blunder, $4=mistake)
  2. If no annotations, run Stockfish on each position to identify blunders (>200cp loss) and mistakes (>100cp loss)
  3. Pass annotated PGN to LLM for natural language analysis
- Output: Structured analysis with explanations for critical moves

### 2.4 New API Endpoints

**Coach Endpoints** (`/api/v1/coach/`):
```
POST /chat          # Single message exchange
POST /chat/stream   # SSE streaming response
```

**Analysis Endpoints** (extend existing `/api/v1/analysis/`):
```
POST /game/{game_id}/analyze   # Analyze a specific game (move-by-move)
```

**User/Account Endpoints** (extend `/api/v1/users/`):
```
PUT /users/{user_id}           # Update account settings
GET /users/{user_id}/games     # Get user's games (local + imported)
```

---

## Phase 3: Game Page Implementation

### 3.1 Chess Board Component
- Extract existing `ChessBoardWidget` from `main_api.py`
- Clean up and modularize
- Add signals for move events

### 3.2 Coach Chat Component
- `QTextEdit` for chat history (markdown rendering)
- `QLineEdit` + send button for user input
- Loading indicator during LLM response
- Context includes: current position FEN, recent moves, Stockfish eval

### 3.3 Game Controls Component
- New Game button (with color selection dialog)
- Save Game button (auto-generates name, saves to DB)
- Load Game button (opens game selection dialog)
- Game status display (whose turn, check/checkmate/stalemate)

### 3.4 Game State Management
- Manages current game session
- Handles auto-save on every move
- Coordinates between board, chat, and controls
- Tracks chat history for context

---

## Phase 4: Settings Page Implementation

### 4.1 Account Form
- Username, email, full name fields
- Skill level dropdown
- Preferred color selection
- Save to database via API

### 4.2 LLM Config Form
- Provider radio buttons (Anthropic/OpenAI/Gemini/Local)
- API key input (password field, show/hide toggle)
- Local endpoint URL (for Ollama etc.)
- Test connection button
- Save to local config file

### 4.3 Chess.com Integration Form
- Username input
- Verify button (checks if profile exists)
- Import games button (fetches and stores in local DB)
- Last sync timestamp display

---

## Phase 5: Analysis Page Implementation

### 5.1 Game List Component
- List view of all games (local + imported from Chess.com)
- Columns: Date, Opponent, Result, Opening, Source
- Filter by: source (local/chess.com), result, date range
- Search by opponent name

### 5.2 Game Viewer Component
- Read-only chess board showing selected game
- Move list with navigation (click to jump, arrows for prev/next)
- Current position FEN display

### 5.3 Analysis Panel Component
- "Analyze Game" button
- Loading state during LLM analysis
- Structured display of analysis:
  - Overall assessment
  - Critical moments (mistakes/blunders) with explanations
  - Key turning points
  - Recommendations

---

## Phase 6: Integration & Polish

### 6.1 Navigation Flow
- Home → clear entry point with visual cards for each section
- Game → remember last game state (but don't persist "in progress")
- Settings → changes apply immediately
- Analysis → remember last selected game

### 6.2 Error Handling
- Graceful degradation if API unavailable
- Clear error messages for LLM failures
- Retry logic for transient failures

### 6.3 Stockfish Integration
- Bundle Stockfish binary or document installation
- Configurable depth for analysis
- Async evaluation to not block UI

---

## File Changes Summary

### New Files (Desktop Client)
- `main.py` - New entry point
- `pages/home/home_page.py`, `home_state.py`
- `pages/game/game_page.py`, `game_state.py`
- `pages/game/components/chess_board.py`, `coach_chat.py`, `game_controls.py`
- `pages/settings/settings_page.py`, `settings_state.py`
- `pages/settings/components/account_form.py`, `llm_config_form.py`, `chesscom_form.py`
- `pages/analysis/analysis_page.py`, `analysis_state.py`
- `pages/analysis/components/game_list.py`, `game_viewer.py`, `analysis_panel.py`
- `shared/components/navigation.py`
- `shared/services/config_service.py`

### New Files (Backend)
- `domain/ports/llm_port.py`
- `domain/ports/chess_engine_port.py`
- `adapters/llm/anthropic_adapter.py`
- `adapters/llm/openai_adapter.py`
- `adapters/llm/gemini_adapter.py`
- `adapters/llm/local_adapter.py`
- `adapters/chess_engine/stockfish_adapter.py`
- `services/coach_service.py`
- `services/move_analysis_service.py`
- `api/endpoints/coach.py`

### Modified Files
- `core_api/models/user.py` - Extend with new fields
- `core_api/api/router.py` - Add coach routes
- `core_api/dependencies.py` - LLM provider injection
- `desktop_client/services/api_client.py` - New endpoints
- `Taskfile.yml` - Update run commands

### Deprecated/Removed
- `desktop_client/main_api.py` - Replaced by new structure

---

## Dependencies to Add

### Backend (core_api)
```toml
openai = "^1.0"           # OpenAI API
google-generativeai = "^0.3"  # Gemini API
stockfish = "^3.28"       # Stockfish Python wrapper
```

### Desktop Client
No new dependencies required (PyQt6 already included)

---

## Testing Strategy

### Unit Tests
- LLM adapter mocks for each provider
- CoachService with mocked LLM
- MoveAnalysisService with sample PGNs
- Config service read/write

### Integration Tests
- Full coach chat flow
- Game analysis end-to-end
- Settings persistence

### Manual Testing
- Navigation between all pages
- Game play with coach interaction
- Settings changes persist correctly
- Analysis of various game types
