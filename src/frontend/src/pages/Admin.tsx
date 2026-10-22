import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Archive, CheckCircle2, Edit3, Eye, EyeOff, Link2, Loader2, Lock, Pause, Play, Plus, RefreshCw, Search, ShieldCheck, Trash2, X } from "lucide-react";
import { apiDelete, apiGet, apiPatch, apiPost, apiPut, apiUpload } from "@/lib/api";
import { errMsg, isAdmin, useMe, usePageMeta } from "@/lib/hooks";
import { beginSession } from "@/lib/session";
import { queryClient } from "@/lib/queryClient";
import type { Me } from "@/lib/types";
import { DIFF_LABELS, STATUS_LABELS, TYPE_LABELS, TYPE_PLURAL, formatDate, mindToText, textToMind } from "@/lib/format";
import type {
  AdminLog, AdminStats, AdminUser, Content, ContentIn, ContentPage, ContentType, Course, Discipline,
  Message, Period, Settings, Status, Submission, SubmissionStatus, Topic, AdminStudent, SupportTicket, SystemStatus,
} from "@/lib/types";
import { NativeSelect } from "@/components/SelectField";
import { EMPTY_SEL, TopicPicker, type TopicSel } from "@/components/TopicPicker";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { cn } from "@/lib/utils";

const SECTIONS = [
  ["painel", "Painel"], ["estrutura", "Cursos & estrutura"], ["importar", "Importar conteúdo"], ["videos", "Videoaulas"], ["conteudos", "Conteúdos"],
  ["usuarios", "Usuários"], ["moderacao", "Moderação"], ["suporte", "Suporte"], ["status", "Status"],
  ["pagamentos", "Pagamentos"], ["logs", "Logs"], ["config", "Configurações"], ["editor", "Editor do site"],
] as const;

const SUB_STATUS: Record<SubmissionStatus, string> = {
  pendente: "Pendente",
  em_analise: "Em análise",
  aprovado: "Aprovado",
  publicado: "Publicado",
  rejeitado: "Rejeitado",
};

function useInvalidate() {
  const qc = useQueryClient();
  return (...keys: string[]) => keys.forEach((k) => qc.invalidateQueries({ queryKey: [k] }));
}

function Stat({ label, value }: { label: string; value: number | string }) {
  return <div className="rounded-2xl border border-slate-200 bg-white p-4"><p className="font-heading text-2xl font-bold">{value}</p><p className="text-xs text-slate-500">{label}</p></div>;
}

function Dashboard() {
  const s = useQuery({ queryKey: ["admin-stats"], queryFn: () => apiGet<AdminStats>("/admin/stats") }).data;
  if (!s) return null;
  const t = s.contents_by_type;
  return (
    <div className="space-y-6">
      <div data-testid="admin-stats" className="grid grid-cols-2 gap-3 md:grid-cols-4 lg:grid-cols-6">
        {([["Usuários", s.users], ["Ativos (30 dias)", s.active_users], ["Cursos", s.courses], ["Períodos", s.periods],
          ["Disciplinas", s.disciplines], ["Assuntos", s.topics], ["Videoaulas", t.video ?? 0], ["Artigos", t.artigo ?? 0], ["Questões", t.questao ?? 0],
          ["Resumos", t.resumo ?? 0], ["PDFs", t.pdf ?? 0], ["Livros", t.livro ?? 0], ["Materiais", t.material ?? 0],
          ["Simulados realizados", s.exams], ["Envios pendentes", s.pending_submissions]] as [string, number][]).map(([l, v]) => <Stat key={l} label={l} value={v} />)}
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-white p-5"><h3 className="font-bold">Pesquisas mais realizadas</h3>
          {s.top_searches.length === 0 && <p className="mt-2 text-sm text-slate-500">Sem dados ainda.</p>}
          {s.top_searches.map((x) => <p key={x.label} className="mt-2 flex justify-between text-sm"><span>{x.label}</span><strong>{x.count}</strong></p>)}
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-5"><h3 className="font-bold">Conteúdos mais acessados</h3>
          {s.top_contents.length === 0 && <p className="mt-2 text-sm text-slate-500">Sem dados ainda.</p>}
          {s.top_contents.map((x) => <p key={x.id} className="mt-2 flex justify-between gap-2 text-sm"><span className="truncate">{x.title}</span><strong>{x.views}</strong></p>)}
        </div>
      </div>
    </div>
  );
}

// ---------- hierarchy ----------
type Entity = "courses" | "periods" | "disciplines" | "topics";
interface EditState { entity: Entity; id?: string; name: string; description: string; status: Status; num_periods: number | string; number: number | string }

