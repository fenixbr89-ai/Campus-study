import { useState } from "react";
import { Link, Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { ArrowRight, CheckCircle2, Loader2, MailCheck } from "lucide-react";
import { apiGet, apiPost } from "@/lib/api";
import { errMsg, useMe, usePageMeta } from "@/lib/hooks";
import { beginSession } from "@/lib/session";
import { queryClient } from "@/lib/queryClient";
import type { Me, Message } from "@/lib/types";
import { AuthShell } from "@/components/AuthShell";
import { Brand, FooterCredit } from "@/components/Brand";
import { Button, buttonVariants } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const inputCls = "h-11 rounded-xl bg-white";

function Field({ id, label, children, hint }: { id: string; label: string; children: React.ReactNode; hint?: string }) {
  return (
    <div className="space-y-1.5">
      <Label htmlFor={id} className="text-sm font-medium text-slate-700">{label}</Label>
      {children}
      {hint && <p className="text-xs text-red-600" data-testid={`${id}-error`}>{hint}</p>}
    </div>
  );
}

export function AccessPage() {
  usePageMeta("Acesso", "Campus Study — seu ambiente inteligente de estudos universitários.");
  const me = useMe();
  if (me.data && !me.isError) return <Navigate to="/inicio" replace />;
  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-b from-emerald-50 via-white to-white">
      <div className="pointer-events-none absolute -top-32 -right-32 size-[28rem] rounded-full bg-emerald-200/40 blur-3xl" />
      <div className="pointer-events-none absolute top-1/2 -left-40 size-[22rem] rounded-full bg-green-100/70 blur-3xl" />
      <div className="relative mx-auto flex min-h-screen max-w-6xl flex-col px-5 pt-6 pb-5 sm:px-8">
        <Brand />
        <div className="my-auto flex items-center justify-center py-12">
          <div className="animate-fade-up w-full max-w-3xl text-center">
            <span data-testid="access-quote" className="inline-flex -translate-y-4 items-center gap-2 rounded-2xl border border-emerald-200 bg-white/80 px-3 py-2 text-xs font-semibold leading-5 text-brand-dark sm:-translate-y-3">
              “A educação é a arma mais poderosa que você pode usar para mudar o mundo.” — Nelson Mandela
            </span>
            <h1 data-testid="access-title" className="mt-5 text-4xl leading-[1.1] font-extrabold tracking-tight text-slate-900 sm:text-5xl md:text-6xl">
              Campus <span className="text-brand">Study</span>
            </h1>
            <p data-testid="access-subtitle" className="mx-auto mt-4 max-w-lg text-lg text-slate-600 sm:text-xl">
              Seu ambiente inteligente de estudos universitários.
            </p>
            <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
              <Link to="/criar-conta" data-testid="access-create-account-button" className={buttonVariants({ size: "lg", className: "h-12 rounded-xl px-6 text-base shadow-lg shadow-green-600/20 active:scale-[0.98]" })}>
                Criar minha conta <ArrowRight className="size-4" />
              </Link>
              <Link to="/entrar" data-testid="access-login-button" className={buttonVariants({ size: "lg", variant: "outline", className: "h-12 rounded-xl bg-white px-6 text-base active:scale-[0.98]" })}>
                Já tenho uma conta
              </Link>
            </div>
            <Link to="/cursos" data-testid="access-explore-courses-link" className="mt-2 inline-block text-sm font-semibold text-brand-dark hover:underline">Explorar cursos sem cadastro →</Link>
          </div>
        </div>
        <p className="text-center text-xs text-slate-400">
          <Link to="/termos-de-uso" className="hover:text-brand-dark">Termos de Uso</Link> · <Link to="/politica-de-privacidade" className="hover:text-brand-dark">Política de Privacidade</Link>
        </p>
        <div className="mt-6 flex justify-center">
          <FooterCredit />
        </div>
      </div>
    </div>
  );
}

