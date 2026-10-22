# Otimização do Campus IA

## Alterações

- Reutilização de uma conexão HTTP persistente com o Gemini para reduzir custo de conexão por pergunta.
- Timeout padrão reduzido de 25s para 18s.
- Retries padrão reduzidos de 2 para 1, evitando esperas longas em falhas temporárias.
- Novo limite de saída `AI_MAX_OUTPUT_TOKENS`, padrão 768 e máximo 2048.
- Perguntas simples recebem instrução explícita para respostas curtas e diretas.
- Verificação de desconexão do cliente passou de 200 ms para 100 ms, melhorando o botão Parar/cancelamento.
- Mesma conexão HTTP reutilizada na geração de imagens.
- Nenhuma chave Gemini foi movida para o frontend.
- Nenhuma rota pública foi removida ou renomeada.

## Variáveis

`src/backend/.env.example` foi atualizado com:

```env
AI_REQUEST_TIMEOUT=18
AI_MAX_RETRIES=1
AI_MAX_OUTPUT_TOKENS=768
```

## Validação

- `python -m py_compile src/backend/routers/ai.py`: OK.
- Verificação estática das novas configurações: OK.
- Build/typecheck do frontend: não executado, pois `node_modules` não está presente no ZIP.
- Não foi feita medição real de latência contra o Gemini neste ambiente, portanto não foi declarado um ganho percentual de velocidade.
