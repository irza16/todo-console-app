interface PrioritySelectorProps {
  value: 'Low' | 'Medium' | 'High' | 'Urgent';
  onChange: (value: 'Low' | 'Medium' | 'High' | 'Urgent') => void;
}

export function PrioritySelector({ value, onChange }: PrioritySelectorProps) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value as 'Low' | 'Medium' | 'High' | 'Urgent')}
      className="border rounded p-2 w-full bg-background"
    >
      <option value="Low">🟢 Low</option>
      <option value="Medium">🟡 Medium</option>
      <option value="High">🟠 High</option>
      <option value="Urgent">🔴 Urgent</option>
    </select>
  );
}