function Structure() {
  const inv = useInvalidate();
  const [courseId, setCourseId] = useState("");
  const [periodId, setPeriodId] = useState("");
  const [discId, setDiscId] = useState("");
  const [edit, setEdit] = useState<EditState | null>(null);
  const courses = useQuery({ queryKey: ["admin-courses"], queryFn: () => apiGet<Course[]>("/admin/courses") });
  const periods = useQuery({ queryKey: ["admin-periods", courseId], enabled: !!courseId, queryFn: () => apiGet<Period[]>(`/admin/periods?course_id=${courseId}`) });
  const discs = useQuery({ queryKey: ["a-discs", periodId], enabled: !!periodId, queryFn: () => apiGet<Discipline[]>(`/admin/disciplines?period_id=${periodId}`) });
  const topics = useQuery({ queryKey: ["a-topics", discId], enabled: !!discId, queryFn: () => apiGet<Topic[]>(`/admin/topics?discipline_id=${discId}`) });
  const refresh = () => inv("admin-courses", "admin-periods", "a-discs", "a-topics", "courses", "course", "f-periods", "f-discs", "f-topics");
  const save = useMutation({
    mutationFn: (e: EditState) => {
      const body = e.entity === "courses" ? { name: e.name, description: e.description, icon: "GraduationCap", num_periods: Number(e.num_periods), status: e.status }
        : e.entity === "periods" ? { course_id: courseId, number: Number(e.number), name: e.name }
        : e.entity === "disciplines" ? { period_id: periodId, name: e.name, description: e.description, status: e.status }
        : { discipline_id: discId, name: e.name, description: e.description, status: e.status };
      return e.id ? apiPut(`/admin/${e.entity}/${e.id}`, body) : apiPost(`/admin/${e.entity}`, body);
    },
    onSuccess: () => { toast.success("Salvo."); setEdit(null); refresh(); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const del = useMutation({
    mutationFn: ({ entity, id }: { entity: Entity; id: string }) => apiDelete<Message>(`/admin/${entity}/${id}`),
    onSuccess: (r) => { toast.success(r.message); refresh(); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const blank = (entity: Entity): EditState => ({ entity, name: "", description: "", status: "publicado", num_periods: 8, number: (periods.data?.length ?? 0) + 1 });
  const Col = ({ title, entity, items, selected, onSelect, canAdd }: {
    title: string; entity: Entity; items: { id: string; name: string; status?: Status; sub?: string; raw: EditState }[];
    selected: string; onSelect?: (id: string) => void; canAdd: boolean;
  }) => (
    <div className="rounded-2xl border border-slate-200 bg-white p-3">
      <div className="mb-2 flex items-center justify-between"><h3 className="font-bold">{title}</h3>
        {canAdd && <Button size="sm" variant="outline" data-testid={`admin-add-${entity}`} onClick={() => setEdit(blank(entity))}><Plus className="size-3.5" /></Button>}
      </div>
      <div className="max-h-[28rem] space-y-1 overflow-y-auto">
        {!canAdd && <p className="p-2 text-xs text-slate-400">Selecione o nível anterior.</p>}
        {items.map((it) => (
          <div key={it.id} className={cn("group flex items-center gap-1 rounded-lg px-2 py-1.5 text-sm", selected === it.id ? "bg-brand-soft" : "hover:bg-slate-50")}>
            <button data-testid={`admin-${entity}-item-${it.id}`} onClick={() => onSelect?.(it.id)} className="min-w-0 flex-1 truncate text-left">
              {it.name} {it.status && it.status !== "publicado" && <span className="text-xs text-amber-600">({STATUS_LABELS[it.status]})</span>}
              {it.sub && <span className="block text-xs text-slate-400">{it.sub}</span>}
            </button>
            <button aria-label="Editar" onClick={() => setEdit(it.raw)} className="p-1 text-slate-400 hover:text-slate-700"><Edit3 className="size-3.5" /></button>
            <button aria-label="Excluir" onClick={() => confirm(`Excluir "${it.name}"?`) && del.mutate({ entity, id: it.id })} className="p-1 text-slate-400 hover:text-red-600"><Trash2 className="size-3.5" /></button>
          </div>
        ))}
      </div>
    </div>
  );
  return (
    <>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <Col title="Cursos" entity="courses" canAdd selected={courseId} onSelect={(id) => { setCourseId(id); setPeriodId(""); setDiscId(""); }}
          items={(courses.data ?? []).map((c) => ({ id: c.id, name: c.name, status: c.status, sub: `${c.num_periods} períodos`, raw: { entity: "courses", id: c.id, name: c.name, description: c.description, status: c.status, num_periods: c.num_periods, number: 1 } }))} />
        <Col title="Períodos" entity="periods" canAdd={!!courseId} selected={periodId} onSelect={(id) => { setPeriodId(id); setDiscId(""); }}
          items={(periods.data ?? []).map((p) => ({ id: p.id, name: p.name, raw: { entity: "periods", id: p.id, name: p.name, description: "", status: "publicado", num_periods: 0, number: p.number } }))} />
        <Col title="Disciplinas" entity="disciplines" canAdd={!!periodId} selected={discId} onSelect={setDiscId}
          items={(discs.data ?? []).map((d) => ({ id: d.id, name: d.name, status: d.status, raw: { entity: "disciplines", id: d.id, name: d.name, description: d.description, status: d.status, num_periods: 0, number: 0 } }))} />
        <Col title="Assuntos" entity="topics" canAdd={!!discId} selected=""
          items={(topics.data ?? []).map((t) => ({ id: t.id, name: t.name, status: t.status, raw: { entity: "topics", id: t.id, name: t.name, description: t.description, status: t.status, num_periods: 0, number: 0 } }))} />
      </div>
      <Dialog open={!!edit} onOpenChange={(o) => !o && setEdit(null)}>
        <DialogContent>
          <DialogHeader><DialogTitle>{edit?.id ? "Editar" : "Adicionar"} {edit && { courses: "curso", periods: "período", disciplines: "disciplina", topics: "assunto" }[edit.entity]}</DialogTitle></DialogHeader>
          {edit && (
            <form className="space-y-3" onSubmit={(e) => { e.preventDefault(); save.mutate(edit); }}>
              {edit.entity === "periods" ? (
                <>
                  <Label>Número</Label><Input data-testid="admin-entity-number-input" type="number" min={1} max={16} value={edit.number} onChange={(e) => setEdit({ ...edit, number: e.target.value })} />
                  <Label>Nome (opcional)</Label><Input data-testid="admin-entity-name-input" placeholder={`${edit.number}º período`} value={edit.name} onChange={(e) => setEdit({ ...edit, name: e.target.value })} />
                </>
              ) : (
                <>
                  <Label>Nome</Label><Input data-testid="admin-entity-name-input" required value={edit.name} onChange={(e) => setEdit({ ...edit, name: e.target.value })} />
                  <Label>Descrição</Label><Textarea data-testid="admin-entity-description-input" value={edit.description} onChange={(e) => setEdit({ ...edit, description: e.target.value })} />
                  {edit.entity === "courses" && (<><Label>Quantidade de períodos</Label><Input data-testid="admin-entity-periods-input" type="number" min={1} max={16} value={edit.num_periods} onChange={(e) => setEdit({ ...edit, num_periods: e.target.value })} /></>)}
                  <Label>Status</Label>
                  <NativeSelect testId="admin-entity-status-select" value={edit.status} onChange={(v) => setEdit({ ...edit, status: v as Status })}>
                    {Object.entries(STATUS_LABELS).map(([k, l]) => <option key={k} value={k}>{l}</option>)}
                  </NativeSelect>
                </>
              )}
              <Button type="submit" data-testid="admin-entity-save-button" disabled={save.isPending} className="w-full">Salvar</Button>
            </form>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}

// ---------- contents ----------
interface Form { id?: string; sel: TopicSel; c: ContentIn; tags: string; optionsText: string; mindText: string }

const LINK_BADGE: Record<string, [string, string]> = { funcionando: ["🟢 Funcionando", "bg-green-100 text-green-800"], indisponivel: ["🔴 Indisponível", "bg-red-100 text-red-800"], verificar: ["🟡 Precisa verificar", "bg-amber-100 text-amber-800"] };

function newForm(type: ContentType): Form {
  return { sel: EMPTY_SEL, tags: "", optionsText: "", mindText: "Tema central\n  Conceito principal\n  Aplicações",
    c: { type, title: "", description: "", topic_id: "", tags: [], difficulty: "", status: "publicado", data: type === "questao" ? { correct_index: 0 } : {} } };
}

function ContentsAdmin({ videosOnly }: { videosOnly: boolean }) {
  const inv = useInvalidate();
  const [type, setType] = useState<string>(videosOnly ? "video" : "");
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");
  const [link, setLink] = useState("");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<string[]>([]);
  const [form, setForm] = useState<Form | null>(null);
  const t = videosOnly ? "video" : type;
  const params = `type=${t}&q=${encodeURIComponent(q)}&status=${status}&link_status=${link}&page=${page}`;
  const list = useQuery({ queryKey: ["admin-contents", params], queryFn: () => apiGet<ContentPage>(`/admin/contents?${params}`) });
  const refresh = () => inv("admin-contents", "admin-stats", "topic", "home", "search");
  const save = useMutation({
    mutationFn: (f: Form) => {
      const data = { ...f.c.data };
      if (f.c.type === "questao") data.options = f.optionsText.split("\n").map((s) => s.trim()).filter(Boolean);
      if (f.c.type === "mapa") data.root = textToMind(f.mindText);
      const body: ContentIn = { ...f.c, topic_id: f.sel.topic_id || f.c.topic_id, tags: f.tags.split(",").map((s) => s.trim()).filter(Boolean), data };
      return f.id ? apiPut<Content>(`/admin/contents/${f.id}`, body) : apiPost<Content>("/admin/contents", body);
    },
    onSuccess: () => { toast.success("Conteúdo salvo."); setForm(null); refresh(); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const upload = useMutation({
    mutationFn: (file: File) => { const fd = new FormData(); fd.append("file", file); return apiUpload<{ url: string; name: string }>("/admin/uploads", fd); },
    onSuccess: (r) => { setForm((current) => current ? { ...current, c: { ...current.c, data: { ...current.c.data, pdf_url: r.url, file_name: r.name } } } : current); toast.success("PDF enviado com sucesso."); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const del = useMutation({ mutationFn: (id: string) => apiDelete<Message>(`/admin/contents/${id}`), onSuccess: (r) => { toast.success(r.message); refresh(); }, onError: (e) => toast.error(errMsg(e)) });
  const bulkDel = useMutation({
    mutationFn: (ids: string[]) => apiPost<Message>("/admin/contents/bulk-delete", { ids }),
    onSuccess: (r) => { toast.success(r.message); setSelected([]); refresh(); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const bulkDelAll = useMutation({
    mutationFn: () => apiPost<Message>("/admin/contents/bulk-delete-all", { type: t, q, status, link_status: link }),
    onSuccess: (r) => { toast.success(r.message); setSelected([]); setPage(1); refresh(); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const setStatusM = useMutation({
    mutationFn: ({ id, s }: { id: string; s: Status }) => apiPatch<Message>(`/admin/contents/${id}/status`, { status: s }),
    onSuccess: (r) => { toast.success(r.message); refresh(); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const check = useMutation({ mutationFn: (id: string) => apiPost<Message>(`/admin/contents/${id}/check-link`), onSuccess: (r) => { toast.info(r.message); refresh(); }, onError: (e) => toast.error(errMsg(e)) });
  const checkAll = useMutation({ mutationFn: () => apiPost<Message>("/admin/videos/check-all"), onSuccess: (r) => { toast.info(r.message); refresh(); }, onError: (e) => toast.error(errMsg(e)) });
  const edit = (c: Content) => setForm({ id: c.id, sel: { ...EMPTY_SEL, topic_id: c.topic_id }, tags: c.tags.join(", "), optionsText: (c.data.options ?? []).join("\n"), mindText: c.data.root ? mindToText(c.data.root) : "Tema central\n  Conceito principal\n  Aplicações",
    c: { type: c.type, title: c.title, description: c.description, topic_id: c.topic_id, tags: c.tags, difficulty: c.difficulty, status: c.status, data: c.data } });
  const setData = (k: string, v: string | number) => form && setForm({ ...form, c: { ...form.c, data: { ...form.c.data, [k]: v } } });
  const fieldsFor: Record<ContentType, [string, string, boolean?][]> = {
    video: [["url", "URL do YouTube *"], ["channel", "Canal"], ["thumbnail", "Thumbnail (opcional — gerada automaticamente)"]],
    pdf: [["pdf_url", "URL do PDF *"], ["file_name", "Nome do arquivo"]],
    livro: [["authors", "Autor(es)"], ["year", "Ano"], ["publisher", "Editora"], ["isbn", "ISBN"], ["url", "Link do livro (opcional)"], ["description", "Descrição / referência", true]],
    artigo: [["authors", "Autores *"], ["year", "Ano"], ["journal", "Revista / fonte"], ["doi", "DOI"], ["url", "URL"], ["abstract", "Resumo", true], ["keywords", "Palavras-chave"]],
    resumo: [["body", "Texto do resumo (Markdown)", true]], material: [["body", "Conteúdo (Markdown)", true], ["url", "Link (opcional)"]],
    questao: [["statement", "Enunciado", true], ["explanation", "Explicação", true]],
    mapa: [],
  };
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        {!videosOnly && (
          <NativeSelect testId="admin-content-type-filter" className="w-44" value={type} onChange={(v) => { setType(v); setPage(1); setSelected([]); }}>
            <option value="">Todos os tipos</option>{(Object.keys(TYPE_PLURAL) as ContentType[]).map((k) => <option key={k} value={k}>{TYPE_PLURAL[k]}</option>)}
          </NativeSelect>
        )}
        <NativeSelect testId="admin-content-status-filter" className="w-40" value={status} onChange={(v) => { setStatus(v); setPage(1); setSelected([]); }}>
          <option value="">Todos os status</option>{Object.entries(STATUS_LABELS).map(([k, l]) => <option key={k} value={k}>{l}</option>)}
        </NativeSelect>
        {videosOnly && (
          <NativeSelect testId="admin-video-link-filter" className="w-48" value={link} onChange={(v) => { setLink(v); setPage(1); setSelected([]); }}>
            <option value="">Todos os links</option>{Object.entries(LINK_BADGE).map(([k, [l]]) => <option key={k} value={k}>{l}</option>)}
          </NativeSelect>
        )}
        <div className="relative min-w-48 flex-1"><Search className="absolute top-3 left-3 size-4 text-slate-400" />
          <Input data-testid="admin-content-search-input" placeholder="Buscar por título, URL ou assunto" value={q} onChange={(e) => { setQ(e.target.value); setPage(1); setSelected([]); }} className="h-10 pl-9" />
        </div>
        {videosOnly && <Button variant="outline" data-testid="admin-check-all-videos" onClick={() => checkAll.mutate()} disabled={checkAll.isPending}><RefreshCw className={cn("size-4", checkAll.isPending && "animate-spin")} /> Verificar todos</Button>}
        {list.data?.items.length ? <label className="inline-flex h-10 items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 text-sm font-medium">
          <input type="checkbox" aria-label="Selecionar todos os conteúdos desta página" checked={list.data.items.every((c) => selected.includes(c.id))} onChange={(e) => setSelected(e.target.checked ? list.data!.items.map((c) => c.id) : [])} />
          Selecionar todos
        </label> : null}
        {selected.length > 0 && <Button variant="outline" className="text-red-600" disabled={bulkDel.isPending} onClick={() => confirm(`Excluir definitivamente ${selected.length} conteúdo(s) selecionado(s)?`) && bulkDel.mutate(selected)}><Trash2 className="size-4" /> Excluir selecionados ({selected.length})</Button>}
        {list.data && list.data.total > 0 && <Button variant="outline" className="text-red-600" disabled={bulkDelAll.isPending} onClick={() => confirm(`ATENÇÃO: excluir definitivamente todos os ${list.data!.total} conteúdos encontrados com os filtros atuais?`) && bulkDelAll.mutate()}><Trash2 className="size-4" /> Excluir todos ({list.data.total})</Button>}
        <Button data-testid="admin-add-content-button" onClick={() => setForm(newForm(videosOnly ? "video" : (type as ContentType) || "resumo"))}><Plus className="size-4" /> {videosOnly ? "Adicionar videoaula" : "Adicionar conteúdo"}</Button>
      </div>
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
        <Table>
          <TableHeader><TableRow><TableHead className="w-10" /> <TableHead>Título</TableHead><TableHead>Tipo</TableHead><TableHead>Assunto</TableHead><TableHead>Status</TableHead>{videosOnly && <TableHead>Link</TableHead>}<TableHead className="text-right">Ações</TableHead></TableRow></TableHeader>
          <TableBody>
            {list.data?.items.length === 0 && <TableRow><TableCell colSpan={videosOnly ? 7 : 6} className="py-8 text-center text-slate-500">Nenhum conteúdo encontrado.</TableCell></TableRow>}
            {list.data?.items.map((c) => (
              <TableRow key={c.id} data-testid={`admin-content-row-${c.id}`}>
                <TableCell className="w-10"><input type="checkbox" aria-label={`Selecionar ${c.title}`} checked={selected.includes(c.id)} onChange={(e) => setSelected((prev) => e.target.checked ? [...prev, c.id] : prev.filter((id) => id !== c.id))} /></TableCell>
                <TableCell className="max-w-xs truncate font-medium">{c.title}</TableCell>
                <TableCell>{TYPE_LABELS[c.type]}</TableCell>
                <TableCell className="max-w-40 truncate text-xs text-slate-500">{c.course_name} · {c.topic_name}</TableCell>
                <TableCell><Badge variant="secondary">{STATUS_LABELS[c.status]}</Badge></TableCell>
                {videosOnly && <TableCell><span className={cn("rounded-md px-2 py-0.5 text-xs font-medium", LINK_BADGE[c.data.link_status ?? "verificar"][1])}>{LINK_BADGE[c.data.link_status ?? "verificar"][0]}</span></TableCell>}
                <TableCell className="text-right whitespace-nowrap">
                  {c.type === "video" && <Button size="icon-sm" variant="ghost" title="Verificar link" onClick={() => check.mutate(c.id)}><Link2 className="size-4" /></Button>}
                  <Button size="icon-sm" variant="ghost" title={c.type === "video" ? "Editar / substituir link" : "Editar"} data-testid={`admin-content-edit-${c.id}`} onClick={() => edit(c)}><Edit3 className="size-4" /></Button>
                  {c.status === "publicado"
                    ? <Button size="icon-sm" variant="ghost" title="Despublicar" onClick={() => setStatusM.mutate({ id: c.id, s: "rascunho" })}><EyeOff className="size-4" /></Button>
                    : <Button size="icon-sm" variant="ghost" title="Publicar" onClick={() => setStatusM.mutate({ id: c.id, s: "publicado" })}><Eye className="size-4" /></Button>}
                  <Button size="icon-sm" variant="ghost" title="Arquivar" onClick={() => setStatusM.mutate({ id: c.id, s: "arquivado" })}><Archive className="size-4" /></Button>
                  <Button size="icon-sm" variant="ghost" title="Excluir" data-testid={`admin-content-delete-${c.id}`} onClick={() => confirm("Excluir definitivamente?") && del.mutate(c.id)}><Trash2 className="size-4 text-red-500" /></Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      {list.data && list.data.pages > 1 && (
        <div className="flex items-center justify-center gap-3 text-sm">
          <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>Anterior</Button> Página {page} de {list.data.pages}
          <Button variant="outline" size="sm" disabled={page >= list.data.pages} onClick={() => setPage(page + 1)}>Próxima</Button>
        </div>
      )}
      <Dialog open={!!form} onOpenChange={(o) => !o && setForm(null)}>
        <DialogContent className="max-h-[92vh] overflow-y-auto sm:max-w-2xl">
          <DialogHeader><DialogTitle>{form?.id ? "Editar" : "Adicionar"} {form && TYPE_LABELS[form.c.type].toLowerCase()}</DialogTitle></DialogHeader>
          {form && (
            <form className="space-y-3" onSubmit={(e) => { e.preventDefault(); save.mutate(form); }}>
              {!form.id && !videosOnly && (
                <NativeSelect testId="admin-content-type-select" value={form.c.type} onChange={(v) => setForm(newForm(v as ContentType))}>
                  {(Object.keys(TYPE_LABELS) as ContentType[]).map((k) => <option key={k} value={k}>{TYPE_LABELS[k]}</option>)}
                </NativeSelect>
              )}
              {form.id && form.c.topic_id && !form.sel.discipline_id && <p className="text-xs text-slate-500">Assunto atual mantido. Selecione abaixo apenas para mover o conteúdo.</p>}
              <TopicPicker admin prefix="admin-content" value={form.sel} onChange={(sel) => setForm({ ...form, sel })} />
              <Input data-testid="admin-content-title-input" required placeholder="Título *" value={form.c.title} onChange={(e) => setForm({ ...form, c: { ...form.c, title: e.target.value } })} />
              <Textarea data-testid="admin-content-description-input" placeholder="Descrição" value={form.c.description} onChange={(e) => setForm({ ...form, c: { ...form.c, description: e.target.value } })} />
              {fieldsFor[form.c.type].map(([k, l, long]) => long
                ? <Textarea key={k} data-testid={`admin-content-field-${k}`} rows={5} placeholder={l} value={String((form.c.data as Record<string, unknown>)[k] ?? "")} onChange={(e) => setData(k, e.target.value)} />
                : <Input key={k} data-testid={`admin-content-field-${k}`} placeholder={l} value={String((form.c.data as Record<string, unknown>)[k] ?? "")} onChange={(e) => setData(k, e.target.value)} />)}
              {form.c.type === "pdf" && (
                <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-3">
                  <Label>Ou envie o PDF diretamente</Label>
                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    <Input type="file" accept="application/pdf,.pdf" disabled={upload.isPending} onChange={(e) => { const file = e.target.files?.[0]; if (file) upload.mutate(file); }} />
                    {upload.isPending && <Loader2 className="size-4 animate-spin" />}
                  </div>
                  <p className="mt-1 text-xs text-slate-500">Até 20 MB. O arquivo é armazenado no banco de dados do projeto.</p>
                </div>
              )}
              {form.c.type === "questao" && (
                <>
                  <Textarea data-testid="admin-content-options-input" rows={5} placeholder="Alternativas (uma por linha)" value={form.optionsText} onChange={(e) => setForm({ ...form, optionsText: e.target.value })} />
                  <NativeSelect testId="admin-content-correct-select" value={String(form.c.data.correct_index ?? 0)} onChange={(v) => setData("correct_index", Number(v))}>
                    {form.optionsText.split("\n").filter((s) => s.trim()).map((o, i) => <option key={i} value={i}>Correta: {String.fromCharCode(65 + i)}) {o.slice(0, 50)}</option>)}
                  </NativeSelect>
                </>
              )}
              {form.c.type === "mapa" && <Textarea data-testid="admin-content-mind-input" rows={10} className="font-mono text-sm" placeholder="Tema central\n  Ramo principal\n    Subramo" value={form.mindText} onChange={(e) => setForm({ ...form, mindText: e.target.value })} />}
              <Input data-testid="admin-content-tags-input" placeholder="Tags (separadas por vírgula)" value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })} />
              <div className="grid grid-cols-2 gap-2">
                <NativeSelect testId="admin-content-difficulty-select" value={form.c.difficulty} onChange={(v) => setForm({ ...form, c: { ...form.c, difficulty: v as ContentIn["difficulty"] } })}>
                  {Object.entries(DIFF_LABELS).map(([k, l]) => <option key={k} value={k}>{k ? `Dificuldade: ${l}` : "Sem dificuldade"}</option>)}
                </NativeSelect>
                <NativeSelect testId="admin-content-status-select" value={form.c.status} onChange={(v) => setForm({ ...form, c: { ...form.c, status: v as Status } })}>
                  {Object.entries(STATUS_LABELS).map(([k, l]) => <option key={k} value={k}>{l}</option>)}
                </NativeSelect>
              </div>
              {(form.c.type === "video" || form.c.type === "pdf" || form.c.type === "livro" || form.c.type === "artigo") && <p className="text-xs text-amber-700">Cadastre somente links e referências reais e verificados. Nunca invente URLs, autores ou DOIs.</p>}
              <Button type="submit" data-testid="admin-content-save-button" disabled={save.isPending || (!form.sel.topic_id && !form.c.topic_id)} className="w-full">Salvar</Button>
            </form>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

function Users() {
  const inv = useInvalidate();
  const [q, setQ] = useState("");
  const users = useQuery({ queryKey: ["admin-users", q], queryFn: () => apiGet<AdminUser[]>(`/admin/users?q=${encodeURIComponent(q)}`) });
  const patch = useMutation({ mutationFn: ({ id, body }: { id: string; body: Record<string, string> }) => apiPatch<Message>(`/admin/users/${id}`, body),
    onSuccess: (r) => { toast.success(r.message); inv("admin-users"); }, onError: (e) => toast.error(errMsg(e)) });
  return (
    <div className="space-y-3">
      <Input data-testid="admin-users-search" placeholder="Buscar por nome" value={q} onChange={(e) => setQ(e.target.value)} className="max-w-sm" />
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
        <Table>
          <TableHeader><TableRow><TableHead>Nome</TableHead><TableHead>E-mail</TableHead><TableHead>Função</TableHead><TableHead>Plano</TableHead><TableHead>Status</TableHead><TableHead>Criado</TableHead><TableHead /></TableRow></TableHeader>
          <TableBody>
            {users.data?.map((u) => (
              <TableRow key={u.id} data-testid={`admin-user-row-${u.id}`}>
                <TableCell className="font-medium">{u.name}</TableCell><TableCell className="text-xs">{u.email_masked}</TableCell>
                <TableCell>
                  <select data-testid={`admin-user-role-${u.id}`} value={u.role} onChange={(e) => patch.mutate({ id: u.id, body: { role: e.target.value } })} className="rounded-md border border-slate-200 bg-white px-1 py-0.5 text-xs">
                    {["student", "admin", "moderator", "editor", "superadmin"].map((r) => <option key={r} value={r}>{r}</option>)}
                  </select>
                </TableCell>
                <TableCell>
                  <select data-testid={`admin-user-plan-${u.id}`} value={u.plan ?? "limitado"} onChange={(e) => patch.mutate({ id: u.id, body: { plan: e.target.value } })} className="rounded-md border border-slate-200 bg-white px-1 py-0.5 text-xs">
                    <option value="limitado">Plano Limitado</option><option value="ilimitado">Plano Ilimitado</option>
                  </select>
                </TableCell>
                <TableCell><Badge variant={u.status === "bloqueado" ? "destructive" : "outline"}>{u.status === "bloqueado" ? "Bloqueado" : "Ativo"}</Badge></TableCell>
                <TableCell className="text-xs">{formatDate(u.created_at)}</TableCell>
                <TableCell>
                  <Button size="sm" variant="outline" data-testid={`admin-user-toggle-${u.id}`} onClick={() => patch.mutate({ id: u.id, body: { status: u.status === "bloqueado" ? "ativo" : "bloqueado" } })}>
                    {u.status === "bloqueado" ? "Desbloquear" : "Bloquear"}
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

function Moderation() {
  const inv = useInvalidate();
  const [status, setStatus] = useState("");
  const list = useQuery({ queryKey: ["admin-subm", status], queryFn: () => apiGet<Submission[]>(`/admin/submissions?status=${status}`) });
  const patch = useMutation({ mutationFn: ({ id, s }: { id: string; s: SubmissionStatus }) => apiPatch<Message>(`/admin/submissions/${id}`, { status: s, reviewer_note: "" }),
    onSuccess: (r) => { toast.success(r.message); inv("admin-subm", "admin-stats", "admin-contents"); }, onError: (e) => toast.error(errMsg(e)) });
  return (
    <div className="space-y-3">
      <NativeSelect testId="admin-moderation-filter" className="max-w-xs" value={status} onChange={setStatus}>
        <option value="">Todos</option>{Object.entries(SUB_STATUS).map(([k, l]) => <option key={k} value={k}>{l}</option>)}
      </NativeSelect>
      {list.data?.length === 0 && <p className="text-sm text-slate-500">Nenhum envio.</p>}
      {list.data?.map((s) => (
        <div key={s.id} data-testid={`admin-submission-${s.id}`} className="rounded-2xl border border-slate-200 bg-white p-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="font-semibold">{s.title} <span className="text-xs font-normal text-slate-500">· {s.kind} · {s.topic_name} · por {s.user_name}</span></p>
            <Badge variant="secondary">{SUB_STATUS[s.status]}</Badge>
          </div>
          <p className="mt-2 line-clamp-4 text-sm whitespace-pre-wrap text-slate-600">{s.body}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {(["em_analise", "aprovado", "publicado", "rejeitado"] as SubmissionStatus[]).map((st) => (
              <Button key={st} size="sm" variant={st === "publicado" ? "default" : "outline"} data-testid={`admin-submission-${st}-${s.id}`} disabled={s.status === st || s.status === "publicado"} onClick={() => patch.mutate({ id: s.id, s: st })}>
                {st === "publicado" && <CheckCircle2 className="size-3.5" />} {SUB_STATUS[st]}
              </Button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function Logs() {
  const logs = useQuery({ queryKey: ["admin-logs"], queryFn: () => apiGet<AdminLog[]>("/admin/logs") });
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
      <Table>
        <TableHeader><TableRow><TableHead>Data</TableHead><TableHead>Administrador</TableHead><TableHead>Ação</TableHead><TableHead>Entidade</TableHead></TableRow></TableHeader>
        <TableBody>{logs.data?.map((l) => <TableRow key={l.id}><TableCell className="text-xs">{formatDate(l.at, true)}</TableCell><TableCell>{l.admin_name}</TableCell><TableCell>{l.action}</TableCell><TableCell className="text-xs">{l.entity}</TableCell></TableRow>)}</TableBody>
      </Table>
    </div>
  );
}


function StudentManagement() {
  const qc = useQueryClient();
  const [q, setQ] = useState("");

  const users = useQuery({
    queryKey: ["admin-students", q],
    queryFn: () => apiGet<AdminUser[]>(`/admin/users?q=${encodeURIComponent(q)}`),
  });

  const patch = useMutation({
    mutationFn: ({ id, body }: { id: string; body: Record<string, string> }) =>
      apiPatch<Message>(`/admin/users/${id}`, body),
    onSuccess: (r) => {
      toast.success(r.message);
      qc.invalidateQueries({ queryKey: ["admin-students"] });
      qc.invalidateQueries({ queryKey: ["admin-users"] });
    },
    onError: (e) => toast.error(errMsg(e)),
  });

  const students = (users.data ?? []).filter((u) => u.role === "student");

  return (
    <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 lg:col-span-2">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="font-heading text-lg font-bold">Gestão de alunos</h3>
          <p className="text-sm text-slate-500">
            Altere diretamente o plano e o status das contas de estudantes.
          </p>
        </div>

        <div className="w-full max-w-md">
          <Input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Pesquisar por nome"
          />
        </div>
      </div>

      <div className="mt-4 overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Aluno</TableHead>
              <TableHead>E-mail</TableHead>
              <TableHead>Plano</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            {students.map((u) => (
              <TableRow key={u.id}>
                <TableCell className="font-semibold">{u.name}</TableCell>

                <TableCell className="text-xs">
                  {u.email_masked}
                </TableCell>

                <TableCell>
                  <NativeSelect
                    testId={`admin-student-plan-${u.id}`}
                    className="w-36"
                    value={u.plan ?? "limitado"}
                    onChange={(v) =>
                      patch.mutate({
                        id: u.id,
                        body: { plan: v },
                      })
                    }
                  >
                    <option value="limitado">Plano Limitado</option>
                    <option value="ilimitado">Plano Ilimitado</option>
                  </NativeSelect>
                </TableCell>

                <TableCell>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() =>
                      patch.mutate({
                        id: u.id,
                        body: {
                          status:
                            u.status === "ativo"
                              ? "bloqueado"
                              : "ativo",
                        },
                      })
                    }
                  >
                    {u.status === "ativo" ? "Bloquear" : "Desbloquear"}
                  </Button>
                </TableCell>
              </TableRow>
            ))}

            {students.length === 0 && (
              <TableRow>
                <TableCell
                  colSpan={4}
                  className="py-6 text-center text-sm text-slate-500"
                >
                  Nenhum estudante encontrado.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

function PaymentsAdmin() {
  const qc = useQueryClient();
  const settings = useQuery({ queryKey: ["admin-settings"], queryFn: () => apiGet<Settings>("/admin/settings") });
  const subscriptions = useQuery({ queryKey: ["admin-stripe-subscriptions"], queryFn: () => apiGet<import("@/lib/types").StripeSubscriptionAdmin[]>("/admin/payments/stripe/subscriptions") });
  const [form, setForm] = useState<Settings["stripe"] | null>(null);
  useEffect(() => { if (settings.data?.stripe) setForm(settings.data.stripe); }, [settings.data]);
  const save = useMutation({
    mutationFn: (stripe: Settings["stripe"]) => apiPut<Settings>("/admin/settings", {
      platform_name: settings.data?.platform_name || "Campus Study", support_email: settings.data?.support_email || "suporte@campusstudy.com",
      default_daily_goal_minutes: Number(settings.data?.default_daily_goal_minutes ?? 60), allow_registration: settings.data?.allow_registration ?? true,
      stripe: { ...stripe, secret_key: stripe.secret_key || "", webhook_secret: stripe.webhook_secret || "" },
      features: settings.data?.features,
    }),
    onSuccess: (d) => { toast.success("Configuração do Stripe salva."); qc.setQueryData(["admin-settings"], d); setForm(d.stripe); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const test = useMutation({ mutationFn: () => apiPost<Message>("/admin/payments/stripe/test", {}), onSuccess: r => toast.success(r.message), onError: e => toast.error(errMsg(e)) });
  const cancel = useMutation({ mutationFn: (id: string) => apiPost<Message>(`/admin/payments/stripe/subscriptions/${id}/cancel`, {}), onSuccess: r => { toast.success(r.message); subscriptions.refetch(); }, onError: e => toast.error(errMsg(e)) });
  if (settings.isLoading) return <div className="rounded-2xl border bg-white p-5">Carregando pagamentos...</div>;
  if (settings.isError) return <div className="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">Não foi possível carregar os pagamentos e configurações do Stripe. Recarregue a página e tente novamente.</div>;
  if (!form) return <div className="rounded-2xl border bg-white p-5">Pagamentos indisponíveis no momento.</div>;
  const patch = (key: keyof Settings["stripe"], value: string | boolean) => setForm({ ...form, [key]: value } as Settings["stripe"]);
  return <div className="space-y-6">
    <div className="rounded-2xl border border-indigo-200 bg-indigo-50 p-4 text-sm text-indigo-950"><b>Stripe</b><p className="mt-1">O Secret Key e o Webhook Secret ficam protegidos no banco e não são devolvidos ao navegador depois de salvos.</p></div>
    <div className="rounded-2xl border border-slate-200 bg-white p-5">
      <div className="flex flex-wrap items-center justify-between gap-3"><div><h3 className="font-heading text-lg font-bold">Checkout e assinaturas</h3><p className="text-sm text-slate-500">Use Test para homologação e Live somente quando os Price IDs de produção estiverem prontos.</p></div><Badge variant={form.enabled ? "default" : "secondary"}>{form.enabled ? "Ativo" : "Desativado"}</Badge></div>
      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <div><Label>Ativar Stripe</Label><NativeSelect testId="admin-stripe-enabled" value={form.enabled ? "true" : "false"} onChange={v => patch("enabled", v === "true")}><option value="true">Ativado</option><option value="false">Desativado</option></NativeSelect></div>
        <div><Label>Ambiente</Label><NativeSelect testId="admin-stripe-mode" value={form.mode} onChange={v => patch("mode", v as "test"|"live")}><option value="test">Test</option><option value="live">Live</option></NativeSelect></div>
        <div className="md:col-span-2"><Label>Publishable Key</Label><Input value={form.publishable_key} onChange={e => patch("publishable_key", e.target.value)} placeholder="pk_test_... ou pk_live_..." /></div>
        <div><Label>Secret Key {form.secret_key_configured && <span className="text-emerald-600">(já configurado)</span>}</Label><Input type="password" autoComplete="new-password" value={form.secret_key} onChange={e => patch("secret_key", e.target.value)} placeholder={form.secret_key_configured ? "•••••••• (manter atual)" : "sk_test_..."} /></div>
        <div><Label>Webhook Secret {form.webhook_secret_configured && <span className="text-emerald-600">(já configurado)</span>}</Label><Input type="password" autoComplete="new-password" value={form.webhook_secret} onChange={e => patch("webhook_secret", e.target.value)} placeholder={form.webhook_secret_configured ? "•••••••• (manter atual)" : "whsec_..."} /></div>
        <div><Label>Price ID mensal</Label><Input value={form.monthly_price_id} onChange={e => patch("monthly_price_id", e.target.value)} placeholder="price_..." /></div>
        <div><Label>Price ID anual</Label><Input value={form.yearly_price_id} onChange={e => patch("yearly_price_id", e.target.value)} placeholder="price_..." /></div>
        <div><Label>Moeda</Label><Input maxLength={3} value={form.currency} onChange={e => patch("currency", e.target.value.toUpperCase())} /></div>
        <div><Label>Preço mensal exibido</Label><Input value={form.monthly_price} onChange={e => patch("monthly_price", e.target.value)} /></div>
        <div><Label>Preço anual exibido</Label><Input value={form.yearly_price} onChange={e => patch("yearly_price", e.target.value)} /></div>
      </div>
      <div className="mt-4 flex flex-wrap gap-2"><Button onClick={() => save.mutate(form)} disabled={save.isPending}>Salvar Stripe</Button><Button variant="outline" onClick={() => test.mutate()} disabled={test.isPending || !form.secret_key_configured}>Testar conexão</Button></div>
      <p className="mt-3 text-xs text-slate-500">Webhook: <code>/api/payments/stripe/webhook</code></p>
    </div>
    <div className="rounded-2xl border border-slate-200 bg-white p-5"><h3 className="font-heading text-lg font-bold">Assinaturas registradas</h3><div className="mt-3 overflow-x-auto"><Table><TableHeader><TableRow><TableHead>Assinatura</TableHead><TableHead>Usuário</TableHead><TableHead>Plano</TableHead><TableHead>Status</TableHead><TableHead>Ação</TableHead></TableRow></TableHeader><TableBody>{(subscriptions.data ?? []).map(s => <TableRow key={s.subscription_id}><TableCell className="font-mono text-xs">{s.subscription_id}</TableCell><TableCell className="font-mono text-xs">{s.user_id}</TableCell><TableCell>{s.plan}</TableCell><TableCell><Badge variant="secondary">{s.status}</Badge></TableCell><TableCell>{["active","trialing","past_due"].includes(s.status) && <Button size="sm" variant="outline" className="text-red-600" onClick={() => confirm("Cancelar esta assinatura no Stripe?") && cancel.mutate(s.subscription_id)}>Cancelar</Button>}</TableCell></TableRow>)}</TableBody></Table>{subscriptions.data?.length === 0 && <p className="py-6 text-center text-sm text-slate-500">Nenhuma assinatura registrada ainda.</p>}</div></div>
  </div>;
}

type SettingsDraft = Omit<Settings, "default_daily_goal_minutes"> & { default_daily_goal_minutes: number | string };

function SettingsAdmin() {
  const qc = useQueryClient();
  const s = useQuery({ queryKey: ["admin-settings"], queryFn: () => apiGet<Settings>("/admin/settings") });
  const [form, setForm] = useState<SettingsDraft | null>(null);
  const [pw, setPw] = useState({ current_password: "", new_password: "", new_password_confirm: "" });
  useEffect(() => { if (s.data) setForm(s.data); }, [s.data]);
  const save = useMutation({
    mutationFn: (f: SettingsDraft) => apiPut<Settings>("/admin/settings", { ...f, default_daily_goal_minutes: Number(f.default_daily_goal_minutes || 0) }),
    onSuccess: (d) => { toast.success("Configurações salvas."); qc.setQueryData(["admin-settings"], d); setForm(d); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const changePw = useMutation({
    mutationFn: () => apiPost<Message>("/admin/change-password", pw),
    onSuccess: (r) => { toast.success(r.message); setPw({ current_password: "", new_password: "", new_password_confirm: "" }); },
    onError: (e) => toast.error(errMsg(e)),
  });
  if (s.isLoading) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-6 text-sm text-slate-500">
        Carregando configurações...
      </div>
    );
  }

  if (s.isError) {
    return (
      <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-sm text-red-700">
        Não foi possível carregar as configurações. Recarregue a página e tente novamente.
      </div>
    );
  }

  if (!form) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-6 text-sm text-slate-500">
        Configurações indisponíveis.
      </div>
    );
  }

  const featureLabels: Record<string,string> = { pdf:"PDFs", videoaulas:"Videoaulas", resumos:"Resumos", materiais:"Materiais de estudo", artigos:"Artigos científicos", questoes:"Questões", mapas:"Mapas mentais", simulados:"Simulados", ranking:"Ranking", anotacoes:"Anotações", favoritos:"Favoritos" };
  const toggleFeature = (plan: "limitado"|"ilimitado", key: keyof Settings["features"]["limitado"]) => setForm({ ...form, features: { ...form.features, [plan]: { ...form.features[plan], [key]: !form.features[plan][key] } } });
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div data-testid="admin-settings-form" className="rounded-2xl border border-slate-200 bg-white p-5">
        <h3 className="font-heading text-lg font-bold">Configurações da plataforma</h3><p className="mt-1 text-sm text-slate-500">Ajustes gerais aplicados a todo o Campus Study.</p>
        <form className="mt-4 space-y-4" onSubmit={(e) => { e.preventDefault(); save.mutate(form); }}>
          <div><Label>Nome da plataforma</Label><Input required value={form.platform_name} onChange={(e) => setForm({ ...form, platform_name: e.target.value })} /></div>
          <div><Label>E-mail de suporte</Label><Input type="email" required value={form.support_email} onChange={(e) => setForm({ ...form, support_email: e.target.value })} /></div>
          <div><Label>Meta diária padrão (minutos)</Label><Input type="number" min={0} value={form.default_daily_goal_minutes} onChange={(e) => setForm({ ...form, default_daily_goal_minutes: e.target.value === "" ? "" : Math.max(0, Number(e.target.value)) })} /><p className="mt-1 text-xs text-slate-500">0 = sem meta. Sem limite máximo.</p></div>
          <div><Label>Cadastro de novos estudantes</Label><NativeSelect testId="admin-allow-registration-select" value={form.allow_registration ? "true" : "false"} onChange={v => setForm({ ...form, allow_registration: v === "true" })}><option value="true">Ativado</option><option value="false">Desativado</option></NativeSelect></div>
          <Button type="submit" disabled={save.isPending} className="w-full">Salvar configurações</Button>
        </form>
      </div>
      <div className="rounded-2xl border border-slate-200 bg-white p-5">
        <h3 className="font-heading text-lg font-bold">Recursos dos planos</h3><p className="mt-1 text-sm text-slate-500">Você controla aqui o que os planos Free e Ilimitado podem usar, sem editar código.</p>
        <div className="mt-4 grid gap-4">{(["limitado","ilimitado"] as const).map(plan=><div key={plan} className="rounded-2xl border p-4"><div className="flex items-center justify-between"><h4 className="font-bold">{plan === "limitado" ? "Plano Free" : "Plano Ilimitado"}</h4><Badge>{Object.values(form.features[plan]).filter(Boolean).length} liberados</Badge></div><div className="mt-3 grid gap-2 sm:grid-cols-2">{Object.keys(form.features[plan]).filter(key => !["campus_ai","relatorios","benefit_labels"].includes(key)).map(key=>{const k=key as keyof Settings["features"]["limitado"];return <label key={key} className="flex items-center gap-2 rounded-xl bg-slate-50 p-2 text-sm"><input type="checkbox" checked={Boolean(form.features[plan][k])} onChange={()=>toggleFeature(plan,k)}/><span>{featureLabels[key]??key}</span></label>})}</div>
<label className="mt-4 block"><span className="text-sm font-semibold">Benefícios exibidos no card do plano</span><span className="mt-1 block text-xs text-slate-500">Um benefício por linha. Esses textos podem ser alterados sem deploy.</span><Textarea className="mt-2" rows={6} value={form.features[plan].benefit_labels.join("\n")} onChange={e=>setForm({...form,features:{...form.features,[plan]:{...form.features[plan],benefit_labels:e.target.value.split("\n").map(x=>x.trim()).filter(Boolean)}}})}/></label></div>)}</div>
        <Button className="mt-4 w-full" onClick={()=>save.mutate(form)} disabled={save.isPending}>Salvar planos e recursos</Button>
      </div>
      <div data-testid="admin-change-password" className="rounded-2xl border border-slate-200 bg-white p-5">
        <h3 className="font-heading text-lg font-bold">Alterar minha senha</h3><p className="mt-1 text-sm text-slate-500">Atualize a senha da sua conta administrativa.</p>
        <form className="mt-4 space-y-4" onSubmit={(e) => { e.preventDefault(); changePw.mutate(); }}>
          <Input type="password" required autoComplete="current-password" placeholder="Senha atual" value={pw.current_password} onChange={e=>setPw({...pw,current_password:e.target.value})}/><Input type="password" required autoComplete="new-password" placeholder="Nova senha" value={pw.new_password} onChange={e=>setPw({...pw,new_password:e.target.value})}/><Input type="password" required autoComplete="new-password" placeholder="Confirmar nova senha" value={pw.new_password_confirm} onChange={e=>setPw({...pw,new_password_confirm:e.target.value})}/><Button type="submit" disabled={changePw.isPending} variant="outline" className="w-full">Alterar senha</Button>
        </form>
      </div>
      <StudentManagement />
    </div>
  );
}


function ContentZipImporter() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const [replaceConflicts, setReplaceConflicts] = useState(false);

  useEffect(() => {
    if (!preview?.import_id || !["queued", "processing"].includes(preview.status)) return;
    let active = true;
    const poll = async () => {
      try {
        const status = await apiGet<any>(`/admin/content/import/${preview.import_id}/status`);
        if (!active) return;
        setPreview((current: any) => ({ ...current, ...status }));
        if (status.status === "confirmed") {
          const created = (status.results ?? []).filter((x: any) => String(x.result).startsWith("created")).length;
          toast.success(`Importação concluída: ${created} itens processados.`);
          setPreview(null);
          setFile(null);
        } else if (status.status === "failed") {
          toast.error(status.error || "A importação falhou.");
          setBusy(false);
        }
      } catch (e) {
        if (active) toast.error(errMsg(e));
      }
    };
    void poll();
    const timer = window.setInterval(() => void poll(), 1500);
    return () => { active = false; window.clearInterval(timer); };
  }, [preview?.import_id, preview?.status]);

  const previewZip = async () => {
    if (!file) return;
    setBusy(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      setPreview(await apiUpload<any>("/admin/content/import/preview", fd));
      toast.success("Prévia gerada. Revise antes de confirmar.");
    } catch (e) {
      toast.error(errMsg(e));
    } finally {
      setBusy(false);
    }
  };

  const confirmImport = async () => {
    if (!preview?.import_id) return;
    setBusy(true);
    try {
      const decisions = Object.fromEntries((preview.conflicts ?? []).map((p: string) => [p, replaceConflicts ? "replace" : "keep"]));
      const r = await apiPost<any>(`/admin/content/import/${preview.import_id}/confirm`, { decisions });
      setPreview((current: any) => ({ ...current, ...r }));
      toast.success("Importação iniciada. Você pode acompanhar o progresso.");
    } catch (e) {
      toast.error(errMsg(e));
      setBusy(false);
    }
  };

  const cancelImport = async () => {
    if (!preview?.import_id || preview.status !== "preview") return;
    try {
      await apiDelete(`/admin/content/import/${preview.import_id}`);
      setPreview(null);
      toast.success("Importação cancelada.");
    } catch (e) {
      toast.error(errMsg(e));
    }
  };

  const progress = preview?.total ? Math.min(100, Math.round((Number(preview.processed ?? 0) / Number(preview.total)) * 100)) : 0;
  return <div className="space-y-5">
    <div className="rounded-2xl border bg-white p-5">
      <h2 className="text-xl font-bold">Importar Conteúdo por ZIP</h2>
      <p className="mt-1 text-sm text-slate-500">O sistema identifica automaticamente Curso → Período → Disciplina → Assunto pela estrutura das pastas.</p>
      <div className="mt-4 flex flex-wrap items-center gap-3">
        <Input type="file" accept=".zip,application/zip" onChange={e => setFile(e.target.files?.[0] ?? null)} />
        <Button onClick={previewZip} disabled={!file || busy}>{busy ? "Processando..." : "Gerar prévia"}</Button>
      </div>
    </div>
    {preview && <div className="rounded-2xl border bg-white p-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="font-bold">Prévia da importação</h3>
          <p className="text-xs text-slate-500">{preview.entries ?? preview.total ?? 0} arquivos reconhecidos</p>
        </div>
        <div className="flex gap-2">
          {preview.status === "preview" && <Button variant="outline" onClick={cancelImport}>Cancelar</Button>}
          {preview.status === "preview" && <Button onClick={confirmImport} disabled={busy}>Confirmar importação</Button>}
        </div>
      </div>
      {["queued", "processing"].includes(preview.status) && <div className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 p-4">
        <div className="flex items-center justify-between gap-3 text-sm font-semibold"><span>{preview.status === "queued" ? "Importação aguardando processamento..." : "Importando conteúdo..."}</span><span>{preview.processed ?? 0}/{preview.total ?? preview.entries ?? 0}</span></div>
        <div className="mt-2 h-2 overflow-hidden rounded-full bg-white"><div className="h-full rounded-full bg-emerald-600 transition-all" style={{ width: `${progress}%` }} /></div>
        <p className="mt-2 text-xs text-emerald-800">Você pode continuar usando o painel enquanto a importação é processada.</p>
      </div>}
      {preview.status === "failed" && <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{preview.error || "A importação falhou."}</div>}
      {preview.status === "preview" && <div className="mt-4">
        {(preview.conflicts ?? []).length > 0 && <div className="mb-4 rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
          <b>Conteúdos já existentes:</b> {preview.conflicts.length}.
          <label className="ml-2 inline-flex items-center gap-2"><input type="checkbox" checked={replaceConflicts} onChange={e => setReplaceConflicts(e.target.checked)} /> substituir os existentes</label>
          <span className="ml-2">desmarcado = manter os existentes.</span>
        </div>}
        <div className="space-y-3">{(preview.groups ?? []).map((g: any) => <div key={g.path} className="rounded-xl border p-3">
          <p className="font-semibold">{g.path.split("/").map((x: string) => x.replaceAll("_", " ")).join(" → ")}</p>
          <ul className="mt-2 space-y-1 text-sm text-slate-600">{g.files.map((f: any) => <li key={f.path}>• {f.filename} — {Math.round(f.size / 1024)} KB</li>)}</ul>
        </div>)}</div>
      </div>}
    </div>}
  </div>;
}

function SiteEditor() {
  const qc=useQueryClient();
  const q=useQuery({queryKey:["site-config"],queryFn:()=>apiGet<any>("/admin/site-config")});
  const [cfg,setCfg]=useState<any>(null);
  useEffect(()=>{if(q.data)setCfg(q.data)},[q.data]);
  if(q.isLoading||!cfg)return <div className="rounded-2xl border bg-white p-6 text-sm text-slate-500">Carregando editor...</div>;
  const texts=Object.entries(cfg.home_texts??{}) as [string,string][];
  const setText=(k:string,v:string)=>setCfg({...cfg,home_texts:{...cfg.home_texts,[k]:v}});
  const addText=()=>{const k=prompt("Chave do texto (ex.: home.titulo)"); if(k)setText(k,"")};
  const removeText=(k:string)=>{const next={...cfg.home_texts}; delete next[k]; setCfg({...cfg,home_texts:next})};
  const save=async()=>{try{const d=await apiPut<any>("/admin/site-config",cfg);qc.setQueryData(["site-config"],d);setCfg(d);toast.success("Editor do site salvo.")}catch(e){toast.error(errMsg(e))}};
  return <div className="space-y-5">
    <div className="rounded-2xl border bg-white p-5"><div className="flex items-center justify-between"><div><h2 className="text-xl font-bold">Textos da tela inicial</h2><p className="text-sm text-slate-500">Cadastre e edite textos configuráveis sem editar o código.</p></div><Button variant="outline" onClick={addText}>Adicionar texto</Button></div>
      <div className="mt-4 space-y-3">{texts.map(([k,v])=><div key={k} className="grid gap-2 rounded-xl border p-3 sm:grid-cols-[180px_1fr_auto]"><Input value={k} onChange={e=>{const old=k;const next={...cfg.home_texts};delete next[old];next[e.target.value]=v;setCfg({...cfg,home_texts:next})}}/><Textarea value={v} onChange={e=>setText(k,e.target.value)}/><Button variant="ghost" onClick={()=>removeText(k)}>Excluir</Button></div>)}</div>
    </div>
    <div className="grid gap-5 md:grid-cols-2">
      <div className="rounded-2xl border bg-white p-5"><h3 className="font-bold">Seções</h3><p className="text-sm text-slate-500">Ative ou desative seções configuradas.</p><div className="mt-3 space-y-2">{Object.entries(cfg.sections??{}).map(([k,v])=><label key={k} className="flex items-center gap-2 rounded-xl bg-slate-50 p-2 text-sm"><input type="checkbox" checked={!!v} onChange={()=>setCfg({...cfg,sections:{...cfg.sections,[k]:!v}})}/>{k}</label>)}</div></div>
      <div className="rounded-2xl border bg-white p-5"><h3 className="font-bold">Tipos de material</h3><p className="text-sm text-slate-500">Controle os tipos disponíveis na configuração.</p><div className="mt-3 space-y-2">{["material","resumo","questao","video","artigo"].map(k=><label key={k} className="flex items-center gap-2 rounded-xl bg-slate-50 p-2 text-sm"><input type="checkbox" checked={(cfg.material_types??[]).includes(k)} onChange={()=>setCfg({...cfg,material_types:(cfg.material_types??[]).includes(k)?cfg.material_types.filter((x:string)=>x!==k):[...(cfg.material_types??[]),k]})}/>{k}</label>)}</div></div>
    </div>
    <Button className="w-full" onClick={save}>Salvar alterações do site</Button>
  </div>;
}

function AdminLoginForm() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const login = useMutation({
    mutationFn: () => apiPost<Me>("/auth/admin-login", { email, password }),
    onSuccess: (data) => { beginSession(); queryClient.setQueryData(["me"], data); toast.success("Acesso administrativo autorizado."); navigate("/admin?secao=painel", { replace: true }); },
    onError: (e) => toast.error(errMsg(e)),
  });
  return <div className="mx-auto max-w-md rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"><h1 className="text-2xl font-extrabold">Acesso administrativo</h1><p className="mt-1 text-sm text-slate-500">Entre com o e-mail e a senha de uma conta da equipe.</p><form className="mt-5 space-y-4" onSubmit={e => { e.preventDefault(); login.mutate(); }}><div><Label>E-mail</Label><Input type="email" autoComplete="username" value={email} onChange={e => setEmail(e.target.value)} required /></div><div><Label>Senha</Label><Input type="password" autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} required /></div><Button className="w-full" type="submit" disabled={login.isPending}>{login.isPending ? "Entrando..." : "Entrar no Admin"}</Button></form></div>;
}


function SupportAdmin() {
  const qc=useQueryClient();
  const tickets=useQuery({queryKey:["admin-support"],queryFn:()=>apiGet<SupportTicket[]>("/support/admin/tickets")});
  const [selected,setSelected]=useState<SupportTicket|null>(null), [reply,setReply]=useState("");
  const send=useMutation({mutationFn:()=>apiPost<SupportTicket>(`/support/admin/tickets/${selected!.id}/reply`,{message:reply}),onSuccess:r=>{setSelected(r);setReply("");qc.invalidateQueries({queryKey:["admin-support"]});toast.success("Resposta enviada.")},onError:e=>toast.error(errMsg(e))});
  const status=useMutation({mutationFn:(v:string)=>apiPatch<Message>(`/support/admin/tickets/${selected!.id}/status?status=${encodeURIComponent(v)}`),onSuccess:()=>{qc.invalidateQueries({queryKey:["admin-support"]});toast.success("Status atualizado.")},onError:e=>toast.error(errMsg(e))});
  return <div className="grid gap-5 lg:grid-cols-[1fr_1.2fr]"><div className="rounded-2xl border bg-white p-4 space-y-2"><h3 className="font-bold">Chamados</h3>{tickets.data?.map(t=><button key={t.id} onClick={()=>setSelected(t)} className={cn("w-full rounded-xl border p-3 text-left",selected?.id===t.id?"border-emerald-500 bg-emerald-50":"hover:bg-slate-50")}><div className="flex justify-between gap-2"><b className="truncate">{t.subject}</b><span className="text-xs">{t.status}</span></div><p className="mt-1 text-xs text-slate-500">{t.user_name} · {t.category}</p></button>)}{tickets.data?.length===0&&<p className="text-sm text-slate-500">Nenhum chamado.</p>}</div><div className="rounded-2xl border bg-white p-5">{!selected?<p className="text-sm text-slate-500">Selecione um chamado.</p>:<><div className="flex flex-wrap justify-between gap-3"><div><h3 className="font-bold">{selected.subject}</h3><p className="text-sm text-slate-500">{selected.user_name} · {selected.user_email}</p></div><NativeSelect value={selected.status} onChange={v=>status.mutate(v)}><option value="aberto">Aberto</option><option value="em_analise">Em análise</option><option value="aguardando_usuario">Aguardando usuário</option><option value="resolvido">Resolvido</option><option value="fechado">Fechado</option></NativeSelect></div><p className="mt-4 whitespace-pre-wrap rounded-xl bg-slate-50 p-4 text-sm">{selected.message}</p><div className="mt-4 space-y-2">{selected.replies?.map(r=><div key={r.id} className="rounded-xl border p-3 text-sm"><b>{r.author_name}</b><p className="mt-1 whitespace-pre-wrap">{r.message}</p></div>)}</div><form className="mt-4 space-y-2" onSubmit={e=>{e.preventDefault();if(reply.trim())send.mutate()}}><Textarea rows={4} value={reply} onChange={e=>setReply(e.target.value)} placeholder="Responder ao estudante"/><Button disabled={send.isPending}>Responder</Button></form></>}</div></div>;
}

function SystemStatusAdmin() {
  const qc=useQueryClient(); const q=useQuery({queryKey:["system-status"],queryFn:()=>apiGet<SystemStatus>("/system-status")});
  const [form,setForm]=useState<SystemStatus|null>(null); useEffect(()=>{if(q.data)setForm(q.data)},[q.data]);
  const save=useMutation({mutationFn:(f:SystemStatus)=>apiPut<SystemStatus>("/system-status",f),onSuccess:d=>{setForm(d);qc.setQueryData(["system-status"],d);toast.success("Status publicado.")},onError:e=>toast.error(errMsg(e))});
  if(!form)return <div className="rounded-2xl border bg-white p-5">Carregando...</div>;
  const incidents=form.incidents??[];
  return <div className="rounded-2xl border bg-white p-5 space-y-5"><div><h3 className="font-bold">Status público</h3><p className="text-sm text-slate-500">Somente administradores podem publicar alterações.</p></div><NativeSelect value={form.overall} onChange={v=>setForm({...form,overall:v as SystemStatus["overall"]})}><option value="operacional">Operacional</option><option value="degradado">Instabilidade</option><option value="indisponivel">Indisponível</option><option value="manutencao">Manutenção</option></NativeSelect><Input value={form.message} onChange={e=>setForm({...form,message:e.target.value})} placeholder="Mensagem pública"/><label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form.maintenance} onChange={e=>setForm({...form,maintenance:e.target.checked})}/> Manutenção programada</label><Textarea value={form.maintenance_message} onChange={e=>setForm({...form,maintenance_message:e.target.value})} placeholder="Detalhes da manutenção"/>
    <div className="rounded-2xl border border-slate-200 p-4 space-y-3"><div className="flex items-center justify-between gap-3"><div><h4 className="font-bold">Incidentes</h4><p className="text-xs text-slate-500">Mantenha um histórico curto e objetivo do que ocorreu.</p></div><Button size="sm" variant="outline" onClick={()=>setForm({...form,incidents:[...incidents,{id:crypto.randomUUID(),title:"",message:"",status:"investigando"}]})}>Adicionar</Button></div>{incidents.map((incident,index)=><div key={incident.id} className="grid gap-2 rounded-xl bg-slate-50 p-3 md:grid-cols-[1fr_auto]"><div className="space-y-2"><Input value={incident.title} onChange={e=>setForm({...form,incidents:incidents.map((x,i)=>i===index?{...x,title:e.target.value}:x)})} placeholder="Título do incidente"/><Textarea value={incident.message} onChange={e=>setForm({...form,incidents:incidents.map((x,i)=>i===index?{...x,message:e.target.value}:x)})} placeholder="Descrição" rows={2}/></div><div className="flex items-end gap-2 md:flex-col md:items-stretch"><NativeSelect value={incident.status} onChange={v=>setForm({...form,incidents:incidents.map((x,i)=>i===index?{...x,status:v as SystemStatus["incidents"][number]["status"]}:x)})}><option value="investigando">Investigando</option><option value="monitorando">Monitorando</option><option value="resolvido">Resolvido</option></NativeSelect><Button size="sm" variant="ghost" onClick={()=>setForm({...form,incidents:incidents.filter((_,i)=>i!==index)})}>Remover</Button></div></div>)}{incidents.length===0&&<p className="text-sm text-slate-500">Nenhum incidente registrado.</p>}</div>
    <Button onClick={()=>save.mutate(form)} disabled={save.isPending}>Publicar status</Button></div>;
}

export default function AdminPage() {
  usePageMeta("Administração");
  const me = useMe();
  const [sp, setSp] = useSearchParams();
  const sec = sp.get("secao") ?? "painel";
  if (me.isLoading) return null;
  if (me.isError || !me.data) return <AdminLoginForm />;
  if (!isAdmin(me.data)) return <AdminLoginForm />;
  return (
    <div className="animate-fade-up rounded-3xl bg-emerald-50/70 p-1 sm:p-2">
      <h1 className="text-3xl font-extrabold tracking-tight">Administração</h1>
      <div className="no-scrollbar -mx-4 mt-5 flex gap-2 overflow-x-auto px-4 pb-1">
        {SECTIONS.map(([k, l]) => (
          <button key={k} data-testid={`admin-section-${k}`} onClick={() => setSp({ secao: k })}
            className={cn("shrink-0 rounded-full border px-4 py-2 text-sm font-medium transition-colors", sec === k ? "border-emerald-700 bg-emerald-600 text-white" : "border-emerald-100 bg-white text-slate-600")}>{l}</button>
        ))}
      </div>
      <div className="mt-6">
        {sec === "painel" && <Dashboard />}
        {sec === "estrutura" && <Structure />}
        {sec === "importar" && <ContentZipImporter />}
        {sec === "videos" && <ContentsAdmin key="v" videosOnly />}
        {sec === "conteudos" && <ContentsAdmin key="c" videosOnly={false} />}
        {sec === "usuarios" && <Users />}
        {sec === "moderacao" && <Moderation />}\n        {sec === "suporte" && <SupportAdmin />}\n        {sec === "status" && <SystemStatusAdmin />}
        {sec === "pagamentos" && <PaymentsAdmin />}
        {sec === "logs" && <Logs />}
        {sec === "config" && <SettingsAdmin />}
        {sec === "editor" && <SiteEditor />}
      </div>
    </div>
  );
}
