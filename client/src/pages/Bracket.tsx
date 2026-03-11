import { useEffect, useState, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../api";
import type { TournamentResponse, MatchResponse, StandingsRow } from "../api";
import { useAuth } from "../auth";

const DERBY_LABELS: Record<string, string> = {
  long_heel: "Long Heel",
  short_heel: "Short Heel",
  pilipino: "Pilipino",
  mexican: "Mexican",
};

export default function Bracket() {
  const { id } = useParams<{ id: string }>();
  const { state } = useAuth();
  const [tournament, setTournament] = useState<TournamentResponse | null>(null);
  const [matches, setMatches] = useState<MatchResponse[]>([]);
  const [standings, setStandings] = useState<StandingsRow[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  const fetchData = () => {
    if (!id) return;
    api<TournamentResponse>(`/api/tournaments/${id}`).then(setTournament).catch(() => setTournament(null));
    api<MatchResponse[]>(`/api/matches/tournaments/${id}`).then(setMatches).catch(() => setMatches([]));
    api<StandingsRow[]>(`/api/entries/tournaments/${id}/standings`).then(setStandings).catch(() => setStandings([]));
  };

  useEffect(() => {
    fetchData();
  }, [id]);

  useEffect(() => {
    if (!id) return;
    const base = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/^http/, "ws");
    const ws = new WebSocket(`${base}/ws/tournaments/${id}`);
    wsRef.current = ws;
    ws.onmessage = () => fetchData();
    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [id]);

  if (!tournament) return <div className="page">Loading...</div>;

  const byRound = matches.reduce<Record<number, MatchResponse[]>>((acc, m) => {
    if (!acc[m.round_number]) acc[m.round_number] = [];
    acc[m.round_number].push(m);
    return acc;
  }, {});
  const rounds = Object.keys(byRound).map(Number).sort((a, b) => a - b);

  return (
    <div className="page">
      <header className="header">
        <Link to="/tournaments">← Derbies</Link>
      </header>
      <h1>{tournament.name}</h1>
      <p>{DERBY_LABELS[tournament.derby_type] || tournament.derby_type} · Status: <strong>{tournament.status}</strong> · Round {tournament.current_round}{tournament.is_tie_breaker ? " (tie-breaker)" : ""}</p>
      {tournament.winner_entry_id && <p className="winner-msg">Tournament finished. See standings for winner.</p>}

      <section className="standings">
        <h2>Standings</h2>
        <table>
          <thead>
            <tr><th>#</th><th>Player</th><th>Breed</th><th>W</th><th>L</th><th>Status</th></tr>
          </thead>
          <tbody>
            {standings.map((row, i) => (
              <tr key={row.entry_id}>
                <td>{i + 1}</td>
                <td>{row.username}</td>
                <td>{row.breed_name}</td>
                <td>{row.wins}</td>
                <td>{row.losses}</td>
                <td>{row.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="bracket">
        <h2>Matches</h2>
        {rounds.map((r) => (
          <div key={r} className="round">
            <h3>Round {r}{tournament.is_tie_breaker ? " (tie-breaker)" : ""}</h3>
            <ul>
              {(byRound[r] || []).map((m) => (
                <li key={m.id} className="match-card">
                  {m.status === "bye" ? (
                    <p>BYE: {m.entry_a_username || "—"} ({m.entry_a_breed || "—"})</p>
                  ) : (
                    <>
                      <p className={m.winner_entry_id === m.entry_a_id ? "winner" : ""}>
                        {m.entry_a_username || "—"} ({m.entry_a_breed || "—"})
                      </p>
                      <p>vs</p>
                      <p className={m.winner_entry_id === m.entry_b_id ? "winner" : ""}>
                        {m.entry_b_username || "—"} ({m.entry_b_breed || "—"})
                      </p>
                      {m.status === "played" && <p className="result">Winner: {m.winner_entry_id === m.entry_a_id ? m.entry_a_username : m.entry_b_username}</p>}
                    </>
                  )}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </section>
    </div>
  );
}
