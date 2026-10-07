"""Transactional email via Resend API or standard SMTP, independent of external platforms."""
import asyncio
import ipaddress
import logging
import os
import re
import smtplib
from email.message import EmailMessage
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)
EMAIL_PROVIDER = os.environ.get("EMAIL_PROVIDER", "none").strip().lower()
EMAIL_FROM_NAME = os.environ.get("EMAIL_FROM_NAME", "Campus Study")
EMAIL_FROM_ADDRESS = os.environ.get("EMAIL_FROM_ADDRESS", "")
EMAIL_REPLY_TO = os.environ.get("EMAIL_REPLY_TO")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.environ.get("SMTP_USE_TLS", "true").lower() not in {"0", "false", "no"}

_SHORTENERS = ("bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly", "goo.gl", "rebrand.ly")
_CRED_ASK = ("reply with your password", "reply with the code", "send your password", "cvv",
             "send us your password", "enter your password below", "confirm your card number",
             "your full card number", "seed phrase", "recovery phrase", "verify your card",
             "social security number", "confirm your bank details")
_HOSTISH = re.compile(r"\b(?:https?://)?((?:[a-z0-9-]+\.)+[a-z]{2,})", re.I)


def _host_ok(host: str) -> bool:
    if not host or "xn--" in host:
        return False
    try:
        ipaddress.ip_address(host)
        return False
    except ValueError:
        pass
    return not any(host == s or host.endswith("." + s) for s in _SHORTENERS)


def _same_site(shown: str, real: str) -> bool:
    return shown == real or real.endswith("." + shown) or shown.endswith("." + real)


class _EmailScan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.urls, self.anchors = set(), [], []
        self._href, self._text = None, []

    def handle_starttag(self, tag, attrs):
        self.tags.add(tag.lower())
        self.urls += [v for k, v in attrs if k.lower() in ("href", "src") and v]
        if tag.lower() == "a":
            self._href = dict((k.lower(), v) for k, v in attrs).get("href")
            self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self._href is not None:
            self.anchors.append((self._href, "".join(self._text)))
            self._href, self._text = None, []


def _assert_safe_email(subject: str, html: str) -> None:
    scan = _EmailScan()
    scan.feed(html)
    if scan.tags & {"form", "input", "textarea", "select"}:
        raise ValueError("No forms or input fields in email (G2)")
    body = f"{subject}\n{html}".lower()
    for p in _CRED_ASK:
        if p in body:
            raise ValueError(f"Email asks the recipient for credentials: {p!r} (G2)")
    for url in scan.urls:
        low = url.strip().lower()
        if low.startswith(("mailto:", "tel:", "cid:", "#")):
            continue
        if not low.startswith("https://"):
            raise ValueError(f"Email links/assets must be absolute https: {url!r} (G3)")
        host = urlparse(low).hostname or ""
        if not _host_ok(host) or urlparse(low).username is not None:
            raise ValueError(f"Shortened, numeric-host or credential-bearing URL: {url!r} (G3)")
    for href, text in scan.anchors:
        real = urlparse(href.strip().lower()).hostname or ""
        if not real:
            continue
        for m in _HOSTISH.finditer(text):
            if not _same_site(m.group(1).lower(), real):
                raise ValueError(f"Anchor text {m.group(1)!r} != real link host {real!r} (G3)")


async def _send_resend(to: str, subject: str, html: str) -> str | None:
    if not RESEND_API_KEY or not EMAIL_FROM_ADDRESS:
        raise HTTPException(503, "E-mail não configurado: defina RESEND_API_KEY e EMAIL_FROM_ADDRESS.")
    payload = {"from": f"{EMAIL_FROM_NAME} <{EMAIL_FROM_ADDRESS}>", "to": [to], "subject": subject, "html": html}
    if EMAIL_REPLY_TO:
        payload["reply_to"] = [EMAIL_REPLY_TO]
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post("https://api.resend.com/emails", headers={"Authorization": f"Bearer {RESEND_API_KEY}"}, json=payload)
    if response.status_code >= 400:
        logger.error("Resend failed: %s %s", response.status_code, response.text[:500])
        raise HTTPException(503, "Não foi possível enviar o e-mail agora. Tente novamente em instantes.")
    return response.json().get("id")


def _send_smtp_sync(to: str, subject: str, html: str) -> None:
    if not SMTP_HOST or not SMTP_USERNAME or not SMTP_PASSWORD or not EMAIL_FROM_ADDRESS:
        raise HTTPException(503, "E-mail não configurado: defina SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD e EMAIL_FROM_ADDRESS.")
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_FROM_ADDRESS}>"
    msg["To"] = to
    if EMAIL_REPLY_TO:
        msg["Reply-To"] = EMAIL_REPLY_TO
    msg.set_content("Este e-mail requer um cliente compatível com HTML.")
    msg.add_alternative(html, subtype="html")
    if SMTP_USE_TLS and SMTP_PORT == 465:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
    else:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.ehlo()
            if SMTP_USE_TLS:
                server.starttls()
                server.ehlo()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)


async def send_email(*, to: str, subject: str, html: str) -> str | None:
    _assert_safe_email(subject, html)
    try:
        if EMAIL_PROVIDER == "resend":
            return await _send_resend(to, subject, html)
        if EMAIL_PROVIDER == "smtp":
            await asyncio.to_thread(_send_smtp_sync, to, subject, html)
            return None
        raise HTTPException(503, "E-mail não configurado. Defina EMAIL_PROVIDER como 'resend' ou 'smtp'.")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Email send error: %s", exc)
        raise HTTPException(503, "Não foi possível enviar o e-mail agora. Tente novamente em instantes.") from exc


def reset_email_html(name: str, link: str, minutes: int) -> str:
    return (
        '<table role="presentation" width="100%" style="background:#f8fafc"><tr><td style="padding:32px;'
        'font-family:Arial,sans-serif;color:#0f172a">'
        '<table role="presentation" width="100%" style="max-width:520px;margin:0 auto;background:#ffffff;'
        'border-radius:16px;border:1px solid #e2e8f0"><tr><td style="padding:32px">'
        '<p style="font-size:20px;font-weight:bold;color:#15803d;margin:0 0 16px">Campus Study</p>'
        f'<p>Olá, {escape(name.split(" ")[0])}!</p>'
        '<p>Recebemos uma solicitação para redefinir a senha da sua conta no Campus Study.</p>'
        f'<p style="margin:24px 0"><a href="{escape(link)}" style="background:#16a34a;color:#ffffff;'
        'padding:12px 24px;border-radius:10px;text-decoration:none;font-weight:bold">Criar nova senha</a></p>'
        f'<p style="font-size:14px;color:#475569">Este link é pessoal, pode ser usado uma única vez e expira em {minutes} minutos.</p>'
        '<p style="font-size:14px;color:#475569">Se você não fez essa solicitação, ignore este e-mail — sua senha continua a mesma.</p>'
        f'<p style="font-size:12px;color:#94a3b8;margin-top:24px">Enviado por {escape(EMAIL_FROM_NAME)}.</p>'
        '</td></tr></table></td></tr></table>'
    )
