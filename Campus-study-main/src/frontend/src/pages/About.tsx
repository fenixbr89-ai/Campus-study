import { BookOpen, CheckCircle2, HeartHandshake, ShieldCheck, Target, Users } from "lucide-react";
import { Link } from "react-router-dom";
import { usePageMeta } from "@/lib/hooks";
import { Button } from "@/components/ui/button";

const sections = [
  { icon: Users, title: "Quem somos", text: "O Campus Study é uma plataforma de estudos universitários criada para reunir, em um só lugar, organização, materiais de estudo, questões, simulados e ferramentas que ajudam o estudante a manter uma rotina acadêmica mais consistente." },
  { icon: Target, title: "Nosso objetivo", text: "Nosso objetivo é tornar o estudo mais simples de organizar e mais fácil de acompanhar, ajudando o estudante a encontrar conteúdo, praticar, revisar e acompanhar sua evolução sem precisar depender de várias ferramentas separadas." },
  { icon: BookOpen, title: "O que oferecemos", text: "A plataforma reúne cursos, videoaulas, PDFs, resumos e, conforme o plano, questões, simulados, artigos científicos, mapas mentais e outras ferramentas de apoio ao estudo." },
  { icon: HeartHandshake, title: "Por que existem planos pagos?", text: "Manter uma plataforma desse tipo envolve infraestrutura, armazenamento, desenvolvimento, segurança, processamento, manutenção, suporte e produção contínua de recursos. Os planos pagos ajudam a sustentar esses custos e permitem que a plataforma continue evoluindo." },
  { icon: ShieldCheck, title: "Nosso compromisso", text: "Queremos construir uma experiência útil, transparente e segura. Por isso, mantemos canais para que estudantes relatem problemas, enviem sugestões e acompanhem respostas da equipe." },
];

export default function AboutPage() {
  usePageMeta("Quem somos", "Conheça o Campus Study, nossos objetivos e como a plataforma funciona.");
  return <div className="animate-fade-up space-y-8">
    <section className="rounded-3xl border border-emerald-100 bg-gradient-to-br from-emerald-50 via-white to-white p-7 sm:p-10">
      <p className="text-sm font-semibold text-brand-dark">Sobre o Campus Study</p>
      <h1 className="mt-2 text-3xl font-extrabold tracking-tight sm:text-4xl">Estudar com mais organização, prática e acompanhamento.</h1>
      <p className="mt-4 max-w-3xl text-slate-600">O Campus Study foi pensado para colocar o estudante no centro da experiência: encontrar o que precisa, estudar no próprio ritmo, praticar com questões e simulados e acompanhar sua evolução.</p>
    </section>
    <div className="grid gap-5 md:grid-cols-2">
      {sections.map(({ icon: Icon, title, text }) => <article key={title} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"><div className="grid size-11 place-items-center rounded-2xl bg-brand-soft text-brand-dark"><Icon className="size-6" /></div><h2 className="mt-4 text-xl font-bold">{title}</h2><p className="mt-2 leading-7 text-slate-600">{text}</p></article>)}
    </div>
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-xl font-bold">Transparência e melhoria contínua</h2>
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        {["Relate erros que encontrar na plataforma.", "Envie sugestões de novas funções ou melhorias.", "Acompanhe suas solicitações pelo próprio aplicativo.", "Receba notificações por e-mail quando houver atualização do chamado."].map(t => <div key={t} className="flex gap-3 text-sm text-slate-600"><CheckCircle2 className="mt-0.5 size-5 shrink-0 text-brand" />{t}</div>)}
      </div>
      <div className="mt-6 flex flex-wrap gap-3"><Link to="/suporte"><Button className="rounded-xl">Enviar erro ou sugestão</Button></Link><Link to="/termos-de-uso"><Button variant="outline" className="rounded-xl">Termos de Uso</Button></Link></div>
    </section>
  </div>;
}
