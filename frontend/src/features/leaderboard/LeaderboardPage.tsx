import { useEffect, useState } from 'react';
import { ChevronIcon, TrophyIcon } from '../../components/icons';
import { httpClient } from '../../shared/api/httpClient';

export function LeaderboardPage() {
  const [minimumScore, setMinimumScore] = useState(0);
  const [sortBy, setSortBy] = useState<'score' | 'date'>('score');
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    setLoading(true);
    httpClient.get('/leaderboard', { params: { minimum_score: minimumScore, sort_by: sortBy, page } })
      .then((res) => setData(res.data))
      .finally(() => setLoading(false));
  }, [minimumScore, sortBy, page]);

  return (
    <section className="panel fade-in-up">
      <div className="row-title">
        <TrophyIcon size={17} />
        <p className="eyebrow">Leaderboard</p>
      </div>
      <h2>Top brew performances</h2>
      <p className="muted">Compare methods and scores from recent submissions.</p>

      <div className="form-grid filters-grid">
        <label>
          Minimum score
          <input type="number" value={minimumScore} onChange={(e) => setMinimumScore(Number(e.target.value))} />
        </label>
        <label>
          Sort
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value as 'score' | 'date')}>
            <option value="score">Score</option>
            <option value="date">Date</option>
          </select>
        </label>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr><th>User</th><th>Score</th><th>Method</th><th>Date</th></tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={4} className="skeleton shimmer">Loading leaderboard…</td>
              </tr>
            ) : data?.items?.length ? data.items.map((item: any) => (
              <tr key={item.brew_id}>
                <td>{item.user_id}</td>
                <td>{item.score}</td>
                <td>{item.method}</td>
                <td>{new Date(item.created_at).toLocaleString()}</td>
              </tr>
            )) : (
              <tr>
                <td colSpan={4} className="muted">No entries yet for this filter.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="pagination-row">
        <button className="btn btn-secondary icon-btn" onClick={() => setPage((p) => Math.max(1, p - 1))}><ChevronIcon size={14} style={{ transform: 'rotate(180deg)' }} /> Prev</button>
        <span className="muted">Page {page}</span>
        <button className="btn btn-secondary icon-btn" onClick={() => setPage((p) => p + 1)}>Next <ChevronIcon size={14} /></button>
      </div>
    </section>
  );
}
