# GM Hamburgueria — automação de postagem

Publica automaticamente no Facebook e Instagram da GM Hamburgueria, direto de mídia já tratada no Google Drive — usando o mesmo modelo de **cronograma curado com aprovação** do Bernardino: nada é escolhido "às cegas" na hora de postar.

## Fluxo

1. `scripts/generate_week_plan.py` monta o cronograma da semana (1 story/dia + 1 post semanal de sexta, que é OU um reel OU um carrossel — nunca os dois na mesma semana) e salva em `content/week_plans/<segunda-feira>.json` com `status: "pending_approval"`.
2. O cronograma aparece no painel (`painel_publicacoes.html`, aba GM) pra Rob revisar.
3. Depois de aprovado (`scripts/approve_week_plan.py content/week_plans/<data>.json`, ou pelo painel), o `status` vira `"approved"`.
4. Só então o `poller.py` (rodando via GitHub Actions) publica os posts do plano aprovado, nos horários da semana.

## Cronograma

- **Story**: todos os dias, 19h30 — 1 item (foto ou vídeo) de `STORIES/Brenda - Stories`.
- **Post semanal**: sexta-feira, 11h00 — OU um carrossel de 5 fotos (`Imagens tratadas/Ano 2026/*`) OU um reel (`Vídeos Tratados/2026/*`), decidido no momento de gerar o cronograma da semana.

Ajuste dias/horários em `SCHEDULE` no topo de `scripts/poller.py`.

## Pools de conteúdo

- `content/gm_stories_manifest.json` — 92 itens (fotos + vídeos).
- `content/gm_reels_manifest.json` — 25 vídeos, de 4 subpastas mensais (Jan/Mar/Abr/Jul 26).
- `content/gm_feed_manifest.json` — 71 fotos (.HEIC, convertidas pra .jpg antes de postar), de 3 subpastas mensais.

Cada item tem `used`/`used_at` — quando o pool esgota, reseta sozinho e recomeça a rotação.

## Segurança contra post duplicado

Aplicado desde o primeiro commit (aprendido com um incidente real no Bernardino):
- **Concurrency group** serializa execuções sobrepostas.
- **Trava de segurança**: se uma execução falhar parcialmente no meio de uma publicação, o slot é marcado como publicado mesmo assim (evita re-tentativa automática que duplicaria o que já saiu) e abre uma Issue urgente pedindo conferência manual. Nenhuma nova execução roda enquanto essa Issue estiver aberta.

## Configuração necessária

No GitHub (`Settings > Secrets and variables > Actions` deste repositório), adicionar:
- `RCLONE_CONFIG` — mesmo formato usado no Bernardino/TopTop (acesso ao Google Drive).
- `FB_PAGE_ACCESS_TOKEN`
- `FB_PAGE_ID`
- `IG_BUSINESS_ID`

Nunca cole esses valores em uma conversa de chat — configure direto pelo GitHub (`gh secret set NOME --repo virandopaulista-droid/gm-hamburgueria-automacao`, digitado no seu terminal).

## Testar

Gerar um cronograma de teste e aprovar:

```
py -3 scripts/generate_week_plan.py
py -3 scripts/approve_week_plan.py content/week_plans/<data-da-segunda>.json
```

Rodar o poller em modo simulação (não publica de verdade, só valida o mount do Drive e a leitura do plano aprovado):

```
gh workflow run poller.yml --repo virandopaulista-droid/gm-hamburgueria-automacao -f live=false
```
