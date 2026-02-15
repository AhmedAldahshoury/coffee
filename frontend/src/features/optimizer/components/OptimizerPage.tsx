import { isAxiosError } from 'axios';
import { FormEvent, useMemo, useState } from 'react';
import { useRecommendation } from '../hooks/useRecommendation';

function getErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string' && detail.length > 0) {
      return detail;
    }

    if (error.code === 'ERR_NETWORK') {
      return 'Network error: backend may be unreachable or blocked by CORS. Verify backend is running on port 8000.';
    }

    return error.message;
  }

  return 'Unknown error while fetching recommendation.';
}

export function OptimizerPage() {
  const [datasetPrefix, setDatasetPrefix] = useState('aeropress.');
  const [method, setMethod] = useState<'mean' | 'median' | 'lowest' | 'highest'>('median');
  const [bestOnly, setBestOnly] = useState(false);
  const [priorWeight, setPriorWeight] = useState(0.666);
  const recommendation = useRecommendation();

  const submit = (event: FormEvent) => {
    event.preventDefault();
    recommendation.mutate({
      dataset_prefix: datasetPrefix,
      method,
      best_only: bestOnly,
      prior_weight: priorWeight,
    });
  };

  const errorMessage = useMemo(() => getErrorMessage(recommendation.error), [recommendation.error]);

  return (
    <section className="panel">
      <h2>Recipe recommendation</h2>
      <form onSubmit={submit} className="form-grid">
        <label>
          Dataset Prefix
          <input value={datasetPrefix} onChange={(e) => setDatasetPrefix(e.target.value)} />
        </label>
        <label>
          Method
          <select value={method} onChange={(e) => setMethod(e.target.value as typeof method)}>
            <option value="mean">Mean</option>
            <option value="median">Median</option>
            <option value="lowest">Lowest</option>
            <option value="highest">Highest</option>
          </select>
        </label>
        <label>
          Prior Weight
          <input
            type="number"
            step="0.001"
            value={priorWeight}
            onChange={(e) => setPriorWeight(Number(e.target.value))}
          />
        </label>
        <label className="inline">
          <input type="checkbox" checked={bestOnly} onChange={(e) => setBestOnly(e.target.checked)} />
          Return historical best only
        </label>
        <button className="btn" type="submit" disabled={recommendation.isPending}>
          {recommendation.isPending ? 'Optimizing...' : 'Get recommendation'}
        </button>
      </form>

      {recommendation.error ? <p className="error">{errorMessage}</p> : null}

      {recommendation.data ? (
        <div className="results">
          <h3>Recommended parameters</h3>
          {recommendation.data.score !== null ? <p>Best score: {recommendation.data.score.toFixed(2)}</p> : null}
          <ul>
            {recommendation.data.suggested_parameters.map((item) => (
              <li key={`${item.name}-${item.fixed}`}>
                <strong>{item.name}</strong>: {String(item.value)} {item.unit ?? ''}{' '}
                {item.fixed ? <em>(fixed)</em> : null}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  );
}
