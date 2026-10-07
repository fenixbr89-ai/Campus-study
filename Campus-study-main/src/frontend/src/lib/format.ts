import type { ContentType, MindNode } from "./types";

export function maskCpf(value: string): string {
  const d = value.replace(/\D/g, "").slice(0, 11);
  return d
    .replace(/(\d{3})(\d)/, "$1.$2")
    .replace(/(\d{3})\.(\d{3})(\d)/, "$1.$2.$3")
    .replace(/(\d{3})\.(\d{3})\.(\d{3})(\d)/, "$1.$2.$3-$4");
}

export function isValidCpf(value: string): boolean {
  const cpf = value.replace(/\D/g, "");
  if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) return false;
  for (const size of [9, 10]) {
    let total = 0;
    for (let i = 0; i < size; i++) total += Number(cpf[i]) * (size + 1 - i);
    let digit = (total * 10) % 11;
    if (digit === 10) digit = 0;
    if (digit !== Number(cpf[size])) return false;
  }
  return true;
}

export function formatDate(iso: string | null | undefined, withTime = false): string {
  if (!iso) return "—";
  const d = new Date(iso.endsWith("Z") || iso.includes("+") ? iso : `${iso}Z`);
  return d.toLocaleString("pt-BR", withTime ? { dateStyle: "short", timeStyle: "short" } : { dateStyle: "short" });
}

export const TYPE_LABELS: Record<ContentType, string> = {
  video: "Videoaula",
  pdf: "PDF",
  livro: "Livro",
  artigo: "Artigo científico",
  resumo: "Resumo",
  questao: "Questão",
  material: "Material",
};

export const TYPE_PLURAL: Record<ContentType, string> = {
  video: "Videoaulas",
  pdf: "PDFs",
  livro: "Livros",
  artigo: "Artigos científicos",
  resumo: "Resumos",
  questao: "Questões",
  material: "Materiais",
};

export const DIFF_LABELS: Record<string, string> = { "": "Todas", facil: "Fácil", medio: "Média", dificil: "Difícil" };
export const STATUS_LABELS: Record<string, string> = { publicado: "Publicado", rascunho: "Rascunho", arquivado: "Arquivado" };

export function minutesLabel(min: number): string {
  if (min < 60) return `${min} min`;
  return `${Math.floor(min / 60)}h${min % 60 ? ` ${min % 60}min` : ""}`;
}

// Mind maps are edited as indented text: two spaces per level.
export function mindToText(node: MindNode, depth = 0): string {
  return [`${"  ".repeat(depth)}${node.label}`, ...node.children.map((c) => mindToText(c, depth + 1))].join("\n");
}

export function textToMind(text: string): MindNode {
  const lines = text.split("\n").filter((l) => l.trim());
  const root: MindNode = { label: lines[0]?.trim() || "Tema central", children: [] };
  const stack: { node: MindNode; depth: number }[] = [{ node: root, depth: 0 }];
  for (const line of lines.slice(1)) {
    const depth = Math.max(1, Math.floor((line.length - line.trimStart().length) / 2));
    const node: MindNode = { label: line.trim(), children: [] };
    while (stack.length > 1 && stack[stack.length - 1].depth >= depth) stack.pop();
    stack[stack.length - 1].node.children.push(node);
    stack.push({ node, depth });
  }
  return root;
}
