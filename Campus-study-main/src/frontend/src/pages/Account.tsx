import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Award, Clock, Flame, Lock, LogOut, Target, Trash2 } from "lucide-react";
import { apiGet, apiPost, apiPut, apiDelete, apiUpload, apiAssetUrl } from "@/lib/api";
import { errMsg, isAdmin, useMe, usePageMeta } from "@/lib/hooks";
import { formatDate, minutesLabel } from "@/lib/format";
import { endSession } from "@/lib/session";
import type { Content, Course, Exam, Me, Message, ProgressOut, Submission, SubmissionIn, UserItem } from "@/lib/types";
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

const KIND_LABELS: Record<string, string> = { resumo: "Resumos", mapa: "Mapas mentais", questoes: "Questões", plano: "Planos de estudo", pdf: "PDFs" };

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
  const del = useMutation({
    mutationFn: (id: string) => apiDelete<Message>(`/items/${id}`),
    onSuccess: () => { toast.success("Item excluído."); qc.invalidateQueries({ queryKey: ["items"] }); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const tabs = ["salvos", ...Object.keys(KIND_LABELS), "simulados"];
  const [generator, setGenerator] = useState<TopicSel>(EMPTY_SEL);
  const generate = useMutation({
    mutationFn: () => apiPost<any>(`/ai/topic-pack/${generator.topic_id}`),
    onSuccess: () => { toast.success("Materiais gerados com sucesso."); qc.invalidateQueries({ queryKey: ["items"] }); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const list = (items.data ?? []).filter((i) => i.kind === tab);
  return (
    <div className="animate-fade-up">
      <h1 className="text-3xl font-extrabold tracking-tight">Minha Biblioteca</h1>
      <section className="mt-5 rounded-3xl border border-emerald-200 bg-emerald-50/70 p-4 sm:p-5">
        <div>
          <h2 className="text-lg font-bold text-emerald-950">Biblioteca automática</h2>
          <p className="mt-1 text-sm text-emerald-800">Escolha Curso → Período → Disciplina → Assunto e gere materiais automaticamente.</p>
        </div>
        <div className="mt-4"><TopicPicker value={generator} onChange={setGenerator} prefix="library-generator" /></div>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <Button onClick={() => generate.mutate()} disabled={!generator.topic_id || generate.isPending}>
            {generate.isPending ? "Gerando materiais..." : "Gerar materiais"}
          </Button>
          {generate.isPending && <span className="text-xs text-emerald-800">Aguarde; o processamento pode levar alguns instantes.</span>}
        </div>
      </section>
      <div className="no-scrollbar -mx-4 mt-5 flex gap-2 overflow-x-auto px-4">
        {tabs.map((t) => (
          <button key={t} data-testid={`library-tab-${t}`} onClick={() => setTab(t)}
            className={cn("shrink-0 rounded-full border px-4 py-2 text-sm font-medium transition-colors", tab === t ? "border-brand bg-brand text-white" : "border-slate-200 bg-white text-slate-600")}>
            {t === "salvos" ? "Materiais salvos" : t === "simulados" ? "Simulados" : KIND_LABELS[t]}
          </button>
        ))}
      </div>
      <div className="mt-6">
        {tab === "salvos" ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {favs.data?.length === 0 && <p className="text-sm text-slate-500">Você ainda não salvou materiais. Toque no ícone de marcador em qualquer videoaula ou artigo.</p>}
            {favs.data?.map((c) => <ContentCard key={c.id} c={c} saved />)}
          </div>
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
  const p = q.isError ? undefined : q.data;
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
        <div className="flex flex-wrap items-end justify-between gap-3"><div><h2 className="text-xl font-bold">Calendário de estudos</h2><p className="text-sm text-slate-500">Quanto mais intenso o estudo do dia, maior o preenchimento.</p></div><div className="text-sm font-semibold text-brand-dark">{p?.month_study_days ?? 0} dias estudados no mês</div></div>
        <div className="mt-5 grid grid-cols-5 gap-2 sm:grid-cols-10">{p?.month.map((d) => <div key={d.date} title={`${new Date(`${d.date}T12:00:00`).toLocaleDateString("pt-BR")}: ${d.minutes} min`} className="flex aspect-square items-end rounded-md bg-slate-100 p-1"><div className="w-full rounded-sm bg-brand transition-all" style={{height:`${Math.max(8,(d.minutes/monthMax)*100)}%`,opacity:d.minutes?0.35+Math.min(0.65,d.minutes/Math.max(monthMax,1)):0.08}} /></div>)}</div>
      </div>
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
            <div className="space-y-1.5"><Label>CPF</Label><Input data-testid="profile-cpf-masked" value={u.cpf_masked} disabled className="rounded-xl" /></div>
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
      <p className="mt-1 text-slate-600">Compartilhe resumos, mapas mentais, questões e materiais. Nada é publicado automaticamente: Pendente → Em análise → Aprovado → Publicado.</p>
      <form className="mt-6 max-w-2xl space-y-4 rounded-3xl border border-slate-200 bg-white p-6" onSubmit={(e) => { e.preventDefault(); send.mutate(); }}>
        <NativeSelect testId="submit-kind-select" value={f.kind} onChange={(v) => setF({ ...f, kind: v as SubmissionIn["kind"] })}>
          <option value="resumo">Resumo</option><option value="mapa">Mapa mental</option><option value="questao">Questão</option><option value="material">Material</option>
        </NativeSelect>
        <TopicPicker prefix="submit" value={sel} onChange={setSel} />
        <Input data-testid="submit-title-input" placeholder="Título" value={f.title} onChange={(e) => setF({ ...f, title: e.target.value })} className="rounded-xl" required minLength={3} />
        <Textarea data-testid="submit-body-input" rows={8} placeholder="Conteúdo (cite as fontes utilizadas)" value={f.body} onChange={(e) => setF({ ...f, body: e.target.value })} className="rounded-xl" required minLength={10} />
        <Button type="submit" data-testid="submit-send-button" disabled={send.isPending || !sel.topic_id} className="rounded-xl">Enviar para moderação</Button>
      </form>
    </div>
  );
}
