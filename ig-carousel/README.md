# ig-carousel — automação de carrossel no Instagram (@sou.airis)

Guia de consulta rápida. Escrito para quem entende de IA mas não é programador.
Voz da Íris: `references/persona-iris.md` (v1.4). Regras de texto e visual: `references/copy-rules.md`. Decisões: `DECISIONS.md`.

---

## O que é

Uma skill do Hermes que transforma uma novidade de IA em um carrossel do Instagram, do começo ao fim:

> Você manda *"saiu X no Claude, faz carrossel"* → o Hermes pesquisa na fonte oficial, escreve o texto, renderiza os slides, sobe as imagens, te mostra e espera seu **"publica"** → publica via API e te devolve o link.

Nada de navegador logado, nada de abrir o Instagram no celular. A publicação usa a API oficial (Graph API). Você é o único que decide o momento de publicar.

### Dois formatos

| Pedido | `formato` | Resultado |
|---|---|---|
| "faz carrossel sobre X" | `carrossel` (padrão) | 6–8 slides → post de carrossel (CAROUSEL) |
| "faz um infográfico de imagem única sobre X" | `infografico` | 1 imagem no estilo papel quente → post IMAGE |

O `infografico` é o caminho curto: 1 `image_generate` → `convert` (pad, sem crop) → mostrar. Upload só no "publica". Sem pesquisa editorial.

---

## Arquitetura

### Fluxo (de cima para baixo)

```
"saiu X no Claude, faz carrossel"
        │
        ▼
1. PESQUISA ── busca a fonte primária (changelog/docs oficial)
        │        ⚠ sem confirmação na fonte → para e te avisa
        ▼
2. COPY ───── escreve os slides na voz da Íris (v1.4: sacada obrigatória, 3 registros)
        │        persona-iris.md + copy-rules.md
        ▼
3. RENDER ─── gera JPEG 1080×1350 por slide (Playwright + Chromium)
        ▼
4. UPLOAD ─── sobe os JPEGs pro R2 e valida cada URL
        ▼
5. APROVAÇÃO ─ te mostra as imagens + legenda e PARA
        │        (só publica quando você responder "publica")
        ▼
6. PUBLICAR ── Graph API (meta.py): cria containers → publica → link
        ▼
7. ESTADO ─── grava permalink no state.json ("publicado")
```

### Papel de cada arquivo

| Arquivo | O que faz |
|---|---|
| `SKILL.md` | Instruções e regras permanentes da skill (o "manual de operação"). |
| `DECISIONS.md` | Log de tudo que decidimos, o que falhou e por quê. Ler a cada execução. |
| `references/persona-iris.md` | Fonte única da voz (v1.4): curador-par, 3 registros, kit de aresta. |
| `references/copy-rules.md` | Regras de texto + identidade visual (paleta, fontes, composição). |
| `templates/slide-template.html` | O "molde" do slide (carrossel). Tem `{{titulo}}`, `{{corpo}}`, `{{numero}}`; o texto é preenchido em HTML e virado imagem pelo Playwright. |
| `templates/infografico-template.html` | Fallback HTML do infográfico (Redação). Não é o caminho padrão. |
| `references/infografico-visual.md` | Estilo do infográfico (papel quente + ouro + cartoon 2.5D). |
| `assets/infografico-referencia.png` | Look de referência do infográfico — não clonar layout/mascote. |
| `assets/iris-avatar.jpg` | Retrato ilustrado da Íris para o rodapé, se a peça tiver assinatura. |
| `assets/bg.jpg` | Textura de fundo fixa (grão fotográfico), aplicada com opacidade baixa. |
| `scripts/pipeline.py` | O executor. Subcomandos: `render`, `convert`, `package`, `upload`, `publish`, `status`. |
| `scripts/publishers/meta.py` | **Único lugar que fala com o Instagram** (Graph API). |
| `scripts/publishers/r2.py` | **Único lugar que fala com o Cloudflare R2** (upload + validação). |
| `.gitignore` | Garante que `.env` e credenciais nunca entrem no git. |

Regra de ouro da arquitetura: **nenhuma lógica de rede fora de `publishers/`**. Todo o resto (render, copy, estado) é local e previsível.

