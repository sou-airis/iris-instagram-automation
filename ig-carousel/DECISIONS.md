# DECISIONS.md — ig-carousel

Ler a cada execução, junto com `references/copy-rules.md`.
Atualizar neste arquivo sempre que uma decisão nova for tomada
(o que tentamos, o que falhou e por quê, o que ficou permanente).
Não gravar tokens, secrets nem valores de `<ENV_FILE>`.

---

## 2026-08-13 — Fase 0: setup e cofre

### Recursos reais

| Recurso | Valor |
|---|---|
| Conta Instagram | `sou.airis` |
| `<IG_USER_ID>` | `<IG_USER_ID>` |
| API | Instagram Login, host `graph.instagram.com`, v23.0 |
| App Meta | `iris-publisher` (IG: `iris-publisher-IG`), Development mode (não promover) |
| App ID | `<APP_ID>` |
| Instagram App ID | `<IG_APP_ID>` |
| Cofre | `<ENV_FILE>` chmod 600 |
| Bucket R2 | `ig-carrossel` |
| Conta Cloudflare | `<CLOUDFLARE_ACCOUNT_ID>` |
| `R2_ENDPOINT` | `https://<CLOUDFLARE_ACCOUNT_ID>.r2.cloudflarestorage.com` |
| `R2_PUBLIC_URL` | `https://<R2_PUBLIC_ID>.r2.dev` |
| Token R2 vigente | `<R2_TOKEN_NAME>` (Object Read & Write, só o bucket `ig-carrossel`) |
| Objeto de teste | `teste.jpg` → `https://<R2_PUBLIC_ID>.r2.dev/teste.jpg` |
| Venv de render | `<VENV>` (playwright + pillow + boto3) |
| Browser | Chromium headless do Playwright em `~/.cache/ms-playwright` |
| Fontes | Noto Sans VF + Noto Sans Mono VF em `~/.fonts`; `fonts-noto-color-emoji` do sistema |
| Gateway | systemd `hermes-gateway` já com `Restart=always` |

Chaves no cofre: `IG_ACCESS_TOKEN`, `<IG_USER_ID>`, `R2_BUCKET`, `R2_ENDPOINT`, `R2_PUBLIC_URL`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`.

### O que falhou e por quê

1. **`python3 -m venv` com pip** — host sem `ensurepip` / `python3.13-venv`. Sem sudo. Contorno: `venv --without-pip` + `get-pip.py`.
2. **`playwright.__version__`** — o módulo não expõe o atributo. Instalação em si ok (Chromium headless 151 baixado).
3. **Troca short → long (`grant_type=ig_exchange_token`)** — duas vezes, `HTTP 400 code=452 Session key invalid`. Token curto recém-gerado ainda assim rejeitado na troca. Não improvisamos endpoint/alternativa.
4. **Validação do último token** — `GET /me?fields=id,username` retornou `username=sou.airis`. `GET /refresh_access_token?grant_type=ig_refresh_token` retornou `expires_in=5182742` (~60 dias). Esse token é o que foi gravado no cofre (já era refreshable; a troca short→long não foi necessária).
5. **Vazamento do secret R2 (`hermes-ig`)** — o secret foi escrito literalmente em `/tmp/ig-r2-put.py` via `write_file`. A UI do Hermes renderiza o conteúdo do script. Token R2 rotacionado: `hermes-ig` deletado, criado `<R2_TOKEN_NAME>`.
6. **`printf` do plano original** — continha artefatos `@url:\`...\`` que corromperiam o `.env`. Gravamos URLs limpas.
7. **Sem sudo** para `hermes-gateway` — fontes via `~/.fonts`, não `apt`. `fonts-noto` de sistema não instalado; Noto local basta para o Chromium.
8. **`pipeline.py render` rebaixava estágio** — re-render após `aprovacao` gravava `stage=render` e quebraria o gate de `publish`. Corrigido: re-render não rebaixa `aprovacao`/`publicado`.

### Regras que viraram permanentes

