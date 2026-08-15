---
name: ig-carousel
description: "Carrossel para Instagram: pesquisa, copy, render, publica."
version: 1.0.0
author: hermes
license: MIT
metadata:
  tags: [instagram, carrossel, graph-api, r2, social-media]
  related_skills: [news-research-reporting]
---

# ig-carousel — carrossel de notícia para Instagram

Publica carrosséis no Instagram do usuário a partir de notícias/features verificadas.
Gatilho típico: "saiu X no Claude, faz carrossel" + (opcional) fonte + ângulo.

## When to Use

- Pedido de "carrossel" / post para Instagram (Telegram, Desktop ou Dashboard) → pipeline de carrossel.
- Pedido de "infográfico" / "post de imagem única" para Instagram → executar `references/infografico-visual.md` (seção **Chat**). Não é o carrossel.
- Publicação SEMPRE via Graph API — nunca navegador logado (regra permanente).
- NÃO publicar sem "publica" do usuário. Carrossel: sem fonte primária → não escreve. Infográfico: não bloquear por pesquisa.

## Arquitetura (inegociável)

```
skills/ig-carousel/
  SKILL.md
  DECISIONS.md                 ← histórico de decisões; LER a cada execução
  references/persona-iris.md   ← voz v1.4; LER a cada execução
  references/copy-rules.md     ← regras de copy + visual Redação (carrossel); LER a cada execução
  references/infografico-visual.md ← receita do infográfico (Chat e Cron); EXECUTAR, não resumir
  assets/infografico-referencia.png ← look do infográfico (não clonar layout/mascote)
  assets/iris-avatar.jpg       ← retrato ilustrado da Íris (rodapé, se houver)
  templates/slide-template.html ← placeholders {{titulo}} {{corpo}} {{numero}} (carrossel)
  templates/infografico-template.html ← fallback HTML (Redação); não é o padrão do infográfico
  scripts/pipeline.py          ← subcomandos: render | convert | upload | package | publish | status
  scripts/publishers/          ← ÚNICO lugar com lógica de rede
    meta.py                    ← publish(package) -> {ok, url, error}; CAROUSEL ou IMAGE (conforme formato)
    r2.py                      ← upload JPEGs pro R2 + validação de URL
    __init__.py
```

**Decisões:** ler `DECISIONS.md`, `references/persona-iris.md` e `references/copy-rules.md` em TODA execução de **carrossel**. Infográfico: executar só `references/infografico-visual.md` (seção Chat).
Atualizar `DECISIONS.md` sempre que uma decisão nova for tomada (falha, contorno, regra permanente, ID de teste).
Mudança relevante nesta pasta → `git commit` com mensagem descritiva. Sem tokens no commit.

- `package` = `{slug, formato, slides:[paths], urls:[], caption, alt_texts:[], source}`.
- `formato` = `carrossel` (padrão) | `infografico` (1 imagem).
- Artefatos em `~/.hermes/ig/<slug>/`: `NN.jpg`, `copy.json`, `state.json`, `package.json`.
- Pesquisa e copy são feitas pelo AGENTE (LLM). O `pipeline.py` executa só o determinístico (render/upload/package/status/publish), em subcomandos resumíveis (checkpoint por slide).
- Venv de render: venv local do pipeline (playwright, pillow, boto3). Browser: cache local do Playwright.

## Regras permanentes (nunca violar)

1. Se usar `image_generate` (slides ou infográfico), conferir visualmente o texto antes de publicar — letra errada/número trocado → corrige antes do "publica".
2. NUNCA navegador/browser logado no Instagram, nem como fallback — risco de bloqueio da conta. API falhou → mostra o erro exato e PARA.
3. NUNCA ação destrutiva (matar processo, derrubar porta, deletar fora de `~/.hermes/ig/`) sem perguntar antes.
4. NUNCA imprimir IG_ACCESS_TOKEN em chat, log ou mensagem de erro.
4b. NUNCA escrever credenciais literais em scripts (.py, .sh, .json) nem em qualquer arquivo fora de `~/.hermes/.env` — inclusive temporários que serão apagados. O conteúdo de `write_file` aparece na UI do Hermes. Ler sempre via `os.environ` / dotenv.
5. Erro → mostra o erro exato e para. Não improvisa alternativa.
6. Slug já "publicado" (state.json) → recusa republicar.
7. Sem "publica" do usuário → não publica. Exceção: o cron `iris-infografico-diario` (`<JOB_INFOGRAFICO_ID>`) é pré-autorizado a publicar 1 infográfico por tick após o auto-gate (não carrega esta skill). Carrossel: sem confirmação em fonte primária → não escreve. Infográfico no chat: não exige fonte primária antes de desenhar.

## Pipeline — infográfico

Executar `references/infografico-visual.md`, seção **Chat**. Não reescrever a receita aqui.

## Pipeline — carrossel

1. **PESQUISA**: web_search + fetch da fonte primária (changelog/docs/blog oficial). Sem confirmação na fonte → para e avisa. Nunca sobre feature não verificada.
2. **COPY**: `formato=carrossel`. Piso 6 slides, até 8–10 só com insight real, máx 20 palavras cada. Slide 1 = gap de insider; último = recap + um CTA. Slides no registro de publicação (sacada obrigatória); legenda no registro solto (fecho `Fonte no último slide. — Í.`). Legenda ≤2200 chars, 5-8 hashtags. alt_text de 1 frase por slide. Ler `references/persona-iris.md`, `references/copy-rules.md` e `DECISIONS.md`. Gravar `copy.json`.
3. **RENDER**: `pipeline.py render <slug>`. Playwright, 1080x1350 JPEG quality 90. Checkpoint por slide.
4. **UPLOAD**: `pipeline.py upload <slug>`. R2; curl -I → 200 + image/jpeg, sem redirect.
5. **APROVAÇÃO**: enviar JPEGs + legenda e PARAR. Só publica após "publica".
6. **PUBLICAÇÃO**: `pipeline.py publish <slug>` → permalink no state.json.
7. **ESTADO**: `pipeline.py status <slug>`.

## Credenciais

`~/.hermes/.env` (chmod 600): `IG_ACCESS_TOKEN`, `<IG_USER_ID>`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ENDPOINT`, `R2_BUCKET`, `R2_PUBLIC_URL`.
Token NUNCA em chat/log/erro.

## Uso diário

"saiu <funcionalidade> no Claude. Fonte: <link se tiver>. Ângulo: <o que destacar>."

## Espelho GitHub (manual, sem automação)

A cada commit de mudança na skill, PERGUNTAR ao usuário: "sincronizar o espelho no GitHub?".
Sim → archive + allow-list (tracked files menos `DECISIONS.md`) → `~/iris-instagram-automation/ig-carousel/` → commit → push via GIT_ASKPASS. Pre-push hook é o gate — bloqueou = mostrar e parar. Sem cron, sem config, sem log.