Os artefatos de cada post ficam em `~/.hermes/ig/<slug>/`: os JPEGs (`01.jpg`, `02.jpg`, …), o `copy.json` (texto), o `package.json` (montagem) e o `state.json` (em que etapa está).

---

## Recursos usados (nomes e IDs reais — nunca credenciais)

| Recurso | Valor |
|---|---|
| Conta Instagram | `@sou.airis` |
| ID da conta IG (API) | `<IG_USER_ID>` |
| API | Instagram Login, host `graph.instagram.com`, versão `v23.0` |
| App Meta | `iris-publisher` (IG: `iris-publisher-IG`), em **Development mode** (não promover) |
| App ID | `<APP_ID>` |
| Instagram App ID | `<IG_APP_ID>` |
| Permissão que importa | `instagram_business_content_publish` |
| Bucket R2 | `ig-carrossel` |
| Endpoint R2 (S3) | `https://<CLOUDFLARE_ACCOUNT_ID>.r2.cloudflarestorage.com` |
| Conta Cloudflare | `<CLOUDFLARE_ACCOUNT_ID>` |
| URL pública (r2.dev) | `https://<R2_PUBLIC_ID>.r2.dev` |
| Token R2 vigente | `<R2_TOKEN_NAME>` (Object Read & Write, escopo: só o bucket `ig-carrossel`) |
| Cofre de credenciais | `~/.hermes/.env` (chmod 600) |
| Ambiente de render | venv local do pipeline (playwright + pillow + boto3) |
| Navegador | Chromium headless do Playwright em `~/.cache/ms-playwright` |
| Fontes | Hook: Darker Grotesque · Corpo: Newsreader · Emoji: Noto Color Emoji |
| Identidade visual | "Redação": fundo `#0A0A0A`, tinta `#F2EDE4`, destaque `#E23D28` |
| Cron de refresh | `ig-token-refresh` (id `<JOB_REFRESH_ID>`) — dias 1 e 15, 12:00 UTC, entrega no Telegram (chat `<TELEGRAM_CHAT_ID>`) |
| Gateway | serviço systemd `hermes-gateway` com `Restart=always` |

Cofre (`~/.hermes/.env`) guarda exatamente estas chaves: `IG_ACCESS_TOKEN`, `<IG_USER_ID>`, `R2_BUCKET`, `R2_ENDPOINT`, `R2_PUBLIC_URL`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`. Os valores delas **nunca** aparecem em chat, log, commit ou arquivo da skill.

Primeiro carrossel publicado (teste real): `claude-fable-5` → https://www.instagram.com/p/Db_4jrkEaPI/

---

## Como usar no dia a dia

Mande (no Telegram, Desktop ou Dashboard):

```
saiu <funcionalidade> no Claude. Fonte: <link se tiver>. Ângulo: <o que destacar>.
```

Exemplo:

```
saiu Claude Fable 5. Fonte: docs.anthropic.com. Ângulo: 1M de contexto e raciocínio que não vaza.
```

Infográfico de imagem única:

```
faz um infográfico de imagem única sobre <assunto>. Fonte: <link>. Ângulo: <o que destacar>.
```

O Hermes faz pesquisa → copy → render → upload e **para** na prévia, te mandando as imagens e a legenda. Aí você decide:

- **"publica"** → publica via API e devolve o permalink.
- Qualquer pedido de ajuste ("título menor", "menos texto no slide 3") → recalibra e mostra de novo.

Você continua no controle: sem o seu "publica", nada vai ao ar.

---

## Como reconstruir do zero (se perder tudo)

Ordem sugerida:

1. **App Meta + token** — developers.facebook.com → Meus apps → criar app (caso de uso Instagram), manter em Development mode. Menu Instagram → Configuração da API com login do Instagram → gerar token com a permissão `instagram_business_content_publish`. Anotar o **token** e o **ID da conta** (`sou.airis` → `<IG_USER_ID>`).
2. **Bucket R2** — Cloudflare → R2 → criar `ig-carrossel` → Settings → habilitar acesso público (subdomínio `r2.dev`) → criar API token Read & Write só desse bucket.
3. **Cofre** — criar `~/.hermes/.env` (chmod 600) com as 7 chaves listadas acima.
4. **Ambiente** — `python3 -m venv --without-pip <VENV_IG>` + `curl -sS https://bootstrap.pypa.io/get-pip.py | <VENV_IG>/bin/python` + `pip install playwright pillow boto3` + `playwright install chromium`. Fontes (Darker Grotesque, Newsreader) em `~/.fonts`.
5. **Skill** — restaurar esta pasta (`git` local em `skills/social-media/ig-carousel/`, ou recriar os arquivos). Garantir `assets/bg.jpg` presente.
6. **Testar** — subir um `teste.jpg` no R2 e rodar `curl -I` (esperar 200 + image/jpeg). Depois um post de teste (Fase 1: container → poll → publish → permalink) e apagar pelo app.
7. **Cron** — recriar `ig-token-refresh` com o script `~/scripts/ig_refresh_token.py`.

