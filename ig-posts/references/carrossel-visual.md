# Carrossel Instagram (Gemini)

Peça âncora: arco Fura a Bolha (metáfora na capa, claro/escuro,
destaque no título e no negrito). Motor: Gemini. Paleta = Redação
(creme / preto / vermelho). Sem filete. Sem foto de pessoa.

Chat lê e executa a seção **Chat**. Sem cron nesta ficha.
Pipeline: `<venv-do-pipeline>/bin/python <caminho-da-skill>/scripts/pipeline.py`

Copy/voz: `references/persona-iris.md` + `references/copy-rules.md`.
Esta ficha não reescreve selo nem fecho da persona. Arco, CTA e
gancho: `copy-rules.md`.

## Prompt

Bloco de estilo — igual em TODOS os slides da série (capa troca
só o parágrafo da metáfora):

```
Slide de carrossel editorial.
Papel claro #F2EDE4 ou papel escuro #0A0A0A, intercalados
(par = escuro, ímpar depois da capa = claro). Capa = metáfora
fotográfica + texto no terço de baixo.
Tinta: creme no slide escuro, preto no slide claro.
Destaque único #E23D28 no título e em até 5 palavras do corpo
(negrito colorido). Sem filete, sem ícone, sem emoji, sem
gradiente, sem foto de pessoa, sem mascote recorrente, sem
@handle, sem CTA visual, sem rodapé.
Wordmark "íris" no topo, pequeno, tracking aberto.
Numeração grande #E23D28 só no canto superior esquerdo.
Sem pílula 2/12.
SAFE ZONE: texto, wordmark e elemento crítico a ≥34px de todas
as bordas (safe 3:4 centrada no 4:5 1080×1350). Fundo (cor/imagem)
pode sangrar até a borda. Texto nunca sangra. Sem coluna vazia.
Texto sempre limpo, PT-BR, exatamente as palavras listadas.
A ilustração NÃO inventa palavra, número, nome nem frase extra.
```

Capa, acrescentar:

```
Imagem: metáfora visual forte, não-literal. As coisas listadas
em capa_literais NÃO são o motivo central. Sem rosto humano.
Seta de swipe só na capa: "deslize →" discreto no canto inferior
direito, dentro da safe zone, #E23D28, corpo pequeno. Nenhum
outro slide leva seta.
```

Slide `prompt_copiavel`, acrescentar:

```
Miolo: retângulo arredondado tipo card. Sem clipe, sem seta de
send, sem chrome de app. Texto do card = TEXTO EXATO, nada mais.
```

Por slide, depois do bloco:

```
TEXTO EXATO no slide, palavra por palavra, nada mais:
Título: <titulo>
Corpo: <corpo>
Destaques em #E23D28: <lista>
Número: <NN>
Wordmark: íris
```

Proporção vai no campo da API, nunca neste texto.
O bloco é texto. Não é referência de imagem.
Não envie `NN.jpg` de outro slide como `image_url`.

## Geração

1. `POST https://openrouter.ai/api/v1/chat/completions`
   `model=google/gemini-3-pro-image`
   `image_config.aspect_ratio="4:5"`
   só texto (Prompt + TEXTO EXATO do slide).
   Sem `image_url`. Sem `/api/v1/images`. Sem seedream.
2. Aceito: PNG ~928×1152 (ratio 0,78–0,82). Fora disso: não rode convert.
3. 1 chamada = 1 slide.
4. Teto: 1 geração + até 2 regens **por slide**.
   Regen só do slide reprovado no gate visual / gate de imagem.
5. Trava de custo: chamadas × US$ 0,136.
   Próxima chamada > US$ 2,00 → abortar (Abortos).
6. `convert <slug> --src <png> --slide N` → só `NN.jpg` 1080×1350.
   Sem crop, sem pad.
   (Fase 2: hoje o convert só grava `01.jpg`.)

## Checkpoint (arquivo, não sessão)

"Aprovado" trava o **arquivo** `NN.jpg`, não a sessão.

- Slide passa no gate visual (e, na capa, no gate de imagem) →
  gravar `NN.jpg` e listar N em `state.json`
  (`slides_locked: […}`, `stage` inalterado).
- Arquivo travado: ninguém sobrescreve, apaga, recorta, re-converte
  nem reabre como referência visual.
