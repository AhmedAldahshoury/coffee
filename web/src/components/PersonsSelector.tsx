import { Button } from './ui/button';

export function PersonsSelector({ persons, selected, onChange }: { persons: string[]; selected: string[]; onChange: (v: string[]) => void }) {
  const toggle = (name: string) => onChange(selected.includes(name) ? selected.filter((s) => s !== name) : [...selected, name]);

  return (
    <div>
      <p className="mb-2 text-sm font-medium">Scoring persons</p>
      <div className="flex flex-wrap gap-2">
        {persons.map((person) => {
          const active = selected.includes(person);
          return (
            <Button
              key={person}
              type="button"
              variant={active ? 'default' : 'outline'}
              aria-pressed={active}
              onClick={() => toggle(person)}
              className="h-8 px-3"
            >
              {person}
            </Button>
          );
        })}
      </div>
    </div>
  );
}
