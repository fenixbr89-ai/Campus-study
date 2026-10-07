import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, BookmarkPlus, CalendarDays, Check, CheckCircle2, Clock, Flame, GraduationCap, HelpCircle, Loader2, Network, NotebookPen, Play, Plus, Search, Square, Target, Trash2 } from "lucide-react";
import { apiDelete, apiGet, apiPost } from "@/lib/api";
import { errMsg, useMe, usePageMeta } from "@/lib/hooks";
import { minutesLabel } from "@/lib/format";
import type { Discipline, ExamPlan, ExamTask, HomeOut, StudySession, SmartSearchResult, ReviewReason } from "@/lib/types";
import { Row } from "@/components/ContentCard";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";

export function SearchHero({ initial = "", autoFocus = false }: { initial?: string; autoFocus?: boolean }) {
  const [q, setQ] = useState(initial);
  const nav = useNavigate();
  const search = useMutation({
    mutationFn: () => apiGet<SmartSearchResult>(`/smart-search?q=${encodeURIComponent(q.trim())}`),
    onSuccess: (result) => nav(result.path),
    onError: () => nav(`/pesquisa?q=${encodeURIComponent(q.trim())}`),
  });
  return (
    <form data-testid="global-search-form" onSubmit={(e) => { e.preventDefault(); if (q.trim()) search.mutate(); }}
      className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-white p-2 shadow-lg shadow-emerald-900/5 transition-shadow duration-200 focus-within:shadow-xl focus-within:ring-2 focus-within:ring-brand/30">
      <Search className="ml-3 size-5 shrink-0 text-slate-400" />
      <input data-testid="global-search-input" autoFocus={autoFocus} value={q} onChange={(e) => setQ(e.target.value)}
        placeholder="Pesquise: inflamação, nervo trigêmeo, derivadas…"
        className="h-12 min-w-0 flex-1 bg-transparent text-base outline-none placeholder:text-slate-400 sm:text-lg" />
      <button data-testid="global-search-submit" type="submit" disabled={search.isPending}
        className="h-12 rounded-xl bg-brand px-5 font-semibold text-white transition-[background-color,transform] duration-150 hover:bg-brand-dark active:scale-[0.97] disabled:cursor-wait disabled:opacity-70">
        {search.isPending ? "Encontrando…" : "Pesquisar"}
      </button>
    </form>
  );
}

const TOOLS = [
  { to: "/simulados", icon: HelpCircle, label: "Simulados", desc: "Treine com nota e explicações" },
    { to: "/biblioteca", icon: NotebookPen, label: "Salvos", desc: "Seus resumos salvos" },
];

