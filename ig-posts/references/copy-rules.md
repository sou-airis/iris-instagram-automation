# Regras de copy — ig-posts

**Precedência (conteúdo de carrossel).** Em conflito: `copy-rules.md` + `carrossel-visual.md` (vigente) vencem restatement em `persona-iris.md`; os três vencem `SKILL.md`; `SKILL.md` vence `DECISIONS.md` (histórico). `AGENTS.md` só aponta — não duplica teto/hook/CTA. `docs/ig-posts/` não é fonte.

Leia e siga em TODA execução. Quando o usuário calibrar visual/copy, atualize ESTE arquivo (não improvise).

## Ordem de escrita (não inverter)

1. Fonte primária ingerida. Sem texto útil → não escreve.
2. `fato_ouro` — o fato aprovado que **não** está no título do comunicado e que justifica o post existir. Sem esse campo, não escreve slide.
3. `gancho_tipo` + `arco` (paleta, não formulário) + `cta_gatilho`.
4. 3 versões de capa e 3 de fecho (`capa_versoes`, `fecho_versoes`). Escolhe uma de cada e justifica contra as duas descartadas (`capa_escolha_porque`, `fecho_escolha_porque`). Sem as 3+justificativa → não passa.
5. Só então os slides do meio. `fato_ouro` tem que aparecer **até o slide 3**.
6. `retorica`: lista `{figura, fato_ancora}`. Toda figura aponta a um fato já aprovado. Sem âncora → a figura cai. Sem cota de quantidade.
7. `selo` + `selo_porque` (uma linha). Sem o porque → selo é decoração, reprova.
8. **TODO slide passa no CONTEXTO e no TESTE_DO_ESTRANHO — não só a capa.** Número sem contexto no miolo = falha (ex.: “19 e 23 minutos” sem dizer do quê).

## Estrutura dos slides

- Piso 5; teto 10. Sem ideia nova, para — não preenche pra bater número.
- Cada slide carrega uma ideia que os outros não carregam. Ideia pode ser **juízo**, não só fato do press.
- **Densidade variável (obrigatória):** pelo menos 1 slide curto (≤6 palavras no corpo) e os outros não podem ter todos o mesmo comprimento (±2 palavras). Sete slides de 11 palavras = falha de ritmo.
- **Teto flexível:** capa (título+corpo) ≤14 palavras. Miolo: 4–28. Sem teto rígido de 18 no total. `prompt_copiavel` continua exceção. **Fecho/CTA:** o teto cede se for preciso completar a fórmula do `cta_gatilho`.
- Slide 1: gap **ou** promessa/hipérbole. O *quê* (substantivo do feito) mora na capa. Número **pode** ir na mesma frase. Capa que só informa “a empresa fez X” (sujeito institucional + verbo de assessoria + objeto) = **CAPA_NAO_E_COMUNICADO** falhou.
- Anti-exemplo de capa (não repetir a estrutura): “A Anthropic pediu ao Claude pra desenhar a molécula de um remédio.” / “O Instagram mostra o teste primeiro pra quem não te segue.”
- Slide 2: entendível sozinho (o feed pode começar nele) **e** pode deixar ponta aberta. Entendível ≠ resolvido.
- Analogia **depois** do factual. Inferência nova → volta ao gate.
- Jargão não aparece cru.
- `gancho_tipo` muda a **forma** do post, não só a frase do 01 (ver catálogo).
- `prompt_copiavel`: só fonte-método + `tipo` (ver ficha). Fora do factual salvo retag.
- Selo: **Substância · Hype · Depende** + `selo_porque`.

### Arco é paleta, não formulário

`arco` declara a família. **Não** obriga 7 posições iguais.

**ARCO_NOTICIA** — lançamento/atualidade. Peças disponíveis (montar as que o `fato_ouro` e o `gancho_tipo` pedirem): capa de tensão · o que é · por que agora · a prova · a virada · o cuidado · fecho. Pode ter 5 slides. O ouro não pode ser o slide 5 de um 7.

**ARCO_METODO** — fonte = tutorial/guia. Peças: promessa · erro comum · quem mediu · tese/passos · cuidado · fecho save.

Mapeamento mínimo `gancho_tipo` → forma:
- G1 — número âncora na capa ou no 02, nunca escondido no 05.
- G2 — a peça escondida é o `fato_ouro`; a capa revela 80%.
- G3 — a crença errada vai na capa; o fato que a derruba até o 03.
- G4 — a consequência na capa; o mecanismo depois.
- G5 — feito + escala na capa (número na mesma frase se o *quê* estiver lá).
- G6 — a ressalva que o anúncio escondeu até o slide 3.

### CTA (um só, no último slide)

