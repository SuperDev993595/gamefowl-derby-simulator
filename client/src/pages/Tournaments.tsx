import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, entryCostForTier } from "../api";
import type { TournamentResponse } from "../api";
import { useAuth } from "../auth";
import { useNavigate } from "react-router-dom";

const DERBY_LABELS: Record<string, string> = {
  long_heel: "Long Heel",
  short_heel: "Short Heel",
  pilipino: "Pilipino",
  mexican: "Mexican",
};

const DERBY_DESCRIPTIONS: Record<string, string> = {
  long_heel: "The favorite of the South.",
  short_heel: "The old timer's favorite.",
  pilipino: "Fast and furious.",
  mexican: "Powerful but smart.",
};

const DERBY_ICONS: Record<string, string> = {
  long_heel: "🥊",
  short_heel: "⚔️",
  pilipino: "⚡",
  mexican: "💪",
};

const PRIZE_TIER_LABELS: Record<string, string> = {
  standard: "Standard",
  grand: "Grand",
  prestigious: "Prestigious",
};

export default function Tournaments() {
  const [list, setList] = useState<TournamentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const { state, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    api<TournamentResponse[]>("/api/tournaments")
      .then(setList)
      .catch(() => setList([]))
      .finally(() => setLoading(false));
  }, []);

  if (state.loading) return <div className="page">Loading...</div>;
  if (!state.token) {
    return (
      <div className="page">
        <p>Please <Link to="/login">sign in</Link> to view derbies.</p>
      </div>
    );
  }

  return (
    <div className="page">
      <header className="header">
        <h1>Derbies</h1>
        <p className="balance">Tokens: {state.tokenBalance}</p>
        <nav>
          <Link to="/">Home</Link>
          {state.isAdmin && <Link to="/admin">Admin</Link>}
          <button type="button" onClick={() => { logout(); navigate("/login"); }}>Logout</button>
        </nav>
      </header>
      {loading ? (
        <p>Loading derbies...</p>
      ) : (
        <ul className="tournament-list">
          {list.map((t) => (
            <li key={t.id} className="tournament-card">
              <h3><span className="derby-icon" aria-hidden="true">{DERBY_ICONS[t.derby_type] ?? "🎯"}</span> {t.name}</h3>
              <p>{DERBY_LABELS[t.derby_type] || t.derby_type} · {t.total_rounds} rounds</p>
              {DERBY_DESCRIPTIONS[t.derby_type] && (
                <p className="derby-desc">{DERBY_DESCRIPTIONS[t.derby_type]}</p>
              )}
              <p className="entry-fee">Entry fee: {entryCostForTier(t.prize_tier)} coins</p>
              <p className="prize-tier">Prize tier: {PRIZE_TIER_LABELS[t.prize_tier ?? "standard"] ?? "Standard"}</p>
              <p>Status: <strong>{t.status}</strong> · Entries: {t.entry_count ?? 0}</p>
              {(t.status === "draft" || t.status === "scheduled") && (
                <Link to={`/enter/${t.id}`}>Enter this derby</Link>
              )}
              <Link to={`/bracket/${t.id}`}>View bracket</Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
