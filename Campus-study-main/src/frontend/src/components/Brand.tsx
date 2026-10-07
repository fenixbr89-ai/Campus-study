import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";

export function Brand({ className, to = "/" }: { className?: string; to?: string }) {
  return (
    <Link to={to} data-testid="brand-logo-link" className={cn("flex items-center gap-2.5 font-heading", className)}>
      <img
        src="/campus-study-logo.png"
        alt="Campus Study"
        className="size-9 rounded-xl object-cover shadow-sm shadow-green-600/20"
      />
      <span className="text-lg font-bold tracking-tight text-slate-900">
        Campus <span className="text-brand">Study</span>
      </span>
    </Link>
  );
}


export function Footer() {
  return (
    <footer data-testid="site-footer" className="mt-16 border-t border-slate-200 pt-8 pb-5 text-sm text-slate-500">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p>© {new Date().getFullYear()} Campus Study. Todos os direitos reservados.</p>
        <nav className="flex flex-wrap gap-4">
          <Link data-testid="footer-terms-link" to="/termos-de-uso" className="hover:text-brand-dark">Termos de Uso</Link>
          <Link data-testid="footer-privacy-link" to="/politica-de-privacidade" className="hover:text-brand-dark">Política de Privacidade</Link>
          <Link data-testid="footer-about-link" to="/quem-somos" className="hover:text-brand-dark">Quem somos</Link>
          <Link data-testid="footer-status-link" to="/status" className="hover:text-brand-dark">Status do sistema</Link>
        </nav>
      </div>
      <p className="mt-3 text-xs text-slate-400">
        As grades curriculares apresentadas são referências e podem variar de uma instituição de ensino para outra.
      </p>
    </footer>
  );
}

export function FooterCredit() {
  return <p data-testid="footer-credit" className="text-xs text-slate-400">© {new Date().getFullYear()} Campus Study · Plataforma de estudos universitários.</p>;
}