- Regenerar o slide 1 depois do 3 aprovado: só gera/grava `01.jpg`.
  `03.jpg` não é lido, não vai no payload, não é invalidado.
- O bloco de estilo em texto **não** substitui esta trava.
- Pode haver mais chamadas de API depois que um slide travou.

## Ata do gate factual

Toda execução do gate (e toda falha de ingestão **antes** da copy)
produz uma ata visível no chat, com:

- `veredito`: APROVADO | REPROVADO_FATO | REPROVADO_INGESTAO
- `detalhe`: uma linha
- `fonte`: URL + data

Códigos:

- `REPROVADO_FATO` — afirmação não sustentada pela fonte
  (nome não literal, número, data, absoluto, encadeamento A→B,
  ressalva invertida/omitida, fonte não cobre a afirmação).
- `REPROVADO_INGESTAO` — não houve texto extraído para comparar
  (PDF sem pdftotext, HTML vazio, curl falhou, paywall,
  fonte grande demais para localizar o trecho).
- `APROVADO` — conferência feita, evidência registrada.

A ata **sempre** é mostrada. Copy só se apresenta como pronta
se o veredito for `APROVADO`.

## Tipo por slide

`copy.json` → cada item de `slides[]` leva:

`tipo`: `afirmacao` | `prompt_copiavel`

- Sem `tipo` → trata como `afirmacao` (fail-closed).
- `afirmacao` — entra no gate factual.
- `prompt_copiavel` — **fora** do gate factual por padrão.
  Ainda passa no gate visual (texto da imagem = copy.json).
- `caption` — sempre `afirmacao` inteira.
- `prompt_copiavel` só existe depois desta regra estar **no disco**.
  Até lá, esse tipo é recusado.

**Retag (obrigatório):** se um slide `prompt_copiavel` contiver
nome próprio, número, data ou encadeamento A→B, o agente
**retagueia para `afirmacao`**, **roda o gate factual nesse slide**
e **só segue se passar**. Não é retag-e-ignorar. Reprovou →
ata `REPROVADO_FATO`, parar e mostrar o motivo — o mesmo
caminho de qualquer outra afirmação.

## CAPA_NOVA_7D — mecanismo (texto, não reopen de imagem)

Campo obrigatório no `copy.json` (capa), gravado **antes** de
gerar qualquer imagem:

`capa_metafora`: `"motivo | enquadramento"`
(ex.: `abelha | close frontal`). 3–8 palavras. Sem isso →
não gera a capa.

Também copiar `capa_metafora` para `state.json` quando o slug
for publicado (para a varredura não depender de achar copy).

**Quando roda:** depois da copy aprovada, **antes** da 1ª
chamada de imagem do slide 01.

**Como:**
1. Listar `~/.hermes/ig/*/state.json` com `stage=publicado`
   e `published_at` nos últimos 7 dias.
2. De cada um, ler `capa_metafora` (state ou copy.json irmão).
   Slug sem o campo (carrossel HTML antigo) → **ignorar**.
3. Normalizar os dois lados: minúsculas, sem acento, espaços
   colapsados.
4. Igual a qualquer uma da janela → reprova. Não gera a capa.
   Ata do gate de imagem: `CAPA_NOVA_7D — metáfora igual a <slug>`.

Limite conhecido: paráfrase (“abelha de óculos” vs “close de
abelha com óculos”) escapa. Aceito: o critério é determinístico,
não semântico.

## METAFORA_CAPA — mecanismo

Campo obrigatório no `copy.json` (capa), gravado **antes** de
gerar:

`capa_literais`: lista de **exatamente 3** substantivos/objetos
mais literais do tema (ex.: `["janela de chat", "teclado", "logo de modelo"]`).
Sem a lista, ou com ≠ 3 itens → não gera a capa.

Checagem em dois tempos:
1. **Antes de gerar (texto):** o `motivo` de `capa_metafora`
   (lado esquerdo do `|`) não pode ser igual a nenhum item de
   `capa_literais` (mesma normalização). Igual → reprova, não gera.
2. **Depois de gerar (visão):** o motivo central da imagem não
   é nenhum dos 3. É → reprova, regen só da capa.

## Chat

