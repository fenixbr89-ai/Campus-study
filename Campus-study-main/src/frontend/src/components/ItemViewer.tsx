import { useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { HelpCircle } from "lucide-react";
import { apiPost } from "@/lib/api";
import { errMsg } from "@/lib/hooks";
import type { Exam, UserItem } from "@/lib/types";
import { Button, buttonVariants } from "@/components/ui/button";
import { Markdown } from "./Markdown";

export function useStartExamFromItem() {
  const nav = useNavigate();
  return useMutation({
    mutationFn: (item: UserItem) => apiPost<Exam>("/exams", {
      source: "item", item_id: item.id, count: item.data.questions?.length ?? 10, discipline_id: null, topic_id: null, difficulty: "",
    }),
    onSuccess: (e) => nav(`/simulados?exame=${e.id}`),
    onError: (e) => toast.error(errMsg(e)),
  });
}

// Renders any personal library item (AI-generated or user-created).
export function ItemViewer({ item }: { item: UserItem }) {
  const start = useStartExamFromItem();
  const d = item.data;
  return (
    <div data-testid={`item-viewer-${item.kind}`} className="space-y-3">
      {d.source && <p className="text-xs text-slate-500">Origem: {d.source}</p>}
      {(item.kind === "resumo" || item.kind === "plano") && <Markdown text={d.body ?? ""} />}
      {item.kind === "pdf" && <p className="text-sm text-slate-600">PDF “{d.filename}” com {d.chars?.toLocaleString("pt-BR")} caracteres extraídos.</p>}
      {item.kind === "questoes" && (
        <>
          <ol className="list-decimal space-y-3 pl-5 text-sm">
            {d.questions?.map((q, i) => (
              <li key={i}>
                <p className="font-medium">{q.statement}</p>
                <ul className="mt-1 text-slate-600">{q.options.map((o, j) => <li key={j}>{String.fromCharCode(65 + j)}) {o}</li>)}</ul>
              </li>
            ))}
          </ol>
          <Button data-testid="item-start-exam-button" onClick={() => start.mutate(item)} disabled={start.isPending} className="rounded-xl">
            <HelpCircle className="size-4" /> Fazer como simulado
          </Button>
        </>
      )}
    </div>
  );
}
