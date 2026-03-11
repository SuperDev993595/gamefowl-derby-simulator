const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getToken(): string | null {
  return localStorage.getItem("token");
}

export async function api<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || String(err) || res.statusText);
  }
  return res.json();
}

export function breedImageUrl(filename: string): string {
  return `${API_BASE}/breed-pics/${encodeURIComponent(filename)}`;
}

export type TokenResponse = {
  access_token: string;
  token_type: string;
  username: string;
  is_admin: boolean;
  token_balance: number;
};

export type UserResponse = {
  id: number;
  username: string;
  email: string;
  token_balance: number;
  is_admin: boolean;
  created_at: string;
};

export type BreedResponse = {
  id: number;
  name: string;
  image_filename: string;
  traits?: { derby_type: string; power: number; speed: number; intelligence: number; stamina: number; accuracy: number }[];
};

export type TournamentResponse = {
  id: number;
  name: string;
  derby_type: string;
  total_rounds: number;
  start_at: string | null;
  status: string;
  current_round: number;
  is_tie_breaker: boolean;
  winner_entry_id: number | null;
  created_at: string;
  entry_count?: number;
};

export type EntryResponse = {
  id: number;
  tournament_id: number;
  user_id: number;
  breed_id: number;
  keep_type?: string;
  token_cost_paid: number;
  status: string;
  wins: number;
  losses: number;
  created_at: string;
  username?: string;
  breed_name?: string;
};

export type MatchResponse = {
  id: number;
  tournament_id: number;
  round_number: number;
  entry_a_id: number | null;
  entry_b_id: number | null;
  winner_entry_id: number | null;
  status: string;
  is_tie_breaker: boolean;
  played_at: string | null;
  entry_a_username?: string | null;
  entry_b_username?: string | null;
  entry_a_breed?: string | null;
  entry_b_breed?: string | null;
};

export type StandingsRow = {
  entry_id: number;
  username: string;
  breed_name: string;
  wins: number;
  losses: number;
  status: string;
};
