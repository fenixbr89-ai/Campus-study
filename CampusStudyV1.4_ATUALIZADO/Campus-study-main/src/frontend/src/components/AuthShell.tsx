import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { BookOpenCheck, Brain, PlayCircle } from "lucide-react";
import { Brand } from "./Brand";

export function AuthShell({ children, title, subtitle }: { children: ReactNode; title: string; subtitle?: string }) {
  return (
    <div className="grid min-h-screen lg:grid-cols-[1.05fr_1fr]">
      <aside className="relative hidden overflow-hidden bg-gradient-to-br from-emerald-50 via-green-50 to-white p-12 lg:flex lg:flex-col">
        <Brand />
        <div className="my-auto max-w-md">
          <h2 className="text-4xl leading-tight font-extrabold tracking-tight text-slate-900">
            Estude com foco. <span className="text-brand">Aprenda de verdade.</span>
          </h2>
          <ul className="mt-8 space-y-4 text-slate-700">
            {[
              [PlayCircle, "Videoaulas e artigos científicos grátis, para sempre"],
              [BookOpenCheck, "Tudo organizado por curso, período, disciplina e assunto"],
              [Brain, "Simulados e mapas mentais inclusos"],
            ].map(([Icon, text], i) => {
              const I = Icon as typeof PlayCircle;
              return (
                <li key={i} className="flex items-center gap-3">
                  <span className="grid size-10 place-items-center rounded-xl bg-white text-brand-dark shadow-sm"><I className="size-5" /></span>
                  {text as string}
                </li>
              );
            })}
          </ul>
        </div>
        <img src="https://images.unsplash.com/photo-1531545514256-b1400bc00f31?crop=entropy&cs=srgb&fm=jpg&q=70&w=900" alt="Estudantes universitários estudando juntos"
          className="absolute -right-24 -bottom-24 h-80 w-[28rem] rotate-[-6deg] rounded-3xl object-cover opacity-90 shadow-2xl" />
      </aside>
      <main className="flex flex-col px-5 py-8 sm:px-10">
        <div className="lg:hidden"><Brand /></div>
        <div className="mx-auto my-auto w-full max-w-md animate-fade-up py-10">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">{title}</h1>
          {subtitle && <p className="mt-2 text-slate-600">{subtitle}</p>}
          <div className="mt-8">{children}</div>
        </div>
        <p className="text-center text-xs text-slate-400">
          <Link to="/termos-de-uso" className="hover:text-brand-dark">Termos de Uso</Link> ·{" "}
          <Link to="/politica-de-privacidade" className="hover:text-brand-dark">Política de Privacidade</Link>
        </p>
      </main>
    </div>
  );
}