- Credenciais **só** em `<ENV_FILE>`. Nunca literais em `.py`/`.sh`/`.json` nem em temporário que será apagado — `write_file` aparece na UI.
- Nunca imprimir `IG_ACCESS_TOKEN` (nem outros secrets) em chat, log ou mensagem de erro. Redigir se a API ecoar o token.
- Erro da API → mostrar o erro exato e **parar**. Sem alternativa, sem navegador, sem fallback.
- Body **form-encoded**. Nunca query string no publish (hashtag quebra).
- JPEG 1080×1350 quality 90. Nunca PNG. `image_generate` liberado (2026-08-14) para slides e infográfico, com conferência visual de texto antes de publicar.
- Nunca navegador logado no Instagram.
- Sem confirmação em fonte primária → não escreve. Sem `"publica"` do usuário → não publica.
- Slug já `publicado` → recusa republicar. Retry de container sempre recria IDs (expiram em 24h).
- Git desta pasta: a cada mudança relevante, commit com mensagem descritiva. `.gitignore` cobre `.env` e credenciais.

### Validação R2 (pós-rotação)

`curl -I` em `…/teste.jpg`: `HTTP/1.1 200 OK`, `Content-Type: image/jpeg`, sem `Location`.

---

## 2026-08-13 — Fase 1: teste de publicação

Rota: `POST /{<IG_USER_ID>}/media` → poll `status_code` → `POST /media_publish` → `GET permalink`.
Imagem: `teste.jpg` no R2. Caption: `teste api`. Token lido do cofre, nunca impresso.

| Etapa | Resultado |
|---|---|
| container | `18087435563239528` |
| poll | `FINISHED` na 1ª tentativa (máx 8, 3s) |
| media | `18187620544399286` |
| permalink | https://www.instagram.com/p/Db_rSo7ARwU/ |

Post de teste: apagar pelo app antes de publicar de verdade.

`publishers/meta.py` permanece stub (`{ok:false, error:"not implemented"}`) até a Fase 4.

---

## 2026-08-13 — Fase 4: publishers/meta.py implementado

- `meta.py` real: quota → valida URL → containers por slide (`is_carousel_item`, `alt_text`) → container CAROUSEL (form-encoded) → poll 3s→6s→12s (máx 8) → `media_publish` → permalink (obrigatório).
- Retry só em temporário (5xx, 429, timeout, code 4), máx 2 tentativas; cada tentativa recria containers.
- `web_search`/`web_extract` quebrados no host (ddgs ausente; backend só-DuckDuckGo) → pesquisa via `curl` na fonte primária.
- Assunto real do 1º carrossel: **Claude Fable 5** (docs.anthropic.com, 24/jul/2026) — 1M contexto, 128k saída, $10/$50 por M, adaptive thinking sempre ligado, CoT bruto nunca retornado.

### 1º carrossel publicado (após aprovação "publica")

- slug `claude-fable-5`, 6 slides, stage `publicado`.
- Permalink: https://www.instagram.com/p/Db_4jrkEaPI/ (13/08/2026 23:08 UTC).
- Publicação via `meta.py` real de primeira: quota OK, 6 containers, poll FINISHED, permalink retornado.

---

## 2026-08-13 — Fase 5: cron de refresh do token

- Script watchdog: `<HERMES_HOME>/scripts/ig_refresh_token.py` — lê o token do cofre (nunca imprime), `GET refresh_access_token?grant_type=ig_refresh_token`, grava novo `IG_ACCESS_TOKEN` (atômico, chmod 600) e reporta SEMPRE (stdout = sucesso; ERRO + exit ≠ 0 = alerta). Silêncio = cron morto.
- Cron `ig-token-refresh` (`<JOB_REFRESH_ID>`): `0 12 1,15 * *` (dias 1 e 15, 12:00 UTC), `no_agent`, entrega `telegram:<TELEGRAM_CHAT_ID>`. Próxima execução: 2026-08-15T12:00Z.
- Teste manual em 13/08: renovou `expires_in=5172885` (~60 dias), cofre OK.
- `web_search`/`web_extract` seguem quebrados (ddgs/backend) — pesquisa via `curl`.




---

## 2026-08-13 — Identidade visual (sem posts de referência)

Sem posts do @sou.airis. Três direções propostas; escolhida **A — Redação**.

