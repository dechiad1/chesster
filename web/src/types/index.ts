// Game data types
export interface GameData {
  game_id: number;
  white_player_id?: number;
  black_player_id?: number;
  start_datetime?: string;
  end_datetime?: string;
  result?: string;
  pgn_data: string;
  source?: string;
  created_at: string;
}

// User data types
export interface UserData {
  user_id: number;
  username: string;
  email: string;
  full_name: string;
  nationality?: string;
  avatar_path?: string;
  rating?: number;
  registration_date: string;
  last_login_date?: string;
  is_active: boolean;
}

// Chess.com game data
export interface ChessComGameData {
  url: string;
  pgn: string;
  time_control: string;
  end_time: number;
  rated: boolean;
  time_class: string;
  rules: string;
  white_username: string;
  white_rating: number;
  white_result: string;
  black_username: string;
  black_rating: number;
  black_result: string;
  opening?: string;
}

// Chess line for exploration
export interface ChessLine {
  description: string;
  moves: string[];  // UCI format
  moves_san: string[];  // SAN format for display
  evaluation?: number;
}

// Coach response types
export type CoachResponseType = 'text' | 'lines';

export interface CoachResponse {
  response_type: CoachResponseType;
  content: string;
  lines?: ChessLine[];
}

// Move result from API
export interface MoveResult {
  fen: string;
  legal: boolean;
  check?: boolean;
  checkmate?: boolean;
  stalemate?: boolean;
  draw?: boolean;
  game_over?: boolean;
}

// Position analysis
export interface PositionAnalysis {
  evaluation: number;
  best_move?: string;
  mate_in?: number;
  principal_variation?: string[];
}

// Game trend analysis
export interface GameTrendAnalysis {
  username: string;
  games_analyzed: number;
  analysis_date: string;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  opening_trends: string;
  time_management: string;
  recommendations: string[];
  win_rate: number;
  most_played_openings: string[];
}

// Game analysis result
export interface GameAnalysis {
  game_id: number;
  critical_moments: Array<{
    move_number: number;
    fen: string;
    evaluation_before: number;
    evaluation_after: number;
    best_move: string;
    played_move: string;
    comment: string;
  }>;
  overall_assessment: string;
  opening_assessment: string;
  middlegame_assessment: string;
  endgame_assessment: string;
}

// API Error
export class APIError extends Error {
  constructor(message: string, public statusCode?: number) {
    super(message);
    this.name = 'APIError';
  }
}
