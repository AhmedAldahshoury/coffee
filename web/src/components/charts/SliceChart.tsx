import Plot from 'react-plotly.js';

export function SliceChart({ x, y, param }: { x: number[]; y: number[]; param: string }) {
  return <Plot data={[{ x, y, mode: 'markers', type:'scatter' }]} layout={{ title:`Slice: ${param}`, xaxis:{ title:param }, yaxis:{ title:'objective' }, autosize:true, margin:{t:40,l:30,r:10,b:30} }} useResizeHandler style={{ width:'100%', height:260 }} />;
}
