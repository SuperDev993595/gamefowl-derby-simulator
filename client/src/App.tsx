import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Tournaments from "./pages/Tournaments";
import EnterTournament from "./pages/EnterTournament";
import Bracket from "./pages/Bracket";
import Admin from "./pages/Admin";
import "./App.css";

function Home() {
  const { state } = useAuth();
  if (state.loading) return <div className="page">Loading...</div>;
  if (state.token) return <Navigate to="/tournaments" replace />;
  return (
    <div className="page">
      <h1>Gamefowl Derby</h1>
      <p>Select roosters, enter derbies, and compete. Long Heel, Short Heel, Long Blade, or Short Blade.</p>
      <nav>
        <a href="/login">Sign in</a>
        <a href="/register">Register</a>
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
        <Route path="/enter/:id" element={<EnterTournament />} />
        <Route path="/bracket/:id" element={<Bracket />} />
        <Route path="/admin" element={<Admin />} />
      </Routes>
    </AuthProvider>
  );
}
