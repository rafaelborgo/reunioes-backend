# Backend do Assistente de Reuniões

Este é o backend para o aplicativo Assistente de Reuniões, que utiliza a API Whisper da OpenAI para transcrição de áudio e geração de insights.

## Funcionalidades

- Transcrição de áudio usando a API Whisper da OpenAI
- Marcação temporal por minuto na transcrição
- Análise da transcrição para gerar insights usando GPT-4
- Exportação de relatórios com os dados organizados

## Requisitos

- Python 3.8+
- OpenAI API Key
- Dependências listadas em requirements.txt

## Configuração

1. Extraia os arquivos deste ZIP em uma pasta de sua preferência

2. Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:
```
OPENAI_API_KEY=sua_chave_api_aqui
PORT=5000
```

3. Instale as dependências:
```
pip install -r requirements.txt
```

## Execução Local

```
python main.py
```

O servidor estará disponível em `http://localhost:5000`

## Deploy no Render

1. Crie uma conta no [Render](https://render.com/) (gratuito)
2. No dashboard, clique em "New" e selecione "Web Service"
3. Escolha "Deploy from existing code" ou "Upload files"
4. Configure o serviço:
   - Nome: reunioes-backend (ou outro de sua preferência)
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn main:app`
5. Em "Advanced" > "Environment Variables", adicione:
   - `OPENAI_API_KEY`: Sua chave da API OpenAI
6. Clique em "Create Web Service"

O deploy levará alguns minutos. Após concluído, você terá um URL permanente para seu backend.

## Endpoints

- `GET /`: Página inicial
- `POST /api/transcribe`: Transcreve um arquivo de áudio usando Whisper
- `POST /api/analyze`: Analisa uma transcrição e gera insights

## Integração com o Frontend

Após o deploy, atualize o frontend para apontar para o novo backend:

1. No arquivo `App.tsx` do frontend, atualize as URLs de fetch:
```javascript
const transcriptionResponse = await fetch('https://seu-backend-no-render.onrender.com/api/transcribe', {
  // ...
});

const insightsResponse = await fetch('https://seu-backend-no-render.onrender.com/api/analyze', {
  // ...
});
```

2. Faça o build e deploy do frontend atualizado