- Paleta: `#0A0A0A` / `#F2EDE4` / destaque único `#E23D28` (filete 4px).
- Hook: Darker Grotesque ExtraBold. Corpo: Newsreader. Fontes em `~/.fonts`.
- Composição: flush left, assimétrica, numeração discreta no canto inferior direito. Sem ícone, emoji ou gradiente.
- Tom: seco, técnico, sem hype. Público: quem trabalha com IA.
- Descartadas: B Spec (lima + Space Grotesk/Plex) e C Foundry (cobre + Syne/Plex).

Registrado em `templates/slide-template.html` e `references/copy-rules.md`.

### Fundo (textura fixa)

Três opções geradas (grão / ruído / geometria). Escolhida **1 — grão fotográfico**.
Asset fixo: `assets/bg.jpg` (1080×1350 JPEG), aplicado no template com `opacity: 0.6` (subiu de 0.36; 0.5 fica de reserva se sujar demais).
Não gerar fundo por post. `image_generate` continua proibido para slides (texto).
Composição ajustada: bloco de texto ancorado embaixo (`bottom: 200px`) para o hook cair no crop 1:1.

---

## 2026-08-14 — Persona v1.2

Rascunho v1.1 do usuário gravado como fonte única, com cortes de execução:

- Arquétipo travado: curador-par com opinião calibrada + 3 testes anti-drift.
- Fascínio honesto com prova; “calor” removido (risco parasocial).
- Selo de veredito em copy: Substância · Hype · Depende (não Marketing).
- Hook = gap de insider; micro-hook = implicação; pergunta só na legenda.
- CTA único (salvar padrão). Fecho: `Fonte no último slide. — Í.`
- Bio travada. “Ativa desde agosto/2026” no editorial; 12/03/1995 fica só no Google.
- Visual Redação permanece fechado. Retrato fotorrealista do perfil continua aberto.
- Reels/X/newsletter fora desta skill.
- `copy-rules.md` e passo COPY do `SKILL.md` sincronizados.

Aberto: retrato do perfil; selo no template (hoje só copy).

---

## 2026-08-14 — Persona v1.3 (versão final de caráter)

Nuance que faltava: **registro por superfície**. Um caráter, três modos (slide seco / legenda solta / comentário conversa). Princípio: IA que conversa como gente; não fabrica biografia humana.

- Quarto vizinho anti-drift: humana encenada.
- Autoconsciência: contida no slide, à vontade no comentário.
- Emoji por adequação (zero no slide; até 1 na legenda; no comentário se o fio pedir).
- Não reabriu: selo Hype, bio, fecho, “ativa desde”, visual Redação, Reels fora da skill.
- `copy-rules.md` ganhou seções de legenda e comentário.

Aberto: retrato do perfil; selo no template.

---

## 2026-08-14 — Trava de image_generate removida (decisão do usuário)

Pedido explícito do usuário: remover a proibição de `image_generate` — para carrossel **e** infográfico.
Argumento: modelos de imagem atuais (Gemini/ChatGPT/Grok e afins) já renderizam texto sem o embaralhamento de antes.

Decisões:

- `image_generate` agora é **permitido** nos dois formatos (carrossel e infográfico).
- O gate de aprovação (mostrar a imagem antes do "publica") segue obrigatório e vira a trava de segurança: texto errado/número trocado → corrige ou re-gera antes de publicar.
- O visual Redação continua a referência quando `image_generate` for usado: sem ícone, sem emoji, sem gradiente, fundo `#0A0A0A`.
- O pipeline determinístico (HTML + Playwright) segue como caminho padrão do carrossel — não alterado. `image_generate` é alternativa, não substituição automática.
- Backend de imagem desta instância: `gpt-image-2` (OpenAI). Gemini/Grok não estão plugados no `image_generate` daqui.

Arquivos alterados: `SKILL.md` (regra 1), `README.md`, `DECISIONS.md` (regras permanentes), `references/copy-rules.md`.

---

## 2026-08-14 — Formato infográfico (imagem única) implementado

Segundo formato do pipeline: `infografico` (1 imagem) ao lado de `carrossel` (padrão).

