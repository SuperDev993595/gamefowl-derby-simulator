import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api, BreedResponse, TournamentResponse } from "../api";
import { breedImageUrl } from "../api";
import { useAuth } from "../auth";

export default function EnterTournament() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { state, refreshBalance } = useAuth();
  const [tournament, setTournament] = useState<TournamentResponse | null>(null);
  const [breeds, setBreeds] = useState<BreedResponse[]>([]);
  const [selectedBreedId, setSelectedBreedId] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    api<TournamentResponse>(`/api/tournaments/${id}`).then(setTournament).catch(() => setTournament(null));
    api<BreedResponse[]>("/api/breeds").then(setBreeds).catch(() => setBreeds([]));
  }, [id]);

  if (!state.token) {
    return (
      <div className="page">
        <p>Please <Link to="/login">sign in</Link> to enter.</p>
      </div>
    );
  }
  if (!tournament) return <div className="page">Loading...</div>;
  if (tournament.status !== "draft" && tournament.status !== "scheduled") {
    return <div className="page">Registration is closed for this derby.</div>;
  }

  async function handleEnter() {
    if (selectedBreedId == null) {
      setError("Select a breed");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      await api(`/api/entries/tournaments/${id}/enter`, {
        method: "POST",
        body: JSON.stringify({ breed_id: selectedBreedId }),
      });
      await refreshBalance();
      navigate(`/bracket/${id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to enter");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page">
      <header className="header">
        <Link to="/tournaments">← Derbies</Link>
        <p className="balance">Tokens: {state.tokenBalance}</p>
      </header>
      <h1>Enter: {tournament.name}</h1>
      <p>Entry cost: 10 tokens. Choose your rooster (breed).</p>
      {error && <p className="error">{error}</p>}
      <div className="breed-grid">
        {breeds.map((b) => (
          <button
            key={b.id}
            type="button"
            className={`breed-card ${selectedBreedId === b.id ? "selected" : ""}`}
            onClick={() => setSelectedBreedId(b.id)}
          >
            <img src={breedImageUrl(b.image_filename)} alt={b.name} />
            <span>{b.name}</span>
          </button>
        ))}
      </div>
      <button type="button" onClick={handleEnter} disabled={submitting || selectedBreedId == null}>
        {submitting ? "Entering..." : "Pay & Enter"}
      </button>
    </div>
  );
}
