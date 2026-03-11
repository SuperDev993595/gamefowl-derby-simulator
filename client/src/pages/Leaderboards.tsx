import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import type { LeaderboardPlayer, LeaderboardBreed, LeaderboardSeasonal } from "../api";
import { useAuth } from "../auth";

type Tab = "players" | "breeds" | "seasonal";

export default function Leaderboards() {
  const { state } = useAuth();
  const [tab, setTab] = useState<Tab>("players");
  const [players, setPlayers] = useState<LeaderboardPlayer[]>([]);
  const [breeds, setBreeds] = useState<LeaderboardBreed[]>([]);
  const [seasonal, setSeasonal] = useState<LeaderboardSeasonal[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    if (tab === "players") {
      api<LeaderboardPlayer[]>("/api/leaderboards/players").then(setPlayers).catch(() => setPlayers([])).finally(() => setLoading(false));
    } else if (tab === "breeds") {
      api<LeaderboardBreed[]>("/api/leaderboards/breeds").then(setBreeds).catch(() => setBreeds([])).finally(() => setLoading(false));
    } else {
      api<LeaderboardSeasonal[]>("/api/leaderboards/seasonal").then(setSeasonal).catch(() => setSeasonal([])).finally(() => setLoading(false));
    }
  }, [tab]);

  return (
    <div className="page">
      <header className="header">
        <Link to="/">← Home</Link>
        {state.token && <Link to="/tournaments">Derbies</Link>}
      </header>
      <h1>Leaderboards</h1>
      <p className="section-desc">Top players, top breeds, and seasonal rankings (last 30 days).</p>

      <div className="leaderboard-tabs">
        <button type="button" className={tab === "players" ? "active" : ""} onClick={() => setTab("players")}>Top Players</button>
        <button type="button" className={tab === "breeds" ? "active" : ""} onClick={() => setTab("breeds")}>Top Breeds</button>
        <button type="button" className={tab === "seasonal" ? "active" : ""} onClick={() => setTab("seasonal")}>Seasonal</button>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : tab === "players" ? (
        <section className="leaderboard-table">
          <table>
            <thead>
              <tr><th>#</th><th>Player</th><th>Wins</th></tr>
            </thead>
            <tbody>
              {players.length === 0 ? (
                <tr><td colSpan={3}>No data yet. Enter derbies to appear here.</td></tr>
              ) : (
                players.map((r) => (
                  <tr key={r.username}>
                    <td>{r.rank}</td>
                    <td>{r.username}</td>
                    <td>{r.total_wins}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </section>
      ) : tab === "breeds" ? (
        <section className="leaderboard-table">
          <table>
            <thead>
              <tr><th>#</th><th>Breed</th><th>Wins</th></tr>
            </thead>
            <tbody>
              {breeds.length === 0 ? (
                <tr><td colSpan={3}>No data yet.</td></tr>
              ) : (
                breeds.map((r) => (
                  <tr key={r.breed_name}>
                    <td>{r.rank}</td>
                    <td>{r.breed_name}</td>
                    <td>{r.total_wins}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </section>
      ) : (
        <section className="leaderboard-table">
          <table>
            <thead>
              <tr><th>#</th><th>Player</th><th>Season Wins (30d)</th></tr>
            </thead>
            <tbody>
              {seasonal.length === 0 ? (
                <tr><td colSpan={3}>No data yet.</td></tr>
              ) : (
                seasonal.map((r) => (
                  <tr key={r.username}>
                    <td>{r.rank}</td>
                    <td>{r.username}</td>
                    <td>{r.season_wins}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}