- Notícia/lançamento: **send**. Método/cheatsheet: **save**.
- Nunca empilhar save+send+follow no mesmo slide.
- Follow só na **legenda**, só se prometer valor recorrente do feed — nunca a pessoa.
- Send não é frase genérica. Antes do último slide, `copy.json` declara `cta_gatilho`:

  - **MOEDA_SOCIAL** — o leitor parece antenado ao enviar.
    Fórmula: “Envia pra quem ainda acha que [crença errada].”
  - **ESPANTO_COMPARTILHADO** — quer que alguém veja junto.
    Fórmula: “Envia pra quem não acredita que isso já existe.”
  - **UTILIDADE_PRATICA** — resolve problema de alguém específico.
    Fórmula: “Envia pra quem usa [ferramenta/contexto] no trabalho.”

- Escolha: ler `arco` + `gancho_tipo` e declarar `cta_gatilho` **antes** de escrever o último slide. Notícia/G5 → MOEDA_SOCIAL ou ESPANTO. ARCO_METODO → UTILIDADE_PRATICA.
- Nunca “precisa saber disso” sem dizer quem e por quê.

## Legenda (registro solto)

- Primeiras ≤125 caracteres: a linha mais afiada, com a keyword do tema. Não copiar o slide 1.
- Corpo: complementa. Fonte primária citada + um ponto que não coube.
- 3–5 hashtags nichadas no fim. Nunca genérica sozinha (`#IA` não conta). Nunca 7+.
- Fecho fixo: `Fonte no último slide. — Í.`
- Kit de aresta cabe (1–2). Graça não substitui fato.
- Emoji: no máximo um.
- **FATOS_NA_LEGENDA:** fatos aprovados que não couberam nos slides vão pra caption. Campo `fatos_legenda`.

## Comentário (registro conversa)

- Curto, sem pedagogia. Malícia e piada autodepreciativa (ofício dela, nunca o leitor).
- Nunca “comente SIM”, nunca aula, nunca vínculo íntimo.

## Alt text

- 1 frase por slide, o que ESTÁ no slide.

## Idioma e tom

- Voz: `persona-iris.md` v1.4 — três registros, aresta §3.7.
- Português (BR), voz ativa, tempo presente.
- **Pergunta de tensão** no slide é permitida (abre loop). **Pergunta de engajamento** (“você já…?”, “comenta se”) é proibida.
- No máximo **um** `!` no carrossel (capa ou CTA). Sem emoji no slide.
- Sem “você não vai acreditar” vazio. Promessa na capa precisa de fato já aprovado.
- Público: leigo inteligente + quem já trabalha com IA. Termo técnico sem tradução = falha.
- Anti-drift: óbvio → corta; só changelog → falta julgamento; ataca pessoa → reescreve; fabrica biografia → corta; sem sacada → insossa; graça no lugar do fato → palhaça; analogia que inventa causa/número → volta ao gate.
- Hipérbole descreve, não afirma. Se a frase pode ser lida como dado (“3× mais rápido”), é claim e vai ao gate. Se é figura (“virou pó o cronograma”), é retórica — desde que `retorica[].fato_ancora` exista.

## Catálogo de ganchos (um por post)

Campo `gancho_tipo`. Não repetir o do último `stage=publicado` (REPERTORIO_VARIADO). Rotacionar ≥4 tipos em 4 posts.

- **G1 NUMERO_ESPECIFICO** — dado real + finitude.
- **G2 CURIOSITY_GAP** — revela quase tudo, esconde o `fato_ouro`.
- **G3 CONTRARIAN** — crença comum na capa; fato até o 03.
- **G4 STAKES_URGENCIA** — consequência na capa.
- **G5 AWE_INCREDULIDADE** — escala na capa, *quê* na mesma frase.
- **G6 CLAREZA_INSIDER** — o que o anúncio não traduz; ressalva cedo.

## Catálogo de pontes

Máx. 1 por slide, no fim. Não em todos. Nunca no último. Variar entre posts.
**Ponte só existe se o slide seguinte entregar o que ela promete.** Se não entregar, corta a ponte — loop aberto que troca o assunto é falha.
**Ponte ideal é específica do post** — anuncia a *próxima peça* (“Aí veio o exame.”, “E o grid?”, “E quem não tem conta?”). Ponte de catálogo é fallback quando a peça não tem nome curto.

Lista: “Só que tem um porém →” · “Agora repara:” · “E o dado que ninguém citou:” · “Mas espera.” · “Traduzindo:” · “Na prática, isso significa:” · “E a parte que assusta?” · “Ainda não é o mais importante.” · “O detalhe que muda tudo:” · “Continua →”

`?` de tensão nas pontes é permitida. `?` de quiz, não.

## Autoteste de leigo (depois do factual, antes de mostrar)

Reprovou → reescreve. Sem entregar copy que já sabe que falha.

