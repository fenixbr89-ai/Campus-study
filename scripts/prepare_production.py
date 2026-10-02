#!/usr/bin/env python3
"""Prepare a production .env for Campus Study V1.
Generates cryptographic secrets locally and asks only for deployment-specific values.
No secret is sent anywhere by this script.
"""
from pathlib import Path
import secrets
import getpass

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / "src" / "backend" / ".env"
EXAMPLE = ROOT / "src" / "backend" / ".env.example"

def ask(label, default=""):
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or default

def main():
    print("\nCAMPUS STUDY V12 — CONFIGURAÇÃO DE PRODUÇÃO\n")
    if ENV.exists():
        answer = input("Já existe src/backend/.env. Substituir? [s/N]: ").strip().lower()
        if answer != "s":
            print("Nenhuma alteração feita.")
            return

    cpf = ask("CPF do primeiro SUPERADMIN (somente dígitos)")
    email = ask("E-mail do primeiro SUPERADMIN")
    name = ask("Nome do primeiro SUPERADMIN", "Administrador Campus Study")
    password = getpass.getpass("Senha inicial do SUPERADMIN (deixe vazio para gerar uma forte): ")
    if not password:
        password = secrets.token_urlsafe(18)
        print(f"Senha inicial gerada: {password}")

    gemini = ask("GEMINI_API_KEY (Enter para deixar IA desativada por enquanto)")
    domain = ask("Domínio do site (ex.: https://campusstudy.com.br)", "http://localhost")

    lines = [
        "MONGO_URL=mongodb://mongo:27017",
        "DB_NAME=campus_study",
        f"CORS_ORIGINS={domain}",
        f"COOKIE_SECURE={'true' if domain.startswith('https://') else 'false'}",
        f"JWT_SECRET={secrets.token_urlsafe(48)}",
        f"CPF_PEPPER={secrets.token_urlsafe(48)}",
        "APP_TZ=America/Sao_Paulo",
        "TERMS_VERSION=1.0",
        "PRIVACY_VERSION=1.0",
        "AI_PROVIDER=gemini",
        "AI_MODEL=gemini-2.5-flash",
        f"GEMINI_API_KEY={gemini}",
        "OPENAI_API_KEY=",
        "OPENAI_MODEL=gpt-4o-mini",
        "EMAIL_PROVIDER=none",
        "EMAIL_FROM_NAME=Campus Study",
        "EMAIL_FROM_ADDRESS=",
        "EMAIL_REPLY_TO=",
        "RESEND_API_KEY=",
        "SMTP_HOST=",
        "SMTP_PORT=587",
        "SMTP_USERNAME=",
        "SMTP_PASSWORD=",
        "SMTP_USE_TLS=true",
        f"ADMIN_NAME={name}",
        f"ADMIN_EMAIL={email}",
        f"ADMIN_CPF={cpf}",
        f"ADMIN_PASSWORD={password}",
    ]
    ENV.parent.mkdir(parents=True, exist_ok=True)
    ENV.write_text("\n".join(lines) + "\n")
    print(f"\nConfiguração criada em: {ENV}")
    print("Agora execute o stack Docker e, depois, o seed do primeiro administrador.")
    print("IMPORTANTE: nunca publique src/backend/.env ou compartilhe esse arquivo.\n")

if __name__ == "__main__":
    main()
