import { useEffect } from "react";
import { Link, NavLink, Outlet, useLocation } from "react-router-dom";
import {
  BookOpen,
  GraduationCap,
  HelpCircle,
  LayoutDashboard,
  LogOut,
  Network,
  ShieldCheck,
  LifeBuoy,
  Trophy,
  Upload,
  User,
  Star,
  RotateCcw,
} from "lucide-react";
import { apiPost, apiAssetUrl } from "@/lib/api";
import { isAdmin, useMe } from "@/lib/hooks";
import { endSession } from "@/lib/session";
import { buttonVariants } from "@/components/ui/button";
import { Brand, Footer } from "./Brand";
import { cn } from "@/lib/utils";
import PwaInstallPrompt from "./PwaInstallPrompt";

const SECTIONS = [
  {
    title: "Principal",
    items: [
      {
        label: "Início",
        icon: LayoutDashboard,
        to: "/inicio",
        id: "inicio",
      },
      {
        label: "Cursos",
        icon: GraduationCap,
        to: "/cursos",
        id: "cursos",
      },
      {
        label: "Minha Biblioteca",
        icon: BookOpen,
        to: "/biblioteca",
        id: "biblioteca",
      },
    ],
  },
  {
    title: "Estudo ativo",
    items: [
      {
        label: "Simulados",
        icon: HelpCircle,
        to: "/simulados",
        id: "simulados",
      },
      {
        label: "Plano de estudos",
        icon: Trophy,
        to: "/meu-plano",
        id: "meu-plano",
      },
      {
        label: "Anotações",
        icon: BookOpen,
        to: "/anotacoes",
        id: "anotacoes",
      },
      {
        label: "Revisar questões",
        icon: RotateCcw,
        to: "/revisao",
        id: "revisao",
      },
      {
        label: "Notificações",
        icon: HelpCircle,
        to: "/notificacoes",
        id: "notificacoes",
      },
      {
        label: "Ranking",
        icon: Trophy,
        to: "/ranking",
        id: "ranking",
      },
    ],
  },
  {
    title: "Minha conta",
    items: [
      {
        label: "Meu progresso",
        icon: Trophy,
        to: "/progresso",
        id: "progresso",
      },
      {
        label: "Enviar conteúdo",
        icon: Upload,
        to: "/enviar-conteudo",
        id: "enviar-conteudo",
      },
      {
        label: "Perfil",
        icon: User,
        to: "/perfil",
        id: "perfil",
      },
      {
        label: "Suporte",
        icon: LifeBuoy,
        to: "/suporte",
        id: "suporte",
      },
      {
        label: "Premium",
        icon: Star,
        to: "/planos",
        id: "planos",
      },
    ],
  },
];

const MOBILE = [
  {
    label: "Início",
    icon: LayoutDashboard,
    to: "/inicio",
    id: "inicio",
  },
  {
    label: "Cursos",
    icon: GraduationCap,
    to: "/cursos",
    id: "cursos",
  },
  {
    label: "Ranking",
    icon: Trophy,
    to: "/ranking",
    id: "ranking",
  },
  {
    label: "Perfil",
    icon: User,
    to: "/perfil",
    id: "perfil",
  },
  {
    label: "Premium",
    icon: Star,
    to: "/planos",
    id: "planos",
  },
];

const ADMIN_MOBILE = {
  label: "Admin",
  icon: ShieldCheck,
  to: "/admin",
  id: "admin",
};

