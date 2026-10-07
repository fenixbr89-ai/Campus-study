import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { LifeBuoy, Send } from "lucide-react";
import { apiGet, apiPost } from "@/lib/api";
import type { SupportTicket } from "@/lib/types";
import { usePageMeta } from "@/lib/hooks";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { NativeSelect } from "@/components/SelectField";
import { toast } from "sonner";

const statuses: Record<string,string> = { aberto:"Aberto", em_analise:"Em análise", aguardando_usuario:"Aguardando você", resolvido:"Resolvido", fechado:"Fechado" };

export default function SupportPage() {
  usePageMeta("Suporte");
  const qc = useQueryClient();
  const q = useQuery({ queryKey:["support-tickets"], queryFn:()=>apiGet<SupportTicket[]>("/support/tickets") });
  const [category,setCategory]=useState("bug"), [subject,setSubject]=useState(""), [message,setMessage]=useState("");
  const create = useMutation({ mutationFn:()=>apiPost<SupportTicket>("/support/tickets",{category,subject,message}), onSuccess:()=>{setSubject("");setMessage("");qc.invalidateQueries({queryKey:["support-tickets"]});toast.success("Chamado aberto.")}, onError:e=>toast.error(e instanceof Error?e.message:"Não foi possível abrir o chamado.") });
  return <div className="animate-fade-up space-y-6">
    <div><div className="flex items-center gap-3"><div className="grid size-11 place-items-center rounded-2xl bg-brand-soft text-brand-dark"><LifeBuoy className="size-6"/></div><div><h1 className="text-3xl font-extrabold">Suporte</h1><p className="text-sm text-slate-500">Abra um chamado e acompanhe a resposta da equipe.</p></div></div></div>
    <form className="rounded-3xl border bg-white p-6 shadow-sm space-y-4" onSubmit={e=>{e.preventDefault();create.mutate()}}>
      <div className="grid gap-4 md:grid-cols-2"><div><Label>Categoria</Label><NativeSelect value={category} onChange={setCategory}><option value="conta">Conta</option><option value="pagamento">Pagamento</option><option value="conteudo">Conteúdo</option><option value="simulado">Simulado</option><option value="bug">Problema técnico</option><option value="privacidade">Privacidade/LGPD</option><option value="outro">Outro</option></NativeSelect></div><div><Label>Assunto</Label><Input value={subject} onChange={e=>setSubject(e.target.value)} minLength={3} maxLength={160} required/></div></div>
      <div><Label>Mensagem</Label><Textarea value={message} onChange={e=>setMessage(e.target.value)} minLength={10} maxLength={10000} rows={6} required/></div>
      <Button disabled={create.isPending}><Send className="size-4"/> {create.isPending?"Enviando...":"Abrir chamado"}</Button>
    </form>
    <div className="space-y-3"><h2 className="text-xl font-bold">Meus chamados</h2>{q.data?.length===0&&<p className="text-sm text-slate-500">Você ainda não abriu chamados.</p>}{q.data?.map(t=><article key={t.id} className="rounded-2xl border bg-white p-5"><div className="flex flex-wrap justify-between gap-2"><h3 className="font-bold">{t.subject}</h3><span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold">{statuses[t.status]||t.status}</span></div><p className="mt-2 text-sm text-slate-600 whitespace-pre-wrap">{t.message}</p>{t.replies?.map(r=><div key={r.id} className="mt-3 rounded-xl bg-slate-50 p-3 text-sm"><b>{r.author_role==="student"?"Você":r.author_name}</b><p className="mt-1 whitespace-pre-wrap">{r.message}</p></div>)}</article>)}</div>
  </div>;
}
