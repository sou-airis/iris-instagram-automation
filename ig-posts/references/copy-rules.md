# Regras de copy — ig-posts

Leia e siga em TODA execução. Quando o usuário calibrar visual/copy, atualize ESTE arquivo (não improvise).

## Estrutura dos slides

- Piso 6; teto 10. Cada slide uma ideia que os outros não carregam. Sem ideia nova, para. Título ≤6 palavras, corpo ≤12, total ≤18. Exceto `prompt_copiavel`.
- Slide 1: gap **ou** promessa/hipérbole. Sem claim que o gate não viu. Sem número no 01 se isso quebrar CONTEXTO_ANTES_DO_NUMERO.
- Slide 2: autossuficiente, microgancho próprio (o feed pode começar nele).
- Analogia **depois** do factual. Inferência nova → volta ao gate.
- Jargão não aparece cru.
- `copy.json` declara `arco` (`noticia` | `metodo`) e `gancho_tipo` (G1–G6) **antes** de mostrar a copy.
- `prompt_copiavel`: só fonte-método + `tipo` (ver ficha). Fora do factual salvo retag.
- Selo: **Substância · Hype · Depende** (um só, em copy).
- Número oficial: linha de custo / como acessa, quando existir.

### Arco por tipo

**ARCO_NOTICIA** (padrão — lançamento/atualidade):
01 Capa: fato + gap **ou** promessa/hipérbole
02 O que é (leigo, autossuficiente)
03 Por que importa agora
04 O dado / a prova
05 A virada / o detalhe
06 O cuidado / ressalva central
07 Recap + CTA send

**ARCO_METODO** (fonte = tutorial/framework/guia):
01 Capa: promessa do resultado
02 O erro comum (autossuficiente)
03 Quem mediu / credibilidade
04 Framework / tese
05–N Passos (`prompt_copiavel` se couber)
N−1 O cuidado
N Recap + CTA save

### CTA (um só, no último slide)

- Notícia/lançamento: **send**. Método/cheatsheet: **save**.
- Nunca empilhar save+send+follow no mesmo slide.
- Follow só na **legenda**, só se prometer valor recorrente do feed — nunca a pessoa.
- Send não é frase genérica. Antes do último slide, `copy.json` declara `cta_gatilho`:

  - **MOEDA_SOCIAL** — o leitor parece antenado ao enviar.
    Fórmula: “Envia pra quem ainda acha que [crença errada].”
    Quando: avanço surpreendente, dado contra o senso comum, feito que parece ficção.
  - **ESPANTO_COMPARTILHADO** — quer que alguém veja junto.
    Fórmula: “Envia pra quem não acredita que isso já existe.”
    Quando: demonstração visual, resultado absurdo, marco verificável.
  - **UTILIDADE_PRATICA** — resolve problema de alguém específico.
    Fórmula: “Envia pra quem usa [ferramenta/contexto] no trabalho.”
    Quando: tutorial, guia, framework aplicável hoje.

- Escolha: ler `arco` + `gancho_tipo` e declarar `cta_gatilho` **antes** de escrever o último slide. Notícia/G5 → MOEDA_SOCIAL ou ESPANTO. ARCO_METODO → UTILIDADE_PRATICA.
- Nunca “precisa saber disso” sem dizer quem e por quê. Se não completa a frase → é MOEDA_SOCIAL, não UTILIDADE.

## Legenda (registro solto)

- Primeiras ≤125 caracteres: a linha mais afiada, com a keyword do tema (nome do modelo/ferramenta/empresa). Não “que post incrível”. Não copiar o slide 1.
- Corpo: complementa os slides. Fonte primária citada + um ponto que não coube no card.
- Segue o `arco`: notícia → contexto extra; método → resumo dos passos.
- 3–5 hashtags nichadas no fim. Nunca genérica sozinha (`#IA` não conta). Nunca 7+.
- Fecho fixo: `Fonte no último slide. — Í.`
- Kit de aresta cabe (1–2). Graça não substitui fato. Sem diário íntimo.
- Emoji: no máximo um. Régua de evidência igual à do slide.
- **FATOS_NA_LEGENDA:** fatos aprovados no gate que não couberam nos slides (limite de palavras) **não se descartam**. Vão obrigatoriamente pra legenda, em linguagem leiga. `copy.json` lista `fatos_legenda: [...]` e cada item tem que aparecer na caption **antes** de mostrar a copy.

## Comentário (registro conversa)

- Curto, sem pedagogia. Responde como colega.
- Malícia e piada autodepreciativa (ofício dela, nunca o leitor) cabem.
- Emoji se um humano no mesmo fio usaria. Nunca enfeite.
- Nunca “comente SIM”, nunca aula, nunca vínculo íntimo.

## Alt text

- 1 frase por slide, descrevendo o que ESTÁ no slide (não o que está na legenda).

## Idioma e tom

- Voz: `references/persona-iris.md` v1.4 — um caráter, três registros (§4.1), aresta (§3.7).
- Slide = publicação com sacada. Legenda = respiro com malícia. Comentário = conversa.
- Português (BR), voz ativa, tempo presente.
- Sem pergunta, sem `!`, sem emoji no slide. Sem “você não vai acreditar” vazio. Promessa na capa precisa de fato já aprovado.
- Público: leigo inteligente + quem já trabalha com IA. Termo técnico sem tradução = falha.
- Anti-drift: óbvio → corta; só changelog → falta julgamento; ataca pessoa → reescreve a claim; fabrica biografia humana → corta; sem sacada → insossa; graça no lugar do fato → palhaça; analogia que inventa causa/número → volta ao gate.

## Catálogo de ganchos (um por post)

