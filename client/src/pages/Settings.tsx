import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth";

const KEY_SOUND = "settings_sound";
const KEY_REDUCED_MOTION = "settings_reduced_motion";

export default function Settings() {
  const { state } = useAuth();
  const [sound, setSound] = useState(() => localStorage.getItem(KEY_SOUND) !== "false");
  const [reducedMotion, setReducedMotion] = useState(() => localStorage.getItem(KEY_REDUCED_MOTION) === "true");

  useEffect(() => {
    localStorage.setItem(KEY_SOUND, String(sound));
  }, [sound]);

  useEffect(() => {
    localStorage.setItem(KEY_REDUCED_MOTION, String(reducedMotion));
    document.documentElement.classList.toggle("reduce-motion", reducedMotion);
  }, [reducedMotion]);

  return (
    <div className="page">
      <header className="header">
        <Link to="/">← Home</Link>
        {state.token && <Link to="/tournaments">Derbies</Link>}
      </header>
      <h1>Settings</h1>
      <section className="settings-section">
        <h2>Sound</h2>
        <label className="setting-row">
          <input type="checkbox" checked={sound} onChange={(e) => setSound(e.target.checked)} />
          <span>Ambient sound (crowd, rooster) when enabled. No sounds used if off.</span>
        </label>
      </section>
      <section className="settings-section">
        <h2>Display</h2>
        <label className="setting-row">
          <input type="checkbox" checked={reducedMotion} onChange={(e) => setReducedMotion(e.target.checked)} />
          <span>Reduce motion (minimize animations).</span>
        </label>
      </section>
    </div>
  );
}
