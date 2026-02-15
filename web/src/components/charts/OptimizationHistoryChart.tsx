import Plot from 'react-plotly.js';

export function OptimizationHistoryChart({ objective }: { objective: Array<{ idx: number; value: number }> }) {
  let running = -Infinity;
  const best = objective.map((v) => { running = Math.max(running, v.value); return running; });
  return <Plot data={[{ x: objective.map((o) => o.idx), y: best, mode: 'lines+markers', name: 'Best so far' }]} layout={{ title: 'Optimization history', autosize: true, margin: { t: 40, l: 30, r: 10, b: 30 } }} useResizeHandler style={{ width: '100%', height: 260 }} />;
}
