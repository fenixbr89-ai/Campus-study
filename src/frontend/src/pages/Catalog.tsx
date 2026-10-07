import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { BookOpen, Bookmark, BookmarkCheck, CheckCircle2, ChevronRight, Circle, ClipboardCheck, ExternalLink, FileText, GraduationCap, Info, Search } from "lucide-react";
import { apiGet, apiPost } from "@/lib/api";
import { errMsg, useMe, usePageMeta } from "@/lib/hooks";
import { TYPE_PLURAL } from "@/lib/format";
import type { ContentType, Course, CourseDetail, DisciplineDetail, Message, TopicDetail } from "@/lib/types";
import { ContentCard } from "@/components/ContentCard";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

function Crumbs({ items }: { items: { label: string; to?: string }[] }) {
  return (
    <nav aria-label="Trilha" data-testid="breadcrumbs" className="mb-4 flex flex-wrap items-center gap-1 text-sm text-slate-500">
      {items.map((it, i) => (
        <span key={i} className="flex items-center gap-1">
          {i > 0 && <ChevronRight className="size-3.5" />}
          {it.to ? <Link to={it.to} className="hover:text-brand-dark">{it.label}</Link> : <span className="font-medium text-slate-800">{it.label}</span>}
        </span>
      ))}
    </nav>
  );
}

function Skeleton({ rows = 6 }: { rows?: number }) {
  return <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{Array.from({ length: rows }).map((_, i) => <div key={i} className="h-28 animate-pulse rounded-2xl bg-slate-200/60" />)}</div>;
}

function Unavailable({ what }: { what: string }) {
  return <p data-testid="load-error" className="rounded-2xl border border-dashed border-slate-300 bg-white p-6 text-sm text-slate-500">Não foi possível carregar {what} agora. Tente novamente em instantes.</p>;
}

