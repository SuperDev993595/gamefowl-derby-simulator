import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, TournamentResponse } from "../api";
import { useAuth } from "../auth";

const DERBY_LABELS: Record<string, string> = {
  long_heel: "Long Heel",
  short_heel: "Short Heel",
  long_blade: "Long Blade",
  short_blade: "Short Blade",
};

export default function Admin() {
  const navigate = useNavigate();
  const { state } = useAuth();
  const [tournaments, setTournaments] = useState<TournamentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [newName, setNewName] = useState("");
  const [newDerbyType, setNewDerbyType] = useState("long_heel");
  const [newRounds, setNewRounds] = useState(10);
  const [advancing, setAdvancing] = useState<number | null>(null);

  useEffect(() => {
    if (!state.token) {
      navigate("/login");
      return;
    }
    if (!state.isAdmin) {
      navigate("/");
      return;
    }
    api<TournamentResponse[]>("/api/tournaments")
      .then(setTournaments)
      .catch(() => setTournaments([]))
      .finally(() => setLoading(false));
  }, [state.token, state.isAdmin, navigate]);

  async function createTournament(e: React.FormEvent) {
    e.preventDefault();
    try {
      const t = await api<TournamentResponse>("/api/tournaments", {
        method: "POST",
        body: JSON.stringify({
          name: newName || "New Derby",
          derby_type: newDerbyType,
          total_rounds: newRounds,
        }),
      });
      setTournaments((prev) => [t, ...prev]);
      setNewName("");
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed");
    }
  }

  async function startTournament(tid: number) {
    try {
      await api(`/api/admin/tournaments/${tid}/start`, { method: "POST" });
      setTournaments((prev) => prev.map((t) => (t.id === tid ? { ...t, status: "running" } : t)));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed");
    }
  }

  async function advanceRound(tid: number) {
    setAdvancing(tid);
    try {
      const res = await api<{ event: string; current_round: number }>(`/api/admin/tournaments/${tid}/advance-round`, { method: "POST" });
      setTournaments((prev) => prev.map((t) => (t.id === tid ? { ...t, current_round: res.current_round, status: res.event === "tournament_finished" ? "finished" : t.status } : t)));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed");
    } finally {
      setAdvancing(null);
    }
  }

  async function restartTournament(tid: number) {
    if (!confirm("Restart this tournament? All matches and entry stats will be reset.")) return;
    try {
      await api(`/api/admin/tournaments/${tid}/restart`, { method: "POST" });
      setTournaments((prev) => prev.map((t) => (t.id === tid ? { ...t, status: "draft", current_round: 0 } : t)));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed");
    }
  }

  async function cloneTournament(tid: number) {
    try {
      await api<{ id: number; name: string }>(`/api/admin/tournaments/${tid}/clone`, { method: "POST" });
      const list = await api<TournamentResponse[]>("/api/tournaments");
      setTournaments(list);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed");
    }
  }

  return (
    <div className="page">
      <header className="header">
        <Link to="/tournaments">← Derbies</Link>
      </header>
      <h1>Admin</h1>
      <form onSubmit={createTournament} className="admin-form">
        <h2>Create tournament</h2>
        <input
          type="text"
          placeholder="Tournament name"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
        />
        <select value={newDerbyType} onChange={(e) => setNewDerbyType(e.target.value)}>
          {Object.entries(DERBY_LABELS).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>
        <input
          type="number"
          min={10}
          max={20}
          value={newRounds}
          onChange={(e) => setNewRounds(Number(e.target.value))}
        />
        <button type="submit">Create</button>
      </form>

      <h2>Tournaments</h2>
      {loading ? <p>Loading...</p> : (
        <ul className="tournament-list">
          {tournaments.map((t) => (
            <li key={t.id} className="tournament-card admin-card">
              <h3>{t.name}</h3>
              <p>{DERBY_LABELS[t.derby_type]} · {t.total_rounds} rounds · Round {t.current_round} · {t.entry_count ?? 0} entries</p>
              <p>Status: <strong>{t.status}</strong></p>
              <div className="admin-actions">
                {(t.status === "draft" || t.status === "scheduled") && (
                  <button type="button" onClick={() => startTournament(t.id)}>Start</button>
                )}
                {t.status === "running" && (
                  <button type="button" onClick={() => advanceRound(t.id)} disabled={advancing === t.id}>
                    {advancing === t.id ? "Advancing..." : "Advance round"}
                  </button>
                )}
                {(t.status === "draft" || t.status === "scheduled" || t.status === "finished") && (
                  <button type="button" onClick={() => restartTournament(t.id)}>Restart</button>
                )}
                <button type="button" onClick={() => cloneTournament(t.id)}>Clone</button>
                <Link to={`/bracket/${t.id}`}>View bracket</Link>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
