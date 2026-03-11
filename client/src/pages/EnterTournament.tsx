import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api, breedImageUrl } from "../api";
import type { BreedResponse, TournamentResponse } from "../api";
import { useAuth } from "../auth";

const QUALITY_NAMES = ["Power", "Speed", "Intelligence", "Accuracy", "Stamina"] as const;
const ENTRY_FEE_COINS = 10;

function ratingLabel(value: number): string {
  if (value <= 3) return "Low";
  if (value <= 5) return "Medium";
  if (value <= 7) return "High";
  return "Very High";
}

// Mirror backend derby/keep modifiers for attribute preview (doc: Dynamic Attribute Adjustment)
const DERBY_MODS: Record<string, number[]> = {
  long_heel: [1, 1, 1, 1, 1],
  short_heel: [1.15, 0.85, 0.95, 1.05, 1.1],
  pilipino: [0.95, 1.2, 1.1, 1.15, 0.85],
  mexican: [1.1, 1, 1.05, 1.25, 1.25],
};
const KEEP_MODS: Record<string, number[]> = {
  bench: [1.05, 0.95, 1, 1, 1.1],
  flypen: [1, 1.1, 1.05, 1.05, 0.9],
};
function adjustedTraits(base: number[], derbyType: string, keepType: string): number[] {
  const d = DERBY_MODS[derbyType] ?? DERBY_MODS.long_heel;
  const k = KEEP_MODS[keepType] ?? KEEP_MODS.bench;
  return base.map((v, i) => Math.min(10, Math.round(v * d[i] * k[i])));
}

export default function EnterTournament() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { state, refreshBalance } = useAuth();
  const [tournament, setTournament] = useState<TournamentResponse | null>(null);
  const [breeds, setBreeds] = useState<BreedResponse[]>([]);
  const [selectedBreedId, setSelectedBreedId] = useState<number | null>(null);
  const [keepType, setKeepType] = useState<"bench" | "flypen">("bench");
  const [showConfirmation, setShowConfirmation] = useState(false);
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

  const derbyType = tournament.derby_type;
  const getTraitForDerby = (b: BreedResponse) =>
    b.traits?.find((t) => t.derby_type === derbyType);

  function handleReturnToSelection() {
    setShowConfirmation(false);
  }

  async function handleEnterDerby() {
    if (selectedBreedId == null) {
      setError("Select a breed");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      await api(`/api/entries/tournaments/${id}/enter`, {
        method: "POST",
        body: JSON.stringify({ breed_id: selectedBreedId, keep_type: keepType }),
      });
      await refreshBalance();
      navigate(`/bracket/${id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to enter");
    } finally {
      setSubmitting(false);
    }
  }

  const selectedBreed = selectedBreedId != null ? breeds.find((b) => b.id === selectedBreedId) : null;
  const baseRatings = selectedBreed ? (() => {
    const t = getTraitForDerby(selectedBreed);
    return t ? [t.power, t.speed, t.intelligence, t.accuracy, t.stamina] : [];
  })() : [];
  const adjustedRatings = baseRatings.length === 5 ? adjustedTraits(baseRatings, derbyType, keepType) : [];
  const canConfirm = selectedBreedId != null;
  const roosterCount = selectedBreedId != null ? 1 : 0;

  const derbyLabel = { long_heel: "Long Heel", short_heel: "Short Heel", pilipino: "Pilipino", mexican: "Mexican" }[derbyType] ?? derbyType;
  const keepLabel = keepType === "bench" ? "Bench" : "Flypen";

  return (
    <div className="page">
      <header className="header">
        <Link to="/tournaments">← Derbies</Link>
        <p className="balance">Tokens: {state.tokenBalance}</p>
      </header>
      <h1>Enter: {tournament.name}</h1>
      <p>Entry cost: {ENTRY_FEE_COINS} tokens. Choose your rooster (breed) and Keep style.</p>
      {error && <p className="error">{error}</p>}

      {!showConfirmation ? (
        <>
          <section className="keep-selection">
            <h3>The Keep</h3>
            <div className="keep-options">
              <label className={keepType === "bench" ? "selected" : ""}>
                <input
                  type="radio"
                  name="keep"
                  value="bench"
                  checked={keepType === "bench"}
                  onChange={() => setKeepType("bench")}
                />
                <span><strong>Bench Keep</strong> — Improves endurance, durability, recovery; slightly reduces explosive speed.</span>
              </label>
              <label className={keepType === "flypen" ? "selected" : ""}>
                <input
                  type="radio"
                  name="keep"
                  value="flypen"
                  checked={keepType === "flypen"}
                  onChange={() => setKeepType("flypen")}
                />
                <span><strong>Flypen Keep</strong> — Improves agility, speed, reflex; slightly reduces stamina.</span>
              </label>
            </div>
          </section>

          <h3>Select breed (five qualities for this derby)</h3>
          <div className="breed-grid">
            {breeds.map((b) => {
              const trait = getTraitForDerby(b);
              const ratings = trait
                ? [trait.power, trait.speed, trait.intelligence, trait.accuracy, trait.stamina]
                : [];
              return (
                <button
                  key={b.id}
                  type="button"
                  className={`breed-card ${selectedBreedId === b.id ? "selected" : ""}`}
                  onClick={() => setSelectedBreedId(b.id)}
                >
                  <img src={breedImageUrl(b.image_filename)} alt={b.name} />
                  <span>{b.name}</span>
                  {ratings.length === 5 && (
                    <ul className="breed-qualities">
                      {QUALITY_NAMES.map((name, i) => (
                        <li key={name}>{name}: {ratingLabel(ratings[i])}</li>
                      ))}
                    </ul>
                  )}
                </button>
              );
            })}
          </div>

          <div className="entry-lineup-bar">
            <span className="lineup-label">Roosters entered: {roosterCount} / 10</span>
            {selectedBreed && <span className="lineup-slot">{selectedBreed.name}</span>}
          </div>

          <button
            type="button"
            onClick={() => setShowConfirmation(true)}
            disabled={!canConfirm}
          >
            Review entry
          </button>
        </>
      ) : (
        <section className="entry-confirmation">
          <h3>Derby Entry Confirmation</h3>
          <p><strong>Derby name:</strong> {tournament.name}</p>
          <p><strong>Derby type:</strong> {derbyLabel}</p>
          <p className="entry-fee"><strong>Entry fee:</strong> {ENTRY_FEE_COINS} coins</p>
          <p><strong>Roosters entered:</strong> {roosterCount} / 10</p>
          <p><strong>Keep type:</strong> {keepLabel}</p>

          {adjustedRatings.length === 5 && (
            <div className="attr-preview">
              <p>Adjusted attributes (derby + keep):</p>
              {QUALITY_NAMES.map((name, i) => (
                <div key={name} className="attr-row">
                  <span className="attr-name">{name}</span>
                  <div className="attr-bar">
                    <div className="attr-fill" style={{ width: `${adjustedRatings[i] * 10}%` }} />
                  </div>
                  <span>{adjustedRatings[i]}/10</span>
                </div>
              ))}
            </div>
          )}

          <div className="confirmation-actions">
            <button type="button" onClick={handleEnterDerby} disabled={submitting}>
              {submitting ? "Entering..." : "Enter the Derby"}
            </button>
            <button type="button" onClick={handleReturnToSelection} disabled={submitting}>
              Return to Selection
            </button>
          </div>
        </section>
      )}
    </div>
  );
}
