import { Check, Crown, Sparkles } from "lucide-react";
import { useMe, usePageMeta } from "@/lib/hooks";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import type { StripePublicConfig } from "@/lib/types";

const limited = ["23 cursos", "Todos os períodos e disciplinas", "Videoaulas", "PDFs e livros", "Resumos", ];
const unlimited = [...limited, "Questões", "Simulados", "Mapas mentais", "Artigos científicos"];

export default function PlansPage() {
  usePageMeta("Planos");
  const me = useMe();
  const stripe = useQuery({ queryKey: ["stripe-config"], queryFn: () => apiGet<StripePublicConfig>("/payments/stripe/config") });
  const monthly = stripe.data?.monthly_price || "19.90";
  const yearly = stripe.data?.yearly_price || "150.00";
  return <div className="animate-fade-up space-y-6">
    <div className="text-center"><div className="mx-auto grid size-14 place-items-center rounded-2xl bg-brand-soft text-brand-dark"><Crown className="size-7" /></div><h1 className="mt-4 text-3xl font-extrabold tracking-tight">Planos Campus Study</h1><p className="mx-auto mt-2 max-w-2xl text-slate-600">Escolha o acesso que melhor atende à sua rotina de estudos.</p></div>
    <div className="grid gap-5 lg:grid-cols-2">
      <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"><h2 className="text-xl font-bold">Plano Limitado</h2><p className="mt-1 text-sm text-slate-500">Recursos principais para estudar.</p><p className="mt-5 text-4xl font-extrabold">R$ 0</p><ul className="mt-5 space-y-3">{limited.map(x=><li key={x} className="flex gap-2 text-sm"><Check className="size-4 shrink-0 text-emerald-600" />{x}</li>)}</ul></section>
      <section className="relative rounded-3xl border-2 border-brand bg-white p-6 shadow-lg"><div className="absolute -top-3 right-5 rounded-full bg-brand px-3 py-1 text-xs font-bold text-white">RECOMENDADO</div><h2 className="flex items-center gap-2 text-xl font-bold"><Sparkles className="size-5 text-brand" /> Ilimitado</h2><p className="mt-1 text-sm text-slate-500">Acesso completo aos recursos liberados da plataforma.</p><div className="mt-5 grid gap-4 sm:grid-cols-2"><div><p className="text-3xl font-extrabold">R$ {monthly.replace(".", ",")}<span className="text-sm font-medium text-slate-500">/mês</span></p></div><div><p className="text-3xl font-extrabold">R$ {yearly.replace(".", ",")}<span className="text-sm font-medium text-slate-500">/ano</span></p><p className="text-xs text-emerald-700">equivale a R$ 12,50/mês</p></div></div><ul className="mt-5 space-y-3">{unlimited.map(x=><li key={x} className="flex gap-2 text-sm"><Check className="size-4 shrink-0 text-emerald-600" />{x}</li>)}</ul><div className="mt-6 grid gap-2 sm:grid-cols-2"><Link to="/checkout?plano=monthly" className="inline-flex h-11 items-center justify-center rounded-xl bg-brand px-5 font-semibold text-white">Assinar mensal</Link><Link to="/checkout?plano=yearly" className="inline-flex h-11 items-center justify-center rounded-xl border border-slate-200 bg-white px-5 font-semibold text-slate-700">Assinar anual</Link></div><p className="mt-3 text-center text-xs text-slate-400">O checkout fica disponível quando o Stripe estiver configurado no Admin.</p></section>
    </div>
  </div>;
}