function UpcomingExamCard({ plan, onAdd }: { plan?: ExamPlan | null; onAdd: () => void }) {
  const qc = useQueryClient();
  const [activeSession, setActiveSession] = useState<StudySession | null>(null);
  const [now, setNow] = useState(Date.now());
  const remove = useMutation({
    mutationFn: async () => {
      if (!plan?.id) throw new Error("ID da prova não encontrado.");
      await qc.cancelQueries({ queryKey: ["home"] });
      return apiDelete<{ message: string }>(`/exam-plans/${plan.id}`);
    },
    onMutate: async () => {
      const previous = qc.getQueryData<HomeOut>(["home"]);
      qc.setQueryData<HomeOut>(["home"], (current) => current ? { ...current, upcoming_exam: null } : current);
      return { previous };
    },
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["home"] });
      await qc.invalidateQueries({ queryKey: ["study-plan"] });
    },
    onError: (e, _vars, context) => {
      if (context?.previous) qc.setQueryData(["home"], context.previous);
      toast.error(errMsg(e));
    },
  });
  const tasks = useQuery({ queryKey: ["exam-tasks", plan?.id], queryFn: () => apiGet<ExamTask[]>(`/exam-plans/${plan!.id}/tasks`), enabled: !!plan });
  const start = useMutation({ mutationFn: (taskId: string) => apiPost<StudySession>("/study-sessions", { task_id: taskId }), onSuccess: (session) => { setActiveSession(session); setNow(Date.now()); } });
  const stop = useMutation({ mutationFn: () => apiPost<StudySession>(`/study-sessions/${activeSession!.id}/stop`), onSuccess: () => { setActiveSession(null); qc.invalidateQueries({ queryKey: ["home"] }); qc.invalidateQueries({ queryKey: ["progress"] }); } });
  useEffect(() => () => {
    if (activeSession?.id && !stop.isPending) void apiPost(`/study-sessions/${activeSession.id}/stop`).catch(() => undefined);
  }, [activeSession?.id]);
  const complete = useMutation({ mutationFn: (taskId: string) => apiPost<{ message: string }>(`/exam-tasks/${taskId}/complete`), onSuccess: () => { qc.invalidateQueries({ queryKey: ["home"] }); qc.invalidateQueries({ queryKey: ["exam-tasks", plan?.id] }); qc.invalidateQueries({ queryKey: ["progress"] }); } });

  useEffect(() => {
    if (!activeSession) return;
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, [activeSession]);

  useEffect(() => {
    if (!activeSession || !tasks.data) return;
    const task = tasks.data.find((t) => t.id === activeSession.task_id);
    if (!task) return;
    const elapsed = Math.max(0, Math.floor((now - new Date(activeSession.started_at).getTime()) / 1000));
    if (elapsed >= task.minutes * 60 && !stop.isPending) {
      stop.mutate();
      complete.mutate(task.id);
    }
  }, [activeSession, now, tasks.data]);

  if (!plan) return (
    <section className="mt-8 rounded-3xl border border-emerald-200 bg-gradient-to-br from-emerald-50 to-white p-5 sm:p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div><p className="text-sm font-semibold text-brand-dark">📆 Prova chegando?</p><h2 className="mt-1 text-xl font-bold">Organize seus estudos antes da prova</h2><p className="mt-1 text-sm text-slate-600">Cadastre uma prova e o Campus Study calcula o que você precisa estudar.</p></div>
        <button type="button" onClick={onAdd} className="inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-brand px-5 font-semibold text-white hover:bg-brand-dark"><Plus className="size-4" /> Cadastrar prova</button>
      </div>
    </section>
  );

  const today = new Date().toISOString().slice(0, 10);
  const todayTasks = (tasks.data ?? []).filter((t) => t.task_date === today);
  const activeTask = activeSession ? todayTasks.find((t) => t.id === activeSession.task_id) : null;
  const activeSeconds = activeSession ? Math.max(0, Math.floor((now - new Date(activeSession.started_at).getTime()) / 1000)) : 0;
  const activeMinutes = Math.floor(activeSeconds / 60).toString().padStart(2, "0");
  const activeRestSeconds = (activeSeconds % 60).toString().padStart(2, "0");

  return (
    <section data-testid="home-upcoming-exam" className="mt-8 rounded-3xl border border-emerald-200 bg-gradient-to-br from-emerald-50 via-white to-white p-5 shadow-sm sm:p-6">
      <div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-sm font-semibold text-brand-dark">📆 Prova chegando</p><h2 className="mt-1 text-2xl font-extrabold tracking-tight">{plan.title}</h2><p className="mt-1 flex items-center gap-1.5 text-sm text-slate-600"><CalendarDays className="size-4" /> {new Date(`${plan.exam_date}T12:00:00`).toLocaleDateString("pt-BR")}</p></div><button type="button" aria-label="Excluir plano da prova" onClick={() => remove.mutate()} disabled={remove.isPending} className="rounded-lg p-2 text-slate-400 hover:bg-red-50 hover:text-red-600"><Trash2 className="size-4" /></button></div>
      <div className="mt-5 grid gap-4 sm:grid-cols-[1fr_auto]"><div><p className="text-3xl font-extrabold text-brand-dark">Faltam {plan.days_left} {plan.days_left === 1 ? "dia" : "dias"}.</p><div className="mt-3 flex items-center justify-between text-sm"><span className="font-semibold">Seu progresso: {plan.progress_pct}%</span><span className="text-slate-500">{plan.topics_completed}/{plan.topics_total} assuntos</span></div><div className="mt-2 h-2.5 overflow-hidden rounded-full bg-emerald-100"><div className="h-full rounded-full bg-brand" style={{ width: `${plan.progress_pct}%` }} /></div></div><div className="grid grid-cols-3 gap-2 sm:min-w-72"><div className="rounded-2xl bg-white p-3 text-center shadow-sm"><p className="text-xl font-bold text-emerald-600">{plan.topics_completed}</p><p className="text-[11px] text-slate-500">Concluídos</p></div><div className="rounded-2xl bg-white p-3 text-center shadow-sm"><p className="text-xl font-bold text-amber-500">{plan.topics_in_progress}</p><p className="text-[11px] text-slate-500">Em andamento</p></div><div className="rounded-2xl bg-white p-3 text-center shadow-sm"><p className="text-xl font-bold text-red-500">{plan.topics_pending}</p><p className="text-[11px] text-slate-500">Pendentes</p></div></div></div>
      <div className="mt-5 grid grid-cols-2 gap-2 sm:grid-cols-4">{[["📝", String(plan.questions_to_practice), "questões"],["🔄", String(plan.revisions), "revisões"],["🎯", String(plan.mock_exams), "simulados"],["⏱️", `${plan.daily_minutes} min`, "por dia"]].map(([icon, value, label]) => <div key={label} className="rounded-2xl border border-slate-100 bg-white p-3"><span>{icon}</span><p className="mt-1 font-bold">{value}</p><p className="text-xs text-slate-500">{label}</p></div>)}</div>

      <div className="mt-5 rounded-2xl border border-emerald-100 bg-white p-4 sm:p-5">
        <div className="flex flex-wrap items-center justify-between gap-2"><div><p className="text-xs font-bold uppercase tracking-wide text-brand-dark">Plano de hoje</p><p className="mt-1 font-semibold">Tarefas salvas para {new Date(`${today}T12:00:00`).toLocaleDateString("pt-BR", { day: "2-digit", month: "long" })}</p></div>{activeSession && <div className="rounded-xl bg-emerald-50 px-3 py-2 text-lg font-extrabold text-brand-dark tabular-nums">{activeMinutes}:{activeRestSeconds}</div>}</div>
        <div className="mt-4 space-y-2">
          {tasks.isLoading && <p className="text-sm text-slate-500">Montando seu plano diário...</p>}
          {!tasks.isLoading && todayTasks.length === 0 && <p className="text-sm text-slate-500">Nenhuma tarefa pendente hoje. O plano será recalculado conforme seu progresso.</p>}
          {todayTasks.map((task) => {
            const running = activeSession?.task_id === task.id;
            return <div key={task.id} className={`flex flex-col gap-3 rounded-2xl border p-3 sm:flex-row sm:items-center sm:justify-between ${task.completed ? "border-emerald-100 bg-emerald-50/60" : "border-slate-100 bg-slate-50/60"}`}>
              <div className="flex min-w-0 items-start gap-3"><span className={`mt-0.5 grid size-9 shrink-0 place-items-center rounded-xl ${task.completed ? "bg-emerald-100 text-emerald-700" : "bg-white text-brand"}`}>{task.completed ? <Check className="size-4" /> : task.kind === "topic" ? <GraduationCap className="size-4" /> : task.kind === "questions" ? <HelpCircle className="size-4" /> : <CheckCircle2 className="size-4" />}</span><div className="min-w-0"><p className={`font-semibold ${task.completed ? "text-emerald-800 line-through" : ""}`}>{task.title}</p><p className="text-xs text-slate-500">{task.minutes} minutos{task.topic_name ? ` · ${task.topic_name}` : ""}</p></div></div>
              {!task.completed && <div className="flex shrink-0 gap-2"><button type="button" onClick={() => running ? stop.mutate() : start.mutate(task.id)} disabled={start.isPending || stop.isPending || (!!activeSession && !running)} className="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-brand px-4 text-sm font-semibold text-white disabled:opacity-50">{(start.isPending || stop.isPending) && running ? <Loader2 className="size-4 animate-spin" /> : running ? <Square className="size-3.5" /> : <Play className="size-4" />}{running ? "Parar" : "Começar"}</button><button type="button" onClick={() => complete.mutate(task.id)} disabled={complete.isPending || !!activeSession} className="inline-flex h-10 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700 disabled:opacity-50">Concluir</button></div>}
            </div>;
          })}
        </div>
        {activeTask && <p className="mt-3 text-xs text-slate-500">A sessão registra o tempo real estudado. Ao atingir {activeTask.minutes} minutos, a tarefa é concluída e o plano é recalculado automaticamente.</p>}
      </div>
    </section>
  );
}