- **CONTEXTO_ANTES_DO_NUMERO** — vale para **todo slide**, não só o 01: todo número tem o *quê* na mesma frase ou no slide. Número órfão (“19 e 23 minutos” sem dizer do quê) → falhou.
- **ANALOGIA_EXPLICA** — analogia lida sozinha faz sentido.
- **SLIDE_AUTOSSUFICIENTE** — entendível sem os outros. Pode sobrar ponta (fato do post, não clickbait).
- **TESTE_DO_ESTRANHO** — quem nunca ouviu o assunto entende o que o post *está dizendo*.
- **SEM_JARGAO_CRU** — termo técnico sem tradução de uma linha → falhou.
- **REPERTORIO_VARIADO** — `gancho_tipo` ≠ último publicado.
- **CONTEXTO_IMPLICITO** — “bloqueado/restrito/preview” sem o porquê literal da fonte → traduz ou usa a frase fallback, sem inventar causa.
- **FATO_OURO_CEDO** — `fato_ouro` preenchido antes dos slides e visível até o slide 3.

## Autoteste de impacto (referente externo — não é opinião solta)

Roda depois do leigo. Sem isto, o post é comunicado diagramado.
Referente de nível e anti-exemplo: `references/banco-referencia.md`.

- **CAPA_3_VERSOES** — `capa_versoes` tem 3 itens; `capa_escolha_porque` diz o que as 2 descartadas falhavam. Idem `fecho_versoes` / `fecho_escolha_porque`. Sem isso → falhou.
- **CAPA_NAO_E_COMUNICADO** — a capa escolhida **não** é sujeito institucional + verbo de assessoria (“pediu”, “lançou”, “anunciou”, “mostra”) + objeto do feito, sem tensão. Anti-exemplos oficiais: as duas capas publicadas em `claude-proteina-20260818` e `instagram-trial-reels-20241210`.
- **SACADA** — existe uma implicação que o título do comunicado não fez. Se o post só resume o paper, falhou. (Referente: o título da fonte vs. o `fato_ouro`.)
- **SELO_FALADO** — `selo_porque` existe e ecoa num slide ou na capa.
- **RITMO_VARIA** — há um slide curto (≤6) e os comprimentos não são todos iguais.
- **RETORICA_ANCORADA** — cada item de `retorica` nomeia `fato_ancora` que o gate viu. Sem âncora → corta a figura, não o post inteiro.
- **CTA_COMPLETO** — o fecho executa a fórmula do `cta_gatilho` declarado, não só o verbo “Envia”. MOEDA_SOCIAL precisa do “pra quem ainda acha que [crença]”. UTILIDADE precisa do “pra quem usa [ferramenta] no trabalho”. Se não couber no teto, **o teto cede** — o CTA é o slide que converte. Falhou → reescreve.
- **MINIATURA_LEGIVEL** — reduzir cada slide a ~160px de largura (tamanho de feed) e conferir que o texto ainda se lê como *texto*, não como borrão. Slide ilegível em miniatura → reprova. (Referente: thumbnail real do feed, não a imagem em tela cheia.)
- **LOOP_NA_CAPA** — a capa abre uma tensão que o slide 2 começa a responder (pergunta de tensão, promessa, contrarian, gap). Capa que só informa o fato → reprova. Referente: pergunta “por que eu deslizaria para o 02?”.
- **RELEITURA** — depois de ler o carrossel inteiro, a capa ganha sentido novo (a peça escondida recontextualiza o gancho). Se a capa lida de novo significa a mesma coisa de antes → não é carrossel, é folheto. Referente: `fato_ouro` vs. primeira leitura da capa.
- **PONTE_ENTREGA** — toda ponte anuncia a peça do próximo slide, e o próximo slide entrega exatamente ela. Ponte que promete uma coisa e entrega outra → reprova.

**Parada:** se depois de reescrever ainda não passa, para e diz **qual** critério e por quê. Não entrega.

## Identidade visual — carrossel (paleta A)

Receita: `references/carrossel-visual.md`. Não reembutir.

- Paleta A: claro `#F2EDE4`, escuro `#0A0A0A`, destaque `#E23D28`. Sem filete.
- Wordmark `íris`. Sem `@sou.airis` no card.
- Capa = metáfora. Miolo = o **mesmo mundo** (objeto/luz), não papel chapado vazio. Sem foto de pessoa. Sem chrome de app. Sem ícone. Sem `image_url` entre slides.
- Textura/grain/luz da metáfora podem. Degradê de startup, não.
- Palavras proibidas no slide: revolucionário, game-changer, incrível, mágico, "IA vai mudar tudo".
- Infográfico é outro visual.

## Identidade visual — infográfico

Não é este arquivo. `references/infografico-visual.md`.
