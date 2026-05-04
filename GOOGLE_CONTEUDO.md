# Conteudo via Google

O site ja esta preparado para carregar publicacoes de uma planilha Google ou de um endpoint JSON do Apps Script.

## Colunas sugeridas na planilha

Use uma aba com a primeira linha assim:

```csv
tipo,titulo,resumo,data,tag,local,imagem,link,status
```

Valores aceitos:

- `tipo`: `obra` ou `informativo`
- `titulo`: titulo do card
- `resumo`: texto curto do card
- `data`: formato `2026-04-29`
- `tag`: assunto, por exemplo `Residencial`, `Comercial`, `Aviso`
- `local`: cidade ou regiao, usado principalmente em obras
- `imagem`: URL publica da imagem, opcional
- `link`: URL de destino, opcional
- `status`: use `publicado`; use `rascunho` para esconder do site

## Como ligar no site

1. No Google Sheets, publique a aba como CSV: `Arquivo > Compartilhar > Publicar na Web`.
2. Copie a URL CSV publicada.
3. Cole essa URL em `dataUrl` dentro de `index.html` e `blog.html`:

```html
<script>
  window.CONNECT_CONTENT_CONFIG = {
    dataUrl: "COLE_A_URL_CSV_AQUI",
    sheetUrl: "COLE_A_URL_DA_PLANILHA_AQUI"
  };
</script>
```

Enquanto `dataUrl` estiver vazio, o site mostra publicacoes de exemplo para manter o layout preenchido.

## JSON por Apps Script

Se preferir Apps Script, retorne um JSON neste formato:

```json
{
  "items": [
    {
      "type": "obra",
      "title": "Sistema residencial em Curitiba",
      "summary": "Projeto em fase de instalacao.",
      "date": "2026-04-29",
      "tag": "Residencial",
      "location": "Curitiba/PR",
      "image": "https://...",
      "link": "https://...",
      "status": "publicado"
    }
  ]
}
```
