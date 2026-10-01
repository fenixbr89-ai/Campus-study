import type { MindNode } from "@/lib/types";

const BRANCH_COLORS = ["#16a34a", "#0d9488", "#059669", "#65a30d", "#0891b2", "#d97706", "#15803d"];

interface Row { label: string; depth: number; key: string }

// Iterative flatten (explicit stack) — keeps JSX rendering non-recursive.
function flatten(branch: MindNode, rootKey: string): Row[] {
  const rows: Row[] = [];
  const stack: { node: MindNode; depth: number; key: string }[] = [{ node: branch, depth: 1, key: rootKey }];
  while (stack.length) {
    const cur = stack.pop()!;
    rows.push({ label: cur.node.label, depth: cur.depth, key: cur.key });
    for (let i = cur.node.children.length - 1; i >= 0; i--) {
      stack.push({ node: cur.node.children[i], depth: cur.depth + 1, key: `${cur.key}-${i}` });
    }
  }
  return rows;
}

export function MindMapView({ root }: { root: MindNode }) {
  return (
    <div data-testid="mind-map-view" className="overflow-x-auto rounded-2xl border border-slate-200 bg-gradient-to-br from-white to-emerald-50/60 p-5">
      <div className="inline-block rounded-2xl bg-brand px-4 py-2 font-heading font-semibold text-white shadow-md shadow-green-600/20">
        {root.label}
      </div>
      <div className="mt-3 grid gap-x-8 gap-y-4 md:grid-cols-2">
        {root.children.map((branch, bi) => {
          const color = BRANCH_COLORS[bi % BRANCH_COLORS.length];
          return (
            <ul key={bi} className="border-l-2 pl-3" style={{ borderColor: `${color}66` }}>
              {flatten(branch, String(bi)).map((r) => (
                <li key={r.key} style={{ paddingLeft: `${(r.depth - 1) * 1.25}rem` }}>
                  <div
                    className="my-1 inline-block rounded-xl border px-3 py-1.5 text-sm shadow-sm transition-transform duration-200 hover:-translate-y-0.5"
                    style={{ borderColor: `${color}66`, background: r.depth === 1 ? `${color}14` : "#ffffff", fontWeight: r.depth === 1 ? 600 : 400, color: "#0f172a" }}
                  >
                    {r.label}
                  </div>
                </li>
              ))}
            </ul>
          );
        })}
      </div>
    </div>
  );
}