export function LoginPage() {
  usePageMeta("Entrar", "Entre no Campus Study com seu e-mail e senha.");
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const login = useMutation({
    mutationFn: () => apiPost<Me>("/auth/login", { email, password }),
    onSuccess: (me) => { beginSession(); queryClient.setQueryData(["me"], me); toast.success(`Bem-vindo(a) de volta, ${me.name.split(" ")[0]}!`); nav("/inicio"); },
    onError: (e) => toast.error(errMsg(e)),
  });
  return <AuthShell title="Entrar no Campus Study" subtitle="Use seu e-mail e sua senha para acessar.">
    <form className="space-y-4" autoComplete="on" onSubmit={(e) => { e.preventDefault(); login.mutate(); }}>
      <Field id="login-email" label="E-mail"><Input id="login-email" data-testid="login-email-input" name="username" type="email" autoComplete="username" placeholder="seu@email.com" className={inputCls} value={email} onChange={(e) => setEmail(e.target.value)} required /></Field>
      <Field id="login-password" label="Senha"><Input id="login-password" data-testid="login-password-input" name="password" type="password" autoComplete="current-password" className={inputCls} value={password} onChange={(e) => setPassword(e.target.value)} required /></Field>
      <div className="text-right"><Link to="/esqueci-minha-senha" data-testid="login-forgot-password-link" className="text-sm font-semibold text-brand-dark hover:underline">Esqueci minha senha</Link></div>
      <Button type="submit" data-testid="login-submit-button" disabled={login.isPending} className="h-11 w-full rounded-xl text-base">{login.isPending && <Loader2 className="size-4 animate-spin" />} Entrar</Button>
    </form>
    <p className="mt-6 text-center text-sm text-slate-600">Ainda não tem conta? <Link to="/criar-conta" data-testid="login-register-link" className="font-semibold text-brand-dark hover:underline">Criar minha conta</Link></p>
  </AuthShell>;
}

export function RegisterPage() {
  usePageMeta("Criar conta", "Crie sua conta grátis no Campus Study com seu nome, e-mail e senha.");
  const nav = useNavigate();
  const [f, setF] = useState({ name: "", email: "", password: "", password_confirm: "" });
  const [terms, setTerms] = useState(false), [privacy, setPrivacy] = useState(false);
  const set = (k: keyof typeof f) => (e: React.ChangeEvent<HTMLInputElement>) => setF({ ...f, [k]: e.target.value });
  const reg = useMutation({
    mutationFn: () => apiPost<Me>("/auth/register", { ...f, accept_terms: terms, accept_privacy: privacy }),
    onSuccess: (me) => { beginSession(); queryClient.setQueryData(["me"], me); toast.success("Conta criada com sucesso!"); nav("/inicio"); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const pwErr = f.password && (f.password.length < 8 || !/\d/.test(f.password) || !/[A-Za-z]/.test(f.password)) ? "Mínimo de 8 caracteres, com letras e números." : undefined;
  const confErr = f.password_confirm && f.password_confirm !== f.password ? "As senhas não coincidem." : undefined;
  const canSubmit = terms && privacy && !pwErr && !confErr && f.name.trim().length >= 3 && !!f.email;
  return <AuthShell title="Criar minha conta" subtitle="Grátis para sempre. Sem cartão de crédito.">
    <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); if (canSubmit) reg.mutate(); }}>
      <Field id="reg-name" label="Nome completo"><Input id="reg-name" data-testid="register-name-input" autoComplete="name" className={inputCls} value={f.name} onChange={set("name")} required minLength={3} /></Field>
      <Field id="reg-email" label="E-mail"><Input id="reg-email" data-testid="register-email-input" type="email" autoComplete="email" className={inputCls} value={f.email} onChange={set("email")} required /></Field>
      <div className="grid gap-4 sm:grid-cols-2">
        <Field id="reg-password" label="Senha" hint={pwErr}><Input id="reg-password" data-testid="register-password-input" type="password" autoComplete="new-password" className={inputCls} value={f.password} onChange={set("password")} required /></Field>
        <Field id="reg-password-confirm" label="Confirmar senha" hint={confErr}><Input id="reg-password-confirm" data-testid="register-password-confirm-input" type="password" autoComplete="new-password" className={inputCls} value={f.password_confirm} onChange={set("password_confirm")} required /></Field>
      </div>
      <div className="space-y-3 rounded-xl bg-slate-50 p-4 text-sm">
        <label className="flex items-start gap-3"><Checkbox data-testid="register-terms-checkbox" checked={terms} onCheckedChange={(v) => setTerms(!!v)} className="mt-0.5" /><span>Li e aceito os <Link to="/termos-de-uso" target="_blank" className="font-semibold text-brand-dark underline">Termos de Uso</Link></span></label>
        <label className="flex items-start gap-3"><Checkbox data-testid="register-privacy-checkbox" checked={privacy} onCheckedChange={(v) => setPrivacy(!!v)} className="mt-0.5" /><span>Li e estou ciente da <Link to="/politica-de-privacidade" target="_blank" className="font-semibold text-brand-dark underline">Política de Privacidade</Link></span></label>
      </div>
      <Button type="submit" data-testid="register-submit-button" disabled={!canSubmit || reg.isPending} className="h-11 w-full rounded-xl text-base">{reg.isPending && <Loader2 className="size-4 animate-spin" />} Criar minha conta</Button>
    </form>
    <p className="mt-6 text-center text-sm text-slate-600">Já tem conta? <Link to="/entrar" data-testid="register-login-link" className="font-semibold text-brand-dark hover:underline">Entrar</Link></p>
  </AuthShell>;
}

