import type { ReactNode } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import AppLayout from "@/components/AppLayout";
import { useMe } from "@/lib/hooks";

import Home from "@/pages/Home";
import AdminPage from "@/pages/Admin";

import {
  AccessPage,
  ForgotPasswordPage,
  LoginPage,
  RegisterPage,
  ResetPasswordPage,
} from "@/pages/Auth";

import { PrivacyPage, TermsPage } from "@/pages/Legal";

import {
  CoursePage,
  CoursesPage,
  DisciplinePage,
  TopicPage,
} from "@/pages/Catalog";

import {
  ExamsPage,
  MindMapsPage,
} from "@/pages/Study";

import {
  LibraryPage,
  ProfilePage,
  ProgressPage,
  SubmitPage,
} from "@/pages/Account";

import {
  NotesPage,
  PlanPage,
  NotificationsPage,
  RankingPage,
  GlobalSearchPage,
  StudyHistoryPage,
  WeeklyGoalsPage,
  CalendarPage,
  ReviewsPage,
} from "@/pages/StudentTools";

import PlansPage from "@/pages/Plans";
import CheckoutPage from "@/pages/Checkout";

function RequireAuth({ children }: { children: ReactNode }) {
  const me = useMe();
  const loc = useLocation();

  if (me.isLoading) {
    return (
      <div className="h-40 animate-pulse rounded-3xl bg-slate-200/60" />
    );
  }

  if (me.isError || !me.data) {
    return (
      <Navigate
        to="/entrar"
        replace
        state={{ from: loc.pathname }}
      />
    );
  }

  return <>{children}</>;
}

const auth = (el: ReactNode) => <RequireAuth>{el}</RequireAuth>;

export default function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<AccessPage />} />

        <Route path="/entrar" element={<LoginPage />} />

        <Route path="/criar-conta" element={<RegisterPage />} />

        <Route
          path="/esqueci-minha-senha"
          element={<ForgotPasswordPage />}
        />

        <Route
          path="/redefinir-senha"
          element={<ResetPasswordPage />}
        />

        <Route path="/termos-de-uso" element={<TermsPage />} />

        <Route
          path="/politica-de-privacidade"
          element={<PrivacyPage />}
        />

        <Route element={<AppLayout />}>
          <Route path="/inicio" element={auth(<Home />)} />


          <Route path="/cursos" element={<CoursesPage />} />

          <Route
            path="/cursos/:c"
            element={<CoursePage />}
          />

          <Route
            path="/cursos/:c/:p"
            element={<CoursePage />}
          />

          <Route
            path="/cursos/:c/:p/:d"
            element={<DisciplinePage />}
          />

          <Route
            path="/cursos/:c/:p/:d/:t"
            element={<TopicPage />}
          />

          <Route
            path="/simulados"
            element={auth(<ExamsPage />)}
          />

          <Route
            path="/mapas-mentais"
            element={auth(<MindMapsPage />)}
          />

          <Route
            path="/biblioteca"
            element={auth(<LibraryPage />)}
          />

          <Route
            path="/progresso"
            element={auth(<ProgressPage />)}
          />

          <Route
            path="/perfil"
            element={auth(<ProfilePage />)}
          />

          <Route
            path="/planos"
            element={auth(<PlansPage />)}
          />

          <Route
            path="/checkout"
            element={auth(<CheckoutPage />)}
          />

          <Route
            path="/anotacoes"
            element={auth(<NotesPage />)}
          />

          <Route
            path="/meu-plano"
            element={auth(<PlanPage />)}
          />

          <Route
            path="/notificacoes"
            element={auth(<NotificationsPage />)}
          />

          <Route
            path="/ranking"
            element={auth(<RankingPage />)}
          />

          <Route path="/pesquisa" element={auth(<GlobalSearchPage />)} />

          <Route path="/historico" element={auth(<StudyHistoryPage />)} />

          <Route path="/metas" element={auth(<WeeklyGoalsPage />)} />

          <Route path="/calendario" element={auth(<CalendarPage />)} />

          <Route path="/revisoes" element={auth(<ReviewsPage />)} />

          <Route
            path="/enviar-conteudo"
            element={auth(<SubmitPage />)}
          />

          <Route
            path="/admin"
            element={<AdminPage />}
          />

          <Route
            path="*"
            element={
              <div
                data-testid="not-found"
                className="py-20 text-center"
              >
                <h1 className="text-3xl font-bold">
                  Página não encontrada
                </h1>

                <p className="mt-2 text-slate-600">
                  O endereço acessado não existe.
                </p>
              </div>
            }
          />
        </Route>
      </Routes>

      <Toaster
        richColors
        position="bottom-right"
      />
    </>
  );
}
