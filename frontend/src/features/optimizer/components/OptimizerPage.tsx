import { FormEvent, useEffect, useMemo, useState } from 'react';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { createRunEvents, fetchRecommendation, startRun, submitScore } from '../api/optimizerApi';

export function OptimizerPage() {
  const [method, setMethod] = useState('median');
  const [nTrials, setNTrials] = useState(50);
  const [selectedPersons, setSelectedPersons] = useState('');
  const [run, setRun] = useState<any>(null);
  const [score, setScore] = useState(8);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState('');
  const [history, setHistory] = useState<{ trial: number; score: number }[]>([]);
  const [recommendation, setRecommendation] = useState<any>(null);

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(''), 2500);
    return () => clearTimeout(t);
  }, [toast]);

  const start = async () => {
    setLoading(true);
    try {
      const data = await startRun({ method, n_trials: nTrials, selected_persons: selectedPersons.split(',').filter(Boolean) });
      setRun(data);
      setToast('Optimization started');
      if (data.latest_trial?.score) setHistory((prev) => [...prev, { trial: data.latest_trial.trial_number, score: data.latest_trial.score }]);
    } finally {
      setLoading(false);
    }
  };

  const onSubmitScore = async (e: FormEvent) => {
    e.preventDefault();
    if (!run?.latest_trial) return;
    const data = await submitScore(run.id, run.latest_trial.id, score);
    setRun(data);
    setHistory((prev) => [...prev, { trial: data.trial_count, score }]);
    setToast('Score submitted');
  };


  useEffect(() => {
    if (!run?.id) return;
    const token = localStorage.getItem('coffee_token');
    if (!token) return;
    const events = createRunEvents(run.id, token);
    events.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      setRun((prev: any) => prev ? { ...prev, status: payload.run_status, best_score: payload.best_score, best_params: payload.best_parameters } : prev);
      if (payload.last_trial_score !== null && payload.last_trial_score !== undefined) {
        setHistory((prev) => [...prev, { trial: payload.trial_number, score: payload.last_trial_score }]);
      }
    };
    return () => events.close();
  }, [run?.id]);
  const runState = useMemo(() => run?.status ?? 'idle', [run]);

  return (
    <section className="optimizer-layout">
      {toast ? <div className="toast">{toast}</div> : null}
      <div className="panel">
        <h2>Optimizer configuration</h2>
        <label>Selected persons (comma separated)<input value={selectedPersons} onChange={(e) => setSelectedPersons(e.target.value)} /></label>
        <label>Method<select value={method} onChange={(e) => setMethod(e.target.value)}><option>median</option><option>mean</option><option>lowest</option><option>highest</option></select></label>
        <label>Trials<input type="number" min={1} max={200} value={nTrials} onChange={(e) => setNTrials(Number(e.target.value))} /></label>
        <button className="btn" onClick={start} disabled={loading || runState === 'running'}>{loading ? 'Starting...' : 'Start Optimisation'}</button>

        <hr />
        <h3>Legacy recommendation</h3>
        <button className="btn btn-secondary" onClick={async () => setRecommendation(await fetchRecommendation({ dataset_prefix: 'aeropress.', method, best_only: false, prior_weight: 0.666 }))}>Get recommendation</button>
        {recommendation ? <p>Suggested: {recommendation.suggested_parameters?.[0]?.name}</p> : <p className="skeleton">No recommendation yet</p>}
      </div>

      <div className="panel">
        <h2>Live optimisation panel</h2>
        <p>Run status: <strong>{runState}</strong></p>
        <p>Trial counter: {run?.trial_count ?? 0} / {run?.n_trials ?? nTrials}</p>
        <p>Best score: {run?.best_score ?? '-'}</p>
        <pre className="result-box">{JSON.stringify(run?.best_params ?? {}, null, 2)}</pre>

        <div style={{ width: '100%', height: 220 }}>
          <ResponsiveContainer>
            <LineChart data={history}>
              <XAxis dataKey="trial" /><YAxis domain={[0, 10]} /><Tooltip />
              <Line dataKey="score" stroke="#22c55e" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {run?.latest_trial?.state === 'suggested' ? (
          <form onSubmit={onSubmitScore} className="form-grid">
            <h3>Submit Score</h3>
            <pre className="result-box">{JSON.stringify(run.latest_trial.parameters, null, 2)}</pre>
            <label>Score<input type="number" min={0} max={10} step={0.1} value={score} onChange={(e) => setScore(Number(e.target.value))} /></label>
            <button className="btn">Submit Score</button>
          </form>
        ) : null}
      </div>
    </section>
  );
}
