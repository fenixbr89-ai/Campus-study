import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Award, Clock, Flame, Lock, LogOut, Target, Trash2 } from "lucide-react";
import { apiGet, apiPost, apiPut, apiDelete, apiUpload, apiAssetUrl } from "@/lib/api";
import { errMsg, isAdmin, useMe, usePageMeta } from "@/lib/hooks";
import { formatDate, minutesLabel } from "@/lib/format";
import { endSession } from "@/lib/session";
import type { Content, Course, Exam, Me, Message, ProgressOut, Submission, SubmissionIn, UserItem, TopicFavorite, AcademicPerformance } from "@/lib/types";
import { ContentCard } from "@/components/ContentCard";
import { ItemViewer } from "@/components/ItemViewer";
import { NativeSelect } from "@/components/SelectField";
import { EMPTY_SEL, TopicPicker, type TopicSel } from "@/components/TopicPicker";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

const KIND_LABELS: Record<string, string> = { resumo: "Resumos", questoes: "Questões", plano: "Planos de estudo", pdf: "PDFs" };

export function LibraryPage() {
  usePageMeta("Minha Biblioteca");
  const me = useMe();
  const qc = useQueryClient();
  const access = !!me.data && !me.isError;
  const [tab, setTab] = useState("salvos");
  const [open, setOpen] = useState<UserItem | null>(null);
  const favs = useQuery({ queryKey: ["favorites"], enabled: !!me.data, queryFn: () => apiGet<Content[]>("/favorites") });
  const items = useQuery({ queryKey: ["items", "all"], enabled: access, queryFn: () => apiGet<UserItem[]>("/items") });
  const exams = useQuery({ queryKey: ["exams"], enabled: access, queryFn: () => apiGet<Exam[]>("/exams") });
  const topicFavorites = useQuery({ queryKey: ["topic-favorites"], enabled: access, queryFn: () => apiGet<TopicFavorite[]>("/topic-favorites") });
  const del = useMutation({
    mutationFn: (id: string) => apiDelete<Message>(`/items/${id}`),
    onSuccess: () => { toast.success("Item excluído."); qc.invalidateQueries({ queryKey: ["items"] }); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const tabs = ["salvos", "assuntos", ...Object.keys(KIND_LABELS), "simulados"];
  const list = (items.data ?? []).filter((i) => i.kind === tab);
  return (
    <div className="animate-fade-up">
      <h1 className="text-3xl font-extrabold tracking-tight">Minha Biblioteca</h1>
      <div className="no-scrollbar -mx-4 mt-5 flex gap-2 overflow-x-auto px-4">
        {tabs.map((t) => (
          <button key={t} data-testid={`library-tab-${t}`} onClick={() => setTab(t)}
            className={cn("shrink-0 rounded-full border px-4 py-2 text-sm font-medium transition-colors", tab === t ? "border-brand bg-brand text-white" : "border-slate-200 bg-white text-slate-600")}>
            {t === "salvos" ? "Materiais salvos" : t === "assuntos" ? "Assuntos favoritos" : t === "simulados" ? "Simulados" : KIND_LABELS[t]}
          </button>
        ))}
      </div>
      <div className="mt-6">
        {tab === "salvos" ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {favs.data?.length === 0 && <p className="text-sm text-slate-500">Você ainda não salvou materiais. Toque no ícone de marcador em qualquer videoaula ou artigo.</p>}
            {favs.data?.map((c) => <ContentCard key={c.id} c={c} saved />)}
          </div>
        ) : tab === "assuntos" ? (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{topicFavorites.data?.map(t=><Link key={t.id} to={t.path} className="rounded-2xl border bg-white p-4 shadow-sm"><p className="font-semibold">{t.name}</p><p className="mt-1 text-xs text-slate-500">{t.discipline_name} · {t.course_name}</p></Link>)}{topicFavorites.data?.length===0&&<p className="text-sm text-slate-500">Nenhum assunto favorito ainda.</p>}</div>
        ) : tab === "simulados" ? (
          <div className="space-y-2">
            {exams.data?.length === 0 && <p className="text-sm text-slate-500">Nenhum simulado ainda.</p>}
            {exams.data?.map((e) => (
              <Link key={e.id} to={`/simulados?exame=${e.id}`} className="flex justify-between rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm">
                <span>{e.title} <span className="text-slate-400">· {formatDate(e.created_at)}</span></span>
                <strong>{e.status === "finalizado" ? e.score?.toFixed(1) : "Em andamento"}</strong>
              </Link>
            ))}
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {list.length === 0 && <p className="text-sm text-slate-500">Nada por aqui ainda. Seus materiais salvos aparecerão aqui.</p>}
            {list.map((i) => (
              <div key={i.id} data-testid={`library-item-${i.id}`} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
                <button onClick={() => setOpen(i)} className="w-full text-left">
                  <p className="font-semibold">{i.title}</p>
                  <p className="text-xs text-slate-500">{formatDate(i.updated_at)}{i.topic_name && ` · ${i.topic_name}`}</p>
                </button>
                <div className="mt-3 flex justify-between">
                  <Button size="sm" variant="outline" onClick={() => setOpen(i)} data-testid={`library-open-${i.id}`}>Abrir</Button>
                  <Button size="sm" variant="ghost" aria-label="Excluir" onClick={() => confirm("Excluir este item?") && del.mutate(i.id)}><Trash2 className="size-4" /></Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      <Dialog open={!!open} onOpenChange={(o) => !o && setOpen(null)}>
        <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
          <DialogHeader><DialogTitle>{open?.title}</DialogTitle></DialogHeader>
          {open && <ItemViewer item={open} />}
        </DialogContent>
      </Dialog>
    </div>
  );
}

export function ProgressPage() {
  usePageMeta("Meu progresso");
  const q = useQuery({ queryKey: ["progress"], queryFn: () => apiGet<ProgressOut>("/progress") });
  const performance = useQuery({ queryKey: ["academic-performance"], queryFn: () => apiGet<AcademicPerformance>("/academic-performance") });
  const p = q.isError ? undefined : q.data;
  const perf = performance.isError ? undefined : performance.data;
  const max = Math.max(1, ...(p?.week.map((d) => d.minutes) ?? [1]));
  const stats = p ? [
    ["Pontos", String(p.points)], ["Sequência", `${p.streak_days} dias`], ["Tempo total", minutesLabel(p.minutes_total)],
    ["Este mês", minutesLabel(p.month_minutes)], ["Dias estudados no mês", String(p.month_study_days)], ["Assuntos concluídos", String(p.topics_completed)],
    ["Disciplinas estudadas", String(p.disciplines_studied)], ["Questões respondidas", String(p.questions_answered)], ["Acertos", `${p.correct_rate}%`], ["Simulados", String(p.exams_taken)],
  ] : [];
  const monthMax = Math.max(1, ...(p?.month.map((d) => d.minutes) ?? [1]));
  return (
    <div className="animate-fade-up">
      <h1 className="text-3xl font-extrabold tracking-tight">Meu progresso</h1>
      <p className="mt-1 text-slate-600">Seu histórico usa o tempo de estudo real registrado nas sessões.</p>
      <div data-testid="progress-stats" className="mt-6 grid grid-cols-2 gap-3 md:grid-cols-5">
        {stats.map(([l, v]) => <div key={l} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"><p className="font-heading text-2xl font-bold">{v}</p><p className="text-xs text-slate-500">{l}</p></div>)}
      </div>
      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div className="rounded-3xl border border-slate-200 bg-white p-5">
          <h2 className="flex items-center gap-2 font-bold"><Clock className="size-4 text-brand" /> Últimos 7 dias</h2>
          <div className="mt-4 flex h-40 items-end gap-2">{p?.week.map((d) => <div key={d.date} className="flex flex-1 flex-col items-center gap-1"><div className="w-full rounded-t-lg bg-brand/80" style={{ height: `${(d.minutes / max) * 100}%`, minHeight: 4 }} title={`${d.minutes} min`} /><span className="text-[10px] text-slate-500">{new Date(`${d.date}T12:00:00`).toLocaleDateString("pt-BR", { weekday: "short" })}</span></div>)}</div>
          <p className="mt-3 flex items-center gap-2 text-sm text-slate-600"><Target className="size-4 text-brand" /> Meta diária: {p?.minutes_today ?? 0}/{p?.daily_goal_minutes ?? 0} min <Link to="/perfil" className="text-brand-dark underline">alterar</Link></p>
        </div>
        <div className="rounded-3xl border border-slate-200 bg-white p-5">
          <h2 className="flex items-center gap-2 font-bold"><Flame className="size-4 text-brand" /> Conquistas</h2>
          <div data-testid="achievements" className="mt-4 grid gap-2 sm:grid-cols-2">{p?.achievements.map((a) => <div key={a.id} className={cn("rounded-xl border p-3", a.unlocked ? "border-emerald-200 bg-brand-soft" : "border-slate-200 opacity-60")}><p className="flex items-center gap-1.5 text-sm font-semibold">{a.unlocked ? <Flame className="size-4 text-brand" /> : <Lock className="size-3.5" />}{a.title}</p><p className="text-xs text-slate-500">{a.description}</p></div>)}</div>
        </div>
      </div>
      <div className="mt-6 rounded-3xl border border-slate-200 bg-white p-5 sm:p-6">
        <div className="flex flex-wrap items-end justify-between gap-3"><div><h2 className="text-xl font-bold">Atividade do mês</h2><p className="text-sm text-slate-500">Quanto mais estudo real você registrar no dia, maior o preenchimento.</p></div><div className="text-sm font-semibold text-brand-dark">{p?.month_study_days ?? 0} dias estudados no mês</div></div>
        <div className="mt-5 grid grid-cols-5 gap-2 sm:grid-cols-10">{p?.month.map((d) => <div key={d.date} title={`${new Date(`${d.date}T12:00:00`).toLocaleDateString("pt-BR")}: ${d.minutes} min`} className="flex aspect-square items-end rounded-md bg-slate-100 p-1"><div className="w-full rounded-sm bg-brand transition-all" style={{height:`${Math.max(8,(d.minutes/monthMax)*100)}%`,opacity:d.minutes?0.35+Math.min(0.65,d.minutes/Math.max(monthMax,1)):0.08}} /></div>)}</div>
      </div>
      {perf && <div className="mt-6 space-y-6">
        <section className="rounded-3xl border border-slate-200 bg-white p-5 sm:p-6">
          <div className="flex flex-wrap items-end justify-between gap-3"><div><h2 className="text-xl font-bold">Desempenho acadêmico</h2><p className="text-sm text-slate-500">Dados calculados a partir das questões realmente respondidas nos simulados finalizados.</p></div><div className="rounded-2xl bg-brand-soft px-4 py-3 text-right"><p className="text-2xl font-extrabold text-brand-dark">{perf.correct_rate}%</p><p className="text-xs text-slate-500">acerto geral</p></div></div>
          <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
            {[['Respondidas',perf.questions_answered],['Acertos',perf.correct],['Erros',perf.incorrect],['Simulados',perf.exams_taken]].map(([label,value]) => <div key={String(label)} className="rounded-2xl bg-slate-50 p-3"><p className="text-xl font-bold">{value}</p><p className="text-xs text-slate-500">{label}</p></div>)}
          </div>
        </section>
        <section className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-3xl border border-slate-200 bg-white p-5">
            <h2 className="font-bold">Por disciplina</h2>
            <div className="mt-4 space-y-3">{perf.by_discipline.slice(0,10).map((b)=><div key={b.label}><div className="flex items-center justify-between gap-3 text-sm"><span className="truncate font-medium">{b.label}</span><span className="shrink-0 font-semibold">{b.correct_rate}% · {b.questions} q.</span></div><div className="mt-1.5 h-2 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-brand" style={{width:`${Math.min(100,b.correct_rate)}%`}}/></div></div>)}{perf.by_discipline.length===0&&<p className="text-sm text-slate-500">Ainda não há questões respondidas suficientes.</p>}</div>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-white p-5">
            <h2 className="font-bold">Por dificuldade</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">{perf.by_difficulty.map((b)=><div key={b.label} className="rounded-2xl border border-slate-200 p-3"><p className="font-semibold">{b.label}</p><p className="mt-1 text-sm text-slate-500">{b.correct_rate}% de acerto · {b.questions} respondidas</p></div>)}{perf.by_difficulty.length===0&&<p className="text-sm text-slate-500">Sem dados por dificuldade ainda.</p>}</div>
          </div>
        </section>
        <section className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-3xl border border-emerald-100 bg-emerald-50 p-5"><h2 className="font-bold text-emerald-900">Pontos fortes</h2>{perf.strengths.length ? <ul className="mt-3 space-y-2">{perf.strengths.map(x=><li key={x} className="rounded-xl bg-white/80 px-3 py-2 text-sm">{x}</li>)}</ul> : <p className="mt-3 text-sm text-emerald-800">Responda mais questões para identificar seus pontos fortes.</p>}</div>
          <div className="rounded-3xl border border-amber-200 bg-amber-50 p-5"><h2 className="font-bold text-amber-900">Pontos para revisão</h2>{perf.needs_review.length ? <ul className="mt-3 space-y-2">{perf.needs_review.map(x=><li key={x} className="rounded-xl bg-white/80 px-3 py-2 text-sm">{x}</li>)}</ul> : <p className="mt-3 text-sm text-amber-800">Nenhum ponto prioritário foi identificado com os dados disponíveis.</p>}</div>
        </section>
        <section className="rounded-3xl border border-slate-200 bg-white p-5">
          <div className="flex flex-wrap items-end justify-between gap-3"><div><h2 className="font-bold">Evolução do desempenho</h2><p className="text-sm text-slate-500">Percentual de acerto por dia em que você respondeu questões.</p></div><span className="text-xs font-semibold text-slate-500">Últimos 30 dias com atividade</span></div>
          <div className="mt-4 space-y-2">{perf.daily_accuracy.slice(-10).map(d=><div key={d.date} className="grid grid-cols-[72px_1fr_58px] items-center gap-3 text-xs"><span className="text-slate-500">{new Date(`${d.date}T12:00:00`).toLocaleDateString("pt-BR",{day:"2-digit",month:"2-digit"})}</span><div className="h-2 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-brand" style={{width:`${Math.min(100,d.correct_rate)}%`}} /></div><span className="text-right font-semibold">{d.correct_rate}%</span></div>)}{perf.daily_accuracy.length===0&&<p className="text-sm text-slate-500">Ainda não há dados suficientes para mostrar evolução.</p>}</div>
        </section>
        <section className="rounded-3xl border border-slate-200 bg-white p-5">
          <h2 className="font-bold">Assuntos com maior necessidade de acompanhamento</h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">{perf.by_topic.filter(x=>x.questions_answered>0).sort((a,b)=>a.correct_rate-b.correct_rate).slice(0,8).map(x=><div key={x.id} className="rounded-2xl border border-slate-200 p-3"><div className="flex items-start justify-between gap-3"><div className="min-w-0"><p className="truncate font-semibold">{x.title}</p><p className="text-xs text-slate-500">{x.discipline_name}</p></div><span className="shrink-0 text-sm font-bold">{x.correct_rate}%</span></div><p className="mt-2 text-xs text-slate-500">{x.questions_answered} questões · {x.study_minutes} min de estudo · {x.completed ? 'concluído' : 'pendente'}</p></div>)}</div>
        </section>
      </div>}
    </div>
  );
}

export function ProfilePage() {
  usePageMeta("Perfil");
  const me = useMe();
  const qc = useQueryClient();
  const courses = useQuery({ queryKey: ["courses"], queryFn: () => apiGet<Course[]>("/courses") });
  const [f, setF] = useState<{ name: string; daily_goal_minutes: number | string; course_id: string; faculty: string; ranking_opt_in: boolean } | null>(null);
  const u = me.isError ? undefined : me.data;
  const form = f ?? (u ? { name: u.name, daily_goal_minutes: u.daily_goal_minutes, course_id: u.course_id ?? "", faculty: u.faculty ?? "", ranking_opt_in: u.ranking_opt_in ?? true } : null);
  const save = useMutation({
    mutationFn: () => apiPut<Me>("/auth/profile", { name: form?.name?.trim(), daily_goal_minutes: Number(form?.daily_goal_minutes || 0), course_id: form?.course_id || null, faculty: form?.faculty?.trim() ?? "", ranking_opt_in: !!form?.ranking_opt_in, avatar_url: u?.avatar_url ?? "" }),
    onSuccess: (m) => {
      qc.setQueryData(["me"], m);
      setF({
        name: m.name,
        daily_goal_minutes: m.daily_goal_minutes,
        course_id: m.course_id ?? "",
        faculty: m.faculty ?? "",
        ranking_opt_in: m.ranking_opt_in ?? true,
      });
      qc.invalidateQueries({ queryKey: ["me"] });
      qc.invalidateQueries({ queryKey: ["home"] });
      setF(null);
      toast.success("Perfil atualizado.");
    },
    onError: (e) => toast.error(errMsg(e)),
  });
  const uploadPhoto = useMutation({
    mutationFn: (file: File) => { const fd = new FormData(); fd.append("file", file); return apiUpload<{ avatar_url: string }>("/auth/profile/photo", fd); },
    onSuccess: (r) => { qc.setQueryData(["me"], (old: Me | undefined) => old ? { ...old, avatar_url: r.avatar_url } : old); toast.success("Foto de perfil atualizada."); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const [pw, setPw] = useState({ current_password: "", new_password: "", new_password_confirm: "" });
  const [deletePw, setDeletePw] = useState("");
  const [deleteConfirm, setDeleteConfirm] = useState("");
  const changePw = useMutation({
    mutationFn: () => apiPost<Message>("/auth/change-password", pw),
    onSuccess: (r) => { toast.success(r.message); setPw({ current_password: "", new_password: "", new_password_confirm: "" }); endSession("/entrar"); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const exportData = useMutation({
    mutationFn: () => apiGet<Record<string, unknown>>("/auth/data-export"),
    onSuccess: (data) => {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json;charset=utf-8" });
      const url = URL.createObjectURL(blob); const a = document.createElement("a");
      a.href = url; a.download = `campus-study-dados-${new Date().toISOString().slice(0,10)}.json`; a.click(); URL.revokeObjectURL(url);
      toast.success("Seus dados foram exportados.");
    },
    onError: (e) => toast.error(errMsg(e)),
  });
  const deleteAccount = useMutation({
    mutationFn: () => apiPost<Message>("/auth/delete-account", { current_password: deletePw, confirmation: deleteConfirm }),
    onSuccess: (r) => { toast.success(r.message); endSession("/"); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const mySubs = useQuery({ queryKey: ["my-submissions"], enabled: !!u, queryFn: () => apiGet<Submission[]>("/submissions/mine") });
  if (!u || !form) return null;
  return (
    <div className="animate-fade-up">
      <div className="rounded-3xl border border-emerald-100 bg-emerald-50 p-5 sm:p-6">
        <div className="flex flex-col items-center text-center sm:items-start sm:text-left">
          {u.avatar_url ? <img src={apiAssetUrl(u.avatar_url)} alt="Foto de perfil" className="size-28 rounded-full object-cover shadow-sm ring-4 ring-white" /> : <div className="grid size-28 place-items-center rounded-full bg-white text-4xl font-bold text-brand-dark shadow-sm ring-4 ring-white">{u.name[0]}</div>}
          <h1 className="mt-4 text-3xl font-extrabold tracking-tight">{u.name}</h1>
          <p className="mt-1 text-sm text-slate-600">{u.email}</p>
          <label className="mt-4 inline-flex cursor-pointer rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold hover:bg-slate-50">
            <input type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={(e) => { const file=e.target.files?.[0]; if(file) uploadPhoto.mutate(file); }} />
            {uploadPhoto.isPending ? "Enviando..." : "Alterar foto"}
          </label>
        </div>
      </div>
      <div className="mt-6 grid gap-6 lg:grid-cols-[1.3fr_1fr]">
        <form className="space-y-4 rounded-3xl border border-slate-200 bg-white p-6" onSubmit={(e) => { e.preventDefault(); save.mutate(); }}>
          <div className="space-y-1.5"><Label htmlFor="p-name">Nome completo</Label><Input id="p-name" data-testid="profile-name-input" value={form.name} onChange={(e) => setF({ ...form, name: e.target.value })} className="rounded-xl" /></div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5"><Label>E-mail</Label><Input value={u.email} disabled className="rounded-xl" /></div>
          </div>
          <div className="space-y-1.5"><Label>Meu curso</Label>
            <NativeSelect testId="profile-course-select" value={form.course_id} onChange={(v) => setF({ ...form, course_id: v })}>
              <option value="">Selecione</option>{courses.data?.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </NativeSelect>
          </div>
          <div className="space-y-1.5"><Label htmlFor="p-faculty">Minha faculdade</Label><Input id="p-faculty" value={form.faculty} onChange={(e) => setF({ ...form, faculty: e.target.value })} placeholder="Ex.: Universidade Federal..." className="rounded-xl" /></div>
          <div className="space-y-1.5"><Label htmlFor="p-goal">Meta diária de estudo (minutos)</Label><Input id="p-goal" data-testid="profile-goal-input" type="number" min={0} value={form.daily_goal_minutes} onChange={(e) => setF({ ...form, daily_goal_minutes: e.target.value === "" ? "" : Math.max(0, Number(e.target.value)) })} className="rounded-xl" /><p className="text-xs text-slate-500">0 significa sem meta. Não existe limite máximo.</p></div>
          <label className="flex items-start gap-3 rounded-xl border border-slate-200 p-3 text-sm"><input type="checkbox" checked={form.ranking_opt_in} onChange={(e) => setF({ ...form, ranking_opt_in: e.target.checked })} className="mt-1" /><span><b>Participar do ranking</b><span className="block text-xs text-slate-500">Seu nome, curso, faculdade e foto opcional podem aparecer para outros estudantes.</span></span></label>
          <Button type="submit" data-testid="profile-save-button" disabled={save.isPending} className="rounded-xl">Salvar alterações</Button>
        </form>
        <div className="space-y-4">
          <div className="rounded-3xl border border-slate-200 bg-white p-6">
            <p className="text-sm text-slate-500">Conta</p>
            <p data-testid="profile-plan" className="font-heading text-xl font-bold">{isAdmin(u) ? "Administrador" : "Estudante"}</p>
            <p className="mt-3 text-xs text-slate-500">Conta criada em {formatDate(u.created_at)}</p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-white p-6">
            <h2 className="font-semibold">Segurança</h2>
            <form className="mt-4 space-y-3" onSubmit={e=>{e.preventDefault();changePw.mutate()}}>
              <Input type="password" autoComplete="current-password" placeholder="Senha atual" value={pw.current_password} onChange={e=>setPw({...pw,current_password:e.target.value})} required />
              <Input type="password" autoComplete="new-password" placeholder="Nova senha" minLength={8} value={pw.new_password} onChange={e=>setPw({...pw,new_password:e.target.value})} required />
              <Input type="password" autoComplete="new-password" placeholder="Confirmar nova senha" minLength={8} value={pw.new_password_confirm} onChange={e=>setPw({...pw,new_password_confirm:e.target.value})} required />
              <Button type="submit" variant="outline" disabled={changePw.isPending}>{changePw.isPending?"Salvando...":"Alterar senha"}</Button>
            </form>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-white p-6">
            <h2 className="font-semibold">Privacidade e dados</h2>
            <p className="mt-2 text-sm text-slate-500">Você pode solicitar uma cópia dos dados associados à sua conta ou excluir a conta permanentemente.</p>
            <div className="mt-4 flex flex-wrap gap-2"><Button variant="outline" onClick={()=>exportData.mutate()} disabled={exportData.isPending}>{exportData.isPending?"Preparando...":"Exportar meus dados"}</Button><Link to="/politica-de-privacidade" className={buttonVariants({variant:"ghost"})}>Política de privacidade</Link></div>
            <div className="mt-5 rounded-2xl border border-red-200 bg-red-50 p-4">
              <p className="font-semibold text-red-800">Excluir minha conta</p>
              <p className="mt-1 text-xs text-red-700">A exclusão é permanente. Informe sua senha e digite exatamente <b>EXCLUIR MINHA CONTA</b>.</p>
              <div className="mt-3 grid gap-2"><Input type="password" placeholder="Senha atual" autoComplete="current-password" value={deletePw} onChange={e=>setDeletePw(e.target.value)} /><Input placeholder="EXCLUIR MINHA CONTA" value={deleteConfirm} onChange={e=>setDeleteConfirm(e.target.value)} /><Button type="button" variant="destructive" disabled={deleteAccount.isPending || deleteConfirm!=="EXCLUIR MINHA CONTA" || !deletePw} onClick={()=>{if(window.confirm("Excluir sua conta definitivamente? Esta ação não pode ser desfeita.")) deleteAccount.mutate()}}>{deleteAccount.isPending?"Excluindo...":"Excluir conta"}</Button></div>
            </div>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-white p-6">
            <p className="font-semibold">Meus envios</p>
            {mySubs.data?.length === 0 && <p className="text-sm text-slate-500">Nenhum envio. <Link to="/enviar-conteudo" className="text-brand-dark underline">Enviar conteúdo</Link></p>}
            {mySubs.data?.map((s) => <p key={s.id} className="mt-2 flex justify-between text-sm"><span className="truncate">{s.title}</span><Badge variant="secondary">{SUB_STATUS[s.status]}</Badge></p>)}
          </div>
          <div className="flex flex-wrap gap-2">
            {isAdmin(u) && <Link to="/admin" data-testid="profile-admin-link" className={buttonVariants({ variant: "outline", className: "rounded-xl" })}>Painel Admin</Link>}
            <Button variant="outline" data-testid="profile-logout-button" className="rounded-xl" onClick={() => endSession("/")}><LogOut className="size-4" /> Sair</Button>
          </div>
        </div>
      </div>
    </div>
  );
}

export const SUB_STATUS: Record<string, string> = { pendente: "Pendente", em_analise: "Em análise", aprovado: "Aprovado", publicado: "Publicado", rejeitado: "Rejeitado" };

export function SubmitPage() {
  usePageMeta("Enviar conteúdo");
  const qc = useQueryClient();
  const [sel, setSel] = useState<TopicSel>(EMPTY_SEL);
  const [f, setF] = useState<Omit<SubmissionIn, "topic_id">>({ kind: "resumo", title: "", body: "" });
  const send = useMutation({
    mutationFn: () => apiPost<Submission>("/submissions", { ...f, topic_id: sel.topic_id }),
    onSuccess: () => { toast.success("Enviado! Seu conteúdo será analisado pela moderação."); setF({ kind: "resumo", title: "", body: "" }); qc.invalidateQueries({ queryKey: ["my-submissions"] }); },
    onError: (e) => toast.error(errMsg(e)),
  });
  return (
    <div className="animate-fade-up">
      <h1 className="text-3xl font-extrabold tracking-tight">Enviar conteúdo</h1>
      <p className="mt-1 text-slate-600">Compartilhe resumos, questões e materiais. Nada é publicado automaticamente: Pendente → Em análise → Aprovado → Publicado.</p>
      <form className="mt-6 max-w-2xl space-y-4 rounded-3xl border border-slate-200 bg-white p-6" onSubmit={(e) => { e.preventDefault(); send.mutate(); }}>
        <NativeSelect testId="submit-kind-select" value={f.kind} onChange={(v) => setF({ ...f, kind: v as SubmissionIn["kind"] })}>
          <option value="resumo">Resumo</option><option value="questao">Questão</option><option value="material">Material</option>
        </NativeSelect>
        <TopicPicker prefix="submit" value={sel} onChange={setSel} />
        <Input data-testid="submit-title-input" placeholder="Título" value={f.title} onChange={(e) => setF({ ...f, title: e.target.value })} className="rounded-xl" required minLength={3} />
        <Textarea data-testid="submit-body-input" rows={8} placeholder="Conteúdo (cite as fontes utilizadas)" value={f.body} onChange={(e) => setF({ ...f, body: e.target.value })} className="rounded-xl" required minLength={10} />
        <Button type="submit" data-testid="submit-send-button" disabled={send.isPending || !sel.topic_id} className="rounded-xl">Enviar para moderação</Button>
      </form>
    </div>
  );
}
