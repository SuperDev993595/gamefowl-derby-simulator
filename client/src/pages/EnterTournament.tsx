import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api, breedImageUrl, entryCostForTier } from "../api";
import type { BreedResponse, TournamentResponse } from "../api";
import { useAuth } from "../auth";

const QUALITY_NAMES = ["Power", "Speed", "Intelligence", "Accuracy", "Stamina"] as const;
const MAX_ROOSTERS = 10;

function ratingLabel(value: number): string {
  if (value <= 3) return "Low";
  if (value <= 5) return "Medium";
  if (value <= 7) return "High";
  return "Very High";
}

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
  const [lineup, setLineup] = useState<number[]>([]); // breed_ids, 1–10
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
  const entryCost = entryCostForTier(tournament.prize_tier);
  const getTraitForDerby = (b: BreedResponse) =>
    b.traits?.find((t) => t.derby_type === derbyType);

  function addToLineup(breedId: number) {
    if (lineup.length >= MAX_ROOSTERS) return;
    setLineup((prev) => [...prev, breedId]);
  }

  function removeFromLineup(index: number) {
    setLineup((prev) => prev.filter((_, i) => i !== index));
  }

  function handleReturnToSelection() {
    setShowConfirmation(false);
  }

  async function handleEnterDerby() {
    if (lineup.length === 0) {
      setError("Select at least one rooster");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      await api(`/api/entries/tournaments/${id}/enter`, {
        method: "POST",
        body: JSON.stringify({ breed_ids: lineup, keep_type: keepType }),
      });
      await refreshBalance();
      navigate(`/bracket/${id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to enter");
    } finally {
      setSubmitting(false);
    }
  }

  const primaryBreed = lineup.length > 0 ? breeds.find((b) => b.id === lineup[0]) : null;
  const baseRatings = primaryBreed
    ? (() => {
        const t = getTraitForDerby(primaryBreed);
        return t ? [t.power, t.speed, t.intelligence, t.accuracy, t.stamina] : [];
      })()
    : [];
  const adjustedRatings = baseRatings.length === 5 ? adjustedTraits(baseRatings, derbyType, keepType) : [];
  const canConfirm = lineup.length >= 1;

  const derbyLabel = { long_heel: "Long Heel", short_heel: "Short Heel", pilipino: "Pilipino", mexican: "Mexican" }[derbyType] ?? derbyType;
  const keepLabel = keepType === "bench" ? "Bench" : "Flypen";

  return (
    <div className="page">
      <header className="header">
        <Link to="/tournaments">← Derbies</Link>
        <p className="balance">Tokens: {state.tokenBalance}</p>
      </header>
      <h1>Enter: {tournament.name}</h1>
      <p>Entry cost: {entryCost} tokens. Select 1–10 roosters (same or mixed breeds), then choose Keep style.</p>
      {error && <p className="error">{error}</p>}

      {!showConfirmation ? (
        <>
          <h3>Select breed (five qualities for this derby)</h3>
          <div className="breed-grid breed-grid-with-desc">
            {breeds.map((b) => {
              const trait = getTraitForDerby(b);
              const ratings = trait
                ? [trait.power, trait.speed, trait.intelligence, trait.accuracy, trait.stamina]
                : [];
              const canAdd = lineup.length < MAX_ROOSTERS;
              return (
                <button
                  key={b.id}
                  type="button"
                  className="breed-card breed-card-with-desc"
                  onClick={() => canAdd && addToLineup(b.id)}
                  disabled={!canAdd}
                >
                  <img src={breedImageUrl(b.image_filename)} alt={b.name} />
                  <span>{b.name}</span>
                  {b.description && <p className="breed-desc">{b.description}</p>}
                  {ratings.length === 5 && (
                    <ul className="breed-qualities">
                      {QUALITY_NAMES.map((name, i) => (
                        <li key={name}>{name}: {ratingLabel(ratings[i])}</li>
                      ))}
                    </ul>
                  )}
                  {canAdd && <span className="add-hint">+ Add to lineup</span>}
                </button>
              );
            })}
          </div>

          <section className="keep-selection">
            <h3>The Keep</h3>
            <div className="keep-options">
              <label className={keepType === "bench" ? "selected" : ""}>
                <input type="radio" name="keep" value="bench" checked={keepType === "bench"} onChange={() => setKeepType("bench")} />
                <span><strong>Bench Keep</strong> — Improves endurance, durability, recovery; slightly reduces explosive speed.</span>
              </label>
              <label className={keepType === "flypen" ? "selected" : ""}>
                <input type="radio" name="keep" value="flypen" checked={keepType === "flypen"} onChange={() => setKeepType("flypen")} />
                <span><strong>Flypen Keep</strong> — Improves agility, speed, reflex; slightly reduces stamina.</span>
              </label>
            </div>
          </section>

          <div className="entry-lineup-bar">
            <span className="lineup-label">Roosters entered: {lineup.length} / {MAX_ROOSTERS}</span>
            {lineup.map((breedId, idx) => {
              const b = breeds.find((x) => x.id === breedId);
              return (
                <span key={`${breedId}-${idx}`} className="lineup-slot">
                  {b?.name ?? `#${breedId}`}
                  <button type="button" className="lineup-remove" onClick={() => removeFromLineup(idx)} aria-label="Remove">×</button>
                </span>
              );
            })}
          </div>

          <button type="button" onClick={() => setShowConfirmation(true)} disabled={!canConfirm}>
            Review entry
          </button>
        </>
      ) : (
        <section className="entry-confirmation">
          <h3>Derby Entry Confirmation</h3>
          <p><strong>Derby name:</strong> {tournament.name}</p>
          <p><strong>Derby type:</strong> {derbyLabel}</p>
          <p className="entry-fee"><strong>Entry fee:</strong> {entryCost} coins</p>
          <p><strong>Roosters entered:</strong> {lineup.length} / {MAX_ROOSTERS}</p>
          <p><strong>Keep type:</strong> {keepLabel}</p>

          {adjustedRatings.length === 5 && primaryBreed && (
            <div className="attr-preview">
              <p>Primary rooster ({primaryBreed.name}) — adjusted attributes (derby + keep):</p>
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