export function ForgotPasswordPage() {
  usePageMeta("Esqueci minha senha", "Recupere o acesso à sua conta Campus Study.");
  const [email, setEmail] = useState("");
  const forgot = useMutation({ mutationFn: () => apiPost<Message>("/auth/forgot-password", { email }), onError: (e) => toast.error(errMsg(e)) });
  return <AuthShell title="Esqueci minha senha" subtitle="Informe o e-mail da sua conta. Enviaremos um link seguro para redefinir a senha.">
    {forgot.isSuccess ? <div data-testid="forgot-success-message" className="rounded-2xl border border-emerald-200 bg-brand-soft p-6"><MailCheck className="size-8 text-brand-dark" /><p className="mt-3 font-semibold text-slate-900">Verifique seu e-mail</p><p className="mt-1 text-sm text-slate-600">{forgot.data.message}</p><p className="mt-2 text-xs text-slate-500">O link expira em 30 minutos e só pode ser usado uma vez.</p></div> : <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); forgot.mutate(); }}><Field id="forgot-email" label="E-mail"><Input id="forgot-email" data-testid="forgot-email-input" type="email" autoComplete="email" placeholder="seu@email.com" className={inputCls} value={email} onChange={(e) => setEmail(e.target.value)} required /></Field><Button type="submit" data-testid="forgot-submit-button" disabled={forgot.isPending || !email} className="h-11 w-full rounded-xl text-base">{forgot.isPending && <Loader2 className="size-4 animate-spin" />} Enviar link de redefinição</Button></form>}
    <p className="mt-6 text-center text-sm"><Link to="/entrar" className="font-semibold text-brand-dark hover:underline">Voltar para o login</Link></p>
  </AuthShell>;
}

export function ResetPasswordPage() {
  usePageMeta("Redefinir senha");
  const [params] = useSearchParams();
  const token = params.get("token") ?? "";
  const nav = useNavigate();
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const valid = useQuery({ queryKey: ["reset-valid", token], enabled: !!token, retry: false,
    queryFn: () => apiGet<Message>(`/auth/reset-password/validate?token=${encodeURIComponent(token)}`) });
  const reset = useMutation({
    mutationFn: () => apiPost<Message>("/auth/reset-password", { token, password, password_confirm: confirm }),
    onSuccess: (r) => { toast.success(r.message); setTimeout(() => nav("/entrar"), 1500); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const invalid = !token || valid.isError;
  return (
    <AuthShell title="Criar nova senha" subtitle="Escolha uma senha forte, com letras e números.">
      {invalid ? (
        <div data-testid="reset-invalid-message" className="rounded-2xl border border-red-200 bg-red-50 p-6 text-sm text-red-800">
          {valid.isError ? errMsg(valid.error) : "Link de redefinição inválido."}
          <Link to="/esqueci-minha-senha" className="mt-3 block font-semibold underline">Solicitar novo link</Link>
        </div>
      ) : reset.isSuccess ? (
        <div data-testid="reset-success-message" className="rounded-2xl border border-emerald-200 bg-brand-soft p-6">
          <CheckCircle2 className="size-8 text-brand-dark" />
          <p className="mt-3 font-semibold">{reset.data.message}</p>
          <Link to="/entrar" className="mt-2 inline-block font-semibold text-brand-dark underline">Ir para o login</Link>
        </div>
      ) : (
        <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); reset.mutate(); }}>
          <Field id="reset-password" label="Nova senha">
            <Input id="reset-password" data-testid="reset-password-input" type="password" autoComplete="new-password" className={inputCls} value={password} onChange={(e) => setPassword(e.target.value)} required />
          </Field>
          <Field id="reset-password-confirm" label="Confirmar nova senha" hint={confirm && confirm !== password ? "As senhas não coincidem." : undefined}>
            <Input id="reset-password-confirm" data-testid="reset-password-confirm-input" type="password" autoComplete="new-password" className={inputCls} value={confirm} onChange={(e) => setConfirm(e.target.value)} required />
          </Field>
          <Button type="submit" data-testid="reset-submit-button" disabled={reset.isPending || !password || password !== confirm} className="h-11 w-full rounded-xl text-base">
            {reset.isPending && <Loader2 className="size-4 animate-spin" />} Salvar nova senha
          </Button>
        </form>
      )}
    </AuthShell>
  );
}
