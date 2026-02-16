import { FormEvent, useEffect, useMemo, useRef, useState } from 'react';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { BoltIcon, CoffeeIcon, SparkIcon } from '../../../components/icons';
import { formatApiError, httpClient } from '../../../shared/api/httpClient';
import { createRunEvents, fetchRecommendation, getRun, listRuns, startRun, submitScore, type OptimizerRun } from '../api/optimizerApi';

interface ActivityEvent { id: number; at: string; message: string; }

function useCountUp(target: number, duration = 600) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    const start = performance.now();
    const tick = (now: number) => {
      const progress = Math.min(1, (now - start) / duration);
      setValue(target * progress);
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [target, duration]);
  return value;
}

function RecommendationCard({ recommendation }: { recommendation: any }) {
  const [showRaw, setShowRaw] = useState(false);
  return (
    <article className="panel subpanel recommendation-card">
      <h3>Recommendation result</h3>
      <p className="muted">Predicted score: <strong>{recommendation?.score ?? '-'}</strong> · Parameters: {recommendation?.suggested_parameters?.length ?? 0}</p>
      <table className="kv-table">
        <thead><tr><th>Parameter</th><th>Value</th><th>Unit</th><th>Fixed</th></tr></thead>
        <tbody>
          {(recommendation?.suggested_parameters ?? []).map((item: any) => (
            <tr key={item.name}><td>{item.name}</td><td>{String(item.value)}</td><td>{item.unit ?? '-'}</td><td>{item.fixed ? 'Yes' : 'No'}</td></tr>
          ))}
        </tbody>
      </table>
      <button type="button" className="btn btn-ghost" onClick={() => setShowRaw((prev) => !prev)}>{showRaw ? 'Hide raw JSON' : 'Show raw JSON'}</button>
      {showRaw ? <pre className="result-box raw-json">{JSON.stringify(recommendation, null, 2)}</pre> : null}
    </article>
  );
}

function pushEvent(setter: React.Dispatch<React.SetStateAction<ActivityEvent[]>>, message: string) {
  setter((prev) => [{ id: Date.now() + Math.random(), at: new Date().toLocaleTimeString(), message }, ...prev].slice(0, 20));
}