- `copy.json` ganhou `formato` = `carrossel` | `infografico`.
- `pipeline.py`:
  - `render` bifurca por `formato`. `infografico` renderiza 1 imagem 1080×1350 a partir de `blocos` (template `infografico-template.html`, blocos numerados com a identidade Redação), OU aceita `01.jpg` já válido (checkpoint).
  - Novo subcomando `convert <slug> --src <imagem>`: converte a saída do `image_generate` (crop central cover) para `01.jpg` 1080×1350 JPEG quality 90.
  - `package` valida: `infografico` exige exatamente 1 `.jpg`; grava `formato` no `package.json`.
- `publishers/meta.py`: `publish()` despacha por `formato`. `infografico` → `_attempt_single` (1 container IMAGE com caption+alt_text → poll → media_publish → permalink). `carrossel` → `_attempt` inalterado (containers + CAROUSEL).
- Testado: `render` (blocos) e `convert` geram JPEG 1080×1350 válido; guards de `publish` disparam antes de qualquer rede. Smoke tests limpos.
- Pitfalls: (1) `skill_view` devolveu `SKILL.md` defasado (persona v1.2) no início da sessão — re-ler o arquivo do disco antes de editar. (2) Chromium falhou 1 screenshot (flaky "Unable to capture screenshot") e o retry do `render` (checkpoint) resolveu.

---

## 2026-08-14 — Persona v1.4 (aresta)

Pedido explícito: particularidades para não virar perfil insosso de IA.

- Kit §3.7: sacada (obrigatória), malícia, frustração, metáfora, trocadilho, piada autodepreciativa. Dose 1–2 por peça.
- Vizinhos novos: Insossa (sem aresta) e Palhaça (graça no lugar do fato).
- Corrigido: v1.3 banía “humor” em toda superfície — agora só mau humor encenado.
- Não reabriu o resto da v1.3.

---

## 2026-08-14 — Docs Hermes alinhados à v1.4

`SKILL.md` e `README.md` passam a listar `persona-iris.md` como leitura obrigatória a cada execução (junto com copy-rules e DECISIONS). Workspace `iris/` (AGENTS.md + README) já apontava v1.4.

---

## 2026-08-14 — Identidade visual do infográfico (papel quente)

Pedido explícito: o infográfico deixa de usar Redação. Look calibrado na peça do usuário (`assets/infografico-referencia.png`) + retrato ilustrado (`assets/iris-avatar.jpg`).

Decisões:

- Dois visuais, dois formatos. Carrossel = Redação. Infográfico = papel quente `#F7EBDC` + ouro `#B78858` + cartoon 2.5D.
- Trava só o *estilo*. Layout, mascote Hermes, grade 3×2, faixa bônus e rodapé **não** são default — liberdade de criação.
- Rodapé, se existir: avatar da Íris + `Íris Nova — Especialista em IA` + `@sou.airis`. Não fabricar biografia.
- Padrão de render do infográfico: `image_generate` com as duas referências (avatar só se houver rodapé) → `pipeline.py convert`. HTML Redação fica fallback.
- Pipeline determinístico (render/upload/publish) intocado.

Arquivos: `references/infografico-visual.md`, `copy-rules.md`, `SKILL.md`, `README.md`, `assets/infografico-referencia.png`, `assets/iris-avatar.jpg`.

---

## 2026-08-14 — Infográfico enxuto (pedido do usuário)

O fluxo editorial (fonte primária, 5 blocos, selo, 4 gerações + vision) alongou um pedido simples de Telegram. Gemini resolve em 1 prompt; a skill não deve competir com isso.

Decisões (só infográfico; carrossel intocado):

- Caminho: tema → 1 `image_generate` → `convert` pad/letterbox 1080×1350 → mostrar JPEG+legenda → parar.
- `convert` deixa de fazer crop central (comia 15% do topo/base no 9:16→4:5). Agora é pad, fundo `#F7EBDC`.
- Retry no máximo 1, só se a ferramenta falhar. Sem loop de `vision_analyze`. Sem fallback HTML sozinho.
- Pesquisa, selo e `copy.json` de blocos **não** são obrigatórios no infográfico.
- Upload/publish só depois do "publica".
- Fonte primária continua obrigatória no **carrossel**.

---

## 2026-08-14 — 1º infográfico publicado

