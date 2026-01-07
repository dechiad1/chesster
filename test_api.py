#!/usr/bin/env python3
"""Simple API test script."""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def test_api():
    """Test basic API functionality."""
    print("🧪 Testing Chess Platform API")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ API server not running. Start with: cd core_api && poetry run python run.py")
        return
    
    # Test create user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/", json=user_data)
        if response.status_code == 200:
            user = response.json()
            print(f"✅ User created: {user['username']} (ID: {user['user_id']})")
            user_id = user['user_id']
        else:
            print(f"❌ User creation failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ User creation error: {e}")
        return
    
    # Test create game
    game_data = {
        "white_player_id": user_id,
        "pgn_data": "[Event \"Test Game\"]\n[White \"Test User\"]\n[Black \"Opponent\"]\n[Result \"1-0\"]\n\n1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 1-0",
        "result": "1-0",
        "source": "test"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/games/", json=game_data)
        if response.status_code == 200:
            game = response.json()
            print(f"✅ Game created: ID {game['game_id']}")
            game_id = game['game_id']
        else:
            print(f"❌ Game creation failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Game creation error: {e}")
        return
    
    # Test get games
    try:
        response = requests.get(f"{BASE_URL}/games/")
        if response.status_code == 200:
            games = response.json()
            print(f"✅ Retrieved {len(games)} games")
        else:
            print(f"❌ Get games failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get games error: {e}")
    
    # Test get specific game
    try:
        response = requests.get(f"{BASE_URL}/games/{game_id}")
        if response.status_code == 200:
            game = response.json()
            print(f"✅ Retrieved game {game_id}: {game['result']}")
        else:
            print(f"❌ Get game failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get game error: {e}")
    
    print("\n🎯 Basic API functionality working!")
    print("📋 Available endpoints:")
    print("  • POST /api/v1/users/ - Create user")
    print("  • GET /api/v1/users/{id} - Get user")
    print("  • POST /api/v1/games/ - Create game")
    print("  • GET /api/v1/games/ - List games")
    print("  • GET /api/v1/games/{id} - Get specific game")
    print("  • PUT /api/v1/games/{id} - Update game")
    print("  • DELETE /api/v1/games/{id} - Delete game")
    print("  • GET /api/v1/games/{id}/pgn - Export PGN")

if __name__ == "__main__":
    test_api()