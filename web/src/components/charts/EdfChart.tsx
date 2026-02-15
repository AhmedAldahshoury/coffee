import Plot from 'react-plotly.js';

export function EdfChart({ values }: { values: number[] }) {
  const vals = values.slice().sort((a,b)=>a-b);
  return <Plot data={[{ x: vals, y: vals.map((_,i)=>(i+1)/vals.length), mode: 'lines', name: 'EDF' }]} layout={{ title:'Empirical distribution', autosize:true, margin:{t:40,l:30,r:10,b:30} }} useResizeHandler style={{ width:'100%', height:260 }} />;
}
