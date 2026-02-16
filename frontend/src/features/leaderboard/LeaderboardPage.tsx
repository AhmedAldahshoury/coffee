import { useEffect, useState } from 'react';
import { ChevronIcon, CoffeeIcon, TrophyIcon } from '../../components/icons';
import { formatApiError, httpClient } from '../../shared/api/httpClient';

const methodFilters = ['all', 'aeropress', 'pourover'];

export function LeaderboardPage() {
  const [minimumScore, setMinimumScore] = useState(0);
  const [sortBy, setSortBy] = useState<'score' | 'date'>('score');
  const [method, setMethod] = useState('all');
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [data, setData] = useState<any>(null);
  const [selected, setSelected] = useState<any>(null);

  useEffect(() => {
    setLoading(true);
    setError('');

    httpClient.get('/leaderboard', {
      params: {
        minimum_score: minimumScore,
        sort_by: sortBy,
        page,
        ...(method !== 'all' ? { method } : {}),
      },
    })
      .then((res) => setData(res.data))
      .catch((err) => setError(formatApiError(err)))
      .finally(() => setLoading(false));
  }, [minimumScore, sortBy, page, method]);

  return (
    <section className="panel fade-in-up">
      <div className="row-title"><TrophyIcon size={17} /><p className="eyebrow">Leaderboard</p></div>
      <h2>Top brew performances</h2>
      <p className="muted">Complete brew sessions and optimiser runs to appear here.</p>

      <div className="pill-row">
        {methodFilters.map((item) => (
          <button key={item} className={method === item ? 'pill active' : 'pill'} onClick={() => { setMethod(item); setPage(1); }}>{item}</button>
        ))}
      </div>

      <div className="form-grid filters-grid">
        <label>Minimum score<input type="number" value={minimumScore} onChange={(e) => setMinimumScore(Number(e.target.value))} /></label>
        <label>Sort<select value={sortBy} onChange={(e) => setSortBy(e.target.value as 'score' | 'date')}><option value="score">Score</option><option value="date">Date</option></select></label>
      </div>

      {error ? <div className="error-banner">Leaderboard request failed: {error}</div> : null}

      <div className="stats-grid compact">
        <div className="stat"><span>Total rows</span><strong>{data?.total ?? 0}</strong></div>
        <div className="stat"><span>Average score</span><strong>{data?.average_score?.toFixed?.(2) ?? '-'}</strong></div>
        <div className="stat"><span>Trials in query</span><strong>{data?.number_of_trials ?? 0}</strong></div>
      </div>

      <div className="table-wrap">
        <table>
          <thead><tr><th>User</th><th>Score</th><th>Method</th><th>Date</th></tr></thead>
          <tbody>
            {loading ? Array.from({ length: 6 }).map((_, i) => <tr key={i}><td colSpan={4} className="skeleton shimmer">Loading row…</td></tr>) : null}
            {!loading && error ? <tr><td colSpan={4} className="muted">Unable to load leaderboard due to API error.</td></tr> : null}
            {!loading && !error && data?.items?.length ? data.items.map((item: any) => (
              <tr key={item.brew_id} className="interactive-row" onClick={() => setSelected(item)}>
                <td>{item.user_id}</td><td>{item.score}</td><td>{item.method}</td><td>{new Date(item.created_at).toLocaleString()}</td>
              </tr>
            )) : null}
            {!loading && !error && !data?.items?.length ? <tr><td colSpan={4}><div className="empty-state"><CoffeeIcon size={18} /><p>No runs yet — complete a brew session to appear here.</p></div></td></tr> : null}
          </tbody>
        </table>
      </div>

      <div className="pagination-row">
        <button className="btn btn-secondary icon-btn" onClick={() => setPage((p) => Math.max(1, p - 1))}><ChevronIcon size={14} style={{ transform: 'rotate(180deg)' }} /> Prev</button>
        <span className="muted">Page {page}</span>
        <button className="btn btn-secondary icon-btn" onClick={() => setPage((p) => p + 1)}>Next <ChevronIcon size={14} /></button>
      </div>

      {selected ? (
        <div className="modal-backdrop" onClick={() => setSelected(null)}>
          <div className="modal panel" onClick={(e) => e.stopPropagation()}>
            <h3>Brew details</h3>
            <pre className="result-box">{JSON.stringify(selected, null, 2)}</pre>
            <button className="btn btn-primary" onClick={() => setSelected(null)}>Close</button>
          </div>
        </div>
      ) : null}
    </section>
  );
}
