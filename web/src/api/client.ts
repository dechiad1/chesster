import {
  GameData,
  UserData,
  ChessComGameData,
  ChessLine,
  CoachResponse,
  MoveResult,
  PositionAnalysis,
  GameTrendAnalysis,
  GameAnalysis,
  APIError,
} from '@/types';

export class ChessAPIClient {
  private baseUrl: string;
  private apiUrl: string;

  constructor(baseUrl: string = '') {
    // Use relative URLs for Vite proxy to work
    this.baseUrl = baseUrl;
    this.apiUrl = `${baseUrl}/api/v1`;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorDetail: string;
      try {
        const errorData = await response.json();
        errorDetail = errorData.detail || response.statusText;
      } catch {
        errorDetail = response.statusText;
      }
      throw new APIError(
        `API error (${response.status}): ${errorDetail}`,
        response.status
      );
    }
    return response.json();
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }

  // Game Management
  async createGame(
    pgnData: string,
    whitePlayerId?: number,
    blackPlayerId?: number,
    result?: string,
    source: string = 'web'
  ): Promise<GameData> {
    const response = await fetch(`${this.apiUrl}/games/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        pgn_data: pgnData,
        white_player_id: whitePlayerId,
        black_player_id: blackPlayerId,
        result,
        source,
      }),
    });
    return this.handleResponse<GameData>(response);
  }

  async getGames(userId?: number, skip: number = 0, limit: number = 100): Promise<GameData[]> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (userId) {
      params.append('user_id', userId.toString());
    }
    const response = await fetch(`${this.apiUrl}/games/?${params}`);
    return this.handleResponse<GameData[]>(response);
  }

  async getGame(gameId: number): Promise<GameData> {
    const response = await fetch(`${this.apiUrl}/games/${gameId}`);
    return this.handleResponse<GameData>(response);
  }

  async updateGame(gameId: number, updates: Partial<GameData>): Promise<GameData> {
    const response = await fetch(`${this.apiUrl}/games/${gameId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    return this.handleResponse<GameData>(response);
  }

  async deleteGame(gameId: number): Promise<boolean> {
    const response = await fetch(`${this.apiUrl}/games/${gameId}`, {
      method: 'DELETE',
    });
    await this.handleResponse(response);
    return true;
  }

  async exportGamePgn(gameId: number): Promise<string> {
    const response = await fetch(`${this.apiUrl}/games/${gameId}/pgn`);
    const data = await this.handleResponse<{ pgn: string }>(response);
    return data.pgn;
  }

  async importGamePgn(pgnData: string): Promise<GameData> {
    const response = await fetch(`${this.apiUrl}/games/import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pgn_data: pgnData }),
    });
    return this.handleResponse<GameData>(response);
  }

  // Chess Operations
  async makeMove(fen: string, move: string): Promise<MoveResult> {
    const response = await fetch(`${this.apiUrl}/chess/move`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fen, move }),
    });
    return this.handleResponse<MoveResult>(response);
  }

  async analyzePosition(fen: string): Promise<PositionAnalysis> {
    const response = await fetch(`${this.apiUrl}/chess/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fen }),
    });
    return this.handleResponse<PositionAnalysis>(response);
  }

  async validateGame(pgn: string): Promise<{ valid: boolean; error?: string }> {
    const response = await fetch(`${this.apiUrl}/chess/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pgn }),
    });
    return this.handleResponse<{ valid: boolean; error?: string }>(response);
  }

  async getOpenings(): Promise<Record<string, string>> {
    const response = await fetch(`${this.apiUrl}/chess/openings`);
    const data = await this.handleResponse<{ openings: Record<string, string> }>(response);
    return data.openings;
  }

  async getOpeningInfo(openingName: string): Promise<any> {
    const response = await fetch(`${this.apiUrl}/chess/openings/${openingName}`);
    return this.handleResponse(response);
  }

  async getStartingPosition(): Promise<{ fen: string }> {
    const response = await fetch(`${this.apiUrl}/chess/starting-position`);
    return this.handleResponse<{ fen: string }>(response);
  }

  // User Management
  async createUser(
    username: string,
    email: string,
    fullName: string,
    password: string,
    additionalData: Record<string, any> = {}
  ): Promise<UserData> {
    const response = await fetch(`${this.apiUrl}/users/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username,
        email,
        full_name: fullName,
        password,
        ...additionalData,
      }),
    });
    return this.handleResponse<UserData>(response);
  }

  async getUser(userId: number): Promise<UserData> {
    const response = await fetch(`${this.apiUrl}/users/${userId}`);
    return this.handleResponse<UserData>(response);
  }

  // Chess.com Integration
  async fetchChessComGames(username: string, count: number = 15): Promise<ChessComGameData[]> {
    const response = await fetch(`${this.apiUrl}/analysis/chesscom/games`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, count }),
    });
    const data = await this.handleResponse<{ games: ChessComGameData[] }>(response);
    return data.games;
  }

  async analyzeChessComGames(
    username: string,
    apiKey: string,
    count: number = 15
  ): Promise<{ success: boolean; analysis?: GameTrendAnalysis }> {
    const response = await fetch(`${this.apiUrl}/analysis/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, api_key: apiKey, count }),
    });
    return this.handleResponse<{ success: boolean; analysis?: GameTrendAnalysis }>(response);
  }

  async getGameAnalysis(
    username: string,
    apiKey: string,
    count: number = 15
  ): Promise<GameTrendAnalysis | null> {
    const result = await this.analyzeChessComGames(username, apiKey, count);
    return result.success && result.analysis ? result.analysis : null;
  }

  // Coach Chat
  async coachChat(
    message: string,
    fen: string,
    moveHistory: string[],
    provider: string = 'anthropic',
    apiKey: string = ''
  ): Promise<CoachResponse> {
    const response = await fetch(`${this.apiUrl}/coach/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        fen,
        move_history: moveHistory,
        provider,
        api_key: apiKey,
      }),
    });
    return this.handleResponse<CoachResponse>(response);
  }

  // Game Analysis
  async analyzeGame(
    gameId: number,
    pgnData: string,
    provider: string = 'anthropic',
    apiKey: string = ''
  ): Promise<GameAnalysis> {
    const response = await fetch(`${this.apiUrl}/analysis/game`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        game_id: gameId,
        pgn_data: pgnData,
        provider,
        api_key: apiKey,
      }),
    });
    return this.handleResponse<GameAnalysis>(response);
  }
}

// Export a singleton instance
export const apiClient = new ChessAPIClient();