export function CoursesPage() {
  usePageMeta("Cursos", "Cursos universitários organizados por período, disciplina e assunto no Campus Study.");
  const [filter, setFilter] = useState("");
  const q = useQuery({ queryKey: ["courses"], queryFn: () => apiGet<Course[]>("/courses") });
  const list = (q.isError ? [] : q.data ?? []).filter((c) => c.name.toLowerCase().includes(filter.toLowerCase()));
  return (
    <div className="animate-fade-up">
      <h1 className="text-3xl font-extrabold tracking-tight">Cursos</h1>
      <p className="mt-1 text-slate-600">Escolha seu curso e navegue por período, disciplina e assunto.</p>
      <div className="relative mt-5 max-w-md">
        <Search className="absolute top-3 left-3 size-4 text-slate-400" />
        <input data-testid="courses-filter-input" value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Filtrar cursos…"
          className="h-10 w-full rounded-xl border border-slate-200 bg-white pr-3 pl-9 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/20" />
      </div>
      <div className="mt-6">
        {q.isLoading ? <Skeleton /> : q.isError ? <Unavailable what="os cursos" /> : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {list.map((c) => (
              <Link key={c.id} to={`/cursos/${c.slug}`} data-testid={`course-card-${c.slug}`}
                className="group flex items-center gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-[transform,box-shadow] duration-200 hover:-translate-y-1 hover:shadow-md">
                <span className="grid size-12 place-items-center rounded-2xl bg-brand-soft text-brand-dark transition-colors group-hover:bg-brand group-hover:text-white"><GraduationCap className="size-6" /></span>
                <div className="min-w-0 flex-1">
                  <p className="font-semibold text-slate-900">{c.name}</p>
                  <p className="text-sm text-slate-500">{c.num_periods} períodos</p>
                </div>
                <ChevronRight className="size-5 text-slate-300 transition-transform group-hover:translate-x-1" />
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export function CoursePage() {
  const { c = "" } = useParams();
  const q = useQuery({ queryKey: ["course", c], queryFn: () => apiGet<CourseDetail>(`/courses/${c}`) });
  const d = q.isError ? undefined : q.data;
  usePageMeta(d?.course.name ?? "Curso", d ? `Materiais de ${d.course.name} por período: videoaulas, artigos, resumos e questões.` : undefined);
  const [open, setOpen] = useState<number | null>(1);
  return (
    <div className="animate-fade-up">
      <Crumbs items={[{ label: "Cursos", to: "/cursos" }, { label: d?.course.name ?? "…" }]} />
      <h1 data-testid="course-title" className="text-3xl font-extrabold tracking-tight">{d?.course.name ?? "Carregando…"}</h1>
      <p className="mt-2 flex items-start gap-2 rounded-xl bg-amber-50 p-3 text-sm text-amber-900">
        <Info className="mt-0.5 size-4 shrink-0" /> A grade curricular é uma referência e pode variar de uma instituição para outra.
      </p>
      <div className="mt-6 space-y-3">
        {q.isLoading && <Skeleton rows={4} />}
        {q.isError && <Unavailable what="este curso" />}
        {d?.periods.map((p) => (
          <div key={p.id} className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            <button data-testid={`period-toggle-${p.slug}`} onClick={() => setOpen(open === p.number ? null : p.number)}
              className="flex w-full items-center justify-between px-5 py-4 text-left">
              <span className="font-heading font-semibold">{p.name}</span>
              <span className="flex items-center gap-2 text-sm text-slate-500">
                {p.disciplines.length} disciplina{p.disciplines.length === 1 ? "" : "s"}
                <ChevronRight className={cn("size-4 transition-transform duration-200", open === p.number && "rotate-90")} />
              </span>
            </button>
            {open === p.number && (
              <div className="grid gap-2 border-t border-slate-100 p-4 sm:grid-cols-2">
                {p.disciplines.length === 0 && <p className="text-sm text-slate-500">Disciplinas deste período em breve.</p>}
                {p.disciplines.map((disc) => (
                  <Link key={disc.id} to={`/cursos/${c}/${p.slug}/${disc.slug}`} data-testid={`discipline-link-${disc.slug}`}
                    className="flex items-center justify-between rounded-xl bg-slate-50 px-4 py-3 text-sm font-medium transition-colors hover:bg-brand-soft hover:text-brand-dark">
                    {disc.name} <ChevronRight className="size-4" />
                  </Link>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export function DisciplinePage() {
  const { c = "", p = "", d = "" } = useParams();
  const navigate = useNavigate();
  const q = useQuery({ queryKey: ["discipline", c, p, d], queryFn: () => apiGet<DisciplineDetail>(`/courses/${c}/${p}/${d}`) });
  const x = q.isError ? undefined : q.data;
  usePageMeta(x ? `${x.discipline.name} — ${x.course.name}` : "Disciplina", x ? `Biblioteca e assuntos de ${x.discipline.name} (${x.period.name}) em ${x.course.name}.` : undefined);
  const topics = x?.topics ?? [];
  return (
    <div className="animate-fade-up">
      <Crumbs items={[{ label: "Cursos", to: "/cursos" }, { label: x?.course.name ?? "…", to: `/cursos/${c}` }, { label: x?.period.name ?? "…" }, { label: x?.discipline.name ?? "…" }]} />
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 data-testid="discipline-title" className="text-3xl font-extrabold tracking-tight">{x?.discipline.name ?? "Carregando…"}</h1>
          {x?.discipline.description && <p className="mt-1 text-slate-600">{x.discipline.description}</p>}
        </div>
      </div>

      <section className="mt-7 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-brand-dark">Conteúdos estudados</p>
        <h2 className="mt-1 text-xl font-bold">Escolha um assunto para começar</h2>
        <p className="mt-1 text-sm text-slate-600">Cada assunto tem uma descrição própria e os conteúdos publicados relacionados.</p>
      </section>

      <h2 className="mt-8 mb-3 text-lg font-bold">Assuntos da disciplina</h2>
      {q.isLoading && <Skeleton rows={3} />}
      {q.isError && <Unavailable what="esta disciplina" />}
      <div className="grid gap-3 sm:grid-cols-2">
        {x?.topics.map((t) => (
          <Link key={t.id} to={`/cursos/${c}/${p}/${d}/${t.slug}`} data-testid={`topic-link-${t.slug}`}
            className="group flex items-center justify-between rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-[transform,box-shadow] hover:-translate-y-1 hover:shadow-md">
            <span className="font-semibold">{t.name}</span>
            <ChevronRight className="size-5 text-slate-300 transition-transform group-hover:translate-x-1" />
          </Link>
        ))}
        {x && x.topics.length === 0 && <p className="text-sm text-slate-500">Assuntos em breve.</p>}
      </div>
    </div>
  );
}

const TABS = ["todos", "pdf", "resumo", "video", "artigo", "mapa", "simulado", "questao"] as const;
type TopicTab = typeof TABS[number];

type BookHit = { id: string; volumeInfo?: { title?: string; authors?: string[]; publishedDate?: string; imageLinks?: { thumbnail?: string }; previewLink?: string; infoLink?: string }; accessInfo?: { webReaderLink?: string; pdf?: { isAvailable?: boolean; acsTokenLink?: string } } };

function StudyHub({ x }: { x: TopicDetail }) {
  const [booksOpen, setBooksOpen] = useState(false);
  const bookQuery = useMemo(() => encodeURIComponent(`${x.topic.name} ${x.discipline.name}`), [x.topic.name, x.discipline.name]);
  const books = useState<BookHit[]>([]);
  const [bookData, setBookData] = books;

  const loadBooks = async () => {
    if (booksOpen) return;
    setBooksOpen(true);
    try {
      const res = await fetch(`https://www.googleapis.com/books/v1/volumes?q=${bookQuery}&maxResults=6&printType=books&langRestrict=pt`);
      const data = await res.json() as { items?: BookHit[] };
      setBookData(data.items ?? []);
    } catch {
      toast.error("Não foi possível consultar livros agora.");
    }
  };

  const openStax = `https://openstax.org/subjects`;
  const ncbi = `https://www.ncbi.nlm.nih.gov/books/?term=${bookQuery}`;
  const googleBooks = `https://books.google.com/books?q=${bookQuery}`;
  const pdfSearch = `https://www.google.com/search?q=${encodeURIComponent(`site:openstax.org filetype:pdf ${x.topic.name} ${x.discipline.name}`)}`;

  return (
    <section className="mt-8 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-brand-dark">Central de estudo</p>
        <h2 className="mt-1 text-xl font-bold">Tudo deste assunto em um só lugar</h2>
        <p className="mt-1 text-sm text-slate-600">Materiais internos e fontes complementares para <strong>{x.topic.name}</strong>.</p>
      </div>

      <div className="mt-5 rounded-2xl border border-emerald-200 bg-emerald-50 p-4">
        <div className="flex items-center gap-2"><FileText className="size-5 text-emerald-700" /><span className="font-semibold text-emerald-950">Materiais internos</span></div>
        <p className="mt-1 text-xs text-emerald-900">Os PDFs cadastrados para este assunto são exibidos dentro do aplicativo e têm opção de download. Fontes externas servem apenas para complementar a pesquisa.</p>
      </div>

      <div className="mt-5 rounded-2xl border border-slate-200 p-4">
        <div className="flex flex-wrap items-center gap-2">
          <BookOpen className="size-5 text-brand-dark" />
          <h3 className="font-semibold">Livros relacionados a este assunto</h3>
          <button onClick={loadBooks} className="ml-auto rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold hover:bg-slate-50">Pesquisar livros</button>
          <a href={googleBooks} target="_blank" rel="noreferrer" className="text-xs font-semibold text-brand-dark hover:underline">Abrir busca completa</a>
        </div>
        {booksOpen && <div className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {bookData.length === 0 && <p className="text-sm text-slate-500">Nenhum livro retornado para esta busca.</p>}
          {bookData.map((b) => {
            const v = b.volumeInfo ?? {};
            const link = v.previewLink ?? v.infoLink ?? b.accessInfo?.webReaderLink;
            return <a key={b.id} href={link} target="_blank" rel="noreferrer" className="flex gap-3 rounded-xl bg-slate-50 p-3 hover:bg-brand-soft">
              {v.imageLinks?.thumbnail && <img src={v.imageLinks.thumbnail} alt="" className="h-16 w-11 rounded object-cover" />}
              <span className="min-w-0"><span className="block line-clamp-2 text-sm font-semibold">{v.title ?? "Livro"}</span><span className="mt-1 block text-xs text-slate-500">{v.authors?.join(", ") ?? "Autor não informado"}</span>{b.accessInfo?.pdf?.isAvailable && <span className="mt-1 inline-block text-[11px] font-semibold text-emerald-700">PDF disponível</span>}</span>
            </a>;
          })}
        </div>}
      </div>

      <div className="mt-5 flex flex-wrap gap-2 text-xs">
        <a href={openStax} target="_blank" rel="noreferrer" className="rounded-lg border border-slate-200 px-3 py-2 font-semibold hover:bg-slate-50">OpenStax</a>
        <a href={ncbi} target="_blank" rel="noreferrer" className="rounded-lg border border-slate-200 px-3 py-2 font-semibold hover:bg-slate-50">NCBI Books</a>
        <a href={pdfSearch} target="_blank" rel="noreferrer" className="rounded-lg border border-slate-200 px-3 py-2 font-semibold hover:bg-slate-50">Buscar PDFs</a>
      </div>
    </section>
  );
}

function StudySessionCard({ topicId }: { topicId: string }) {
  const qc = useQueryClient();
  const activeQuery = useQuery({ queryKey: ["study-active"], queryFn: () => apiGet<any>("/study-sessions/active") });
  const [session, setSession] = useState<any>(null);
  const [now, setNow] = useState(Date.now());
  useEffect(() => { if (activeQuery.data?.topic_id === topicId) setSession(activeQuery.data); }, [activeQuery.data, topicId]);
  useEffect(() => {
    if (!session) return;
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    const onVisibility = () => { if (document.visibilityState === "hidden" && !stop.isPending) stop.mutate(); };
    document.addEventListener("visibilitychange", onVisibility);
    return () => { window.clearInterval(id); document.removeEventListener("visibilitychange", onVisibility); };
  }, [session]);
  const start = useMutation({ mutationFn: () => apiPost<any>("/study-sessions", { topic_id: topicId }), onSuccess: s => { setSession(s); setNow(Date.now()); qc.setQueryData(["study-active"], s); } });
  const stop = useMutation({ mutationFn: () => apiPost<any>(`/study-sessions/${session.id}/stop`), onSuccess: () => { setSession(null); qc.setQueryData(["study-active"], null); qc.invalidateQueries({ queryKey: ["progress"] }); qc.invalidateQueries({ queryKey: ["home"] }); } });
  useEffect(() => () => {
    if (session?.id && !stop.isPending) void apiPost(`/study-sessions/${session.id}/stop`).catch(() => undefined);
  }, [session?.id]);
  const seconds = session ? Math.max(0, Math.floor((now - new Date(session.started_at).getTime()) / 1000)) : 0;
  const mm = String(Math.floor(seconds / 60)).padStart(2,"0"); const ss=String(seconds%60).padStart(2,"0");
  return <section className="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-4">
    <div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-xs font-bold uppercase tracking-wide text-emerald-700">Tempo de estudo</p><p className="mt-1 text-sm text-emerald-900">Só conte quando você iniciar uma sessão real de estudo nesta página.</p></div>
    {session?.topic_id === topicId ? <div className="flex items-center gap-2"><span className="rounded-xl bg-white px-3 py-2 text-lg font-extrabold tabular-nums text-emerald-800">{mm}:{ss}</span><Button variant="outline" onClick={()=>stop.mutate()} disabled={stop.isPending} className="bg-white">Parar</Button></div> : <Button onClick={()=>start.mutate()} disabled={start.isPending} className="rounded-xl">Começar a estudar</Button>}</div>
  </section>;
}

function tabLabel(tab: TopicTab, count: number) {
  const labels: Record<TopicTab,string> = { todos:"Tudo", pdf:"Material Principal", resumo:"Resumo", video:"Videoaulas", artigo:"Artigos científicos", mapa:"Mapas mentais", simulado:"Simulados", questao:"Questões" };
  return `${labels[tab]} (${count})`;
}

export function TopicPage() {
  const { c = "", p = "", d = "", t = "" } = useParams();
  const me = useMe();
  const qc = useQueryClient();
  const [tab, setTab] = useState<TopicTab>("todos");
  const q = useQuery({ queryKey: ["topic", c, p, d, t, me.data?.id ?? ""], queryFn: () => apiGet<TopicDetail>(`/courses/${c}/${p}/${d}/${t}`) });
  const x = q.isError ? undefined : q.data;
  usePageMeta(x ? `${x.topic.name} — ${x.discipline.name}` : "Assunto", x ? `Videoaulas, artigos científicos, resumos e questões sobre ${x.topic.name} (${x.discipline.name}, ${x.course.name}).` : undefined);
  const topicFav = useQuery({ queryKey:["topic-favorite", x?.topic.id], enabled:!!x?.topic.id && !!me.data, queryFn:()=>apiGet<any[]>("/topic-favorites") });
  const isTopicFav = !!x?.topic.id && (topicFav.data??[]).some((f:any)=>f.id===x.topic.id);
  const toggleTopicFav = useMutation({ mutationFn:()=>apiPost<Message>(`/topic-favorites/${x!.topic.id}`), onSuccess:r=>{toast.success(r.message);qc.invalidateQueries({queryKey:["topic-favorite"]});qc.invalidateQueries({queryKey:["topic-favorites"]})}, onError:e=>toast.error(errMsg(e)) });
  const toggle = useMutation({
    mutationFn: () => apiPost<Message>(`/progress/topics/${x!.topic.id}`),
    onSuccess: (r) => { toast.success(r.message); qc.invalidateQueries({ queryKey: ["topic"] }); qc.invalidateQueries({ queryKey: ["home"] }); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const items = (x?.contents ?? []).filter((it) => {
    if (tab === "todos") return true;
    if (tab === "pdf") return (it.type === "material" || it.type === "pdf") && !!it.data.pdf_url;
    if (tab === "simulado") return false;
    return it.type === tab;
  });
  const count = (k: TopicTab) => {
    if (k === "todos") return x?.contents.length ?? 0;
    if (k === "pdf") return x?.contents.filter((it) => (it.type === "material" || it.type === "pdf") && !!it.data.pdf_url).length ?? 0;
    if (k === "simulado") return 0;
    return x?.contents.filter((it) => it.type === k).length ?? 0;
  };
  const isPremiumFeature = (k: TopicTab) => k === "questao" || k === "simulado";
  const canPremium = !!me.data && me.data.plan === "premium";
  return (
    <div className="animate-fade-up">
      <Crumbs items={[{ label: "Cursos", to: "/cursos" }, { label: x?.course.name ?? "…", to: `/cursos/${c}` }, { label: x?.period.name ?? "…" },
        { label: x?.discipline.name ?? "…", to: `/cursos/${c}/${p}/${d}` }, { label: x?.topic.name ?? "…" }]} />
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 data-testid="topic-title" className="text-3xl font-extrabold tracking-tight">{x?.topic.name ?? "Carregando…"}</h1>
          <p className="mt-1 text-slate-600">{x?.discipline.name} · {x?.period.name} · {x?.course.name}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {me.data && !me.isError && x && <Button variant="outline" onClick={()=>toggleTopicFav.mutate()} disabled={toggleTopicFav.isPending} aria-label={isTopicFav?"Remover assunto dos favoritos":"Favoritar assunto"} className="rounded-xl">{isTopicFav?<BookmarkCheck className="size-4 text-brand"/>:<Bookmark className="size-4"/>}{isTopicFav?"Favoritado":"Favoritar assunto"}</Button>}
          {me.data && !me.isError && x && (
            <Button data-testid="topic-complete-button" variant={x.completed ? "secondary" : "default"} onClick={() => toggle.mutate()} disabled={toggle.isPending} className="rounded-xl">
              {x.completed ? <CheckCircle2 className="size-4 text-brand" /> : <Circle className="size-4" />} {x.completed ? "Concluído" : "Marcar como concluído"}
            </Button>
          )}
        </div>
      </div>
      {x && <section className="mt-6 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-brand-dark">Sobre este conteúdo</p>
        <p className="mt-2 whitespace-pre-line text-sm leading-6 text-slate-700">{x.topic.description || `Estude ${x.topic.name}, com conceitos fundamentais, aplicações e materiais selecionados para a disciplina ${x.discipline.name}.`}</p>
      </section>}
      {x && <StudySessionCard topicId={x.topic.id} />}
      <div className="no-scrollbar -mx-4 mt-6 flex gap-2 overflow-x-auto px-4 pb-1">
        {TABS.map((k) => (
          <button key={k} data-testid={`topic-tab-${k}`} onClick={() => { if (isPremiumFeature(k) && !canPremium) { toast.error("Este recurso está disponível no Premium."); return; } setTab(k); }}
            className={cn("shrink-0 rounded-full border px-4 py-2 text-sm font-medium transition-colors duration-150",
              tab === k ? "border-brand bg-brand text-white" : "border-slate-200 bg-white text-slate-600 hover:border-brand/40",
              isPremiumFeature(k) && !canPremium && "opacity-70")}>
            {tabLabel(k, count(k))}{isPremiumFeature(k) && !canPremium ? " 🔒" : ""}
          </button>
        ))}
      </div>
      <div className="mt-6">
        {q.isLoading && <Skeleton />}
        {q.isError && <Unavailable what="este assunto" />}
        {x && tab === "simulado" && canPremium && (
          <div className="mb-4 rounded-2xl border border-emerald-200 bg-emerald-50 p-4"><p className="font-semibold text-emerald-900">Simulado deste assunto</p><p className="mt-1 text-sm text-emerald-800">Use o botão abaixo para gerar um simulado com questões publicadas para este assunto.</p><Button className="mt-3 rounded-xl" onClick={async () => { try { const exam = await apiPost<any>("/exams", { source:"banco", discipline_id:x.discipline.id, topic_id:x.topic.id, difficulty:"", count:20, item_id:null }); window.location.href=`/simulados?exame=${exam.id}`; } catch(e) { toast.error(errMsg(e)); } }}>Começar simulado</Button></div>
        )}
        {x && items.length === 0 && tab !== "simulado" && (
          <p data-testid="topic-empty" className="rounded-2xl border border-dashed border-slate-300 bg-white p-6 text-sm text-slate-500">
            {`Ainda não há ${tab === "todos" ? "conteúdos" : TYPE_PLURAL[tab].toLowerCase()} publicados neste assunto.`}
          </p>
        )}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((it) => <ContentCard key={it.id} c={it} saved={x?.favorite_ids.includes(it.id)} />)}
        </div>
      </div>
    </div>
  );
}
