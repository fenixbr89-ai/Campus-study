import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { Bookmark, BookmarkCheck, ExternalLink, FileText, PlayCircle } from "lucide-react";
import { apiPost, apiAssetUrl } from "@/lib/api";
import { errMsg, useMe } from "@/lib/hooks";
import { DIFF_LABELS, TYPE_LABELS } from "@/lib/format";
import type { Content, Message } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Markdown } from "./Markdown";

export function useFavorite() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (content_id: string) => apiPost<Message>("/favorites", { content_id }),
    onSuccess: (r) => {
      toast.success(r.message);
      qc.invalidateQueries({ queryKey: ["favorites"] });
      qc.invalidateQueries({ queryKey: ["topic"] });
    },
    onError: (e) => toast.error(errMsg(e)),
  });
}

function ContentBody({ c }: { c: Content }) {
  const [revealed, setRevealed] = useState<number | null>(null);
  const d = c.data;
  switch (c.type) {
    case "video":
      return (
        <div className="space-y-3">
          <div className="aspect-video overflow-hidden rounded-2xl bg-slate-900">
            <iframe data-testid="video-player-iframe" className="size-full" src={`https://www.youtube-nocookie.com/embed/${d.video_id}`}
              title={c.title} allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen />
          </div>
          {d.channel && <p className="text-sm text-slate-500">Canal: <strong>{d.channel}</strong></p>}
          {c.description && <p className="text-sm text-slate-700">{c.description}</p>}
          <a href={d.url} target="_blank" rel="noopener noreferrer" data-testid="video-open-youtube-link" className="inline-flex items-center gap-1 text-sm font-semibold text-brand-dark">
            Abrir no YouTube <ExternalLink className="size-3.5" />
          </a>
        </div>
      );
    case "pdf":
      return (
        <div className="space-y-3 text-sm text-slate-700">
          <p>{d.file_name || c.title}</p>
          {d.pdf_url ? <a href={apiAssetUrl(d.pdf_url)} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 font-semibold text-brand-dark">Abrir PDF <ExternalLink className="size-3.5" /></a> : <p className="text-slate-500">PDF sem link cadastrado.</p>}
        </div>
      );
    case "livro":
      return (
        <div className="space-y-3 text-sm text-slate-700">
          {d.authors && <p><strong>Autor(es):</strong> {d.authors}</p>}
          {d.year && <p><strong>Ano:</strong> {d.year}</p>}
          {d.publisher && <p><strong>Editora:</strong> {d.publisher}</p>}
          {d.isbn && <p><strong>ISBN:</strong> {d.isbn}</p>}
          {d.url && <a href={d.url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 font-semibold text-brand-dark">Abrir referência <ExternalLink className="size-3.5" /></a>}
        </div>
      );
    case "artigo":
      return (
        <div className="space-y-3 text-sm text-slate-700">
          <p><strong>Autores:</strong> {d.authors || "—"}</p>
          <p><strong>Ano:</strong> {d.year || "—"} · <strong>Fonte:</strong> {d.journal || "—"}</p>
          {d.doi && <p><strong>DOI:</strong> {d.doi}</p>}
          {d.abstract && <div className="rounded-xl bg-slate-50 p-4"><p className="mb-1 font-semibold">Resumo</p>{d.abstract}</div>}
          {d.keywords && <p><strong>Palavras-chave:</strong> {d.keywords}</p>}
          {(d.url || d.doi) && (
            <a href={d.url || `https://doi.org/${d.doi}`} target="_blank" rel="noopener noreferrer" data-testid="article-open-link" className="inline-flex items-center gap-1 font-semibold text-brand-dark">
              Acessar artigo na fonte original <ExternalLink className="size-3.5" />
            </a>
          )}
        </div>
      );
    case "questao":
      return (
        <div className="space-y-2">
          <p className="font-medium text-slate-900">{(d as { statement?: string }).statement || c.title}</p>
          {d.options?.map((o, i) => (
            <button key={i} data-testid={`question-option-${i}`} onClick={() => setRevealed(i)}
              className={`block w-full rounded-xl border px-4 py-2.5 text-left text-sm transition-colors duration-150 ${
                revealed === null ? "border-slate-200 hover:border-brand hover:bg-brand-soft"
                  : i === d.correct_index ? "border-green-500 bg-green-50" : i === revealed ? "border-red-400 bg-red-50" : "border-slate-200 opacity-60"}`}>
              <strong className="mr-2">{String.fromCharCode(65 + i)})</strong>{o}
            </button>
          ))}
          {revealed !== null && (
            <div data-testid="question-explanation" className="rounded-xl bg-slate-50 p-4 text-sm">
              <p className="font-semibold">{revealed === d.correct_index ? "Resposta correta! 🎉" : `Resposta correta: ${String.fromCharCode(65 + (d.correct_index ?? 0))}`}</p>
              <p className="mt-1 text-slate-600">{d.explanation}</p>
            </div>
          )}
        </div>
      );
    case "material":
      if (d.pdf_url) return (
        <div className="space-y-3">
          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-slate-100">
            <iframe data-testid="pdf-viewer-iframe" src={apiAssetUrl(d.pdf_url)} title={c.title} className="h-[65vh] w-full" />
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <a href={apiAssetUrl(d.pdf_url)} download={d.file_name || "material.pdf"} className="inline-flex items-center gap-1.5 rounded-xl bg-brand px-3 py-2 text-sm font-semibold text-white hover:bg-brand-dark">Baixar PDF</a>
            <span className="text-xs text-slate-500">O PDF é aberto dentro do Campus Study.</span>
          </div>
        </div>
      );
      return (
        <div>
          <Markdown text={d.body || c.description} />
          {d.url && <a href={d.url} target="_blank" rel="noopener noreferrer" className="mt-2 inline-flex items-center gap-1 text-sm font-semibold text-brand-dark">Abrir material <ExternalLink className="size-3.5" /></a>}
        </div>
      );
    default:
      return <Markdown text={d.body || c.description} />;
  }
}

export function ContentCard({ c, saved, compact = false }: { c: Content; saved?: boolean; compact?: boolean }) {
  const [open, setOpen] = useState(false);
  const me = useMe();
  const fav = useFavorite();
  const openIt = () => {
    setOpen(true);
    apiPost("/contents/" + c.id + "/view").catch(() => undefined);
  };
  const thumb = c.type === "video" ? c.data.thumbnail : undefined;
  return (
    <>
      <article data-testid={`content-card-${c.id}`}
        className={`group flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition-[transform,box-shadow] duration-200 hover:-translate-y-1 hover:shadow-md ${compact ? "w-64 shrink-0 snap-start sm:w-72" : ""}`}>
        <button onClick={openIt} data-testid={`content-open-${c.id}`} className="text-left">
          {thumb ? (
            <div className="relative aspect-video bg-slate-100">
              <img src={thumb} alt="" loading="lazy" className="size-full object-cover" />
              <PlayCircle className="absolute inset-0 m-auto size-12 text-white/90 drop-shadow transition-transform duration-200 group-hover:scale-110" />
            </div>
          ) : (
            <div className="flex h-24 items-center gap-3 bg-gradient-to-br from-emerald-50 to-white px-4">
              <span className="grid size-10 place-items-center rounded-xl bg-white text-brand-dark shadow-sm">
                <FileText className="size-5" />
              </span>
              <span className="text-xs font-semibold tracking-wide text-brand-dark uppercase">{TYPE_LABELS[c.type]}</span>
            </div>
          )}
          <div className="p-4 pb-2">
            <div className="mb-2 flex flex-wrap gap-1.5">
              <Badge variant="secondary" className="rounded-md">{TYPE_LABELS[c.type]}</Badge>
              {c.difficulty && <Badge variant="outline" className="rounded-md">{DIFF_LABELS[c.difficulty]}</Badge>}
            </div>
            <h3 className="line-clamp-2 font-sans text-[15px] font-semibold text-slate-900">{c.title}</h3>
            <p className="mt-1 line-clamp-1 text-xs text-slate-500">{c.discipline_name} · {c.topic_name}</p>
          </div>
        </button>
        <div className="mt-auto flex items-center justify-between px-4 pb-3">
          <Link to={c.path} data-testid={`content-topic-link-${c.id}`} className="text-xs font-medium text-slate-500 hover:text-brand-dark">{c.course_name}</Link>
          {me.data && !me.isError && (
            <button data-testid={`content-save-${c.id}`} aria-label="Salvar" onClick={() => fav.mutate(c.id)}
              className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-brand-soft hover:text-brand-dark">
              {saved ? <BookmarkCheck className="size-4 text-brand-dark" /> : <Bookmark className="size-4" />}
            </button>
          )}
        </div>
      </article>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl" data-testid="content-dialog">
          <DialogHeader>
            <DialogTitle className="pr-6 font-heading text-lg">{c.title}</DialogTitle>
            <DialogDescription>{c.course_name} · {c.period_name} · {c.discipline_name} · {c.topic_name}</DialogDescription>
          </DialogHeader>
          <ContentBody c={c} />
          {me.data && !me.isError && (
            <Button variant="outline" data-testid="content-dialog-save-button" onClick={() => fav.mutate(c.id)}>
              {saved ? <BookmarkCheck className="size-4" /> : <Bookmark className="size-4" />} {saved ? "Remover dos salvos" : "Salvar na biblioteca"}
            </Button>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}

export function Row({ title, items, testId, empty }: { title: string; items: Content[]; testId: string; empty: string }) {
  return (
    <section data-testid={testId} className="mt-10">
      <h2 className="mb-4 text-xl font-bold tracking-tight">{title}</h2>
      {items.length === 0 ? (
        <p className="rounded-2xl border border-dashed border-slate-300 bg-white p-6 text-sm text-slate-500">{empty}</p>
      ) : (
        <div className="no-scrollbar -mx-4 flex snap-x snap-mandatory gap-4 overflow-x-auto px-4 pb-2 scroll-smooth">
          {items.map((c) => <ContentCard key={c.id} c={c} compact />)}
        </div>
      )}
    </section>
  );
}