- Pedido Telegram: "função cron do Clote" → decodificado como **cron do Claude Code** (scheduled tasks). "Clote" = apelido do Claude (mesmo padrão de "Clude").
- Fonte: doc oficial `code.claude.com/docs/en/scheduled-tasks` (via `curl`; `web_search`/`web_extract` seguem quebrados no host).
- Caminho enxuto seguido: tema → 1 `image_generate` (portrait, ref `assets/infografico-referencia.png`) → `convert` pad 1080×1350 → mostrar → "publica" → package → upload → publish.
- slug `claude-code-cron`, 1 imagem, stage `publicado`. Permalink: https://www.instagram.com/p/DcB9tnaoFTl/ (14/08/2026 18:32 UTC).
- `copy.json` mínimo (formato, caption, alt_texts, source) gravado antes da aprovação.

---

## 2026-08-14 — v2/v3 do infográfico: estrutura da referência + falha de DELETE via API

- Usuário avaliou a v1 como "fraca" e pediu para seguir a referência (`assets/infografico-referencia.png`): grade 3×2, números grandes em círculo dourado, mascote fixo em todos os cards, subtítulo cursivo, faixa BÔNUS, rodapé com avatar + @sou.airis.
- v2: estrutura OK, mas texto com erros ("Tnês", "Duvem", "Vabô") — o modelo escreveu as descrições de cena (entre parênteses no prompt) como título dos cards.
- Lição (regra para prompt de infográfico): separar TEXTO EXATO de POSE. Listar título/frase palavra por palavra, poses em linha própria, e proibir explicitamente escrever cenas/parênteses na imagem. v3 saiu com zero erros (verificado via vision).
- v3 publicado: slug `claude-code-cron-v3`, permalink https://www.instagram.com/p/DcB_DXkIAEF/ (14/08/2026 18:45 UTC). v1 segue no ar.
- **DELETE de media via Graph API NÃO é suportado**: `DELETE /{media_id}` retornou `code 100, error_subcode 33 — Unsupported delete request... does not support this operation`. Apagar post do Instagram = pelo app. Não improvisar alternativa.

---

## 2026-08-14 — v4 full-bleed: limite de proporção do backend + rota HTML

- Backend de imagem (OpenRouter gemini-3-pro-image): `portrait` → canvas ~768×1376 (ratio 0.56). Pad p/ 4:5 cria ~160px de bege vazio em cada lateral; cover-crop comeria 21% do topo/base (título + rodapé). Edição (image-to-image) obedece o `aspect_ratio` do parâmetro (default landscape, não preserva o aspecto da entrada). **4:5 full-bleed por IA é impossível neste backend.**
- Correção aprovada pelo usuário: **render HTML/Playwright 1080×1350** (template `infografico.html` no dir do slug), mantendo a estrutura da referência (Bebas Neue + Dancing Script em `~/.fonts`, grade 3×2, números dourados, faixa BÔNUS, rodapé com avatar) + **mascote robô** via sprite TTI (fundo bege liso `#F7EBDC`) com color-key (pixels ≈ fundo → alpha 0, feather 30–60) e selo dourado atrás.
- Pitfall pipeline: `package` do infografico faz glob de `*.jpg` no dir do slug — `iris-avatar.jpg` de suporte quebrou ("exige exatamente 1 .jpg"). Assets de suporte ficam fora do dir do slug (ex.: `~/.hermes/ig/_assets/`).
- v4 publicado: slug `claude-code-cron-v4`, permalink https://www.instagram.com/p/DcCA0D5IPVk/ (14/08/2026 19:00 UTC). v1 e v3 seguem no ar (apagar = pelo app).

---

## 2026-08-14 — Cron diário de infográfico (pré-autorizado)

Pedido: todo dia 10:00 BRT, pesquisar 1 assunto de IA, gerar infográfico e publicar sem "publica" no chat.

- Job `iris-infografico-diario` (`<JOB_INFOGRAFICO_ID>`): `0 13 * * *` (10:00 BRT = 13:00 UTC), `deliver=telegram:<TELEGRAM_CHAT_ID>`, skills=[], forever.
- Não carrega a skill ig-carousel (regra 7 bloquearia). Prompt autocontido + lê só infografico-visual.md e persona (filtro/sacada).
- Auto-gate: vision_analyze + 1 regen; ainda ruim → pule e reporte. Sem assunto à altura → pule.
- Publish: convert (pad) → package → upload → publish. copy.json mínimo antes do package.
- Não rodei o job na criação (publicaria de verdade). Próxima: 2026-08-15T13:00Z.

