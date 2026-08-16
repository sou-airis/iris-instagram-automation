# Infográfico Instagram

Peça âncora: Toast 1 (`toast-1-busca-20260815`) — https://www.instagram.com/p/DcDxq57FQZp/

Chat lê e executa a seção **Chat**. Cron lê e executa a seção **Cron**.
Cron também lê persona §3.7.
Pipeline: `<venv-do-pipeline>/bin/python <caminho-da-skill>/scripts/pipeline.py`

## Prompt

```
Infográfico editorial sobre: <TEMA>
Estilo: ilustração cartoon 2.5D, fundo papel creme, paleta sóbria e quente, traço limpo.
Canvas cheio. Título e blocos usam a largura da página.
Título no topo; blocos em sequência: o que é / o que mudou / por que importa / fecho.
Poucas palavras por bloco. Blocos grandes, texto respirando.
Linguagem simples e concatenada, uma ideia por bloco, história que começa do zero.
No rodapé, em faixa creme: "IA explicada de forma simples. Siga @sou.airis"
```

## Copy

1. Primeiro bloco é sempre **O que é?** (definir o assunto antes de avançar). Sem isso o gate visual reprova.
2. Depois: o que mudou → por que importa → fecho prático.
3. 1 ideia por bloco, frase curta, a próxima puxa a anterior.
4. Zero jargão de benchmark. Número vira frase.
5. Sem metáfora solta ("receita", "base") sem contexto.
6. Título: nome + o que ele é agora.

Caption no `copy.json`: curta, 5–8 hashtags já no texto, fecho `— Í.`

## Geração

1. `POST https://openrouter.ai/api/v1/chat/completions` com `model=google/gemini-3-pro-image`, `image_config.aspect_ratio="4:5"`, só texto (Prompt + `<TEMA>`). Sem `image_url`.
2. Aceito: PNG ~928×1152 (ratio 0.78–0.82). Fora disso: não rode `convert`.
3. Retry 1 só se a chamada falhar vazia.
4. `convert <slug> --src <png>`: fonte ~4:5 → resize exato 1080×1350. Sem crop, sem pad, sem canvas creme.

## Chat

1. Decodificar o pedido. Montar o `<TEMA>` (seção Copy).
2. Gerar (seção Geração).
3. `convert` → **`upload`** (R2) → mostrar o **LINK público** + legenda curta. **Parar.**
4. **O pedido de `"publica"` só sai junto com o link**: a mensagem de aprovação deve SEMPRE conter a URL pública da imagem. A entrega por anexo (`MEDIA:`) pode falhar em silêncio — o link R2 é a via confiável de conferência. Sem link entregue ao usuário, não há aprovação possível: não publicar.
5. Sem `"publica"` do usuário → não publica. Aborto → deletar o objeto do R2 e remover o slug.
6. Com `"publica"`: gravar `copy.json` `{formato, caption, alt_texts, source?}` (hashtags já na caption) → `package` → `upload` → `publish`.

## Cron

Job `iris-infografico-diario` (`<JOB_INFOGRAFICO_ID>`). Não carrega esta skill. O job é a autorização: depois dos gates, publica. Não espera `"publica"`.

1. **Assunto** — 1 candidato dos últimos 1–2 dias, fonte primária, sacada, não rumor. `web_search`; se falhar, `curl` HN e changelogs oficiais. Falhou → `pulei: <motivo>` e pare.
2. **Dedup** — slug kebab 2–4 palavras + YYYYMMDD (dir existe → acrescente `-HHMM`). Tema cujo slug já existe em `~/.hermes/ig/` → não repetir.
3. **TEMA** — primeiro bloco sempre **O que é?** (seção Copy).
4. **Gerar** — seção Geração. PNG fora de 0.78–0.82 → não `convert`. Relatório: `pulei: proporção <LxA> (ratio X), não é 4:5`.
5. **Gate visual** — 1 `vision_analyze`: texto PT-BR legível; começa do zero; sem corte; sem coluna vazia nas laterais; sem neon/escuro. Ruim → 1 regen (mesmo prompt). Ainda ruim → `pulei: <motivo visual>`.
6. **copy.json** — gravar antes do passo 7:
   `{formato, caption, alt_texts, blocos:[{titulo, corpo}], source:{url, date}}`
   `blocos` = o `<TEMA>` que foi pro Gemini. Hashtags já na caption.
7. **Gate factual** — `curl` da `source.url`. Confronta caption + `blocos`.
   Ingestão: extrair texto legível (HTML em texto; PDF via pdftotext ou equivalente)
   e o trecho pertinente ao assunto. Sem texto útil, ou fonte grande demais
   para localizar as afirmações → REPROVA: fonte não verificável.
   Não confrontar contra bytes crus. Sem evidência de conferência → reprova
   (não aprova por omissão).
   - datas: existem na fonte e batem
   - absolutos (garantido/sempre/nunca/infalível/100%/totalmente): a fonte
     sustenta sem ressalva
   - números batem
   - todo nome de modelo/produto/empresa/pessoa no slide e na caption
     aparece LITERALMENTE na fonte. Não aparece → reprova
   - encadeamento: se o post diz que A causou/motivou B, a fonte precisa
     sustentar essa ligação explicitamente. Inferiu → reprova
   - ressalva central omitida ou invertida → reprova
   Não julga tom, gancho, voz, hashtags, `— Í.`. Não reescreve sozinho.
   Reprovou: caption se o erro é na legenda; 1 regen da imagem se o erro é no slide.
   Ainda ruim ou fonte não verificável → `pulei: fato não confere — <o quê>`. Não publica.
8. **Publicar** — `convert` → `package` → `upload` → `publish`. Erro de API → erro exato e pare.
9. **Relatório** — assunto + permalink, ou `pulei: <motivo>`. Sem log, sem token.
