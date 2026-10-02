import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { ApiError, apiGet } from "./api";
import type { Me } from "./types";

export function useMe() {
  return useQuery({
    queryKey: ["me"],
    queryFn: () => apiGet<Me>("/auth/me"),
    retry: false,
    staleTime: 60_000,
  });
}

export const STAFF = ["admin", "superadmin", "editor", "moderator"];

export function isPremium(me: Me | undefined): boolean { return !!me && me.plan === "premium"; }
export function trialExpired(me: Me | undefined): boolean { return !!me && me.plan === "free" && !me.trial_active; }


export function isAdmin(me: Me | undefined): boolean {
  return !!me && (me.role === "admin" || me.role === "superadmin");
}

export function usePageMeta(title: string, description?: string) {
  useEffect(() => {
    document.title = title ? `${title} | Campus Study` : "Campus Study";
    if (description) {
      let tag = document.querySelector<HTMLMetaElement>('meta[name="description"]');
      if (!tag) {
        tag = document.createElement("meta");
        tag.name = "description";
        document.head.appendChild(tag);
      }
      tag.content = description;
      document.querySelector<HTMLMetaElement>('meta[property="og:title"]')?.setAttribute("content", document.title);
      document.querySelector<HTMLMetaElement>('meta[property="og:description"]')?.setAttribute("content", description);
    }
  }, [title, description]);
}

export function errMsg(err: unknown): string {
  if (err instanceof ApiError) {
    const body = err.body as { detail?: unknown } | null;
    if (body && typeof body.detail === "string") return body.detail;
    if (body && Array.isArray(body.detail)) return "Verifique os campos preenchidos e tente novamente.";
    if (err.status === 401) return "Faça login para continuar.";
    if (err.status >= 500) return "O servidor está indisponível no momento. Tente novamente.";
  }
  return "Algo deu errado. Verifique sua conexão e tente novamente.";
}
