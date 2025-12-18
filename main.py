import os
import datetime as dt
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from openai import OpenAI

MODEL = os.getenv("MODEL", "gpt-5-nano")

PROMPT = """
Você é um agente curador de notícias de tênis do ecossistema SportsOn.

Tarefa:
- Buscar notícias publicadas nas últimas 24 horas
- Usar fontes confiáveis de tênis
- Selecionar 2 a 4 notícias
- Ranqueá-las por importância (1 = mais importante)
- Para cada notícia, gerar:
  • Título curto
  • Fonte + link
  • UMA frase curta e inteligente
- Tom profissional e sóbrio
- Leve viés pró-tênis brasileiro quando aplicável
- Não inventar fatos
- Se houver dúvida factual, descarte a notícia

IMPORTANTE:
- Use no máximo 6 buscas (web search) por execução
"""

def send_email(subject, body):
    sg = SendGridAPIClient(os.environ["SENDGRID_API_KEY"])
    message = Mail(
        from_email=os.environ["FROM_EMAIL"],
        to_emails=os.environ["TO_EMAIL"],
        subject=subject,
        plain_text_content=body,
    )
    sg.send(message)

def main():
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    response = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": "Você é um curador editorial rigoroso e objetivo."},
            {"role": "user", "content": PROMPT},
        ],
        tools=[{"type": "web_search"}],
    )

    texto = response.output_text.strip()
    hoje = dt.datetime.now().strftime("%Y-%m-%d")
    assunto = f"Curadoria Tênis — últimas 24h — {hoje}"

    send_email(assunto, texto)

if __name__ == "__main__":
    main()
