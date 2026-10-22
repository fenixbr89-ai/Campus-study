import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Bell, Check, Clock, Plus, Search, Trash2, Trophy } from "lucide-react";
import { apiDelete, apiGet, apiPost, apiPut, apiAssetUrl } from "@/lib/api";
import { errMsg, usePageMeta } from "@/lib/hooks";
import type { GlobalSearchItem, Note, Notification, PersonalStudyPlanOut, RankingEntry, StudyHistoryEvent, StudyPlan, QuestionReview } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { TopicPicker, EMPTY_SEL, type TopicSel } from "@/components/TopicPicker";

const dayOptions = [
  ["0", "Seg"], ["1", "Ter"], ["2", "Qua"], ["3", "Qui"], ["4", "Sex"], ["5", "Sáb"], ["6", "Dom"],
] as const;

function cleanExplanation(explanation: unknown): string {
  const text = String(explanation ?? "").trim();
  if (!text) return "";
  return text
    .replace(/^A\s+resposta\s+correta\s+é\s+(?:a\s+)?alternativa\s+[A-E]\s*(?:porque\s*:?)?\s*/i, "")
    .replace(/^A\s+alternativa\s+correta\s+é\s+[A-E]\s*(?:porque\s*:?)?\s*/i, "")
    .trim();
}

