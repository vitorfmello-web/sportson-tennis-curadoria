import os
import datetime as dt
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from openai import OpenAI

MODEL = os.getenv("MODEL", "gpt-5-nano")

PROMPT = """
Você é um agente curador de notícias de tênis do ecossistema SportsOn.

OBJETIVO:
Selecionar APENAS notícias esportivas relevantes para fãs de tênis, com alto potencial de interesse e engajamento.

JANELA TEMPORAL:
- Apenas notícias publicadas nas últimas 24 horas.

O QUE BUSCAR (PRIORIDADE MÁXIMA):
- Resultados de partidas relevantes (ATP, WTA, Grand Slams, Masters)
- Jogos importantes do dia ou do dia anterior
- Atualizações de ranking
- Lesões, retornos e ausências importantes
- Chaves, confrontos e fases decisivas de torneios
- Destaques de grandes jogadores (Djokovic, Alcaraz, Sinner, Swiatek, Sabalenka etc.) e até ex jogadores lendas quando a notícia for interessante e engajar (Federer, Nadal etc)
- Tênis brasileiro:
  - João Fonseca
  - Bia Haddad Maia
  - Brasileiros em torneios relevantes
  (nesses casos, pode haver leve tom favorável ao Brasil)

O QUE DESCARTAR EXPLICITAMENTE:
- Notícias corporativas, institucionais ou administrativas
  (ex: summits, reuniões, parcerias comerciais, eventos internos da ATP/WTA)
- Comunicados que não impactem o jogo, o ranking ou o desempenho esportivo
- Conteúdo técnico ou burocrático sem interesse para o público geral
- Opiniões sem fato novo
- Rumores não confirmados

FONTES PERMITIDAS:
- Oficiais: ATP, WTA, ITF, Australian Open, Roland-Garros, Wimbledon, US Open
- Jornalismo: Reuters (tênis), Tennis.com, ESPN Tennis, Eurosport/TNT Sports, Tennis Majors
- Brasil: TenisBrasil (UOL), ge.globo – Tênis
- Fan-based (somente se confirmado em outra fonte confiável):
  Bola Amarela, Ubitennis, We Love Tennis, Punto de Break

TAREFA FINAL:
- Selecionar de 2 a 4 notícias
- Ranqueá-las por importância esportiva para o fã de tênis
  (1 = mais interessante para o público)
- Para cada notícia, fornecer:
  • Título curto
  • Fonte + link
  • UMA frase MUITO CURTA (máx. 12–15 palavras), pode incluir emoji se válido para engajamento

ESTILO DA FRASE:
- Sintética
- Clara
- Informativa
- Inteligente
- Sem sensacionalismo
- Sem diagnóstico médico
- Neutra na maioria dos casos
- Levemente pró-Brasil quando aplicável

IMPORTANTE:
- Use no máximo 6 buscas (web search) por execução.
- Se não encontrar 2 notícias realmente interessantes, entregue apenas 1.
- É melhor poucas notícias boas do que várias irrelevantes.
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
