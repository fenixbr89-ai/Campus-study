import { useState } from "react";
import { Network, Search } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import { usePageMeta } from "@/lib/hooks";
import type { Content, SearchOut } from "@/lib/types";
import { ContentCard } from "@/components/ContentCard";
import { Input } from "@/components/ui/input";

export default function MindMapsPage() {
  const [q, setQ] = useState("");
  const result = useQuery({
    queryKey: ["mind-maps", q],
    queryFn: () => apiGet<SearchOut>(`/search?type=mapa&q=${encodeURIComponent(q.trim())}&page=1`),
  });
  usePageMeta("Mapas mentais", "Mapas mentais organizados por assunto para revisar e visualizar conexões.");

  return (
    <div className="animate-fade-up">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="flex items-center gap-2 text-brand-dark"><Network className="size-5" /><span className="text-sm font-semibold">Ferramenta de estudo</span></div>
          <h1 className="mt-1 text-3xl font-extrabold tracking-tight">Mapas mentais</h1>
          <p className="mt-1 text-slate-600">Visualize as conexões entre os conteúdos e revise os assuntos com mais facilidade.</p>
        </div>
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3 top-3 size-4 text-slate-400" />
          <Input className="pl-9" placeholder="Buscar mapa mental..." value={q} onChange={(e) => setQ(e.target.value)} />
        </div>
      </div>

      {result.isLoading && <div className="mt-6 rounded-2xl border bg-white p-6 text-sm text-slate-500">Carregando mapas mentais...</div>}
      {result.isError && <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-6 text-sm text-red-700">Não foi possível carregar os mapas mentais.</div>}
      {result.data && result.data.items.length === 0 && <div className="mt-6 rounded-2xl border border-dashed bg-white p-8 text-center text-sm text-slate-500">Nenhum mapa mental publicado ainda.</div>}

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {(result.data?.items ?? []).map((c: Content) => <ContentCard key={c.id} c={c} />)}
      </div>
    </div>
  );
}
