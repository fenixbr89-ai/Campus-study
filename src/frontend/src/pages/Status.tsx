import { useQuery } from "@tanstack/react-query";
import { CheckCircle2, CircleAlert, Wrench, XCircle } from "lucide-react";
import { apiGet } from "@/lib/api";
import type { SystemStatus } from "@/lib/types";
import { usePageMeta } from "@/lib/hooks";

const labels = { operacional: "Operacional", degradado: "Instabilidade", indisponivel: "Indisponível", manutencao: "Manutenção" };
const incidentLabels = { investigando: "Investigando", monitorando: "Monitorando", resolvido: "Resolvido" };

export default function StatusPage() {
  usePageMeta("Status do sistema");
  const q = useQuery({ queryKey: ["system-status"], queryFn: () => apiGet<SystemStatus>("/system-status") });
  if (q.isLoading) return <div className="rounded-3xl border bg-white p-8">Carregando status...</div>;
  if (q.isError || !q.data) return <div className="rounded-3xl border border-red-200 bg-red-50 p-8 text-red-700">Não foi possível consultar o status.</div>;
  const s = q.data;
  const Icon = s.overall === "operacional" ? CheckCircle2 : s.overall === "manutencao" ? Wrench : s.overall === "indisponivel" ? XCircle : CircleAlert;
  return (
    <div className="animate-fade-up space-y-6">
      <div className="rounded-3xl border bg-white p-7">
        <div className="flex items-center gap-3"><Icon className="size-8" /><div><h1 className="text-3xl font-extrabold">Status do Campus Study</h1><p className="text-sm text-slate-500">{labels[s.overall]}</p></div></div>
        {s.message && <p className="mt-4 text-slate-700">{s.message}</p>}
        {s.maintenance && <div className="mt-4 rounded-2xl bg-amber-50 p-4 text-sm">{s.maintenance_message || "Há uma manutenção programada."}</div>}
      </div>
      <section className="rounded-3xl border bg-white p-6">
        <h2 className="text-xl font-bold">Serviços</h2>
        <div className="mt-4 space-y-3">{s.services.map(x => <div key={x.name} className="flex items-center justify-between rounded-2xl border p-4"><div><b>{x.name}</b>{x.description && <p className="text-sm text-slate-500">{x.description}</p>}</div><span className="text-sm font-semibold">{labels[x.status]}</span></div>)}</div>
      </section>
      {s.incidents?.length > 0 && <section className="rounded-3xl border bg-white p-6">
        <h2 className="text-xl font-bold">Histórico de incidentes</h2>
        <div className="mt-4 space-y-3">{s.incidents.map(i => <article key={i.id} className="rounded-2xl border p-4"><div className="flex flex-wrap items-center justify-between gap-2"><h3 className="font-semibold">{i.title}</h3><span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold">{incidentLabels[i.status]}</span></div>{i.message && <p className="mt-2 text-sm text-slate-600">{i.message}</p>}</article>)}</div>
      </section>}
    </div>
  );
}
