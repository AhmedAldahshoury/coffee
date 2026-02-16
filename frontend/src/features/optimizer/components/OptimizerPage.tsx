import { FormEvent, useEffect, useMemo, useState } from 'react';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { BoltIcon, SparkIcon } from '../../../components/icons';
import { createRunEvents, fetchRecommendation, startRun, submitScore } from '../api/optimizerApi';

export function OptimizerPage() {
  const [method, setMethod] = useState('median');
  const [nTrials, setNTrials] = useState(50);
  const [selectedPersons, setSelectedPersons] = useState('');
  const [run, setRun] = useState<any>(null);
  const [score, setScore] = useState(8);
  const [loading, setLoading] = useState(false);
  const [recommendationLoading, setRecommendationLoading] = useState(false);
  const [toast, setToast] = useState<{ message: string; kind: 'success' | 'warning' | 'info' } | null>(null);
  const [history, setHistory] = useState<{ trial: number; score: number }[]>([]);
  const [recommendation, setRecommendation] = useState<any>(null);

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 2500);
    return () => clearTimeout(t);
  }, [toast]);

  const start = async () => {
    setLoading(true);
    try {
      const data = await startRun({ method, n_trials: nTrials, selected_persons: selectedPersons.split(',').map((name) => name.trim()).filter(Boolean) });
      setRun(data);
      setToast({ message: 'Optimization started', kind: 'success' });
      if (data.latest_trial?.score) {
        setHistory((prev) => [...prev, { trial: data.latest_trial.trial_number, score: data.latest_trial.score }]);
      }
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
    setToast({ message: 'Score submitted', kind: 'success' });
  };

  const onLoadRecommendation = async () => {
    setRecommendationLoading(true);
    try {
      const data = await fetchRecommendation({ dataset_prefix: 'aeropress.', method, best_only: false, prior_weight: 0.666 });
      setRecommendation(data);
      setToast({ message: 'Recommendation loaded', kind: 'info' });
    } finally {
      setRecommendationLoading(false);
    }
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
    <section className="optimizer-layout fade-in-up">
      {toast ? (
        <div className={`toast toast-${toast.kind}`}>
          <SparkIcon size={14} />
          <span>{toast.message}</span>
        </div>
      ) : null}
      <div className="panel">
        <p className="eyebrow">Setup</p>
        <h2>Optimizer configuration</h2>
        <p className="muted">Set trial preferences and launch your next precision run.</p>

        <label>
          Selected persons (comma separated)
          <input value={selectedPersons} onChange={(e) => setSelectedPersons(e.target.value)} placeholder="alice,bob,charlie" />
        </label>
        <label>
          Method
          <select value={method} onChange={(e) => setMethod(e.target.value)}>
            <option>median</option>
            <option>mean</option>
            <option>lowest</option>
            <option>highest</option>
          </select>
        </label>
        <label>
          Trials
          <input type="number" min={1} max={200} value={nTrials} onChange={(e) => setNTrials(Number(e.target.value))} />
        </label>
        <button className="btn btn-primary" onClick={start} disabled={loading || runState === 'running'}>
          <BoltIcon size={14} />
          <span>{loading ? 'Starting...' : 'Start optimisation'}</span>
        </button>

        <hr />

        <h3>Legacy recommendation</h3>
        <button className="btn btn-secondary" onClick={onLoadRecommendation} disabled={recommendationLoading}>
          <span>{recommendationLoading ? 'Loading recommendation…' : 'Get recommendation'}</span>
        </button>
        {recommendationLoading ? <p className="skeleton shimmer">Preparing recommendation…</p> : null}
        {recommendation ? <p className="muted">Suggested: {recommendation.suggested_parameters?.[0]?.name}</p> : <p className="muted">No recommendation yet.</p>}
      </div>

      <div className="panel">
        <p className="eyebrow">Realtime</p>
        <h2>Live optimization panel</h2>
        <div className="stats-grid">
          <div className="stat"><span>Status</span><strong>{runState}</strong></div>
          <div className="stat"><span>Trial</span><strong>{run?.trial_count ?? 0} / {run?.n_trials ?? nTrials}</strong></div>
          <div className="stat"><span>Best score</span><strong>{run?.best_score ?? '-'}</strong></div>
        </div>

        <pre className="result-box">{JSON.stringify(run?.best_params ?? {}, null, 2)}</pre>

        <div className="chart-wrap">
          <ResponsiveContainer>
            <LineChart data={history}>
              <XAxis dataKey="trial" tick={{ fill: 'var(--text-muted)', fontSize: 12 }} axisLine={{ stroke: 'var(--border-subtle)' }} tickLine={false} />
              <YAxis domain={[0, 10]} tick={{ fill: 'var(--text-muted)', fontSize: 12 }} axisLine={{ stroke: 'var(--border-subtle)' }} tickLine={false} />
              <Tooltip contentStyle={{ background: 'var(--bg2)', border: '1px solid var(--border-strong)', borderRadius: '12px', color: 'var(--text-primary)' }} />
              <Line dataKey="score" stroke="var(--teal-500)" strokeWidth={2.7} dot={{ r: 2, fill: 'var(--accent-500)' }} activeDot={{ r: 4, fill: 'var(--accent-400)' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {run?.latest_trial?.state === 'suggested' ? (
          <form onSubmit={onSubmitScore} className="form-grid score-form fade-in-up">
            <h3>Submit score</h3>
            <pre className="result-box">{JSON.stringify(run.latest_trial.parameters, null, 2)}</pre>
            <label>
              Score
              <input type="number" min={0} max={10} step={0.1} value={score} onChange={(e) => setScore(Number(e.target.value))} />
            </label>
            <button className="btn btn-primary">Submit score</button>
          </form>
        ) : null}
      </div>
    </section>
  );
}
