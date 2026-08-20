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
   **REGRA ANTI-TEASER-DUPLICADO:** além de existir post novo, o post mais
   recente NÃO pode ter `story_teaser_feito` no state.json. Se o campo existir
   (lista não vazia) → o post já foi "consumido" por um story anterior → NÃO
   vira teaser de novo → cai direto para 3c, mesmo dentro da janela de 24h.
   Vale para os 3 jobs: quem gerar teaser primeiro consome o post; os outros
   caem para pensamento solto automaticamente. A regra decide pelo campo,
   nunca pelo horário.
2. **3b — teaser/CTA (se houve post E não consumido):** ler o `copy.json` do post
   mais recente (o TEMA dele). Texto curto sobre o tema + CTA tipo
   "Vem ver no feed" (Hermes escreve, voz v1.4). Tom esperado:
   "chamada de atenção/explicação".
   **2 camadas de texto (regra 2026-08-18):** hook (≤40 chars) + corpo em
   1ª pessoa (~95 chars) que dá contexto do post SEM entregar tudo. Ex.:
   hook "REFIZ O PROMPT" + corpo "O post de hoje conta a receita da pele."
   **RE-CHECAGEM ANTES DE GRAVAR (corrida entre jobs):** após gerar a imagem
   e passar os gates, IMEDIATAMENTE antes de gravar/publish, RELER o state.json
   do post original. Se `story_teaser_feito` já existe (outro job gravou no
   meio-tempo) → ABORTA o teaser (descarta a imagem gerada, NÃO publica) e cai
   para 3c. Senão, grava e publica — leitura+gravação+publish em sequência
   rápida (janela residual de segundos, benigna: pior caso = 2 stories, apagar
   um no app). NUNCA lock de arquivo (lock órfão queimaria o post para sempre).
   **Gravação:** no state.json do POST ORIGINAL (slug do carrossel/infográfico,
   NÃO o do story), campo `"story_teaser_feito": ["<slug-do-story>"]` — se já
   existir, APPEND do novo slug (nunca sobrescrever). Editar o JSON direto
   preservando os demais campos (merge, mesmo do save_state do pipeline — sem
   subcomando novo).
3. **3c — pensamento solto (se NÃO houve post):** opinião/gancho da persona,
   sem CTA. Tom esperado: "pensativo/natural".
   **2 camadas de texto (regra 2026-08-18):** hook (≤40 chars) + corpo em
   1ª pessoa (micro-momento + sacada — o que ela está fazendo e por quê).
   Ex.: hook "A IA SE ENTREGA NA PELE" + corpo "Hoje mudamos o prompt pra
   minhas fotos ficarem mais realistas. Adeus, pele de boneca."
4. Sempre ler `persona-iris.md` §3.7 para a voz (sacada obrigatória).

## Cron (job fino — aponta para ESTA receita, não copia o fluxo)

Jobs (todos leem esta seção, na ordem; o job É a autorização — depois dos
gates, publica. Não espera "publica". Uma execução = no máximo 1 story):
- `iris-story-teaser` — a cada 30 min com monitor_script (detecta post novo
  no feed das últimas 24h; saída muda → acorda o agente → 3b; saída estável →
  silêncio, zero tokens).
- `iris-story-manha` — diário 10:05 BRT (`5 13 * * *` = 13:05 UTC). Lógica
  3a/3b/3c completa: post novo não consumido → teaser; consumido ou sem post →
  3c ("bom dia"/pensamento solto).
- `iris-story-noite` — diário 19:00 BRT (`0 22 * * *` = 22:00 UTC). Mesma
  lógica completa: aleatório se consumido; teaser se post novo não consumido.

1. **3a** — checar post novo + regra anti-teaser-duplicado (acima).
2. **3b ou 3c** — decidir conteúdo; se teaser, re-checagem + gravação de
   `story_teaser_feito` (append na lista) no state.json do post original
   IMEDIATAMENTE antes do publish (passo único: reler → gravar → publicar).
3. **Cenário** (guarda da persona `iris-aparencia.md` §2) → **gerar**
   (seedream-4.5 + `image_config.aspect_ratio="9:16"` OBRIGATÓRIO + âncora
   única `dreamina-headshot-frontal.jpg`) → **convert** (1080×1920 + overlay).