function ExamPlanDialog({ open, onOpenChange, courseId }: { open: boolean; onOpenChange: (v: boolean) => void; courseId?: string | null }) {
  const qc = useQueryClient(); const [title, setTitle] = useState("Prova de Matemática"); const [examDate, setExamDate] = useState(""); const [disciplineId, setDisciplineId] = useState("");
  const disciplines = useQuery({ queryKey: ["exam-plan-disciplines", courseId], queryFn: () => apiGet<Discipline[]>(`/filters/disciplines${courseId ? `?course_id=${encodeURIComponent(courseId)}` : ""}`), enabled: open });
  const create = useMutation({
    mutationFn: () => apiPost<ExamPlan>("/exam-plans", { title: title.trim(), exam_date: examDate, discipline_id: disciplineId }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["home"] }); onOpenChange(false); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const today = new Intl.DateTimeFormat("en-CA", { timeZone: "America/Sao_Paulo", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());
  return <Dialog open={open} onOpenChange={onOpenChange}><DialogContent className="max-w-lg rounded-3xl p-6"><DialogHeader><DialogTitle className="text-xl">📆 Cadastrar prova</DialogTitle></DialogHeader><form className="space-y-4" onSubmit={(e) => { e.preventDefault(); if (title.trim() && examDate && disciplineId) create.mutate(); }}><div><label className="text-sm font-medium">Nome da prova</label><input value={title} onChange={(e) => setTitle(e.target.value)} className="mt-1 h-11 w-full rounded-xl border border-slate-200 px-3 outline-none focus:border-brand" placeholder="Prova de Matemática" /></div><div className="grid gap-3 sm:grid-cols-2"><div><label className="text-sm font-medium">Data da prova</label><input required min={today} type="date" value={examDate} onChange={(e) => setExamDate(e.target.value)} className="mt-1 h-11 w-full rounded-xl border border-slate-200 px-3 outline-none focus:border-brand" /></div><div><label className="text-sm font-medium">Disciplina</label><select required value={disciplineId} onChange={(e) => setDisciplineId(e.target.value)} className="mt-1 h-11 w-full rounded-xl border border-slate-200 bg-white px-3 outline-none focus:border-brand"><option value="">Selecione...</option>{disciplines.data?.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}</select></div></div>{create.isError && <p className="text-sm text-red-600">Não foi possível cadastrar a prova. Confira os campos.</p>}<button disabled={create.isPending || !examDate || !disciplineId} className="h-11 w-full rounded-xl bg-brand font-semibold text-white disabled:opacity-50">{create.isPending ? "Calculando plano..." : "Cadastrar e calcular plano"}</button></form></DialogContent></Dialog>;
}

export function ExamsPage() {
  usePageMeta("Simulados");
  const [sp] = useSearchParams();
  const examId = sp.get("exame");
  const me = useMe();
  const [courseId, setCourseId] = useState("");
  const [periodId, setPeriodId] = useState("");
  const [disciplineId, setDisciplineId] = useState("");
  const [topicId, setTopicId] = useState("");
  const [count] = useState<number>(20);
  const [exam, setExam] = useState<any>(null);
  const [answers, setAnswers] = useState<number[]>([]);
  const [reviewReasons, setReviewReasons] = useState<Record<number, ReviewReason>>({});
  const courses = useQuery({ queryKey: ["exam-courses"], queryFn: () => apiGet<any[]>("/courses") });
  const periods = useQuery({ queryKey: ["exam-periods", courseId], queryFn: () => apiGet<any[]>(`/filters/periods?course_id=${encodeURIComponent(courseId)}`), enabled: !!courseId });
  const disciplines = useQuery({ queryKey: ["exam-disciplines", periodId], queryFn: () => apiGet<any[]>(`/filters/disciplines?period_id=${encodeURIComponent(periodId)}`), enabled: !!periodId });
  const topics = useQuery({ queryKey: ["exam-topics", disciplineId], queryFn: () => apiGet<any[]>(`/filters/topics?discipline_id=${encodeURIComponent(disciplineId)}`), enabled: !!disciplineId });
  const load = useQuery({ queryKey: ["exam", examId], queryFn: () => apiGet<any>(`/exams/${examId}`), enabled: !!examId });
  useEffect(() => { if (load.data) { setExam(load.data); setAnswers(load.data.questions.map((q:any) => q.chosen ?? -1)); setReviewReasons({}); } }, [load.data]);
  const start = useMutation({ mutationFn: () => apiPost<any>("/exams", { source:"banco", course_id: courseId || null, period_id: periodId || null, discipline_id: disciplineId || null, topic_id: topicId || null, difficulty:"", count: Number(count || 0), item_id:null, mode:"estudo", shuffle_questions:true, shuffle_options:true }), onSuccess: e => { setExam(e); setAnswers(e.questions.map(() => -1)); setReviewReasons({}); window.history.replaceState({}, "", `/simulados?exame=${e.id}`); } });
  const submit = useMutation({ mutationFn: () => apiPost<any>(`/exams/${exam.id}/submit`, { answers, duration_seconds: 0 }), onSuccess: e => setExam(e) });
  const premium = !!me.data && (me.data.plan === "premium" || me.data.trial_active);
  if (!premium) return <div className="rounded-3xl border border-amber-200 bg-amber-50 p-6"><h1 className="text-2xl font-extrabold">🔒 Simulados são Premium</h1><p className="mt-2 text-sm text-amber-900">Seu período gratuito terminou ou sua conta está no Free. Assine o Premium para gerar simulados automaticamente.</p><Link className="mt-4 inline-flex rounded-xl bg-brand px-5 py-3 font-semibold text-white" to="/planos">Conhecer Premium</Link></div>;
  if (exam) {
    const done = exam.status === "finalizado";
    return <div className="space-y-5"><div><h1 className="text-3xl font-extrabold">{exam.title}</h1><p className="mt-1 text-sm text-slate-500">{exam.total} questões · feedback imediato durante o estudo</p></div>
      {exam.questions.map((q:any, i:number) => { const selected = answers[i] ?? -1; const correct = q.correct_index; const reviewReason = reviewReasons[i] ?? "revisar"; return <div key={i} className="rounded-2xl border border-slate-200 bg-white p-5"><p className="font-bold">{i+1}. {q.statement}</p><div className="mt-4 grid gap-2">{q.options.map((op:string,j:number) => { const chosen = selected===j; const isCorrect = (chosen || done) && j===correct; const isWrong = done && chosen && j!==correct; return <button key={j} type="button" onClick={()=>!done&&setAnswers(a=>a.map((v,k)=>k===i?j:v))} aria-label={`Alternativa ${String.fromCharCode(65+j)}`} className={`min-h-11 rounded-xl border p-3 text-left text-sm ${isCorrect?"border-emerald-400 bg-emerald-50":isWrong?"border-red-300 bg-red-50":chosen?"border-brand bg-brand-soft":"border-slate-200 hover:border-brand/50"}`}>{String.fromCharCode(65+j)}) {op}</button>; })}</div>{(selected>=0 || done) && <p className={`mt-3 text-sm font-semibold ${selected===correct?"text-emerald-700":"text-red-700"}`}>{selected===correct?`✓ Você acertou. A alternativa correta é ${String.fromCharCode(65+correct)}.`:`✗ Você errou. A alternativa correta é ${String.fromCharCode(65+correct)}.`} {q.explanation}</p>}<div className="mt-4 flex flex-wrap items-center gap-2"><label htmlFor={`review-reason-${i}`} className="text-xs font-semibold text-slate-600">Marcar para:</label><select id={`review-reason-${i}`} value={reviewReason} onChange={e=>setReviewReasons(r=>({...r,[i]:e.target.value as ReviewReason}))} className="min-h-10 rounded-xl border border-slate-200 bg-white px-3 text-xs font-semibold"><option value="revisar">Revisar depois</option><option value="importante">Importante</option><option value="dificil">Difícil</option><option value="duvida">Dúvida</option></select><button type="button" onClick={async()=>{try{await apiPost(`/question-reviews`,{exam_id:exam.id,question_index:i,review_reason:reviewReason});toast.success("Questão salva na revisão.");}catch(e){toast.error(errMsg(e));}}} className="inline-flex min-h-10 items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-xs font-semibold hover:border-brand/40"><BookmarkPlus className="size-4"/> Salvar revisão</button></div></div>; })}
      {!done ? <button onClick={()=>submit.mutate()} disabled={submit.isPending || answers.some((a:number)=>a<0)} className="w-full rounded-xl bg-brand py-3 font-semibold text-white disabled:opacity-50">{submit.isPending?"Corrigindo...":"Finalizar simulado"}</button> : <div className="rounded-3xl border border-emerald-200 bg-emerald-50 p-6 text-center"><p className="text-sm text-emerald-800">Resultado final</p><p className="mt-1 text-4xl font-extrabold text-emerald-900">{exam.correct}/{exam.total}</p><p className="mt-1 font-semibold">{exam.correct} acertos · {exam.total-exam.correct} erros</p><Link to="/simulados" className="mt-4 inline-flex rounded-xl border border-emerald-300 bg-white px-4 py-2 font-semibold text-emerald-800">Novo simulado</Link></div>}</div>;
  }
  return <div className="space-y-5"><div><h1 className="text-3xl font-extrabold">Simulados</h1><p className="mt-1 text-slate-500">As questões vêm do banco validado do Campus Study; nenhuma questão é inventada para completar o simulado.</p></div><div className="rounded-3xl border border-slate-200 bg-white p-5"><div className="grid gap-4 md:grid-cols-4"><div><label className="text-sm font-semibold">Curso</label><select value={courseId} onChange={e=>{setCourseId(e.target.value);setPeriodId("");setDisciplineId("");setTopicId("")}} className="mt-1 h-11 w-full rounded-xl border bg-white px-3"><option value="">Selecione</option>{courses.data?.map((c:any)=><option key={c.id} value={c.id}>{c.name}</option>)}</select></div><div><label className="text-sm font-semibold">Período</label><select value={periodId} onChange={e=>{setPeriodId(e.target.value);setDisciplineId("");setTopicId("")}} disabled={!courseId} className="mt-1 h-11 w-full rounded-xl border bg-white px-3"><option value="">Todos os períodos</option>{periods.data?.map((p:any)=><option key={p.id} value={p.id}>{p.name || `${p.number}º período`}</option>)}</select></div><div><label className="text-sm font-semibold">Disciplina</label><select value={disciplineId} onChange={e=>{setDisciplineId(e.target.value);setTopicId("")}} disabled={!periodId} className="mt-1 h-11 w-full rounded-xl border bg-white px-3"><option value="">Todas as disciplinas</option>{disciplines.data?.map((d:any)=><option key={d.id} value={d.id}>{d.name}</option>)}</select></div><div><label className="text-sm font-semibold">Assunto</label><select value={topicId} onChange={e=>setTopicId(e.target.value)} disabled={!disciplineId} className="mt-1 h-11 w-full rounded-xl border bg-white px-3"><option value="">Todos os assuntos</option>{topics.data?.map((t:any)=><option key={t.id} value={t.id}>{t.name}</option>)}</select></div></div><div className="mt-4 flex flex-wrap items-center gap-3"><span className="rounded-xl bg-slate-100 px-3 py-2 text-sm font-semibold">20 questões</span><button onClick={()=>start.mutate()} disabled={start.isPending || (!courseId && !periodId && !disciplineId && !topicId)} className="rounded-xl bg-brand px-5 py-3 font-semibold text-white disabled:opacity-50">{start.isPending?"Gerando...":"Gerar simulado"}</button></div><p className="mt-3 text-xs text-slate-500">Você pode gerar por curso, disciplina ou assunto. O resultado é corrigido no próprio aplicativo.</p></div></div>;
}

export default function Home() {
  usePageMeta("Início");
  const me = useMe();
  const home = useQuery({ queryKey: ["home"], queryFn: () => apiGet<HomeOut>("/home") });
  const site = useQuery({ queryKey: ["site-config-public"], queryFn: () => apiGet<any>("/site-config/public") });
  const data = home.isError ? undefined : home.data;
  const first = me.data?.name.split(" ")[0] ?? "";
  const hour = new Date().getHours();
  const greet = hour < 12 ? "Bom dia" : hour < 18 ? "Boa tarde" : "Boa noite";
  const p = data?.progress;
  const goalPct = p ? Math.min(100, Math.round((p.minutes_today / Math.max(1, p.daily_goal_minutes)) * 100)) : 0;
  const [examDialogOpen, setExamDialogOpen] = useState(false);

  return (
    <div className="animate-fade-up">
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-100 via-green-50 to-white p-6 sm:p-10">
        <div className="pointer-events-none absolute -top-20 -right-20 size-72 rounded-full bg-emerald-200/50 blur-3xl" />
        <p className="relative text-sm font-semibold text-brand-dark">{greet}{first && `, ${first}`} 👋</p>
        <h1 data-testid="home-greeting" className="relative mt-1 max-w-2xl text-3xl leading-[1.15] font-extrabold tracking-tight text-slate-900 sm:text-4xl">
          {site.data?.home_texts?.["home.title"] || "O que vamos estudar hoje?"}
        </h1>
        <div className="relative mt-6 max-w-3xl"><SearchHero /></div>
      </section>

      <section data-testid="home-progress" className="mt-6 grid grid-cols-2 gap-3 md:grid-cols-4">
        {[
          { icon: Flame, label: "Sequência", value: `${p?.streak_days ?? 0} dias` },
          { icon: Clock, label: "Hoje", value: minutesLabel(p?.minutes_today ?? 0) },
          { icon: Target, label: "Pontos", value: String(p?.points ?? 0) },
          { icon: GraduationCap, label: "Assuntos concluídos", value: String(p?.topics_completed ?? 0) },
        ].map((s) => (
          <Link to="/progresso" key={s.label} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-transform duration-200 hover:-translate-y-0.5">
            <s.icon className="size-5 text-brand" />
            <p className="mt-2 font-heading text-xl font-bold">{s.value}</p>
            <p className="text-xs text-slate-500">{s.label}</p>
          </Link>
        ))}
      </section>
      <div className="mt-3 rounded-2xl border border-slate-200 bg-white p-4">
        <div className="flex justify-between text-sm"><span className="font-medium">Meta diária</span><span className="text-slate-500">{p?.minutes_today ?? 0}/{p?.daily_goal_minutes ?? 60} min</span></div>
        <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-brand transition-[width] duration-500" style={{ width: `${goalPct}%` }} /></div>
      </div>

      <UpcomingExamCard plan={data?.upcoming_exam} onAdd={() => setExamDialogOpen(true)} />
      <ExamPlanDialog open={examDialogOpen} onOpenChange={setExamDialogOpen} courseId={me.data?.course_id} />

      {data && data.continue_studying.length > 0 && (
        <section data-testid="home-continue-studying" className="mt-10">
          <h2 className="mb-4 text-xl font-bold tracking-tight">Continuar estudando</h2>
          <div className="no-scrollbar -mx-4 flex snap-x gap-3 overflow-x-auto px-4 pb-2">
            {data.continue_studying.map((h) => (
              <Link key={h.topic_id} to={h.path} data-testid={`continue-item-${h.topic_id}`}
                className="w-60 shrink-0 snap-start rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-[transform,box-shadow] duration-200 hover:-translate-y-1 hover:shadow-md">
                <p className="text-xs text-slate-500">{h.course_name}</p>
                <p className="mt-1 font-semibold">{h.topic_name}</p>
                <p className="text-sm text-slate-500">{h.discipline_name}</p>
              </Link>
            ))}
          </div>
        </section>
      )}

      <section className="mt-10">
        <h2 className="mb-4 text-xl font-bold tracking-tight">Ferramentas de estudo</h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          {TOOLS.map((t) => (
            <Link key={t.to} to={t.to} data-testid={`home-tool-${t.to.slice(1)}`}
              className="group rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-[transform,box-shadow] duration-200 hover:-translate-y-1 hover:shadow-md">
              <span className="grid size-10 place-items-center rounded-xl bg-brand-soft text-brand-dark transition-colors group-hover:bg-brand group-hover:text-white"><t.icon className="size-5" /></span>
              <p className="mt-3 font-semibold">{t.label}</p>
              <p className="text-xs text-slate-500">{t.desc}</p>
            </Link>
          ))}
        </div>
      </section>

      <section data-testid="home-courses" className="mt-10">
        <div className="mb-4 flex items-end justify-between">
          <h2 className="text-xl font-bold tracking-tight">Cursos</h2>
          <Link to="/cursos" data-testid="home-all-courses-link" className="text-sm font-semibold text-brand-dark">Ver todos</Link>
        </div>
        <div className="no-scrollbar -mx-4 flex snap-x gap-3 overflow-x-auto px-4 pb-2">
          {(data?.courses ?? []).map((c) => (
            <Link key={c.id} to={`/cursos/${c.slug}`} data-testid={`home-course-${c.slug}`}
              className="w-44 shrink-0 snap-start rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-[transform,box-shadow] duration-200 hover:-translate-y-1 hover:shadow-md">
              <GraduationCap className="size-6 text-brand" />
              <p className="mt-3 font-semibold leading-tight">{c.name}</p>
              <p className="text-xs text-slate-500">{c.num_periods} períodos</p>
            </Link>
          ))}
        </div>
      </section>

      {site.data?.sections?.recommended !== false && <Row title={site.data?.home_texts?.["home.recommended"] || "Recomendados para você"} items={data?.recommended ?? []} testId="home-recommended" empty="Assim que houver materiais publicados, eles aparecem aqui." />}
      {site.data?.sections?.videos !== false && <Row title={site.data?.home_texts?.["home.videos"] || "Videoaulas"} items={data?.videos ?? []} testId="home-videos" empty="Nenhuma videoaula publicada ainda. Os administradores estão curando videoaulas reais do YouTube." />}
      {site.data?.sections?.articles !== false && <Row title={site.data?.home_texts?.["home.articles"] || "Artigos científicos"} items={data?.articles ?? []} testId="home-articles" empty="Nenhum artigo científico publicado ainda. Em breve, artigos com fontes verificadas." />}
    </div>
  );
}