---

## Armadilhas que encontramos (e a saída)

| # | Problema | Resolução |
|---|---|---|
| 1 | `python3 -m venv` falhava (sem `ensurepip` / `python3.13-venv`, e sem sudo) | `venv --without-pip` + bootstrap do pip via `get-pip.py`. |
| 2 | Troca short→long (`ig_exchange_token`) deu `code=452 Session key invalid` | O token recém-gerado já era *refreshable*. Validar com `GET /me?fields=id,username` e seguir com ele. |
| 3 | **Vazamento de secret**: segredo escrito literalmente num script apareceu na UI do Hermes | Regra permanente: credencial só no cofre; script lê via `os.environ`/dotenv. Token R2 rotacionado. |
| 4 | `printf` do plano com artefatos `@url:\`…\`` corromperia o `.env` | Gravar URLs limpas, sem wrapper. |
| 5 | Sem sudo para pacote de sistema | Fontes locais em `~/.fonts` (não `apt`). |
| 6 | `render` rebaixava o estágio de `aprovacao` para `render` (quebraria o gate de publicar) | Re-render não rebaixa mais estágio avançado. |
| 7 | `web_search`/`web_extract` quebrados (backend só-DuckDuckGo, `ddgs` ausente) | Pesquisa via `curl` direto na fonte primária. |
| 8 | PNG é rejeitado pela API da Meta | Sempre JPEG, quality 90, exatamente 1080×1350. |
| 9 | Hashtag quebra se for na query string | Corpo sempre form-encoded (`application/x-www-form-urlencoded`). |
| 10 | Container de mídia expira em 24h | Retry sempre recria containers; nunca reutiliza IDs antigos. |

---

## Manutenção e troubleshooting

**Token de acesso.** O cron `ig-token-refresh` renova sozinho nos dias 1 e 15 (12:00 UTC) e te avisa no Telegram — em caso de sucesso **ou** falha. Se ficar sem notícia nesses dias, o cron morreu (silêncio é o alarme). Se o token morrer de vez: gerar outro no app Meta, gravar no `.env`, validar com `GET /me` e pedir o refresh manual.

**Quota.** Antes de publicar, o `meta.py` checa `content_publishing_limit`; se estourar, ele para com mensagem clara (limite diário do Instagram, não é erro nosso).

**Publicação falhou?** A regra é: mostrar o erro exato e parar — sem improvisar, sem navegador, sem repetir às cegas. `meta.py` só re-tenta erro temporário (5xx, timeout, rate limit), no máximo 2 vezes. Erro de permissão/token/formato é reportado na hora.

**Onde olhar o estado de um post.** `python3 scripts/pipeline.py status <slug>` (mostra o `state.json`). Se o slug já estiver `publicado`, o pipeline se recusa a republicar.

**Quer mudar o visual ou a voz.** Carrossel: `templates/slide-template.html` + seção Redação em `copy-rules.md`. Infográfico: `references/infografico-visual.md`. Voz: `references/persona-iris.md` (pedido explícito, commit).

**Nunca, em hipótese alguma:** navegador logado no Instagram (risco de bloqueio da conta) ou ação destrutiva fora de `~/.hermes/ig/` sem perguntar. `image_generate` é permitido (2026-08-14), mas o texto da imagem é conferido visualmente antes de publicar — o gate de aprovação garante.
