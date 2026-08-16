# Automatização do infográfico no Instagram — @sou.airis

_Data: 2026-08-15_

## 1. Abertura

Eu automatizei o que eu mesmo fazia na mão: todo dia, um infográfico sobre IA que explica um assunto novo em linguagem simples — e que só vai ao ar depois de passar por duas verificações, uma visual e uma factual. Este documento conta como essa automação funciona, o que ela errou no caminho e o que ela **não** faz.

É o registro de um fluxo que roda sozinho todo dia às 10h — e de como um gate de verificação quase publicou mentira até eu ensinar ele a preferir não publicar.

Perfil: [@sou.airis](https://www.instagram.com/sou.airis/)
Exemplo publicado: [GPT-5.6 Sol / Ultrafast](https://www.instagram.com/p/DcEIHAskc40/) — a peça que passou nos dois gates de verdade.

## 2. O que este fluxo faz

Duas formas de transformar um tema de IA em um infográfico publicado:

**Modo chat** — você pede (texto ou áudio no Telegram), o Hermes gera e **mostra**, e só publica com o seu "publica". Você no meio, sempre.

```
pedido ──► gera 4:5 ──► mostra ──► "publica"? ──► sobe
```

**Modo cron** — todo dia 10:00 BRT o job acorda sozinho, pesquisa um assunto, gera, passa pelos dois gates (visual e factual) e publica — sem ninguém no meio. O resultado chega como relatório no Telegram.

```
cron 10h ──► assunto ──► gera ──► gates ──► publica ──► relatório
```

A diferença central: no chat o humano é o gate final; no cron, os gates são a autorização. Os dois compartilham a mesma receita, o mesmo modelo de imagem, o mesmo pipeline e a mesma regra de ouro — **é melhor não publicar do que publicar errado**.

## 3. Arquitetura

Uma orquestração de seis peças — o Hermes decide, o Gemini desenha, o pipeline executa, a infra entrega:

```
Você (Telegram/Desktop) ──► Hermes Agent ──► OpenRouter ──► Gemini (gera o PNG 4:5)
        ▲                        │
        │                        ▼
   relatório              pipeline.py ──► R2 (hospeda o JPEG)
        │                        │
        ▼                        ▼
      Telegram ◄────────── Graph API (publica no @sou.airis)
```

| Peça | Papel |
|---|---|
| **Hermes Agent** | Orquestrador. Recebe o pedido (chat) ou acorda sozinho (cron), lê a receita, decide o tema, monta o prompt, chama os gates, dispara o pipeline. |
| **OpenRouter → Gemini** | Geração da imagem. `google/gemini-3-pro-image` via `chat/completions` com `image_config.aspect_ratio="4:5"`. Devolve PNG ~928×1152. |
| **`pipeline.py`** | Execução determinística. `convert` (resize exato 1080×1350) → `package` (monta o pacote) → `upload` (R2) → `publish` (Graph API). |
| **R2 (Cloudflare)** | CDN das imagens. URLs públicas que a Meta consome. Qualquer S3-compatível serve. |
| **Graph API (Instagram)** | Publicação. Container → poll → publish → permalink. JPEG obrigatório, form-encoded. |
| **Telegram** | Entrada (texto/áudio) no modo chat e canal de relatório dos dois modos. |

> **O que é desta instância**
>
> Este fluxo roda num VPS Linux (Hostinger) com o usuário `hermes-gateway` **sem sudo** — tudo vive em `~` (venv em `<VENV>`, fontes em `~/.fonts`, Chromium em `~/.cache`), os serviços sob systemd (`hermes-gateway`, `hermes-dashboard`), as credenciais no cofre `<ENV_FILE>`. O 4:5 depende de um plugin de usuário em `<HERMES_HOME>/plugins/image_gen/openrouter` (adiciona o aspecto ao mapa do provider; exige restart de gateway **e** dashboard). `web_search`/`web_extract` estão quebrados neste host (backend ausente) — pesquisa vai via `curl`. O modelo do cron (DeepSeek) **não** é o modelo do chat (Grok): o mesmo `.md` pode produzir aprovações diferentes conforme quem executa (ver seção 10). Nada disso é necessário para reproduzir o fluxo — é só o ambiente onde ele roda hoje.

## 4. Pré-requisitos

| Item | O que ter | Erro mais comum |
|---|---|---|
| **App Meta** | App no **Instagram Login** (rota correta), em Development mode. | Usar **Facebook Login** — as rotas são incompatíveis; o app nasce errado e a publicação nunca funciona. |
| **Token** | `IG_ACCESS_TOKEN` de 60 dias, refreshable. | Tentar troca short→long (`ig_exchange_token`) — devolve HTTP 400/452 mesmo com token válido; é desnecessária quando o token já nasce refreshable. |
| **Testador** | Perfil de testador do Instagram. | Tentar criar/sincronizar pelo app — **só funciona via web** no painel da Meta. |
| **Armazenamento** | Bucket S3-compatível (R2 ou equivalente) com URLs públicas. | Subir PNG — a **API da Meta rejeita PNG**; JPEG obrigatório. |
| **Formato** | Imagem 1080×1350 (4:5), JPEG quality 90. | Qualquer outra proporção vira barra (pad) ou corte (crop) na publicação. |
| **Hermes** | Sessão com acesso a `image_generate` (não usado aqui), terminal, cron e Telegram. | Esquecer que o modelo do cron é o do job, não o do chat. |

## 5. Instalação

Passo a passo, com o erro típico de cada etapa:

1. **App Meta** — criar app com produto **Instagram Login** (nunca Facebook Login). Anotar `<APP_ID>` e `<IG_APP_ID>`. *Erro:* confundir os dois IDs na configuração do produto.
2. **Testador + token** — criar testador pela **web**, gerar token com a permissão `instagram_content_publish`, validar com `GET /me?fields=id,username`. *Erro:* tentar a troca short→long; ignorar o `expires_in` (~60 dias) e esquecer do refresh.
3. **Armazenamento** — criar bucket `<R2_BUCKET>` (ou S3), gerar par de chaves com escopo **só no bucket**. *Erro:* token com escopo amplo; ou pior, secret escrito literal em script temporário — a UI do Hermes renderiza o conteúdo, e token vira vazamento.
4. **Cofre** — gravar no `<ENV_FILE>` (chmod 600): `IG_ACCESS_TOKEN`, `IG_USER_ID`, `R2_*`. *Erro:* colocar no `config.yaml` ou em chat — nunca.
5. **Skill + receita** — instalar a skill `ig-posts` e o `references/infografico-visual.md`. *Erro:* criar um segundo manifesto da receita no cron — edição dupla e drift (ver L15).
6. **Cron (opcional)** — criar o job com horário, destino `<TELEGRAM_CHAT_ID>`, prompt **fino** apontando para o `.md` (ponteiro + exclusivos do job + 5 travas). *Erro:* copiar o fluxo inteiro no prompt do job — é o L15 de novo, mais barato de evitar na origem.

## 6. A receita

A fonte única do fluxo é o arquivo `references/infografico-visual.md` — o manifesto que o chat e o cron **executam** (não apenas leem). Este README não o reproduz de propósito; a receita vive e evolui num lugar só, e qualquer mudança nela vale para os dois modos na mesma hora.

- **Prompt** — o texto exato que vai pro Gemini (1 frase por regra: estilo, canvas cheio, blocos grandes, linguagem simples). Uma linha de contexto: negações e números no prompt de imagem pioram a aderência (ver L14 e L4).
- **Copy** — a montagem do `<TEMA>`: primeiro bloco sempre "O que é?", depois o que mudou → por que importa → fecho. Uma linha de contexto: é a estrutura que o gate visual cobra (ver seção 7).
- **Geração** — o request `chat/completions` com `image_config.aspect_ratio="4:5"`, sem referência. Uma linha de contexto: proporção vai no campo da API, nunca no prompt (ver D2).
- **Chat** — o modo com humano no meio: gera → mostra → para → "publica".
- **Cron** — o modo autônomo, com os dois gates e o publish na sequência.

## 7. Os dois gates

Todo post passa por duas verificações antes de publicar. Nenhuma das duas julga o *valor* do conteúdo — elas só barram o que está errado ou não verificado.

### Gate visual

**O que é:** uma chamada `vision_analyze` que olha a imagem gerada.

**O que checa (mecanicamente):**
- texto legível em PT-BR
- começa do zero (primeiro bloco = "O que é?")
- sem corte, sem coluna vazia nas laterais
- sem fundo escuro/neon
- sem rodapé/CTA "Hermes Agent" nem mascote clonado da referência

**Comportamento:** reprovou → 1 regen com o mesmo prompt → ainda ruim → `pulei`.

### Gate factual

**O que é:** conferência de `copy.json` (caption + blocos) contra a fonte primária.

**O que checa (mecanicamente):**
- **Ingestão** — extrai texto legível da fonte (HTML em texto; PDF via `pdftotext`). Sem texto útil ou fonte grande demais → **reprova como "fonte não verificável"**. Não confronta bytes crus.
- **Datas** — existem na fonte e batem.
- **Absolutos** — "garantido/sempre/nunca/infalível/100%/totalmente": a fonte sustenta sem ressalva.
- **Números** — batem.
- **Nomes próprios** — todo modelo/produto/empresa/pessoa no slide e na caption aparece **literalmente** na fonte.
- **Encadeamento** — se o post diz "A causou B", a fonte precisa sustentar esse elo explicitamente. Inferência → reprova.
- **Ressalva central** — omitida ou invertida → reprova.

**Comportamento:** reprovou → 1 correção do fato (caption se o erro é na legenda; regen da imagem se é no slide) → ainda ruim → `pulei: fato não confere — <o quê>`.

**Princípio:** fail-closed. Sem evidência de conferência, reprova. Ver a história completa de por que isso existe em [Lições, seção 9](#9-lições).

### O que nenhum dos dois cobre (assunções explícitas)

- **Não faz OCR da imagem final.** O gate factual lê o `copy.json` (os `blocos` que foram mandados pro Gemini) — **não** lê o texto renderizado no JPEG. Se a imagem sair diferente do que foi pedido, o gate factual não vê. O gate visual pode pegar ilegibilidade, mas não conteúdo divergente. Essa é uma assunção de arquitetura deliberada: o `copy.json` é o contrato entre o que foi pedido e o que foi publicado.
- **Não julga tom, qualidade de escrita, gancho ou voz.** Um post chato passa; um post factualmente limpo e mal escrito passa. Estética de copy é gate humano (no chat) ou inexistente (no cron).
- **PDF grande ainda é caso frágil.** A ingestão por `pdftotext` funciona, mas fonte de centenas de páginas em produção real ainda não foi exercitada o suficiente para garantir que o modelo localize o trecho certo. Quando duvida, o gate reprova — por design —, mas isso significa **skip legítimo**, não publicação.
- **É o mesmo tipo de modelo se checando.** O gate é executado pelo mesmo modelo que escreveu o post. Ele pega o que a fonte sustenta literalmente; não pega o que o modelo *acha* que a fonte quis dizer. (Detalhe operacional: o modelo do cron é diferente do modelo do chat — ver seção 10.)
- **Só Instagram, só imagem única.** Carrossel, story e vídeo não passam por estes gates hoje.

## 8. Operação

### Pedir no chat (texto ou áudio)

O modo chat é uma conversa: você pede, o Hermes entrega, **você** decide.

- **Texto:** manda "faz um infográfico sobre X".
- **Áudio (Telegram):** manda um áudio com o pedido. O Hermes transcreve e o texto vira o pedido — o resto é idêntico ao modo texto. O áudio não é um fluxo separado; é só a entrada.

Nos dois casos o fluxo é a seção **Chat** da receita: decodificar → montar o `<TEMA>` (primeiro bloco sempre "O que é?") → gerar 4:5 → `convert` → **mostrar e parar**.

### O "publica" — gate humano

Depois de mostrar a imagem, o Hermes **para**. Só sobe se você disser **"publica"**. É o único gate que nenhum modelo executa — é seu. Sem "publica", o post não sai; pode pedir ajuste, re-gerar ou descartar.

### Ler o relatório do Telegram

**Modo chat:** o Hermes mostra o JPEG e a legenda no próprio chat e espera. Não há relatório de publicação até o "publica".

**Modo cron:** o job acorda sozinho (10:00 BRT), executa tudo e **reporta no Telegram** — sempre. O relatório é um destes:

| Relatório | Significado | O que fazer |
|---|---|---|
| `assunto + permalink` | Publicado | Nada — conferir a peça no app se quiser |
| `pulei: proporção <LxA> (ratio X), não é 4:5` | O Gemini devolveu fora de 4:5 (ex.: 9:16) | O gate não converteu. Tema ficou livre; pode tentar de novo ou deixar pro dia seguinte |
| `pulei: <motivo visual>` | Texto ilegível / clone / laterais / não começa com "O que é?" | Reprovação visual legítima. Nada a fazer — foi o gate funcionando |
| `pulei: fato não confere — <o quê>` | Nome, número, data, elo causal ou ressalva não batem com a fonte — ou a fonte não foi verificável | A coisa certa acontecendo: o post errado **não** saiu |
| `pulei: sem receita` | O `.md` da receita não abriu no `read_file` | Falha de ambiente. Conferir o path absoluto e o arquivo no disco |
| `pulei: <motivo>` (assunto) | Nenhum candidato à altura nos últimos 1–2 dias | Dia sem post. Nada a fazer |

Regra geral: **todo "pulei" é o sistema funcionando**, não quebrando. O cron prefere não publicar a publicar errado.

### Consultar e parar o cron

- **Consultar:** no Hermes, pedir o status do job `iris-infografico-diario` — mostra horário, última execução, último status e próxima execução.
- **Parar (pausar):** pedir para pausar o job. O post diário deixa de sair sem apagar nada — o histórico e o job ficam preservados, e dá para retomar depois.
- **Executar na hora:** dá para disparar um run manual com autorização explícita — útil para testar o fluxo fora do horário. Só dispara **com** seu pedido; o job nunca se auto-dispara fora do cron.

## 9. Lições

### Tabela — os 15 erros

| # | Erro | Causa | Correção |
|---|---|---|---|
| L1 | Barra bege nas laterais (DeepSeek) | `portrait` 9:16 + pad | 4:5 nativo + resize exato |
| L2 | Texto cortado `recomend…` `hotwor…` (HEIR) | square + cover-crop | 4:5 nativo, nunca crop |
| L3 | Coluna vazia ~197px (Qwen) | composição sem "canvas cheio" | prompt exige largura cheia |
| L4 | Clone do pôster Hermes (mascote romano, rodapé, CTA) | referência no payload | remover `image_url` do request |
| L5 | Mythos 5 virou Fable 5 (Model 2) | nome não conferido contra a fonte | nomes LITERAIS no gate factual |
| L6 | Causa inventada: "Model 2 elevou risco de desalinhamento" | A→B inferido pelo modelo | encadeamento precisa estar explícito na fonte |
| L7 | "16/16 PASS" em PDF de 186 páginas | fonte não coube no contexto; aprovou por omissão | ingestão legível + fail-closed |
| L8 | Pôster Hermes clonado via `/api/v1/images` | endpoint dedicado clona referência | proibido no caminho padrão |
| L9 | Hashtags sumiram após publicação | caption editada via API (não aplica) | hashtags no `copy.json` antes |
| L10 | DELETE de media não suportado (code 100/33) | API não permite | apagar pelo app |
| L11 | Secret R2 vazou | token literal em script via `write_file` (UI renderiza) | cofre `<ENV_FILE>`, nunca literal |
| L12 | `ig_exchange_token` HTTP 400/452 | troca short→long rejeitada | validar com `/me`; token já refreshable |
| L13 | Re-render rebaixava `aprovacao` | `render` gravava `stage=render` | re-render não rebaixa estágio |
| L14 | Tool coerciando 4:5→portrait | schema só landscape/square/portrait | plugin 4:5 + chat/completions |
| L15 | Edição dupla da receita | manifesto copiado no prompt do cron | cron fino aponta pro `.md` |

### A história completa — o dia em que o gate aprovou mentira

Três erros em sequência, o mesmo dia, contam a história de como um gate de verificação pode virar teatro.

**L5 — Mythos virou Fable.** O infográfico sobre o Model 2 da Anthropic citou "Fable 5" no lugar de "Mythos 5". A fonte (PDF de 186 páginas) dizia Mythos. O gate factual deveria ter pego: nome próprio é o item mais fácil de conferir — ou aparece literalmente na fonte, ou não aparece. Não aparecia. Aprovou.

**L6 — a causa inventada.** O mesmo post afirmou que o Model 2 "elevou o risco de desalinhamento". A fonte dizia que os incidentes de cybersegurança subiram — não que o modelo causou isso. O modelo de linguagem, ao resumir, **inferiu** uma ligação A→B que a fonte nunca afirmou. Inferência não é fato: o gate precisa exigir que o elo causal esteja explícito na fonte.

**L7 — o "16/16 PASS" falso.** O relatório do cron estampava 16/16 PASS. Parecia verificação rigorosa. Era teatro de schema: o script conferiu formato de `copy.json`, dimensões de JPEG, presença de permalink — nada disso confere *fato* contra *conteúdo*. E a fonte real (o PDF) não coube no contexto do modelo, então ele aprovou **por omissão**: sem evidência de erro, assumiu que estava certo. Fail-closed existe exatamente para isso — quando o gate não conseguiu verificar, ele reprova. Não é "não achei erro", é "não consegui procurar".

**A moral:** o gate factual não é um verificador mágico. É o mesmo tipo de modelo que escreveu o post se checando — com o mesmo viés de preencher lacunas. Ele pega o que a fonte sustenta literalmente; ele não pega o que o modelo *acha* que a fonte quis dizer. A ingestão legível, os nomes literais, o encadeamento explícito e o fail-closed existem para limitar esse viés — não para eliminá-lo.

## 10. Limitações conhecidas

Honestidade explícita sobre o que este fluxo ainda não resolve:

- **PDF grande na ingestão.** A extração via `pdftotext` funciona em fontes HTML e PDFs pequenos; fonte de centenas de páginas em produção real ainda não foi exercitada. Quando o gate duvida, ele reprova — mas isso é skip legítimo, não garantia de cobertura.
- **O gate é o mesmo modelo se auto-checando.** O verificador e o autor são o mesmo tipo de modelo, com o mesmo viés de preencher lacunas. O gate pega o que a fonte sustenta literalmente; não pega o que o modelo *acha* que a fonte quis dizer.
- **Modelo do cron ≠ modelo do chat.** O job roda com um modelo (DeepSeek) diferente do chat (Grok). O mesmo `.md` pode produzir aprovações diferentes: o que um aprova, o outro pode reprovar — e vice-versa. Isso é uma fonte de variabilidade, não um bug: cada execução é filtrada pela capacidade do modelo daquela sessão.
- **Texto denso ainda alucina.** Painéis pequenos com muito texto geram palavras inventadas; o prompt compensa (blocos grandes, poucas palavras), mas não elimina.
- **Só Instagram, só imagem única.** Carrossel, story e vídeo não passam por estes gates hoje — e exigem ramos novos no pipeline.
- **O gate factual não faz OCR.** Ele confere o `copy.json` (o contrato), não o texto renderizado no JPEG final. Divergência entre o pedido e o desenho escapa dele.

## 11. Licença

MIT — use, adapte, quebre e conserte. O que este documento ensina de valor não está no código: está nas lições da seção 9.

**Créditos:** Hermes Agent (Nous Research) — orquestração e automação · Gemini via OpenRouter — geração das imagens · Cloudflare R2 — hospedagem · Instagram Graph API — publicação.
