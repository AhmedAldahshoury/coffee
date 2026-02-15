import Plot from 'react-plotly.js';

export function ImportanceChart({ labels, values }: { labels: string[]; values: number[] }) {
  return <Plot data={[{ x: labels, y: values, type: 'bar' }]} layout={{ title:'Importance (|correlation|)', autosize:true, margin:{t:40,l:30,r:10,b:30} }} useResizeHandler style={{ width:'100%', height:260 }} />;
}
