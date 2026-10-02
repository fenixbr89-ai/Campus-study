import { Fragment, type ReactNode } from "react";

// Minimal, safe Markdown renderer (headings, lists, bold) — no HTML injection.
function inline(text: string): ReactNode[] {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
    part.startsWith("**") && part.endsWith("**") ? <strong key={i}>{part.slice(2, -2)}</strong> : <Fragment key={i}>{part}</Fragment>,
  );
}

export function Markdown({ text, className = "" }: { text: string; className?: string }) {
  const blocks: ReactNode[] = [];
  let list: { ordered: boolean; items: string[] } | null = null;
  const flush = () => {
    if (!list) return;
    const Tag = list.ordered ? "ol" : "ul";
    blocks.push(
      <Tag key={blocks.length} className={`${list.ordered ? "list-decimal" : "list-disc"} my-2 space-y-1 pl-5`}>
        {list.items.map((it, i) => <li key={i}>{inline(it)}</li>)}
      </Tag>,
    );
    list = null;
  };
  for (const raw of text.split("\n")) {
    const line = raw.trimEnd();
    const ul = line.match(/^\s*[-*]\s+(.*)/);
    const ol = line.match(/^\s*\d+[.)]\s+(.*)/);
    if (ul || ol) {
      const ordered = !!ol;
      if (!list || list.ordered !== ordered) { flush(); list = { ordered, items: [] }; }
      list.items.push((ul ?? ol)![1]);
      continue;
    }
    flush();
    if (!line.trim()) continue;
    const h = line.match(/^(#{1,4})\s+(.*)/);
    if (h) {
      const size = h[1].length <= 2 ? "text-lg" : "text-base";
      blocks.push(<h3 key={blocks.length} className={`${size} mt-4 mb-1 font-semibold text-slate-900`}>{inline(h[2])}</h3>);
    } else {
      blocks.push(<p key={blocks.length} className="my-2">{inline(line)}</p>);
    }
  }
  flush();
  return <div className={`text-sm leading-relaxed text-slate-700 sm:text-base ${className}`}>{blocks}</div>;
}