4. **Gates** (autorização do job):
   - visual (1 `vision_analyze` com TOM ESPERADO explícito: "chamada de
     atenção" p/ teaser; "pensativo/natural" p/ 3c) → ruim: 1 regen → ainda
     ruim: `pulei: <motivo visual>`;
   - factual (claim → fonte via curl, nomes literais, datas, números, A→B,
     ressalva, fail-closed; sem claim → `sem_claim: true` declarado);
   - reprovou → `pulei: <motivo>`, não publica.
5. **Publicar** — `convert` → `package` → `upload` → `publish`. Story não tem
   permalink: relatório = "story publicado (media_id …) — confira no app".
6. **Relatório** — tipo (teaser/pensamento) + media_id, ou `pulei: <motivo>`.
   Sem log, sem token.

## Escolher cenário (depois do tipo de conteúdo)

- **TOM é do TEXTO, não da pose.** O tom do 3b ("chamada de atenção") vale
  para o overlay/CTA. A pose vem do sorteio — NUNCA derivar pose de "explicando"
  por causa do tom.
- **Sorteio determinístico (obrigatório, não inventar pose):**
  `python3 <scripts-do-gateway>/ig_story_cena_sorteio.py`
  → imprime JSON com a `cena` sorteada (pose/expressão/ângulo/enquadramento/
  cenário/look + `prompt_parte` pronta para colar) e o `teto` do dia.
  Colar o `prompt_parte` no prompt de cena. Não escolher manualmente.
  Saída estável por dia (sorteia 1x). Se o script falhar → `pulei: sorteio`.
- **Teto diário (regra 2026-08-19):** máx 2 stories/dia civil BRT. Se
  `teto.pode_publicar == false` → `pulei: teto diário atingido (2 stories)`,
  NÃO gera, NÃO publica. Conta stories com `stage=publicado` no dia BRT.
- **Ficha de cena no state.json DO STORY (após o publish; também se `pulei`
  depois de gerar):** gravar o que FOI usado, para o próximo story consultar:
  ```json
  "cena": { "pose": "...", "expressao": "...", "angulo": "...",
            "enquadramento": "...", "cenario": "...", "look": N }
  ```
  O script lê o último story publicado e exclui pose/enquadramento repetidos
  e `explicando` em sequência.
- GUARDA (iris-aparencia.md §2): proibido cama/pijama/academia/banho/festa/
  romance/sofrimento. Só ofício e contexto.
- Prompt de cena: "A mesma mulher da foto de referência. Íris
  <prompt_parte do sorteio>, luz natural, still fotorrealista."
  SEM texto no prompt.
- **Tail anti-cara-de-IA (OBRIGATÓRIO, colar no fim do prompt; blocos
  completos e mapeamento na ficha `~/iris/iris-aparencia.md` §7):** "Cabelo
  com fios individuais, frizz leve, baby hairs na testa, volume natural com
  movimento, luz refletindo entre os fios, sem cabelo de plástico. Pele com
  textura real e poros visíveis, penugem fina no rosto, brilho natural na
  zona T, maquiagem levemente marcada, sem airbrush, sem pele de boneca.
  Enquadramento levemente imperfeito, expressão relaxada, luz ambiente
  natural."
- Alavanca final (só se o resultado ainda tiver cara de IA): adicionar
  "processamento de foto de celular" ao tail (ficha §7 nota técnica).

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

## Overlay (FIX 2026-08-17)

- `_overlay_story` (pipeline.py): título com quebra em **até 2 linhas** + autosize 64→36 até caber (margem 40px/lado). Antes: fonte fixa 64px desenhava texto largo fora da tela → corte lateral (ex.: "O TRABALHO NÃO SUMIU..." virou "ABALHO NÃO SUMIU..."). O código GARANTE o encaixe — o gate visual não substitui o guard.
- Limite prático do overlay: ≈26 chars a 64px; textos maiores quebram em 2 linhas ou reduzem a fonte. CTA curto inalterado.
- **Corpo (regra 2 camadas, 2026-08-18):** campo `corpo` no overlay — autosize 34→24, máx 3 linhas, no MESMO bloco de scrim do título (gap 18). Limite prático: ~95 chars a 34px. Sem `corpo` → overlay antigo (título+CTA), defensivo.

## copy.json (schema do story — gravar ANTES do gate)

```json
{ "formato": "story",
  "caption": "texto curto 1ª pessoa, alinhado ao corpo (opcional, sem hashtag obrigatória)",
  "alt_texts": ["1 frase"],
  "overlay": { "titulo": "hook (≤40 chars)",
               "corpo": "contexto 1ª pessoa (~95 chars, máx 3 linhas) — OBRIGATÓRIO (regra 2 camadas)",
               "cta": "Siga @sou.airis" },
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
- overlay legível: título + corpo + CTA visíveis, sem corte, contraste (scrim) ok;
- TOM da cena == tom esperado (chamada de atenção / pensativo-natural);
- sem texto escrito pela difusão no fundo (overlay é o único texto).
Ruim → 1 regen (mesmo prompt) → ainda ruim → `pulei: <motivo visual>`.

## Gate factual (por conteúdo)

- Claim no texto (número/nome próprio/data/%/elo causal) → `source` OBRIGATÓRIA
  + conferência via curl (nomes literais, datas, números, A→B, ressalva,
  fail-closed). Reprovou → corrige ou `pulei: fato não confere — <o quê>`.
- Sem claim → `sem_claim: true` declarado; o gate confere a AUSÊNCIA de claim
  no texto antes de liberar (não aprova "porque é story").
