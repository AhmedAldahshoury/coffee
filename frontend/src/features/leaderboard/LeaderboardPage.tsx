import { useEffect, useState } from 'react';
import { httpClient } from '../../shared/api/httpClient';

export function LeaderboardPage() {
  const [minimumScore, setMinimumScore] = useState(0);
  const [sortBy, setSortBy] = useState<'score' | 'date'>('score');
  const [page, setPage] = useState(1);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    httpClient.get('/leaderboard', { params: { minimum_score: minimumScore, sort_by: sortBy, page } }).then((res) => setData(res.data));
  }, [minimumScore, sortBy, page]);

  return (
    <section className="panel">
      <h2>Leaderboard</h2>
      <div className="form-grid">
        <label>Minimum score<input type="number" value={minimumScore} onChange={(e) => setMinimumScore(Number(e.target.value))} /></label>
        <label>Sort<select value={sortBy} onChange={(e) => setSortBy(e.target.value as 'score' | 'date')}><option value="score">Score</option><option value="date">Date</option></select></label>
      </div>
      <table>
        <thead><tr><th>User</th><th>Score</th><th>Method</th><th>Date</th></tr></thead>
        <tbody>
          {data?.items?.map((item: any) => <tr key={item.brew_id}><td>{item.user_id}</td><td>{item.score}</td><td>{item.method}</td><td>{new Date(item.created_at).toLocaleString()}</td></tr>)}
        </tbody>
      </table>
      <div>
        <button className="btn btn-secondary" onClick={() => setPage((p) => Math.max(1, p - 1))}>Prev</button>
        <button className="btn btn-secondary" onClick={() => setPage((p) => p + 1)}>Next</button>
      </div>
    </section>
  );
}
