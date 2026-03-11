import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, breedImageUrl } from "../api";
import type { BreedResponse } from "../api";
import { useAuth } from "../auth";

const QUALITY_NAMES = ["Power", "Speed", "Intelligence", "Accuracy", "Stamina"] as const;
const DERBY_LABELS: Record<string, string> = {
  long_heel: "Long Heel",
  short_heel: "Short Heel",
  pilipino: "Pilipino",
  mexican: "Mexican",
};

function ratingLabel(value: number): string {
  if (value <= 3) return "Low";
  if (value <= 5) return "Medium";
  if (value <= 7) return "High";
  return "Very High";
}

export default function MyEntry() {
  const { state } = useAuth();
  const [breeds, setBreeds] = useState<BreedResponse[]>([]);
  const [derbyFilter, setDerbyFilter] = useState<string>("long_heel");

  useEffect(() => {
    api<BreedResponse[]>("/api/breeds").then(setBreeds).catch(() => setBreeds([]));
  }, []);

  if (!state.token) {
    return (
      <div className="page">
        <p>Please <Link to="/login">sign in</Link> to view your entry options.</p>
      </div>
    );
  }

  const getTraitForDerby = (b: BreedResponse) =>
    b.traits?.find((t) => t.derby_type === derbyFilter);

  return (
    <div className="page">
      <header className="header">
        <Link to="/">← Home</Link>
        <Link to="/tournaments">Enter Tournament</Link>
        <p className="balance">Tokens: {state.tokenBalance}</p>
      </header>
      <h1>My Entry</h1>
      <p className="section-desc">
        Browse all breeds. Each breed includes an image and ratings. Select up to 10 roosters (same or mixed breeds) when entering a derby.
      </p>
      <div className="derby-filter">
        <label>Qualities for derby type:</label>
        <select value={derbyFilter} onChange={(e) => setDerbyFilter(e.target.value)}>
          {Object.entries(DERBY_LABELS).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>
      </div>
      <div className="breed-gallery my-entry-gallery">
        {breeds.map((b) => {
          const trait = getTraitForDerby(b);
          const ratings = trait
            ? [trait.power, trait.speed, trait.intelligence, trait.accuracy, trait.stamina]
            : [];
          return (
            <article key={b.id} className="breed-card-large">
              <img src={breedImageUrl(b.image_filename)} alt={b.name} />
              <h3>{b.name}</h3>
              <p className="breed-description">
                {b.description || "A classic gamefowl breed. Traits vary by derby type and keep style."}
              </p>
              {ratings.length === 5 && (
                <ul className="breed-qualities">
                  {QUALITY_NAMES.map((name, i) => (
                    <li key={name}>{name}: {ratingLabel(ratings[i])}</li>
                  ))}
                </ul>
              )}
              <Link to={`/tournaments`} className="link-button">Enter a derby</Link>
            </article>
          );
        })}
      </div>
    </div>
  );
}
