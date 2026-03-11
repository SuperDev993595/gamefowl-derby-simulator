import { Link } from "react-router-dom";
import { useAuth } from "../auth";

export default function Settings() {
  const { state } = useAuth();

  return (
    <div className="page">
      <header className="header">
        <Link to="/">← Home</Link>
        {state.token && <Link to="/tournaments">Derbies</Link>}
      </header>
      <h1>Settings</h1>
      <section className="settings-placeholder">
        <p>Game and account settings will appear here.</p>
        <p className="muted">Sound · Display · Notifications</p>
      </section>
    </div>
  );
}
