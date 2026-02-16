import { useEffect, useMemo, useState } from 'react';
import { BoltIcon, CheckIcon, CoffeeIcon, NoteIcon, PauseIcon, PlayIcon, RotateIcon, TagIcon, TimerIcon } from '../../../components/icons';
import { formatApiError } from '../../../shared/api/httpClient';
import { listRuns, submitScore, type OptimizerRun } from '../api/optimizerApi';

interface BrewStep {
  name: string;
  duration: number;
}

const defaultSteps: BrewStep[] = [
  { name: 'Bloom', duration: 30 },
  { name: 'Pour', duration: 30 },
  { name: 'Stir/Swirl', duration: 10 },
  { name: 'Steep', duration: 60 },
  { name: 'Plunge', duration: 30 },
];

const tastes = ['sour', 'bitter', 'weak', 'strong', 'balanced'];

function formatClock(totalSeconds: number) {
  const mins = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
  const secs = Math.floor(totalSeconds % 60).toString().padStart(2, '0');
  return `${mins}:${secs}`;
}

export function BrewSessionPage() {
  const [setup, setSetup] = useState({ method: 'aeropress', brand: '', dose: 18, grind: 12, temp: 90, ratio: '1:15', targetTime: 160 });
  const [steps] = useState(defaultSteps);
  const [stepIndex, setStepIndex] = useState(0);
  const [stepRemaining, setStepRemaining] = useState(defaultSteps[0].duration);
  const [elapsed, setElapsed] = useState(0);
  const [running, setRunning] = useState(false);
  const [score, setScore] = useState(8);
  const [selectedTastes, setSelectedTastes] = useState<string[]>([]);
  const [notes, setNotes] = useState('');
  const [activeRun, setActiveRun] = useState<OptimizerRun | null>(null);
  const [sessions, setSessions] = useState<any[]>([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const raw = localStorage.getItem('brew_sessions');
    if (raw) setSessions(JSON.parse(raw));

    listRuns().then((runs) => {
      const candidate = runs.find((run) => run.status !== 'finished' || run.latest_trial?.state === 'suggested') ?? runs[0] ?? null;
      setActiveRun(candidate);
    }).catch(() => setActiveRun(null));
  }, []);

  useEffect(() => {
    if (!running) return undefined;
    const id = window.setInterval(() => {
      setElapsed((prev) => prev + 1);
      setStepRemaining((prev) => {
        if (prev > 1) return prev - 1;
        setStepIndex((idx) => Math.min(idx + 1, steps.length - 1));
        return steps[Math.min(stepIndex + 1, steps.length - 1)].duration;
      });
    }, 1000);
    return () => window.clearInterval(id);
  }, [running, stepIndex, steps]);

  const totalDuration = useMemo(() => steps.reduce((sum, step) => sum + step.duration, 0), [steps]);
  const completed = useMemo(() => steps.slice(0, stepIndex).reduce((sum, step) => sum + step.duration, 0) + (steps[stepIndex].duration - stepRemaining), [stepIndex, stepRemaining, steps]);
  const progress = Math.min(100, Math.round((completed / totalDuration) * 100));
  const bestScore = useMemo(() => Math.max(...sessions.map((s) => s.score), 0), [sessions]);

  const applySuggestion = () => {
    const params = activeRun?.latest_trial?.parameters;
    if (!params) {
      setError('No optimiser suggestion available yet.');
      return;
    }

    setSetup((prev) => ({
      ...prev,
      dose: Number(params.coffee_amount ?? prev.dose),
      grind: Number(params.grinder_setting_clicks ?? prev.grind),
      temp: Number(params.temperature_c ?? prev.temp),
      targetTime: Number(params.brew_time_seconds ?? prev.targetTime),
    }));

    setError('');
    setMessage('Applied current optimiser suggestion.');
  };

  const resetTimer = () => {
    setRunning(false);
    setStepIndex(0);
    setStepRemaining(steps[0].duration);
    setElapsed(0);
  };

  const saveSession = () => {
    const item = {
      id: Date.now(),
      setup,
      score,
      tastes: selectedTastes,
      notes,
      createdAt: new Date().toISOString(),
    };
    const updated = [item, ...sessions].slice(0, 20);
    setSessions(updated);
    localStorage.setItem('brew_sessions', JSON.stringify(updated));
    setMessage('Session saved locally.');
  };

  const submitToOptimiser = async () => {
    if (!activeRun?.latest_trial) {
      setError('No active optimiser trial waiting for score.');
      return;
    }

    try {
      const updated = await submitScore(activeRun.id, activeRun.latest_trial.id, score);
      setActiveRun(updated);
      setMessage('Submitted session score to optimiser.');
      setError('');
    } catch (err) {
      setError(formatApiError(err));
    }
  };

  const toggleTaste = (taste: string) => {
    setSelectedTastes((prev) => prev.includes(taste) ? prev.filter((t) => t !== taste) : [...prev, taste]);
  };

  return (
    <section className="brew-layout fade-in-up">
      {error ? <div className="error-banner">{error}</div> : null}
      {message ? <div className="success-banner">{message}</div> : null}

      <div className="panel">
        <p className="eyebrow">Setup</p>
        <h2>Brew Session</h2>
        <p className="muted">Setup → Brew timer steps → Rate → Save → Learn</p>

        <div className="setup-grid">
          <label>Method<select value={setup.method} onChange={(e) => setSetup({ ...setup, method: e.target.value })}><option value="aeropress">Aeropress</option><option value="pourover">Pourover</option></select></label>
          <label>Coffee brand<input value={setup.brand} onChange={(e) => setSetup({ ...setup, brand: e.target.value })} placeholder="Ethiopia Yirgacheffe" /></label>
          <label>Dose (g)<input type="number" value={setup.dose} onChange={(e) => setSetup({ ...setup, dose: Number(e.target.value) })} /></label>
          <label>Grind<input type="number" value={setup.grind} onChange={(e) => setSetup({ ...setup, grind: Number(e.target.value) })} /></label>
          <label>Water temp (°C)<input type="number" value={setup.temp} onChange={(e) => setSetup({ ...setup, temp: Number(e.target.value) })} /></label>
          <label>Ratio<input value={setup.ratio} onChange={(e) => setSetup({ ...setup, ratio: e.target.value })} /></label>
          <label>Target time (s)<input type="number" value={setup.targetTime} onChange={(e) => setSetup({ ...setup, targetTime: Number(e.target.value) })} /></label>
        </div>

        <button className="btn btn-secondary icon-btn" onClick={applySuggestion}><BoltIcon size={14} /> Apply current optimiser suggestion</button>

        <div className="timer-block">
          <div className="progress-ring"><strong>{formatClock(stepRemaining)}</strong><span>{progress}%</span></div>
          <div>
            <p className="muted">Current step</p>
            <h3>{steps[stepIndex].name}</h3>
            <p className="muted">Elapsed: {formatClock(elapsed)} / Target: {formatClock(totalDuration)}</p>
            <div className="timeline">
              {steps.map((step, idx) => (
                <div key={step.name} className={idx === stepIndex ? 'timeline-item active' : idx < stepIndex ? 'timeline-item done' : 'timeline-item'}>
                  <span>{step.name}</span>
                  <small>{step.duration}s</small>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="timer-controls">
          <button className="btn btn-primary icon-btn" onClick={() => setRunning((p) => !p)}>{running ? <PauseIcon size={14} /> : <PlayIcon size={14} />} {running ? 'Pause' : 'Start'}</button>
          <button className="btn btn-secondary icon-btn" onClick={resetTimer}><RotateIcon size={14} /> Reset</button>
          <button className="btn btn-secondary" onClick={() => setStepIndex((idx) => Math.min(idx + 1, steps.length - 1))}>Skip step</button>
          <button className="btn btn-ghost" onClick={() => setStepRemaining((v) => v + 10)}>+10s</button>
        </div>
      </div>

      <div className="panel">
        <p className="eyebrow">Rate & log</p>
        <h3>Capture tasting result</h3>
        <label><TimerIcon size={14} /> Score: {score.toFixed(1)}<input type="range" min={0} max={10} step={0.1} value={score} onChange={(e) => setScore(Number(e.target.value))} /></label>

        <div className="taste-tags">
          {tastes.map((taste) => (
            <button key={taste} className={selectedTastes.includes(taste) ? 'pill active' : 'pill'} onClick={() => toggleTaste(taste)}><TagIcon size={13} /> {taste}</button>
          ))}
        </div>

        <label><NoteIcon size={14} /> Notes<textarea className="textarea" value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Describe extraction, balance, aftertaste…" /></label>

        <div className="timer-controls">
          <button className="btn btn-primary" onClick={submitToOptimiser}>Submit to optimiser</button>
          <button className="btn btn-secondary" onClick={saveSession}>Save session</button>
        </div>

        <hr />
        <h3>Session summary</h3>
        <pre className="result-box">{JSON.stringify({ setup, score, selectedTastes, notes, activeRun: activeRun?.id }, null, 2)}</pre>
        <div className="stats-grid compact">
          <div className="stat"><span>Personal best</span><strong>{bestScore ? bestScore.toFixed(1) : '-'}</strong></div>
          <div className="stat"><span>Delta vs best</span><strong>{bestScore ? (score - bestScore).toFixed(1) : '-'}</strong></div>
          <div className="stat"><span>Next suggestion preview</span><strong>{activeRun?.latest_trial?.state ?? 'unavailable'}</strong></div>
        </div>

        {!sessions.length ? (
          <div className="empty-state"><CoffeeIcon size={18} /><p>No saved sessions yet. Brew once and save to start learning trends.</p></div>
        ) : (
          <div className="session-list">
            {sessions.slice(0, 3).map((item) => <p key={item.id}><CheckIcon size={14} /> {new Date(item.createdAt).toLocaleString()} · score {item.score}</p>)}
          </div>
        )}
      </div>
    </section>
  );
}
