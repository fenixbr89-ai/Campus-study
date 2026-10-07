import { useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { FileText, Mic, Paperclip, Send, Sparkles, Square, User, Volume2, X } from "lucide-react";
import { toast } from "sonner";
import { apiAssetUrl, apiPost, apiPostSignal, ApiError } from "@/lib/api";
import { errMsg, usePageMeta } from "@/lib/hooks";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

type Attachment = { id: string; file: File; preview?: string };
type ChatMessage = { role: "user" | "assistant"; content: string; imageUrl?: string; attachments?: string[] };
type AIResponse = { answer?: string; message?: string; image_url?: string };
type SpeechRecognitionCtor = new () => SpeechRecognitionLike;
type SpeechRecognitionLike = { lang: string; continuous: boolean; interimResults: boolean; onresult: ((e: any) => void) | null; onend: (() => void) | null; onerror: (() => void) | null; start: () => void; stop: () => void };

const STORAGE_KEY = "campus-study-ai-history";

function getSpeechRecognition(): SpeechRecognitionCtor | null {
  const w = window as any;
  return w.SpeechRecognition || w.webkitSpeechRecognition || null;
}

export default function CampusAI() {
  usePageMeta("Campus IA");
  const [params] = useSearchParams();
  const initial = useMemo(() => params.get("mensagem")?.trim() ?? "", [params]);
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    try { return JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "[]") as ChatMessage[]; } catch { return []; }
  });
  const [text, setText] = useState(initial);
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const controllerRef = useRef<AbortController | null>(null);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const voiceRequestRef = useRef(false);
  const fileRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => () => {
    controllerRef.current?.abort();
    recognitionRef.current?.stop();
    attachments.forEach(a => a.preview && URL.revokeObjectURL(a.preview));
  }, []);

  useEffect(() => { sessionStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-50))); }, [messages]);

  const sendMessage = async (value: string) => {
    if (!value || controllerRef.current) return;
    const controller = new AbortController();
    controllerRef.current = controller;
    setIsSending(true);
    const names = attachments.map(a => a.file.name);
    setMessages(current => [...current, { role: "user", content: value, attachments: names }]);
    setText("");
    try {
      let response: AIResponse;
      if (attachments.length) {
        const fd = new FormData();
        fd.append("message", value);
        attachments.forEach(a => fd.append("files", a.file, a.file.name));
        const res = await fetch("/api/ai/chat-with-files", { method: "POST", body: fd, signal: controller.signal });
        if (!res.ok) {
          const body = await res.json().catch(() => null);
          throw new ApiError(res.status, body);
        }
        response = await res.json();
      } else {
        response = await apiPostSignal<AIResponse>("/ai/chat", { message: value }, controller.signal);
      }
      if (controller.signal.aborted) return;
      const answer = response.answer || response.message || "Não recebi uma resposta da IA.";
      setMessages(current => [...current, { role: "assistant", content: answer, imageUrl: response.image_url }]);
      if (voiceRequestRef.current) {
        voiceRequestRef.current = false;
        speak(answer);
      }
      attachments.forEach(a => a.preview && URL.revokeObjectURL(a.preview));
      setAttachments([]);
    } catch (e) {
      if ((e as Error)?.name === "AbortError") return;
      toast.error(errMsg(e));
    } finally {
      if (controllerRef.current === controller) { controllerRef.current = null; setIsSending(false); }
    }
  };

  const submit = () => {
    const value = text.trim();
    if (!value || controllerRef.current) return;
    sendMessage(value);
  };

  const stop = () => {
    controllerRef.current?.abort();
    controllerRef.current = null;
    setIsSending(false);
  };

  const addFiles = (list: FileList | null) => {
    if (!list) return;
    const incoming = Array.from(list);
    if (attachments.length + incoming.length > 5) {
      toast.error("Você pode anexar no máximo 5 arquivos por pergunta.");
      return;
    }
    const allowed = new Set(["application/pdf", "text/plain", "text/markdown", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "image/png", "image/jpeg", "image/webp"]);
    const valid = incoming.filter(file => {
      if (file.size > 10 * 1024 * 1024) { toast.error(`${file.name} excede 10 MB.`); return false; }
      if (!allowed.has(file.type)) { toast.error(`${file.name}: formato não suportado.`); return false; }
      return true;
    }).map(file => ({ id: crypto.randomUUID(), file, preview: file.type.startsWith("image/") ? URL.createObjectURL(file) : undefined }));
    setAttachments(current => [...current, ...valid]);
    if (fileRef.current) fileRef.current.value = "";
  };

  const removeAttachment = (id: string) => {
    setAttachments(current => {
      const item = current.find(a => a.id === id);
      if (item?.preview) URL.revokeObjectURL(item.preview);
      return current.filter(a => a.id !== id);
    });
  };

  const toggleVoice = () => {
    if (isListening) { recognitionRef.current?.stop(); return; }
    const Ctor = getSpeechRecognition();
    if (!Ctor) { toast.error("Seu navegador não oferece reconhecimento de voz."); return; }
    const recognition = new Ctor();
    recognition.lang = "pt-BR"; recognition.continuous = false; recognition.interimResults = true;
    recognition.onresult = (event: any) => {
      const transcript = Array.from(event.results as any[]).map((r: any) => r[0]?.transcript || "").join("");
      setText(transcript);
    };
    recognition.onend = () => { setIsListening(false); recognitionRef.current = null; };
    recognition.onerror = () => { setIsListening(false); recognitionRef.current = null; toast.error("Não foi possível reconhecer sua voz."); };
    recognitionRef.current = recognition;
    voiceRequestRef.current = true;
    setIsListening(true);
    recognition.start();
  };

  const speak = (content: string) => {
    if (!("speechSynthesis" in window)) { toast.error("Seu navegador não oferece leitura em voz alta."); return; }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(content);
    utterance.lang = "pt-BR";
    window.speechSynthesis.speak(utterance);
  };

  useEffect(() => {
    if (!initial) return;
    if (!messages.some(m => m.role === "user" && m.content === initial)) {
      sendMessage(initial);
    }
    // initial is a URL action and should run only once.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initial]);

  return <div className="mx-auto flex min-h-[calc(100vh-12rem)] max-w-4xl flex-col gap-4">
    <div className="flex items-center gap-3"><div className="grid size-11 place-items-center rounded-2xl bg-brand-soft text-brand-dark"><Sparkles className="size-6" /></div><div><h1 className="text-3xl font-extrabold tracking-tight">Campus IA</h1><p className="text-sm text-slate-500">Converse com a IA sobre seus estudos, matérias e dúvidas.</p></div></div>
    <div className="flex flex-1 flex-col rounded-3xl border border-slate-200 bg-white p-3 shadow-sm sm:p-6">
      <div className="min-h-[26rem] flex-1 space-y-4 overflow-y-auto pr-1">
        {messages.length === 0 && <div className="grid min-h-[22rem] place-items-center text-center"><div><Sparkles className="mx-auto size-10 text-brand"/><h2 className="mt-3 text-xl font-bold">Como posso ajudar nos estudos?</h2><p className="mt-1 max-w-md text-sm text-slate-500">Pergunte sobre um tema, envie uma questão, PDF ou imagem.</p></div></div>}
        {messages.map((m, i) => <div key={i} className={`flex gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}><div className={`max-w-[92%] rounded-2xl px-4 py-3 sm:max-w-[85%] ${m.role === "user" ? "bg-brand text-white" : "bg-slate-50 text-slate-800"}`}><div className="flex gap-3">{m.role === "user" ? <User className="mt-0.5 size-4 shrink-0"/> : <Sparkles className="mt-0.5 size-4 shrink-0 text-brand"/>}<p className="whitespace-pre-wrap text-sm leading-6">{m.content}</p></div>{m.attachments?.length ? <div className="mt-2 flex flex-wrap gap-1">{m.attachments.map(name => <span key={name} className="rounded-lg bg-black/5 px-2 py-1 text-[11px]">{name}</span>)}</div> : null}{m.imageUrl && <a href={apiAssetUrl(m.imageUrl)} target="_blank" rel="noreferrer" className="mt-3 block"><img src={apiAssetUrl(m.imageUrl)} alt="Imagem gerada pelo Campus IA" className="max-h-[28rem] w-full rounded-xl object-contain" /></a>}{m.role === "assistant" && <button type="button" onClick={() => speak(m.content)} className="mt-2 inline-flex items-center gap-1 text-xs text-slate-500 hover:text-brand"><Volume2 className="size-3.5"/> Ouvir</button>}</div></div>)}
        {isSending && <div className="flex justify-start"><div className="flex items-center gap-2 rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-500"><span>Campus IA está pensando…</span><Button size="sm" variant="outline" onClick={stop}><Square className="size-3"/> Parar</Button></div></div>}
      </div>
      {attachments.length > 0 && <div className="mt-3 flex flex-wrap gap-2 rounded-2xl border border-slate-100 bg-slate-50 p-2">{attachments.map(a => <div key={a.id} className="relative flex items-center gap-2 rounded-xl bg-white p-2 text-xs shadow-sm">{a.preview ? <img src={a.preview} alt="" className="size-12 rounded-lg object-cover"/> : <FileText className="size-8 text-brand"/>}<span className="max-w-40 truncate">{a.file.name}</span><button type="button" aria-label={`Remover ${a.file.name}`} onClick={() => removeAttachment(a.id)} className="rounded-full p-1 hover:bg-slate-100"><X className="size-3.5"/></button></div>)}</div>}
      <div className="mt-3 flex items-end gap-2 rounded-2xl border border-slate-200 p-2 focus-within:ring-2 focus-within:ring-brand/20">
        <input ref={fileRef} type="file" multiple accept=".pdf,.txt,.md,.docx,image/*" className="hidden" onChange={e => addFiles(e.target.files)} />
        <Button type="button" variant="ghost" className="size-11 shrink-0 rounded-xl p-0" aria-label="Anexar arquivo" onClick={() => fileRef.current?.click()} disabled={isSending}><Paperclip className="size-5"/></Button>
        <Button type="button" variant="ghost" className={`size-11 shrink-0 rounded-xl p-0 ${isListening ? "text-red-600" : ""}`} aria-label="Microfone" onClick={toggleVoice} disabled={isSending}><Mic className="size-5"/></Button>
        <Textarea value={text} onChange={e=>setText(e.target.value)} onKeyDown={e=>{ if(e.key === "Enter" && !e.shiftKey){e.preventDefault();submit();}}} placeholder="Digite sua mensagem..." className="min-h-12 flex-1 resize-none border-0 shadow-none focus-visible:ring-0"/>
        {isSending ? <Button type="button" variant="outline" onClick={stop} className="h-11 shrink-0 rounded-xl px-3"><Square className="size-4"/> <span className="hidden sm:inline">Parar</span></Button> : <Button type="button" onClick={submit} disabled={!text.trim()} className="size-11 shrink-0 rounded-xl p-0"><Send className="size-4"/></Button>}
      </div>
    </div>
  </div>;
}
