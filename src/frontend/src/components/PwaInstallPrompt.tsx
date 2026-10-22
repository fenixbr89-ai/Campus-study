import { useEffect, useState } from "react";
import { Download, Share2 } from "lucide-react";
import { Button } from "@/components/ui/button";

type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed"; platform: string }>;
};

function isIos() {
  const ua = window.navigator.userAgent;
  const iPadDesktopMode = window.navigator.platform === "MacIntel" && window.navigator.maxTouchPoints > 1;
  return (/iphone|ipad|ipod/i.test(ua) || iPadDesktopMode) && !("MSStream" in window);
}

function isStandalone() {
  return window.matchMedia("(display-mode: standalone)").matches ||
    Boolean((window.navigator as Navigator & { standalone?: boolean }).standalone);
}

export default function PwaInstallPrompt() {
  const [installEvent, setInstallEvent] = useState<BeforeInstallPromptEvent | null>(null);
  const [ios, setIos] = useState(false);
  const [installed, setInstalled] = useState(false);

  useEffect(() => {
    setIos(isIos());
    const standalone = isStandalone();
    setInstalled(standalone);
    const onBeforeInstall = (event: Event) => {
      event.preventDefault();
      setInstallEvent(event as BeforeInstallPromptEvent);
    };
    const onInstalled = () => {
      setInstalled(true);
      setInstallEvent(null);
    };
    window.addEventListener("beforeinstallprompt", onBeforeInstall);
    window.addEventListener("appinstalled", onInstalled);
    return () => {
      window.removeEventListener("beforeinstallprompt", onBeforeInstall);
      window.removeEventListener("appinstalled", onInstalled);
    };
  }, []);

  if (installed) return null;

  if (installEvent) {
    return (
      <Button variant="outline" onClick={async () => {
        await installEvent.prompt();
        await installEvent.userChoice;
        setInstallEvent(null);
      }}>
        <Download className="size-4" /> Instalar Campus Study
      </Button>
    );
  }

  if (ios) {
    return (
      <div className="rounded-2xl border border-brand/20 bg-brand-soft p-4 text-sm text-slate-700">
        <p className="font-semibold">Instalar Campus Study no iPhone/iPad</p>
        <p className="mt-1">No Safari, toque em <Share2 className="inline size-4" /> Compartilhar e depois em <b>Adicionar à Tela de Início</b>.</p>
      </div>
    );
  }

  return null;
}
