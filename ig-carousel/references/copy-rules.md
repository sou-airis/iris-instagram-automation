# Regras de copy — ig-carousel

Leia e siga em TODA execução. Quando o usuário calibrar visual/copy, atualize ESTE arquivo (não improvise).

## Estrutura dos slides

- Piso 6 slides; sobe até 8–10 só com insight real. Máximo 20 palavras por slide (título + corpo).
- Slide 1: gap de insider. Fórmula: `[fato confirmado]. [o que a doc/o marketing não diz].` Sem clickbait, sem mistério.
- Slides 2..N-1: 1 ideia por slide. Ordem: o que é → por que importa → o que muda na prática. Última linha = implicação (micro-hook), nunca pergunta.
- Todo carrossel leva um selo: **Substância · Hype · Depende** (um só, em copy).
- Quando existir número oficial: linha de custo / como acessa.
- Último slide: recap salvável (~3 linhas) + **um** CTA. Padrão = salvar. Send só se for moeda social. Seguir só em capa de série. Comentar nunca no slide.

## Legenda (registro solto)

- Até 2200 caracteres. Primeira linha = resumo (é o que o feed corta).
- 5-8 hashtags (nicho + gerais). Sem repetir a keyword em excesso.
- Fecho fixo: `Fonte no último slide. — Í.`
- Pode divagar, comentar o processo, opinar fora do lançamento, fazer pergunta real.
- Kit de aresta cabe aqui (1–2): malícia, frustração, metáfora, um trocadilho, piada no próprio ofício. Graça não substitui fato.
- Ainda colega — não diário íntimo. Sem rotina doméstica, corpo, romance, sofrimento.
- Emoji: no máximo um, se ajudar a escanear ou fechar o tom.
- Régua de evidência igual à do slide. Soltar o tom ≠ soltar o fato.

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
- Sem pergunta, sem `!`, sem emoji no slide. Sem "você não vai acreditar".
- Público: quem já trabalha com IA. Não explicar o óbvio.
- Anti-drift: óbvio → corta; só changelog → falta julgamento; ataca pessoa → reescreve a claim; fabrica biografia humana → corta; sem sacada → insossa; graça no lugar do fato → palhaça.

## Identidade visual — direção A, Redação (2026-08-13)

- Paleta: fundo `#0A0A0A`, tinta `#F2EDE4`, destaque único `#E23D28` (filete 4px, nada mais).
- Tipografia: hook em Darker Grotesque ExtraBold; corpo em Newsreader. Sem Inter/Roboto/Noto no slide.
- Composição: texto ancorado no terço central-inferior (cresce para cima). Hook precisa caber no crop 1:1 do feed (faixa y 135–1215). Flush left, respiro à direita. Numeração discreta no canto inferior direito. Sem ícone, sem emoji, sem gradiente.
- Fundo: textura fixa `assets/bg.jpg` (grão fotográfico), opacidade 0.6 sobre `#0A0A0A`.
- Palavras proibidas no slide: revolucionário, game-changer, incrível, mágico, "IA vai mudar tudo", emoji, robô.
- `image_generate` liberado (2026-08-14). No **carrossel**, se usado, manter o visual Redação e conferir o texto antes de publicar. No **infográfico**, o visual é outro: `references/infografico-visual.md` (papel quente + ouro + cartoon 2.5D). Não misturar as duas identidades na mesma peça.

## Identidade visual — infográfico

Não é Redação. Detalhe em `references/infografico-visual.md`.

- `image_generate` com `aspect_ratio=4:5` (nativo). Se a tool forçar `portrait`, fallback chat/completions 4:5. `convert` = resize exato 1080×1350.
- Prompt FULL-BLEED + copy começando do zero. Sem crop, sem pad, sem HTML, sem clonar rodapé/mascote da referência.
- Chat: 1 generate → mostrar. Cron: 1 vision; ruim → pule.
