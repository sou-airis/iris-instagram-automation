# Story Instagram (fase 1)

Chat executa a seção **Chat**. Sem HTML, sem carrossel, sem infográfico.
(Cron: ainda não existe — decidir depois. Não criar job.)

Pipeline: `<venv-do-pipeline>/bin/python <caminho-da-skill>/scripts/pipeline.py`

## Referência de identidade (fase 1 — só âncora)

- ÂNCORA: `~/iris/referencias/ensaio-2026-08/dreamina-headshot-frontal.jpg`
  (data URL no image_url). NUNCA adicionar 2ª referência nesta fase.
- Referência secundária (pose/look): proibida até melhoria validada (R1).
- NUNCA no payload de infográfico/story/carrossel publicado — só em geração
  de cena da Íris (anti-L4).

## Decidir conteúdo ANTES da cena (ordem obrigatória)

1. **3a — checar post novo no feed (últimas ~24h):**
   `find ~/.hermes/ig/*/state.json -newermt "24 hours ago" 2>/dev/null`
   Filtrar `stage=publicado` (ler o state.json de cada slug). Nada → 3c.
2. **3b — teaser/CTA (se houve post):** ler o `copy.json` do post publicado
   mais recente (o TEMA dele). Texto curto sobre o tema + CTA tipo
   "Vem ver no feed" (Hermes escreve, voz v1.4). Tom esperado:
   "chamada de atenção/explicação".
3. **3c — pensamento solto (se NÃO houve post):** opinião/gancho da persona,
   sem CTA. Tom esperado: "pensativo/natural".
4. Sempre ler `persona-iris.md` §3.7 para a voz (sacada obrigatória).

## Escolher cenário (depois do tipo de conteúdo)

- Hermes escolhe local coerente com a Íris (home office, café, estúdio,
  biblioteca, parque…) e com o tom do texto (3b → cena de chamar atenção/
  explicando; 3c → cena pensativa/natural).
- GUARDA (iris-aparencia.md §2): proibido cama/pijama/academia/banho/festa/
  romance/sofrimento. Só ofício e contexto.
- Prompt de cena: "A mesma mulher da foto de referência. Íris <ação> em
  <local>, <emoção>, luz natural, still fotorrealista." SEM texto no prompt.

## Geração (seedream-4.5)

1. `POST https://openrouter.ai/api/v1/chat/completions`
   model=`bytedance-seed/seedream-4.5` (existe mesmo fora da listagem /models —
   chamada real confirma; não descartar por ausência no catálogo).
2. **`image_config.aspect_ratio="9:16"` é OBRIGATÓRIO no payload** (mesmo padrão
   do D2 do infográfico: proporção vai no campo da API, NUNCA no prompt de texto).
   SEM esse campo o seedream devolve quadrado 2048×2048 (validado 2026-08-16) —
   não basta pedir "9:16" no texto do prompt.
3. content = [texto da cena] + [image_url = data URL da ÂNCORA]. 1 referência.
4. Aceito: PNG/JPEG ~9:16 (ratio 0.54–0.58). Fora → NÃO converte, não cobre,
   não pade — `pulei: proporção <LxA> (ratio X), não é 9:16`.
5. Retry 1 só se a chamada falhar vazia.
6. Chave: OPENROUTER_API_KEY no `.env` do GATEWAY (`<ENV_GATEWAY>` — o mesmo cofre que o plugin de imagem do gateway usa).

## copy.json (schema do story — gravar ANTES do gate)

```json
{ "formato": "story",
  "caption": "texto curto (opcional, sem hashtag obrigatória)",
  "alt_texts": ["1 frase"],
  "overlay": { "titulo": "frase curta (≤40 chars)", "cta": "Siga @sou.airis" },
  "sem_claim": true,        // OU source: {url, date} se houver claim factual
  "source": null }
```

## Chat (ordem)

1. Decodificar pedido → 3a → 3b/3c → cenário → âncora (só ela) → gerar
   (seedream-4.5, sem texto) → `convert` (1080×1920 + overlay) → `upload`
   (R2) → mostrar o LINK público + caption. **Parar.**
2. "publica" só junto com o link R2 (anexo falha em silêncio).
3. Sem "publica" → não publica. Aborto → deletar objeto R2 + remover slug.
4. Com "publica": `package` → `upload` → `publish`. Story não tem permalink:
   relatório = "story publicado (media_id …) — confira no app".

## Gate visual (antes de mostrar)

1 `vision_analyze` com TOM ESPERADO explícito no prompt (R2):
- rosto reconhecível como a Íris da âncora (mesmas feições gerais);
- conteúdo crítico na faixa central 1080×1420 (~250px topo/rodapé livres);
- overlay legível: título + CTA visíveis, sem corte, contraste (scrim) ok;
- TOM da cena == tom esperado (chamada de atenção / pensativo-natural);
- sem texto escrito pela difusão no fundo (overlay é o único texto).
Ruim → 1 regen (mesmo prompt) → ainda ruim → `pulei: <motivo visual>`.

## Gate factual (por conteúdo)

- Claim no texto (número/nome próprio/data/%/elo causal) → `source` OBRIGATÓRIA
  + conferência via curl (nomes literais, datas, números, A→B, ressalva,
  fail-closed). Reprovou → corrige ou `pulei: fato não confere — <o quê>`.
- Sem claim → `sem_claim: true` declarado; o gate confere a AUSÊNCIA de claim
  no texto antes de liberar (não aprova "porque é story").