Campo `gancho_tipo` no `copy.json`. Não repetir o tipo do último post **publicado** em `~/.hermes/ig/` (REPERTORIO_VARIADO). Rotacionar ≥4 tipos em cada ciclo de 4 posts. G5 e G2 pesam mais em notícia.

- **G1 NUMERO_ESPECIFICO** — dado real + finitude. Ex.: “A Anthropic fez 3 mudanças silenciosas no Claude. A segunda muda o workflow.”
- **G2 CURIOSITY_GAP** — revela quase tudo, esconde uma peça. Ex.: “Todo mundo viu o lançamento. Quase ninguém viu o que estava no slide 5.”
- **G3 CONTRARIAN** — contradiz crença comum com fato. Ex.: “O modelo mais barato da OpenAI bateu o mais caro em código.”
- **G4 STAKES_URGENCIA** — consequência real e imediata. Ex.: “Isso torna o jeito atual de RAG obsoleto.”
- **G5 AWE_INCREDULIDADE** — escala absurda ou feito improvável. Ex.: “Uma IA desenhou molécula de remédio. Em laboratório real.” (número fica no slide 4 se o 01 tiver que cumprir CONTEXTO_ANTES_DO_NUMERO.)
- **G6 CLAREZA_INSIDER** — traduz o que o anúncio não traduz. Ex.: “O que o paper do Gemini 3 realmente diz. Sem o hype.”

## Catálogo de pontes (bucket brigades)

Máx. 1 por slide, no **fim**. Não em todos. Usar em 2, 4 e N−2 (nunca no último). Variar — não a mesma em posts seguidos.

Lista: “Só que tem um porém →” · “Agora repara:” · “E o dado que ninguém citou:” · “Mas espera.” · “Traduzindo:” · “Na prática, isso significa:” · “E a parte que assusta?” · “Ainda não é o mais importante.” · “O detalhe que muda tudo:” · “Continua →”

Nota: itens com “?” chocam a regra “sem pergunta no slide”. Preferir as pontes sem interrogação até essa regra reabrir.

## Autoteste de leigo (antes de mostrar a copy)

Roda **depois** do gate factual e **antes** de apresentar a copy ao humano.
É o próprio agente se checando — sem modelo extra, sem gastar o ciclo do humano.
Reprovou → reescreve → repete. Sem entregar copy que o agente já sabe que falha.

Critérios (todos binários):

- **CONTEXTO_ANTES_DO_NUMERO** — o slide 1 diz *o que aconteceu* em linguagem concreta **antes** de qualquer número ou analogia. Se o leitor não sabe o que foi feito, o número não significa nada. Falhou → reescreve.
- **ANALOGIA_EXPLICA** — toda analogia, lida sozinha (sem o termo técnico ao lado), faz sentido pra quem não sabe o termo. Se a analogia também precisa de explicação, não é tradução: é imagem vaga. Falhou → reescreve.
- **SLIDE_AUTOSSUFICIENTE** — cada slide entendível sem ter lido os outros (o feed mostra fora de ordem). Falhou → reescreve.
- **TESTE_DO_ESTRANHO** — reler do começo como quem nunca ouviu o assunto. Se o próprio agente não entenderia o que o post diz, não entrega. Falhou → reescreve.
- **SEM_JARGAO_CRU** — nenhum termo técnico sem tradução ou contexto de uma linha (binder, NMR, LC-MS, hit rate, encaixe de proteína, etc.). Falhou → reescreve.
- **REPERTORIO_VARIADO** — `gancho_tipo` deste post ≠ o do último `stage=publicado` em `~/.hermes/ig/` (quem não tem o campo não conta). Igual → reescreve com outro tipo.
- **CONTEXTO_IMPLICITO** — termos de bolha (“bloqueado”, “restrito”, “indisponível”, “acesso limitado”, “em preview”, “fechado para terceiros”, “não disponível comercialmente” e similares) sem uma linha de *porquê* reprovam.
  Motivo **literal** na fonte → explique em linguagem leiga no slide (≤18 palavras no total).
  Motivo **não** literal → use “essa tarefa não está disponível no modelo mais capaz”, sem inferir causa (bug, política ou plano).
  Nunca deixar o leitor adivinhar.

**Parada:** se depois de reescrever ainda não passa, para e diz ao humano **qual** critério não cumpre e por quê (ex.: a fonte não dá base pra explicar X em linguagem simples). Não entrega copy que falha no autoteste.

## Identidade visual — carrossel (paleta A, 2026-08-19)

Receita executável: `references/carrossel-visual.md`. Não reembutir.

- Paleta A: claro `#F2EDE4`, escuro `#0A0A0A`, destaque único `#E23D28` no título e em até 5 palavras do corpo. Sem filete.
- Wordmark `íris` no topo. Sem `@sou.airis` no card. Sem rodapé novo.
- Numeração grande só no canto superior esquerdo. Fundo claro/escuro intercalado (par = escuro).
- Capa: metáfora visual, não ilustração literal. Sem foto de pessoa.
- Sem ícone, sem emoji, sem gradiente.
- Palavras proibidas no slide: revolucionário, game-changer, incrível, mágico, "IA vai mudar tudo", emoji, robô.
- Infográfico é outro visual: `references/infografico-visual.md`. Não misturar na mesma peça.

## Identidade visual — infográfico

Não é Redação. Detalhe em `references/infografico-visual.md`.

- `image_generate` com `aspect_ratio=4:5` (nativo). Se a tool forçar `portrait`, fallback chat/completions 4:5. `convert` = resize exato 1080×1350.
- Prompt FULL-BLEED + copy começando do zero. Sem crop, sem pad, sem HTML, sem clonar rodapé/mascote da referência.
- Chat: 1 generate → mostrar. Cron: 1 vision; ruim → pule.
