import { Link } from "react-router-dom";
import { useAuth } from "../auth";

export default function Leaderboards() {
  const { state } = useAuth();

  return (
    <div className="page">
      <header className="header">
        <Link to="/">← Home</Link>
        {state.token && <Link to="/tournaments">Derbies</Link>}
      </header>
      <h1>Leaderboards</h1>
      <p className="section-desc">Top players, top breeds, and seasonal rankings.</p>
      <section className="leaderboards-placeholder">
        <p>Leaderboard data will appear here once rankings are available.</p>
        <p className="muted">Top players · Top breeds · Seasonal rankings</p>
      </section>
    </div>
  );
}
