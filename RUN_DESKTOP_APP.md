# Running the Desktop Chess App with API

## Quick Start

### 1. Start the API Server
```bash
cd core_api
poetry run python run.py
```
The API will start at http://localhost:8000

### 2. Start the Desktop App
In a new terminal:
```bash
cd desktop_client
poetry run python run_app.py
```

## Features Available

### ✅ **Working Now**
- **Chess board** with piece movement and validation
- **Move history** with navigation
- **Save/Load games** to/from API database
- **PGN import/export** from local files
- **Opening book** with 15 chess openings
- **API connection status** in status bar
- **Game management** - create, load, save games
- **Local fallback** - works even if API is disconnected

### 🎮 **How to Use**

1. **Play Chess**: Click pieces to select and move them
2. **Save Game**: Click "Save Game" to store in API database
3. **Load Games**: Click "Load Games" to see saved games, double-click to load
4. **Import PGN**: Click "Load PGN File" to import games from files
5. **Export PGN**: Click "Save PGN" to export current game
6. **Openings**: Click an opening name to load it on the board
7. **Navigate**: Click moves in the history to jump to that position

### 🔄 **API Integration**

The app automatically:
- Connects to the API server on startup
- Shows connection status in the status bar
- Saves games to the database when you click "Save Game"
- Loads your saved games list from the API
- Falls back to local-only mode if API is unavailable

### 🚨 **Troubleshooting**

**"API Disconnected" message:**
- Make sure the API server is running: `cd core_api && poetry run python run.py`
- Check that it's accessible at http://localhost:8000/health
- The app will still work locally without the API

**Import errors:**
- Make sure you ran `poetry install` in the desktop_client directory
- The shared package should be automatically installed

**Chess piece display issues:**
- This is normal on some systems - the Unicode chess symbols may not display perfectly
- The game logic still works correctly

## Next Steps

This desktop app now demonstrates the full API integration! The same API endpoints could power:
- A web client (React/TypeScript)
- A mobile app
- A chess bot interface
- Real-time multiplayer features

All game data is now stored in the database and accessible via RESTful API endpoints.