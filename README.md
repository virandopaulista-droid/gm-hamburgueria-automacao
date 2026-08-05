# GM Hamburgueria — automação de postagem

Publica automaticamente no Facebook e Instagram da GM Hamburgueria, direto de mídia já tratada no Google Drive. Sem plano curado (diferente do Bernardino) — escolhe aleatoriamente um item não usado de cada pool, mesmo modelo do TopTop Pizzaria.

## Cronograma

- **Story**: todos os dias, 19h30 — 1 item (foto ou vídeo) de `STORIES/Brenda - Stories`.
- **Feed**: sexta-feira, 11h00 — carrossel de 5 fotos de `Imagens tratadas/Ano 2026/*`.
- **Reel**: segunda-feira, 18h00 — 1 vídeo de `Vídeos Tratados/2026/*`.

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

```
gh workflow run poller.yml --repo virandopaulista-droid/gm-hamburgueria-automacao -f live=false
```

Roda em modo simulação (não publica de verdade) — valida o mount do Drive e a seleção de mídia.