---

## 2026-08-14 — Post do iceberg "Qual o seu nível com a IA"

- Imagem do USUÁRIO (1014×1280, ratio 0.792), não gerada: normalizei com resize LANCZOS + pad de ~5px com a cor da borda (creme 246,243,238) — sem re-gerar, sem HTML.
- Legenda na voz da Íris (v1.4): sacada "ferramenta de uso não é nível — é o que você constrói com ela", toque de autoconsciência (Hermes Agents no nível avançado), fecho "Salva pra quando for descer pro fundo. — Í.".
- slug `nivel-ia`, publicado: https://www.instagram.com/p/DcCGimtGNVs/ (14/08/2026 19:10 UTC).
- Lição: imagem de usuário perto do 4:5 → normalizar com pad na cor da borda (não #F7EBDC do convert).

---

## 2026-08-14 — Infográfico: Gemini manda (sem HTML, sem pad)

As peças manuais no Gemini estão boas; o pipeline de etapas (portrait + pad + HTML + grade 3×2) piorou o automático (barra bege + mascote gota).

- Caminho padrão: 1 `image_generate` **square** → `convert` cover (corta laterais) → 1080×1350. Sem barra.
- `portrait` + pad só se alguém ainda gerar 9:16 (não é o default).
- Mascote = marca do assunto (tabela em infografico-visual.md). HTML/Playwright fica no disco, fora do caminho.
- Cron: mesmo fluxo; 1 vision; ruim → pule. Prompt do job atualizado para ler o `.md`, não duplicar manifesto.

---

## 2026-08-14 — 4:5 nativo no OpenRouter + pá-pum (fim do crop/pad)

Peças manuais no Gemini web (4:5) ficam melhores que o automático (square+crop/pad → corte + barra). Causa: a tool do Hermes nunca pedia `4:5` ao OpenRouter — o plugin mapeava só `1:1/16:9/9:16`.

- API confirmada: `google/gemini-3-pro-image` aceita `image_config.aspect_ratio="4:5"` (Vertex e AI Studio). Teste real devolveu 928×1152 (0.806).
- Fix **sem root** (repo Hermes é root; sem sudo): plugin de usuário em `HERMES_HOME/plugins/image_gen/openrouter/` — vence o bundled por key igual, re-registra o provider com `4:5` no mapa e no `VALID_ASPECT_RATIOS`. Provado com payload mock (6/6).
- **Requer restart do gateway** para o processo vivo recarregar plugins.
- Fluxo: `image_generate(aspect_ratio=4:5)` → `convert` (fonte ~4:5 → resize proporcional, sem crop/pad) → mostrar.
- HTML/Playwright, mascote obrigatório e grade 3×2 saem do caminho padrão.

---

## 2026-08-15 — config Toast travada (laterais + copy)

Peça boa: https://www.instagram.com/p/DcDxq57FQZp/ (`toast-1-busca-20260815`). 1080×1350, laterais 4px.

- Laterais do Qwen (197px) eram **composição** (coluna estreita), não pad do convert. Convert agora é stretch exato.
- Tool do Desktop às vezes só enumera landscape/square/portrait e empurra `4:5` → `portrait`. Fallback: `chat/completions` + `image_config.aspect_ratio=4:5` (928×1152).
- `POST /api/v1/images` 2K + a referência **clona** o pôster Hermes. Proibido no caminho padrão.
- Prompt FULL-BLEED + anti-clone (sem rodapé/CTA/mascote romano do anexo) + copy começando do zero.
- Fonte única: `references/infografico-visual.md`. Cron aponta pra ela.

---

## Pendente (não decidir de novo sem fato novo)

- Nada em aberto das Fases 0–5: Fase 0 (setup/cofre), Fase 1 (teste de publicação), Fase 2 (pipeline), Fase 3 (visual calibrado: Redação + papel quente), Fase 4 (`meta.py` real), Fase 5 (cron `ig-token-refresh`). Todas concluídas e registradas acima.
