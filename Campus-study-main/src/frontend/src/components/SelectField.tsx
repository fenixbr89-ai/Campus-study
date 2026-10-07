export function NativeSelect({
  value, onChange, children, testId, className = "", disabled,
}: {
  value: string; onChange: (v: string) => void; children: React.ReactNode; testId?: string; className?: string; disabled?: boolean;
}) {
  return (
    <select
      data-testid={testId}
      value={value}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value)}
      className={`h-10 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm text-slate-800 transition-colors duration-150 outline-none focus:border-brand focus:ring-2 focus:ring-brand/20 disabled:opacity-50 ${className}`}
    >
      {children}
    </select>
  );
}
