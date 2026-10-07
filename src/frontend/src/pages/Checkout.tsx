import { Link, useSearchParams } from "react-router-dom";
import { CheckCircle2, ShieldCheck } from "lucide-react";
import { useMe, usePageMeta } from "@/lib/hooks";
import { useMutation, useQuery } from "@tanstack/react-query";
import { apiGet, apiPost } from "@/lib/api";
import type { StripePublicConfig, StripeCheckoutOut } from "@/lib/types";
import { buttonVariants } from "@/components/ui/button";
import { toast } from "sonner";
import { errMsg } from "@/lib/hooks";

export default function CheckoutPage() {
  usePageMeta("Checkout Premium");
  const me = useMe();
  const [sp] = useSearchParams();
  const plan = sp.get("plano") === "yearly" ? "yearly" : "monthly";
  const stripe = useQuery({ queryKey: ["stripe-config"], queryFn: () => apiGet<StripePublicConfig>("/payments/stripe/config") });
  const configuredPrice = plan === "yearly" ? stripe.data?.yearly_price : stripe.data?.monthly_price;
  const price = configuredPrice ? `R$ ${configuredPrice.replace(".", ",")} / ${plan === "yearly" ? "ano" : "mês"}` : plan === "yearly" ? "R$ 150,00 / ano" : "R$ 19,90 / mês";
  const checkout = useMutation({
    mutationFn: () => apiPost<StripeCheckoutOut>("/payments/stripe/checkout", { plan }),
    onSuccess: (r) => { window.location.href = r.url; },
    onError: (e) => toast.error(errMsg(e)),
  });
  const success = sp.get("sucesso") === "1";
  return <div className="mx-auto max-w-2xl animate-fade-up py-4">
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
      <Link to="/planos" className="text-sm font-semibold text-brand-dark hover:underline">← Voltar aos planos</Link>
      <div className="mt-6 flex items-center gap-3"><div className="grid size-12 place-items-center rounded-2xl bg-emerald-50 text-emerald-700"><ShieldCheck /></div><div><h1 className="text-2xl font-extrabold">Checkout Premium</h1><p className="text-sm text-slate-500">Pagamento seguro processado pelo Stripe.</p></div></div>
      {success && <div className="mt-5 flex gap-2 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-900"><CheckCircle2 className="mt-0.5 size-4 shrink-0"/>Pagamento recebido. O acesso Premium será confirmado pela integração do Stripe.</div>}
      <div className="mt-6 rounded-2xl bg-slate-50 p-4"><p className="text-sm font-semibold">Plano {plan === "yearly" ? "Anual" : "Mensal"}</p><p className="mt-1 text-2xl font-extrabold">{price}</p><p className="mt-1 text-xs text-slate-500">Conta: {me.data?.email}</p></div>
      <div className="mt-6"><button type="button" onClick={() => checkout.mutate()} disabled={checkout.isPending || stripe.isLoading || !stripe.data?.enabled || !stripe.data?.configured} className="flex h-12 w-full items-center justify-center rounded-xl bg-brand px-5 font-semibold text-white hover:bg-brand-dark disabled:cursor-not-allowed disabled:opacity-50">{checkout.isPending ? "Abrindo checkout..." : "Assinar com Stripe"}</button></div>
      {!stripe.isLoading && !stripe.data?.configured && <p className="mt-3 text-sm text-amber-700">O checkout ainda precisa ser configurado pelo administrador no painel de pagamentos.</p>}
      <div className="mt-6 space-y-2 text-xs text-slate-500"><p className="flex gap-2"><CheckCircle2 className="size-4 text-emerald-600" />A assinatura fica vinculada à sua conta do Campus Study.</p><p>O pagamento é realizado na página segura do Stripe e a confirmação é enviada ao Campus Study por webhook.</p></div>
      <Link to="/planos" className={buttonVariants({ variant: "outline", className: "mt-6 w-full" })}>Escolher outro plano</Link>
    </div>
  </div>;
}
