export function PersonsSelector({ persons, selected, onChange }: { persons: string[]; selected: string[]; onChange: (v: string[]) => void }) {
  const toggle = (name: string) => onChange(selected.includes(name) ? selected.filter((s) => s !== name) : [...selected, name]);
  return <div><p className="mb-2 text-sm">Persons</p><div className="flex flex-wrap gap-2">{persons.map((p) => <button key={p} className={`rounded-full border px-3 py-1 text-sm ${selected.includes(p) ? 'bg-primary text-white' : 'bg-card'}`} onClick={() => toggle(p)}>{p}</button>)}</div></div>;
}