export default function AppLayout() {
  const me = useMe();
  const user = me.data && !me.isError ? me.data : undefined;
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  // Only a real study session is counted. While visible, flush the active session every 15s.
  // When the tab is hidden, stop the session so background time cannot inflate the ranking.
  useEffect(() => {
    if (!user || isAdmin(user)) return;
    let stopped = false;
    const beat = async () => {
      if (stopped || document.visibilityState !== "visible") return;
      try {
        const res = await fetch("/api/study-sessions/active", { credentials: "include" });
        const session = res.ok ? await res.json() : null;
        if (session?.id) await apiPost(`/study-sessions/${session.id}/heartbeat`);
      } catch { /* session may have ended */ }
    };
    const timer = window.setInterval(beat, 15000);
    void beat();
    const onVisibility = () => {
      if (document.visibilityState === "hidden") {
        fetch("/api/study-sessions/active", { credentials: "include" }).then(r => r.ok ? r.json() : null).then(session => {
          if (session?.id) return apiPost(`/study-sessions/${session.id}/stop`).catch(() => undefined);
          return undefined;
        }).catch(() => undefined);
      } else {
        void beat();
      }
    };
    document.addEventListener("visibilitychange", onVisibility);
    return () => { stopped = true; window.clearInterval(timer); document.removeEventListener("visibilitychange", onVisibility); };
  }, [user]);

  return (
    <div className="min-h-screen bg-background">
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 flex-col border-r border-emerald-100 bg-lime-50 lg:flex">
        <div className="px-5 py-5">
          <Brand to={user ? "/inicio" : "/"} />
        </div>

        <nav className="flex-1 space-y-6 overflow-y-auto px-3 pb-6">
          {SECTIONS.map((s) => (
            <div key={s.title}>
              <p className="px-3 pb-2 text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
                {s.title}
              </p>

              {s.items.map((it) => (
                <NavLink
                  key={it.to}
                  to={it.to}
                  data-testid={`sidebar-nav-${it.id}`}
                  className={({ isActive }) =>
                    cn(
                      "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors duration-150",
                      isActive
                        ? "bg-brand-soft text-brand-dark"
                        : "text-slate-600 hover:bg-slate-50 hover:text-slate-900",
                    )
                  }
                >
                  <it.icon className="size-[18px]" />
                  {it.label}
                </NavLink>
              ))}
            </div>
          ))}

          {isAdmin(user) && (
            <NavLink
              to="/admin"
              data-testid="sidebar-nav-admin"
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors duration-150",
                  isActive
                    ? "bg-emerald-600 text-white"
                    : "text-slate-600 hover:bg-emerald-50",
                )
              }
            >
              <ShieldCheck className="size-[18px]" />
              Painel Admin
            </NavLink>
          )}
        </nav>

        {user && (
          <div className="border-t border-slate-200 p-4">
            <div className="flex items-center gap-3">
              {user.avatar_url ? <img src={apiAssetUrl(user.avatar_url)} alt="" className="size-9 rounded-full object-cover" /> : <span className="grid size-9 place-items-center rounded-full bg-brand-mint font-semibold text-brand-dark">{user.name[0]}</span>}

              <div className="min-w-0 flex-1">
                <p
                  data-testid="sidebar-user-name"
                  className="truncate text-sm font-semibold"
                >
                  {user.name}
                </p>

                <p
                  data-testid="sidebar-user-plan"
                  className="text-xs text-slate-500"
                >
                  {isAdmin(user) ? "Administrador" : user.plan === "premium" || user.trial_active ? "Acesso completo" : "Plano Limitado"}
                </p>
              </div>

              <button
                data-testid="sidebar-logout-button"
                aria-label="Sair"
                onClick={() => endSession("/")}
                className="rounded-lg p-2 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700"
              >
                <LogOut className="size-4" />
              </button>
            </div>
          </div>
        )}
      </aside>

      <header className="sticky top-0 z-30 flex items-center justify-between border-b border-emerald-100 bg-emerald-50/95 px-4 py-3 backdrop-blur-md lg:hidden">
        <Brand to={user ? "/inicio" : "/"} />

        {user ? (
          <Link
            to="/biblioteca"
            data-testid="mobile-header-library-link"
            className="rounded-xl p-2 text-slate-600 hover:bg-slate-100"
            aria-label="Minha Biblioteca"
          >
            <BookOpen className="size-5" />
          </Link>
        ) : (
          <Link
            to="/entrar"
            data-testid="mobile-header-login-link"
            className={buttonVariants({
              size: "sm",
              className: "rounded-lg",
            })}
          >
            Entrar
          </Link>
        )}
      </header>

      {!user && !me.isLoading && (
        <div className="hidden border-b border-slate-200 bg-white/90 px-8 py-3 backdrop-blur-md lg:ml-64 lg:flex lg:items-center lg:justify-end lg:gap-3">
          <span className="text-sm text-slate-500">
            Crie sua conta grátis para salvar materiais e acompanhar seu
            progresso.
          </span>

          <Link
            to="/entrar"
            data-testid="topbar-login-link"
            className={buttonVariants({
              variant: "outline",
              size: "sm",
            })}
          >
            Entrar
          </Link>

          <Link
            to="/criar-conta"
            data-testid="topbar-register-link"
            className={buttonVariants({
              size: "sm",
            })}
          >
            Criar conta
          </Link>
        </div>
      )}

      <main className="px-4 pt-5 pb-28 sm:px-6 lg:ml-64 lg:px-10 lg:pt-8 lg:pb-5">
        <div className="mx-auto max-w-6xl">
          <div className="mb-4"><PwaInstallPrompt /></div>
          <Outlet />
          <Footer />
        </div>
      </main>

      <nav
        data-testid="mobile-bottom-nav"
        className="safe-pb fixed inset-x-0 bottom-0 z-50 flex items-center justify-around border-t border-emerald-100 bg-emerald-50/95 px-2 backdrop-blur-md lg:hidden"
      >
        {(isAdmin(user) ? [...MOBILE, ADMIN_MOBILE] : MOBILE).map((it) => (
          <NavLink
            key={it.to}
            to={it.to}
            data-testid={`bottom-nav-${it.id}`}
            className={({ isActive }) =>
              cn(
                "flex min-h-16 min-w-0 flex-1 flex-col items-center justify-center gap-1 text-[11px] font-medium transition-colors duration-150",
                isActive ? "text-brand-dark" : "text-slate-500",
              )
            }
          >
            {({ isActive }) => (
              <>
                <span
                  className={cn(
                    "grid h-7 w-12 place-items-center rounded-full transition-colors duration-150",
                    isActive && "bg-brand-mint",
                  )}
                >
                  <it.icon className="size-5" />
                </span>

                {it.label}
              </>
            )}
          </NavLink>
        ))}
      </nav>
    </div>
  );
      }