export function NotesPage() {
  usePageMeta("Minhas anotações");
  const qc = useQueryClient();
  const [query, setQuery] = useState("");
  const notes = useQuery({ queryKey: ["notes", query], queryFn: () => apiGet<Note[]>(query.trim() ? `/notes/search?q=${encodeURIComponent(query.trim())}` : "/notes") });
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Note | null>(null);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [sel, setSel] = useState<TopicSel>(EMPTY_SEL);
  const save = useMutation({
    mutationFn: () => editing
      ? apiPut<Note>(`/notes/${editing.id}`, { title: title.trim(), body: body.trim(), content_id: editing.content_id, topic_id: editing.topic_id })
      : apiPost<Note>("/notes", { title: title.trim(), body: body.trim(), content_id: null, topic_id: sel.topic_id || null }),
    onSuccess: () => { toast.success("Anotação salva."); setOpen(false); setEditing(null); setTitle(""); setBody(""); setSel(EMPTY_SEL); qc.invalidateQueries({ queryKey: ["notes"] }); qc.invalidateQueries({ queryKey: ["global-search"] }); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const del = useMutation({ mutationFn: (id: string) => apiDelete(`/notes/${id}`), onSuccess: () => { toast.success("Anotação excluída."); qc.invalidateQueries({ queryKey: ["notes"] }); }, onError: (e) => toast.error(errMsg(e)) });
  const begin = (n?: Note) => { setEditing(n ?? null); setTitle(n?.title ?? ""); setBody(n?.body ?? ""); setSel({course_id:"",period_id:"",discipline_id:"",topic_id:n?.topic_id ?? ""}); setOpen(true); };
  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div><h1 className="text-3xl font-bold">Minhas anotações</h1><p className="text-slate-500">Escreva resumos, dúvidas, lembretes e observações livres.</p></div>
        <Button onClick={() => begin()}><Plus className="size-4" /> Nova anotação</Button>
      </div>
      <div className="relative max-w-2xl"><Search className="absolute top-3 left-3 size-4 text-slate-400" /><Input value={query} onChange={e => setQuery(e.target.value)} placeholder="Pesquisar nas suas anotações..." className="pl-9" /></div>
      {notes.isLoading && <div className="rounded-2xl border bg-white p-6 text-sm text-slate-500">Carregando anotações...</div>}
      {notes.isError && <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-sm text-red-700">Não foi possível carregar suas anotações.</div>}
      {!notes.isLoading && !notes.isError && notes.data?.length === 0 && <div className="rounded-2xl border border-dashed bg-white p-8 text-center text-sm text-slate-500">Nenhuma anotação encontrada.</div>}
      <div className="grid gap-3 md:grid-cols-2">
        {(notes.data ?? []).map(n => (
          <article key={n.id} className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="flex items-start justify-between gap-3"><div className="min-w-0"><h3 className="font-bold break-words">{n.title}</h3><p className="mt-1 text-[11px] text-slate-400">Atualizada em {new Date(n.updated_at).toLocaleString("pt-BR")}</p></div><div className="flex shrink-0 gap-1"><Button size="icon" variant="ghost" aria-label="Editar anotação" onClick={() => begin(n)}>✎</Button><Button size="icon" variant="ghost" aria-label="Excluir anotação" onClick={() => window.confirm("Excluir esta anotação?") && del.mutate(n.id)}><Trash2 className="size-4" /></Button></div></div>
            <p className="mt-3 whitespace-pre-wrap break-words text-sm text-slate-600">{n.body}</p>
          </article>
        ))}
      </div>
      <Dialog open={open} onOpenChange={setOpen}><DialogContent><DialogHeader><DialogTitle>{editing ? "Editar anotação" : "Nova anotação"}</DialogTitle></DialogHeader><Input maxLength={160} value={title} onChange={e => setTitle(e.target.value)} placeholder="Título"/><TopicPicker prefix="note" value={sel} onChange={setSel} requireTopic={false}/><Textarea maxLength={10000} value={body} onChange={e => setBody(e.target.value)} placeholder="Escreva sua anotação..." className="min-h-44"/><Button onClick={() => save.mutate()} disabled={save.isPending || title.trim().length < 1 || body.trim().length < 1}>{save.isPending ? "Salvando..." : "Salvar"}</Button></DialogContent></Dialog>
    </div>
  );
}

export function PlanPage() {
  usePageMeta("Meu plano de estudos");
  const qc = useQueryClient();
  const plan = useQuery({ queryKey: ["study-plan"], queryFn: () => apiGet<StudyPlan>("/study-plan") });
  const personal = useQuery({ queryKey: ["personal-study-plans"], queryFn: () => apiGet<PersonalStudyPlanOut[]>("/personal-study-plans") });
  const redistribute = useMutation({ mutationFn: () => apiPost<StudyPlan>("/study-plan/redistribute"), onSuccess: d => { qc.setQueryData(["study-plan"], d); toast.success("Plano redistribuído."); }, onError: e => toast.error(errMsg(e)) });
  const completeExam = useMutation({ mutationFn: (id: string) => apiPost(`/exam-tasks/${id}/complete`), onSuccess: () => { qc.invalidateQueries({ queryKey: ["study-plan"] }); qc.invalidateQueries({ queryKey: ["home"] }); qc.invalidateQueries({ queryKey: ["progress"] }); }, onError: e => toast.error(errMsg(e)) });
  const completePersonal = useMutation({ mutationFn: (p: { plan: string; task: string }) => apiPost(`/personal-study-plans/${p.plan}/tasks/${p.task}/complete`), onSuccess: () => qc.invalidateQueries({ queryKey: ["personal-study-plans"] }), onError: e => toast.error(errMsg(e)) });
  const delPersonal = useMutation({ mutationFn: (id: string) => apiDelete(`/personal-study-plans/${id}`), onSuccess: () => { toast.success("Plano excluído."); qc.invalidateQueries({ queryKey: ["personal-study-plans"] }); qc.invalidateQueries({ queryKey: ["study-plan"] }); }, onError: e => toast.error(errMsg(e)) });
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<string | null>(null);
  const [sel, setSel] = useState<TopicSel>(EMPTY_SEL);
  const [title, setTitle] = useState("Plano semanal");
  const [startTime, setStartTime] = useState("19:00");
  const [minutes, setMinutes] = useState<number | string>(60);
  const [days, setDays] = useState<string[]>(["0", "2", "4"]);
  const save = useMutation({
    mutationFn: () => {
      const payload = { title: title.trim(), days, start_time: startTime, minutes_per_session: Number(minutes || 0), discipline_ids: sel.discipline_id ? [sel.discipline_id] : [], topic_ids: sel.topic_id ? [sel.topic_id] : [] };
      return editing ? apiPut<PersonalStudyPlanOut>(`/personal-study-plans/${editing}`, payload) : apiPost<PersonalStudyPlanOut>("/personal-study-plans", payload);
    },
    onSuccess: () => { toast.success(editing ? "Plano atualizado." : "Plano criado e salvo."); closeForm(); qc.invalidateQueries({ queryKey: ["personal-study-plans"] }); qc.invalidateQueries({ queryKey: ["study-plan"] }); },
    onError: e => toast.error(errMsg(e)),
  });
  function closeForm() { setOpen(false); setEditing(null); setSel(EMPTY_SEL); setTitle("Plano semanal"); setStartTime("19:00"); setMinutes(60); setDays(["0", "2", "4"]); }
  function openNew() { setEditing(null); setSel(EMPTY_SEL); setTitle("Plano semanal"); setStartTime("19:00"); setMinutes(60); setDays(["0", "2", "4"]); setOpen(true); }
  function openEdit(p: PersonalStudyPlanOut) {
    setEditing(p.plan.id); setTitle(p.plan.title); setStartTime(p.plan.start_time); setMinutes(p.plan.minutes_per_session); setDays(p.plan.days);
    const topicId=p.plan.topic_ids[0] ?? ""; const disciplineId=p.plan.discipline_ids[0] ?? "";
    setSel({ course_id:p.plan.course_id ?? "", period_id:p.plan.period_id ?? "", discipline_id:disciplineId, topic_id:topicId }); setOpen(true);
  }
  const tasks = plan.data?.tasks ?? [];
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between"><div><h1 className="text-3xl font-bold">Meu Plano de Estudos</h1><p className="text-slate-500">Planos de prova e planos pessoais ficam salvos no sistema.</p></div><Button onClick={openNew}><Plus className="size-4" /> Criar plano pessoal</Button></div>
      {plan.data?.pending_minutes ? <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm">Você tem <b>{plan.data.pending_minutes} minutos</b> pendentes. <Button className="ml-2" variant="outline" onClick={() => redistribute.mutate()} disabled={redistribute.isPending}>{redistribute.isPending ? "Redistribuindo..." : "Redistribuir"}</Button></div> : null}
      {plan.isLoading && <div className="rounded-2xl border bg-white p-6 text-sm text-slate-500">Carregando plano...</div>}
      {plan.isError && <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-sm text-red-700">Não foi possível carregar seu plano.</div>}
      <section className="space-y-3"><div className="flex items-center justify-between"><h2 className="text-lg font-bold">Tarefas de provas</h2><span className="text-xs text-slate-400">{tasks.length} tarefas</span></div>{tasks.map(t => <div key={t.id} className={`flex flex-wrap items-center gap-3 rounded-2xl border bg-white p-4 ${t.completed ? "opacity-60" : ""}`}><button type="button" aria-label={t.completed ? "Desmarcar tarefa" : "Concluir tarefa"} onClick={() => completeExam.mutate(t.id)} disabled={completeExam.isPending} className="grid size-10 shrink-0 place-items-center rounded-full bg-brand-soft"><Check className="size-4 text-brand-dark" /></button><div className="min-w-0 flex-1"><p className="font-semibold">{t.title}</p><p className="text-xs text-slate-500">{new Date(`${t.date}T12:00:00`).toLocaleDateString("pt-BR")} · {t.discipline_name}{t.topic_name ? ` · ${t.topic_name}` : ""}</p></div><span className="text-sm font-bold">{t.minutes} min</span></div>)}</section>
      <section><div className="flex items-center justify-between"><h2 className="text-lg font-bold">Planos pessoais</h2><span className="text-xs text-slate-400">{personal.data?.length ?? 0}</span></div><div className="mt-3 space-y-4">{(personal.data ?? []).map(p => <div key={p.plan.id} className="rounded-3xl border bg-white p-5 shadow-sm"><div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between"><div><h3 className="font-bold">{p.plan.title}</h3><p className="text-xs text-slate-500">{p.plan.days.map(d => dayOptions.find(x => x[0] === d)?.[1]).filter(Boolean).join(" · ")} · {p.plan.start_time} · {p.plan.minutes_per_session} min</p></div><div className="flex gap-1 self-start"><Button size="sm" variant="outline" onClick={() => openEdit(p)}>Editar</Button><Button size="sm" variant="ghost" className="text-red-600" onClick={() => window.confirm("Excluir este plano? ") && delPersonal.mutate(p.plan.id)}><Trash2 className="size-4" /> Excluir</Button></div></div><div className="mt-3 grid gap-2 md:grid-cols-2">{p.tasks.slice(0, 14).map(t => <button key={t.id} type="button" onClick={() => completePersonal.mutate({ plan: p.plan.id, task: t.id })} className={`rounded-xl border p-3 text-left ${t.completed ? "bg-emerald-50" : "bg-slate-50 hover:bg-white"}`}><div className="flex items-center gap-2"><Check className="size-4"/><span className="font-semibold">{t.title}</span></div><p className="mt-1 text-xs text-slate-500">{new Date(`${t.date}T12:00:00`).toLocaleDateString("pt-BR")} · {t.start_time} · {t.minutes} min</p></button>)}</div></div>)}{personal.data?.length === 0 && <p className="rounded-2xl border border-dashed bg-white p-6 text-sm text-slate-500">Nenhum plano pessoal criado ainda.</p>}</div></section>
      <Dialog open={open} onOpenChange={v => { if (v) setOpen(true); else closeForm(); }}><DialogContent className="max-h-[90vh] overflow-y-auto"><DialogHeader><DialogTitle>{editing ? "Editar plano pessoal" : "Criar plano pessoal"}</DialogTitle></DialogHeader><Input value={title} onChange={e => setTitle(e.target.value)} maxLength={160} placeholder="Nome do plano"/><TopicPicker prefix="personal-plan" value={sel} onChange={setSel} requireTopic={false}/><div><p className="mb-2 text-sm font-semibold">Dias da semana</p><div className="grid grid-cols-4 gap-2 sm:grid-cols-7">{dayOptions.map(([value,label]) => <button key={value} type="button" onClick={() => setDays(x => x.includes(value) ? x.filter(y => y !== value) : [...x, value])} className={`rounded-xl border px-3 py-2 text-sm font-semibold ${days.includes(value) ? "border-brand bg-brand text-white" : "bg-white"}`}>{label}</button>)}</div></div><div className="grid gap-3 sm:grid-cols-2"><div><label className="text-sm font-medium">Horário</label><Input type="time" value={startTime} onChange={e => setStartTime(e.target.value)}/></div><div><label className="text-sm font-medium">Minutos por sessão</label><Input type="number" min={15} max={240} value={minutes} onChange={e => setMinutes(e.target.value === "" ? "" : Math.max(15, Math.min(240, Number(e.target.value))))}/></div></div><Button onClick={() => save.mutate()} disabled={save.isPending || !title.trim() || days.length === 0 || !sel.discipline_id}>{save.isPending ? "Salvando..." : editing ? "Salvar alterações" : "Salvar plano"}</Button></DialogContent></Dialog>
    </div>
  );
}


export function NotificationsPage() {
  usePageMeta("Notificações"); const qc=useQueryClient();
  const ns=useQuery({queryKey:["notifications"],queryFn:()=>apiGet<Notification[]>("/notifications")});
  const gen=useMutation({mutationFn:()=>apiPost("/notifications/generate"),onSuccess:()=>{toast.success("Lembretes atualizados.");qc.invalidateQueries({queryKey:["notifications"]})},onError:e=>toast.error(errMsg(e))});
  useEffect(()=>{ gen.mutate(); },[]);
  const read=useMutation({mutationFn:(id:string)=>apiPost(`/notifications/${id}/read`),onSuccess:()=>qc.invalidateQueries({queryKey:["notifications"]}),onError:e=>toast.error(errMsg(e))});
  return <div className="space-y-5"><div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between"><div><h1 className="text-3xl font-bold">Notificações</h1><p className="text-slate-500">Provas, tarefas, metas e revisões reais do seu estudo.</p></div><Button onClick={()=>gen.mutate()} disabled={gen.isPending}><Bell className="size-4"/>{gen.isPending?"Atualizando...":"Atualizar lembretes"}</Button></div>{ns.isLoading&&<div className="rounded-2xl border bg-white p-6 text-sm text-slate-500">Carregando...</div>}{ns.isError&&<div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-sm text-red-700">Não foi possível carregar as notificações.</div>}<div className="space-y-3">{(ns.data??[]).map(n=><button key={n.id} onClick={()=>!n.read&&read.mutate(n.id)} className={`w-full rounded-2xl border p-4 text-left ${n.read?"bg-white":"bg-brand-soft"}`}><div className="flex items-start justify-between gap-3"><div><p className="font-bold">{n.title}</p><p className="mt-1 text-sm text-slate-600">{n.body}</p></div>{!n.read&&<span className="mt-1 size-2 rounded-full bg-brand"/>}</div><p className="mt-2 text-[11px] text-slate-400">{new Date(n.created_at).toLocaleString("pt-BR")}</p></button>)}{ns.data?.length===0&&!ns.isLoading&&<p className="rounded-2xl border border-dashed bg-white p-8 text-center text-sm text-slate-500">Nenhuma notificação no momento.</p>}</div></div>
}

export function RankingPage(){
  usePageMeta("Ranking"); const me=useQuery({queryKey:["me"],queryFn:()=>apiGet<any>("/auth/me")}); const qc=useQueryClient(); const ranking=useQuery({queryKey:["ranking"],queryFn:()=>apiGet<RankingEntry[]>("/ranking"),refetchInterval:5000,refetchOnWindowFocus:true}); const enabled=!!me.data?.ranking_opt_in; const toggle=useMutation({mutationFn:(v:boolean)=>apiPost(`/ranking-opt-in?enabled=${v}`),onSuccess:()=>{qc.invalidateQueries({queryKey:["ranking"]});qc.invalidateQueries({queryKey:["me"]})},onError:e=>toast.error(errMsg(e))}); const rows=ranking.data??[]; const my=rows.find(r=>r.is_me);
  return <div className="space-y-5"><div><h1 className="text-3xl font-bold">Ranking mensal</h1><p className="text-slate-500">A pontuação vem dos minutos de estudo real registrados neste mês.</p></div><div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 p-4"><div><p className="font-semibold text-emerald-950">Participação no ranking</p><p className="text-xs text-emerald-800">Você controla se seu perfil aparece para outros participantes.</p></div><Button onClick={()=>toggle.mutate(!enabled)} variant={enabled?"outline":"default"}>{enabled?"Sair do ranking":"Participar do ranking"}</Button></div>{my&&<div className="rounded-2xl border bg-white p-4"><p className="text-xs uppercase tracking-wide text-slate-400">Sua posição</p><div className="mt-2 flex items-center gap-3"><b className="text-2xl">{my.position}º</b>{my.avatar_url?<img src={apiAssetUrl(my.avatar_url)} alt="" className="size-11 rounded-full object-cover"/>:<div className="grid size-11 place-items-center rounded-full bg-brand-soft font-bold text-brand-dark">{my.name[0]}</div>}<div className="min-w-0 flex-1"><b>{my.name}</b><p className="truncate text-xs text-slate-500">{my.course_name}{my.faculty?` · ${my.faculty}`:""}</p></div><strong>{my.minutes} min</strong></div></div>}<div className="rounded-2xl border bg-white p-4">{rows.slice(0,20).map(r=><div key={r.position} className="flex items-center gap-3 border-b py-4 last:border-0"><b className="w-9 text-center">{r.position===1?"🥇":r.position===2?"🥈":r.position===3?"🥉":`${r.position}º`}</b>{r.avatar_url?<img src={apiAssetUrl(r.avatar_url)} alt="" className="size-10 rounded-full object-cover"/>:<div className="grid size-10 place-items-center rounded-full bg-slate-100 font-semibold">{r.name[0]}</div>}<div className="min-w-0 flex-1"><p className="font-semibold">{r.name}{r.is_me&&" · Você"}</p><p className="truncate text-xs text-slate-500">{r.course_name||"Curso não informado"}{r.faculty?` · ${r.faculty}`:""}</p></div><div className="text-right"><strong>{r.points} pts</strong><p className="text-[11px] text-slate-400">{r.minutes} min</p></div></div>)}{rows.length===0&&<p className="py-8 text-center text-sm text-slate-500">Ainda não há participantes com tempo de estudo registrado neste mês.</p>}</div></div>
}

export function GlobalSearchPage(){
  usePageMeta("Pesquisa global");
  const [params] = useState(()=>new URLSearchParams(window.location.search));
  const [q,setQ]=useState(params.get("q")??"");
  const [courseId,setCourseId]=useState(""); const [periodId,setPeriodId]=useState(""); const [disciplineId,setDisciplineId]=useState(""); const [topicId,setTopicId]=useState(""); const [type,setType]=useState("");
  const courses=useQuery({queryKey:["search-courses"],queryFn:()=>apiGet<any[]>("/courses")});
  const periods=useQuery({queryKey:["search-periods",courseId],enabled:!!courseId,queryFn:()=>apiGet<any[]>(`/filters/periods?course_id=${encodeURIComponent(courseId)}`)});
  const disciplines=useQuery({queryKey:["search-disciplines",periodId,courseId],enabled:!!courseId,queryFn:()=>apiGet<any[]>(`/filters/disciplines?${periodId?`period_id=${encodeURIComponent(periodId)}&`:``}course_id=${encodeURIComponent(courseId)}`)});
  const topics=useQuery({queryKey:["search-topics",disciplineId],enabled:!!disciplineId,queryFn:()=>apiGet<any[]>(`/filters/topics?discipline_id=${encodeURIComponent(disciplineId)}`)});
  const result=useQuery({queryKey:["global-search",q,courseId,periodId,disciplineId,topicId,type],enabled:q.trim().length>0,queryFn:()=>apiGet<{query:string;items:GlobalSearchItem[];total:number}>(`/global-search?q=${encodeURIComponent(q.trim())}`)});
  const content=useQuery({queryKey:["search-content",q,courseId,periodId,disciplineId,topicId,type],enabled:q.trim().length>0,queryFn:()=>apiGet<any>(`/search?q=${encodeURIComponent(q.trim())}&course_id=${encodeURIComponent(courseId)}&period_id=${encodeURIComponent(periodId)}&discipline_id=${encodeURIComponent(disciplineId)}&topic_id=${encodeURIComponent(topicId)}&type=${encodeURIComponent(type)}`)});
  const submit=(e:React.FormEvent)=>{e.preventDefault(); if(q.trim()){result.refetch();content.refetch();}};
  return <div className="space-y-5"><div><h1 className="text-3xl font-bold">Pesquisa avançada</h1><p className="text-slate-500">Pesquise no catálogo e refine por curso, período, disciplina, assunto e tipo de conteúdo.</p></div>
    <form onSubmit={submit} className="space-y-3 rounded-3xl border bg-white p-4"><div className="flex flex-col gap-2 sm:flex-row"><Input value={q} onChange={e=>setQ(e.target.value)} placeholder="Curso, assunto, videoaula, PDF..."/><Button type="submit" disabled={!q.trim()||result.isFetching}>Pesquisar</Button></div>
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-5"><select aria-label="Curso" value={courseId} onChange={e=>{setCourseId(e.target.value);setPeriodId("");setDisciplineId("");setTopicId("")}} className="h-10 rounded-xl border bg-white px-3 text-sm"><option value="">Todos os cursos</option>{courses.data?.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}</select><select aria-label="Período" value={periodId} onChange={e=>{setPeriodId(e.target.value);setDisciplineId("");setTopicId("")}} disabled={!courseId} className="h-10 rounded-xl border bg-white px-3 text-sm"><option value="">Todos os períodos</option>{periods.data?.map(p=><option key={p.id} value={p.id}>{p.name||`${p.number}º período`}</option>)}</select><select aria-label="Disciplina" value={disciplineId} onChange={e=>{setDisciplineId(e.target.value);setTopicId("")}} disabled={!courseId} className="h-10 rounded-xl border bg-white px-3 text-sm"><option value="">Todas as disciplinas</option>{disciplines.data?.map(d=><option key={d.id} value={d.id}>{d.name}</option>)}</select><select aria-label="Assunto" value={topicId} onChange={e=>setTopicId(e.target.value)} disabled={!disciplineId} className="h-10 rounded-xl border bg-white px-3 text-sm"><option value="">Todos os assuntos</option>{topics.data?.map(t=><option key={t.id} value={t.id}>{t.name}</option>)}</select><select aria-label="Tipo de conteúdo" value={type} onChange={e=>setType(e.target.value)} className="h-10 rounded-xl border bg-white px-3 text-sm"><option value="">Todos os tipos</option><option value="pdf">PDF</option><option value="resumo">Resumo</option><option value="video">Vídeo</option><option value="artigo">Artigo</option><option value="questao">Questão</option><option value="material">Material</option></select></div></form>
    {result.isFetching&&<div className="rounded-2xl border bg-white p-6 text-sm text-slate-500">Pesquisando...</div>}{result.isError&&<div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-sm text-red-700">Não foi possível concluir a pesquisa.</div>}
    <div className="grid gap-5 lg:grid-cols-2"><section><h2 className="mb-3 font-bold">Catálogo</h2><div className="space-y-2">{(content.data?.items??[]).map((item:any)=><a key={item.id} href={item.path||"#"} className="block rounded-2xl border bg-white p-4 hover:border-brand/40"><p className="font-semibold">{item.title}</p><p className="mt-1 text-xs text-slate-500">{item.type}{item.topic_name?` · ${item.topic_name}`:""}</p></a>)}{content.data&&!content.data.items.length&&<p className="rounded-2xl border border-dashed bg-white p-6 text-center text-sm text-slate-500">Nenhum conteúdo corresponde aos filtros.</p>}</div></section><section><h2 className="mb-3 font-bold">Cursos, assuntos e seus registros</h2><div className="space-y-2">{(result.data?.items??[]).map(item=><a key={`${item.kind}:${item.id}`} href={item.path||"#"} className="block rounded-2xl border bg-white p-4 hover:border-brand/40"><div className="flex items-start justify-between gap-3"><div><p className="font-semibold">{item.title}</p>{item.subtitle&&<p className="mt-1 text-xs text-slate-500">{item.subtitle}</p>}</div><span className="rounded-full bg-slate-100 px-2 py-1 text-[11px]">{item.kind}</span></div></a>)}{result.data&&!result.data.items.length&&<p className="rounded-2xl border border-dashed bg-white p-6 text-center text-sm text-slate-500">Nenhum resultado.</p>}</div></section></div></div>
}

export function StudyHistoryPage(){
  usePageMeta("Histórico de estudos"); const h=useQuery({queryKey:["study-history"],queryFn:()=>apiGet<StudyHistoryEvent[]>("/study-history")});
  return <div className="space-y-5"><div><h1 className="text-3xl font-bold">Histórico de estudos</h1><p className="text-slate-500">Atividades registradas a partir do seu uso real do sistema.</p></div>{h.isLoading&&<div className="rounded-2xl border bg-white p-6 text-sm text-slate-500">Carregando histórico...</div>}{h.isError&&<div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-sm text-red-700">Não foi possível carregar o histórico.</div>}<div className="space-y-3">{(h.data??[]).map(e=><a key={e.id} href={e.path||"#"} className="flex gap-3 rounded-2xl border bg-white p-4 hover:border-brand/40"><div className="mt-1 grid size-9 shrink-0 place-items-center rounded-xl bg-brand-soft"><Clock className="size-4 text-brand-dark"/></div><div className="min-w-0"><p className="font-semibold">{e.title}</p><p className="text-sm text-slate-500">{e.kind}{e.subtitle?` · ${e.subtitle}`:""}</p><p className="mt-1 text-xs text-slate-400">{new Date(e.date).toLocaleString("pt-BR")}</p></div></a>)}{h.data?.length===0&&!h.isLoading&&<p className="rounded-2xl border border-dashed bg-white p-8 text-center text-sm text-slate-500">Ainda não há atividades registradas.</p>}</div></div>
}

export function QuestionReviewPage(){
  usePageMeta("Revisar questões");
  const qc=useQueryClient();
  const [dueOnly,setDueOnly]=useState(true);
  const reviews=useQuery({queryKey:["question-reviews",dueOnly],queryFn:()=>apiGet<QuestionReview[]>(`/question-reviews?due_only=${dueOnly}`)});
  const remove=useMutation({mutationFn:(id:string)=>apiDelete(`/question-reviews/${id}`),onSuccess:()=>{toast.success("Questão removida da revisão.");qc.invalidateQueries({queryKey:["question-reviews"]})},onError:e=>toast.error(errMsg(e))});
  const complete=useMutation({mutationFn:({id,correct}:{id:string;correct:boolean})=>apiPost<QuestionReview>(`/question-reviews/${id}/complete?correct=${correct}`),onSuccess:()=>{toast.success("Revisão registrada.");qc.invalidateQueries({queryKey:["question-reviews"]})},onError:e=>toast.error(errMsg(e))});
  return <div className="space-y-5">
    <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between"><div><h1 className="text-3xl font-bold">Revisar questões</h1><p className="text-slate-500">Questões marcadas por você ficam salvas e retornam conforme o intervalo de revisão.</p></div><Button variant={dueOnly?"default":"outline"} onClick={()=>setDueOnly(v=>!v)}>{dueOnly?"Só para hoje":"Todas as salvas"}</Button></div>
    {reviews.isLoading&&<div className="rounded-2xl border bg-white p-6 text-sm text-slate-500">Carregando revisões...</div>}
    {reviews.isError&&<div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-sm text-red-700">Não foi possível carregar suas revisões.</div>}
    <div className="space-y-4">{(reviews.data??[]).map((r)=><article key={r.id} className="rounded-3xl border bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500"><span className="rounded-full bg-brand-soft px-2 py-1 font-semibold text-brand-dark">{r.difficulty||"questão"}</span><span className="rounded-full bg-slate-100 px-2 py-1 font-semibold">{{revisar:"Revisar depois",importante:"Importante",dificil:"Difícil",duvida:"Dúvida"}[r.review_reason]||"Revisar depois"}</span>{r.discipline_name&&<span>{r.discipline_name}</span>}{r.topic_name&&<span>· {r.topic_name}</span>}<span className="ml-auto">Próxima: {new Date(`${r.due_date}T12:00:00`).toLocaleDateString("pt-BR")}</span></div>
      <h2 className="mt-3 text-base font-bold leading-6">{r.statement}</h2>
      <div className="mt-4 grid gap-2">{r.options.map((option,i)=><div key={i} className={`rounded-xl border p-3 text-sm ${i===r.correct_index?"border-emerald-300 bg-emerald-50":"border-slate-200"}`}><b className="mr-2">{String.fromCharCode(65+i)}.</b>{option}{i===r.correct_index&&<span className="ml-2 text-xs font-semibold text-emerald-700">Resposta correta</span>}</div>)}</div>
      {cleanExplanation(r.explanation)&&<p className="mt-4 rounded-xl bg-slate-50 p-3 text-sm text-slate-600"><b>Explicação:</b> {cleanExplanation(r.explanation)}</p>}
      <div className="mt-4 flex flex-wrap gap-2"><Button size="sm" onClick={()=>complete.mutate({id:r.id,correct:true})}>Acertei</Button><Button size="sm" variant="outline" onClick={()=>complete.mutate({id:r.id,correct:false})}>Errei</Button><Button size="sm" variant="ghost" onClick={()=>remove.mutate(r.id)}><Trash2 className="size-4"/> Remover</Button></div>
    </article>)}{reviews.data?.length===0&&!reviews.isLoading&&<div className="rounded-3xl border border-dashed bg-white p-8 text-center text-sm text-slate-500">Nenhuma questão está aguardando revisão. Em um resultado de simulado, marque questões que queira revisar.</div>}</div>
  </div>;
}
