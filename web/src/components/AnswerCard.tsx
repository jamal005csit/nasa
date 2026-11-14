// Reusable answer card for the four Trend Lab panels (What / Where / How much / Is it significant).

export function AnswerCard({
  label,
  value,
  sub,
  footer,
  testId,
}: {
  label: string;
  value: React.ReactNode;
  sub?: React.ReactNode;
  footer?: React.ReactNode;
  testId?: string;
}) {
  return (
    <article
      className="rounded-xl border border-border bg-surface/80 p-4 flex flex-col gap-2"
      data-testid={testId}
    >
      <header className="text-[10px] uppercase tracking-widest text-muted">
        {label}
      </header>
      <div className="text-2xl font-sans font-medium leading-tight">{value}</div>
      {sub ? <div className="text-xs text-muted">{sub}</div> : null}
      {footer ? <div className="mt-auto pt-2 border-t border-border">{footer}</div> : null}
    </article>
  );
}