export function OptimizerPage() {
  const [method, setMethod] = useState('median');
  const [nTrials, setNTrials] = useState(50);
  const [selectedPersons, setSelectedPersons] = useState('');
  const [run, setRun] = useState<OptimizerRun | null>(null);
  const [score, setScore] = useState(8);
  const [loading, setLoading] = useState(false);
  const [recommendationLoading, setRecommendationLoading] = useState(false);
  const [toast, setToast] = useState<{ message: string; kind: 'success' | 'warning' | 'info' } | null>(null);
  const [errorBanner, setErrorBanner] = useState('');
  const [history, setHistory] = useState<{ trial: number; score: number }[]>([]);
  const [recommendation, setRecommendation] = useState<any>(null);
  const [sseStatus, setSseStatus] = useState<'disconnected' | 'connected' | 'retrying' | 'polling'>('disconnected');
  const [lastEventTime, setLastEventTime] = useState<string | null>(null);
  const [eventsLog, setEventsLog] = useState<ActivityEvent[]>([]);
  const [datasetInfo, setDatasetInfo] = useState<{ runs: number; leaderboardTotal: number; avgScore: number; lastSync: string } | null>(null);

  const pollTimer = useRef<number | null>(null);

  const runState = useMemo(() => {
    if (run?.latest_trial?.state === 'suggested' && run.status !== 'finished') return 'waiting_for_score';
    return run?.status ?? 'idle';
  }, [run]);

  const progressLabel = useMemo(() => {
    if (!run) return `0 / ${nTrials}`;
    const current = Math.min(run.trial_count + (run.latest_trial?.state === 'suggested' ? 1 : 0), run.n_trials);
    return `${current} / ${run.n_trials}`;
  }, [run, nTrials]);

  const totalBrews = useCountUp(datasetInfo?.leaderboardTotal ?? 0);
  const bestScoreCounter = useCountUp(run?.best_score ?? 0);
  const avgScoreCounter = useCountUp(datasetInfo?.avgScore ?? 0);
  const streakCounter = useCountUp(eventsLog.filter((e) => e.message.includes('Score submitted')).length);

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 2500);
    return () => clearTimeout(t);
  }, [toast]);

  useEffect(() => {
    let active = true;
    const loadDatasetInfo = async () => {
      try {
        const [runs, leaderboard] = await Promise.all([
          listRuns(),
          httpClient.get('/leaderboard', { params: { page: 1, page_size: 1 } }),
        ]);
        if (!active) return;
        setDatasetInfo({
          runs: runs.length,
          leaderboardTotal: leaderboard.data.total ?? 0,
          avgScore: Number(leaderboard.data.average_score ?? 0),
          lastSync: new Date().toLocaleTimeString(),
        });
      } catch {
        if (!active) return;
        setDatasetInfo(null);
      }
    };
    loadDatasetInfo();
    return () => { active = false; };
  }, [run?.id]);

  const stopPolling = () => {
    if (pollTimer.current) { window.clearInterval(pollTimer.current); pollTimer.current = null; }
  };

  const startPolling = (runId: string) => {
    if (pollTimer.current) return;
    setSseStatus('polling');
    pushEvent(setEventsLog, 'Live updates unavailable, polling every 2s.');
    pollTimer.current = window.setInterval(async () => {
      try {
        const latest = await getRun(runId);
        setRun(latest);
        setLastEventTime(new Date().toLocaleTimeString());
        if (latest.status === 'finished') { stopPolling(); setSseStatus('disconnected'); }
      } catch (error) {
        setErrorBanner(formatApiError(error));
      }
    }, 2000);
  };

  const start = async () => {
    setLoading(true);
    setErrorBanner('');
    try {
      const data = await startRun({ method, n_trials: nTrials, selected_persons: selectedPersons.split(',').map((name) => name.trim()).filter(Boolean) });
      setRun(data);
      setToast({ message: 'Optimization started', kind: 'success' });
      pushEvent(setEventsLog, `Run started: ${data.id}`);
      setHistory([]);
    } catch (error) {
      setErrorBanner(formatApiError(error));
      pushEvent(setEventsLog, `Run start failed: ${formatApiError(error)}`);
    } finally {
      setLoading(false);
    }
  };

  const onSubmitScore = async (e: FormEvent) => {
    e.preventDefault();
    if (!run?.latest_trial) return;
    setErrorBanner('');
    try {
      const data = await submitScore(run.id, run.latest_trial.id, score);
      setRun(data);
      setHistory((prev) => [...prev, { trial: data.trial_count, score }]);
      setToast({ message: 'Score submitted', kind: 'success' });
      pushEvent(setEventsLog, `Score submitted for trial ${run.latest_trial.trial_number}`);
    } catch (error) {
      setErrorBanner(formatApiError(error));
    }
  };

  const onLoadRecommendation = async () => {
    setRecommendationLoading(true);
    setErrorBanner('');
    try {
      const data = await fetchRecommendation({ dataset_prefix: 'aeropress.', method, best_only: false, prior_weight: 0.666 });
      setRecommendation(data);
      setToast({ message: 'Recommendation loaded', kind: 'info' });
    } catch (error) {
      setErrorBanner(formatApiError(error));
    } finally {
      setRecommendationLoading(false);
    }
  };

  useEffect(() => {
    if (!run?.id) return undefined;
    const token = localStorage.getItem('coffee_token');
    if (!token) return undefined;

    stopPolling();
    setSseStatus('retrying');
    const events = createRunEvents(run.id, token);

    events.onopen = () => { setSseStatus('connected'); setErrorBanner(''); pushEvent(setEventsLog, 'SSE connected.'); };
    events.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      setRun((prev) => prev ? { ...prev, status: payload.run_status, best_score: payload.best_score, best_params: payload.best_parameters } : prev);
      setLastEventTime(new Date().toLocaleTimeString());
      pushEvent(setEventsLog, `Event: trial=${payload.trial_number}, status=${payload.run_status}`);
      if (payload.last_trial_score !== null && payload.last_trial_score !== undefined) setHistory((prev) => [...prev, { trial: payload.trial_number, score: payload.last_trial_score }]);
    };
    events.onerror = () => { setSseStatus('retrying'); events.close(); startPolling(run.id); };

    return () => { events.close(); stopPolling(); setSseStatus('disconnected'); };
  }, [run?.id]);

  return (
    <section className="optimizer-layout fade-in-up">
      {toast ? <div className={`toast toast-${toast.kind}`}><SparkIcon size={14} /><span>{toast.message}</span></div> : null}
      {errorBanner ? <div className="error-banner">{errorBanner}</div> : null}

      <div className="panel kpi-strip">
        <div className="stat"><span>Total brews</span><strong>{Math.round(totalBrews)}</strong></div>
        <div className="stat"><span>Best score</span><strong>{bestScoreCounter.toFixed(2)}</strong></div>
        <div className="stat"><span>Current streak</span><strong>{Math.round(streakCounter)}</strong></div>
        <div className="stat"><span>Avg score</span><strong>{avgScoreCounter.toFixed(2)}</strong></div>
      </div>

      <div className="panel">
        <p className="eyebrow">Setup</p>
        <h2>Optimizer configuration</h2>
        <label>Selected persons (comma separated)<input value={selectedPersons} onChange={(e) => setSelectedPersons(e.target.value)} placeholder="alice,bob,charlie" /></label>
        <label>Method<select value={method} onChange={(e) => setMethod(e.target.value)}><option>median</option><option>mean</option><option>lowest</option><option>highest</option></select></label>
        <label>Trials<input type="number" min={1} max={200} value={nTrials} onChange={(e) => setNTrials(Number(e.target.value))} /></label>
        <button className="btn btn-primary" onClick={start} disabled={loading || runState === 'running'}><BoltIcon size={14} /> {loading ? 'Starting...' : 'Optimise now'}</button>

        <hr />
        <h3>Recommendation</h3>
        <button className="btn btn-secondary" onClick={onLoadRecommendation} disabled={recommendationLoading}>{recommendationLoading ? 'Loading…' : 'Get recommendation'}</button>
        {recommendationLoading ? <p className="skeleton shimmer">Preparing recommendation…</p> : null}
        {recommendation ? <RecommendationCard recommendation={recommendation} /> : <div className="empty-state"><CoffeeIcon size={17} /><p>No recommendation loaded. Start with “Get recommendation”.</p></div>}
      </div>

      <div className="panel">
        <p className="eyebrow">Run monitor</p>
        <h2>Live optimisation panel</h2>
        {!run ? <div className="empty-state"><SparkIcon size={17} /><p>No active run yet. Start a run to receive trial suggestions.</p></div> : null}
        <div className="stats-grid compact">
          <div className="stat"><span>Run id</span><strong className="mono">{run?.id ?? '-'}</strong></div>
          <div className="stat"><span>Status</span><strong className={`status-pill ${runState}`}>{runState}</strong></div>
          <div className="stat"><span>Progress</span><strong>{progressLabel}</strong></div>
        </div>

        {run?.latest_trial ? <article className="panel subpanel trial-card"><h3>Trial Card</h3><pre className="result-box">{JSON.stringify(run.latest_trial.parameters, null, 2)}</pre></article> : null}

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
            <h3>Waiting for your score</h3>
            <p className="muted">Trial #{run.latest_trial.trial_number} is ready for evaluation.</p>
            <label>Score<input type="number" min={0} max={10} step={0.1} value={score} onChange={(e) => setScore(Number(e.target.value))} /></label>
            <button className="btn btn-primary">Submit score</button>
          </form>
        ) : null}

        <hr />
        <h3>Run activity</h3>
        <div className="stats-grid compact">
          <div className="stat"><span>SSE connection</span><strong className={`status-pill ${sseStatus}`}>{sseStatus}</strong></div>
          <div className="stat"><span>Last event</span><strong>{lastEventTime ?? '-'}</strong></div>
          <div className="stat"><span>Dataset sync</span><strong>{datasetInfo?.lastSync ?? '-'}</strong></div>
        </div>
        {sseStatus === 'polling' ? <p className="warning-banner">Live updates unavailable, polling…</p> : null}
        <div className="activity-log">{eventsLog.length ? eventsLog.map((entry) => <p key={entry.id}><strong>{entry.at}</strong> — {entry.message}</p>) : <p className="muted">No activity yet.</p>}</div>
      </div>
    </section>
  );
}
