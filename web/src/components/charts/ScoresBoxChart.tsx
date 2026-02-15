import Plot from 'react-plotly.js';

export function ScoresBoxChart({ data }: { data: Array<{ name: string; values: number[] }> }) {
  return <Plot data={data.map((d)=>({ y:d.values, type:'box', name:d.name }))} layout={{ title:'Scores distribution per person', autosize:true, margin:{t:40,l:30,r:10,b:30} }} useResizeHandler style={{ width:'100%', height:260 }} />;
}