1. Fonte primária. Ingestão local (`curl`; HTML→texto; PDF→pdftotext).
   Sem texto útil → ata `REPROVADO_INGESTAO` e não escreve.
   `web_search`/`web_extract` quebrados nesta instalação.
   `r.jina.ai` não é evidência do gate.
2. Copy → `copy.json`
   `{formato: carrossel,
    capa_metafora, capa_literais,
    slides:[{titulo,corpo,tipo,destaques?}],
    caption, alt_texts, source:{url,date}}`.
   Piso 6, teto 10. Sem ideia nova, para. Título ≤6, corpo ≤12,
   total ≤18 palavras/slide, exceto `prompt_copiavel`.
   Capa = gap **ou** promessa/hipérbole. Analogia só depois do factual.
   Jargão não aparece cru.
   **Slide 2:** o feed pode começar nele. Entrega valor sozinho,
   microgancho próprio (não é continuação), passa SLIDE_AUTOSSUFICIENTE.
   `copy.json` declara `arco` (noticia|metodo) e `gancho_tipo` (G1–G6).
   `prompt_copiavel` só se a fonte for um método colável
   (e só com a seção Tipo no disco).
3. **Gate factual** (antes de apresentar a copy; antes de qualquer imagem).
   Confrontar **por slide** `tipo=afirmacao` + a `caption`
   contra o texto extraído. Não confrontar bytes crus.
   Não confrontar slide `prompt_copiavel` **salvo retag** (seção Tipo).
   Ingestão OK e afirmação ausente no texto → `REPROVADO_FATO`
   (`fonte não cobre a afirmação: <trecho>`).
   `REPROVADO_INGESTAO` só sem texto extraído.
   - datas batem
   - absolutos sustentados sem ressalva
   - números batem
   - nomes LITERAIS na fonte (sem apelido)
   - A→B explícito na fonte
   - ressalva central omitida/invertida → `REPROVADO_FATO`
   Não julga tom, gancho, voz, hashtags, `Fonte no último slide. — Í.`
   1 correção + re-gate; ainda ruim → parar com a ata.
4. `APROVADO`: **autoteste de leigo** (`copy-rules.md`). Falhou → reescreve; ainda falha → parar e dizer o critério. Passou: mostrar slides + legenda + ata. **Parar.**
   Sem ok na copy → não gera imagem.
5. Com ok: **CAPA_NOVA_7D + METAFORA_CAPA (passo texto)**;
   se passou, gerar cada slide (Geração + Checkpoint).
6. Gate visual, por slide: PT-BR legível; texto = copy.json
   (título, corpo, número, wordmark íris, destaques na cor certa);
   nenhuma palavra/número/nome extra; família = paleta A +
   alternância planejada (não “todo slide igual”); sem faixa lateral.
   Capa: também o **gate de imagem** (visão).
   Passou → travar `NN.jpg`. Falhou → regen só desse slide.
7. Gate de imagem (só capa) — binário:
   - METAFORA_CAPA: ver seção do mecanismo.
   - SEM_PESSOA: nenhum rosto/corpo fotorealista na imagem. Há → reprova.
   - CAPA_NOVA_7D: ver seção do mecanismo (roda **antes** de gerar).
8. Todos travados: convert → package → upload → links R2 +
   legenda. **Parar.** `"publica"` só com os links.
9. Abortos — seção abaixo.
10. `"publica"` → publish. Erro de API → erro exato e parar.
    Ao publicar: gravar `capa_metafora` no `state.json`.

## Abortos

**A — Custo (próxima chamada > US$ 2,00)**
Trabalho pago não se descarta. `NN.jpg` travados ficam.
`stage=incompleto` + motivo teto_custo + chamadas + US$ +
slides_locked + o que falta. Sem R2. Sem apagar slug.
Relatório no chat. Completar = ok novo + estimativa
(`N × 0,136`). Descartar = ok explícito.

**B — Sem `"publica"` (peça pronta, recusou)**
Apagar objetos R2 desta peça + remover o slug. Não confundir com A.

## O que este arquivo não cobre

- Voz, selo, fecho, fórmula de hook: persona + copy-rules.
- OCR “é verdade?” no JPEG: factual lê copy.json (só `afirmacao`);
  visual lê a imagem contra o copy.json.
- Story, cron, reply, pack, HTML como caminho padrão.
- Foto da Íris no card (escopo Stories).
- Instalar pdftotext / consertar web_search.
