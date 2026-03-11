import { Routes, Route, Link } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Tournaments from "./pages/Tournaments";
import EnterTournament from "./pages/EnterTournament";
import Bracket from "./pages/Bracket";
import Admin from "./pages/Admin";
import Leaderboards from "./pages/Leaderboards";
import Settings from "./pages/Settings";
import MyEntry from "./pages/MyEntry";
import "./App.css";

function Home() {
  const { state } = useAuth();
  if (state.loading) return <div className="page">Loading...</div>;
  return (
    <div className="page home-landing">
      <h1 className="game-title">GAMEFOWL DERBY</h1>
      <p className="tagline">Select roosters, enter derbies, and compete.</p>
      <nav className="main-menu">
        {state.token ? (
          <>
            <Link to="/tournaments" className="menu-btn">Enter Tournament</Link>
            <Link to="/my-entry" className="menu-btn">My Entry</Link>
            <Link to="/tournaments" className="menu-btn">The Keep</Link>
            <Link to="/leaderboards" className="menu-btn">Leaderboards</Link>
            <Link to="/settings" className="menu-btn">Settings</Link>
            <span className="balance-inline">Tokens: {state.tokenBalance}</span>
          </>
        ) : (
          <>
            <Link to="/login" className="menu-btn">Sign in</Link>
            <Link to="/register" className="menu-btn">Register</Link>
          </>
        )}
      </nav>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/tournaments" element={<Tournaments />} />
        <Route path="/my-entry" element={<MyEntry />} />
        <Route path="/enter/:id" element={<EnterTournament />} />
        <Route path="/bracket/:id" element={<Bracket />} />
        <Route path="/leaderboards" element={<Leaderboards />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/admin" element={<Admin />} />
      </Routes>
    </AuthProvider>
  );
}
