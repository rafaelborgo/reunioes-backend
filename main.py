import os
import json
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI  # Importar OpenAI
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas as rotas

# Configurar o cliente OpenAI (nova forma para v1.x+)
try:
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )
except Exception as e:
    # Log inicialização falhou (opcional, mas bom para debug)
    print(f"Erro ao inicializar cliente OpenAI: {e}")
    client = None # Garante que o app não quebre se a chave estiver faltando

# Configuração para upload de arquivos
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16MB para upload

@app.route('/')
def index():
    return "API de Transcrição de Áudio para Reuniões (v1.1 - OpenAI Client)"

@app.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    if not client:
         return jsonify({'error': 'Cliente OpenAI não inicializado corretamente. Verifique a chave da API.'}), 500

    if 'audio' not in request.files:
        return jsonify({'error': 'Nenhum arquivo de áudio enviado'}), 400
    
    audio_file = request.files['audio']
    
    if audio_file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400
    
    # Criar arquivo temporário para o áudio
    temp_audio_path = None # Inicializar variável
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
            audio_file.save(temp_audio.name)
            temp_audio_path = temp_audio.name
        
        # Enviar para a API Whisper da OpenAI usando o cliente
        with open(temp_audio_path, "rb") as audio_file_obj:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file_obj,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
        
        # Processar a transcrição para adicionar marcações de tempo por minuto
        segments = transcription.segments
        formatted_transcription = format_transcription_with_timestamps(segments)
        
        return jsonify({
            'success': True,
            'transcription': formatted_transcription
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
         # Limpar o arquivo temporário sempre
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)

def format_transcription_with_timestamps(segments):
    """
    Formata a transcrição com marcações de tempo por minuto.
    """
    formatted_text = ""
    current_minute = -1
    
    for segment in segments:
        # Converter o tempo de início para minutos
        start_time = segment['start'] # Acessar como dicionário
        minute = int(start_time / 60)
        
        # Adicionar marcação de tempo quando mudar o minuto
        if minute > current_minute:
            current_minute = minute
            minutes = minute
            seconds = int(start_time % 60)
            formatted_text += f"\n[{minutes:02d}:{seconds:02d}] "
        
        # Adicionar o texto do segmento
        formatted_text += segment['text'] + " " # Acessar como dicionário
    
    return formatted_text.strip()

@app.route('/api/analyze', methods=['POST'])
def analyze_transcription():
    if not client:
         return jsonify({'error': 'Cliente OpenAI não inicializado corretamente. Verifique a chave da API.'}), 500

    data = request.json
    
    if not data or 'transcription' not in data:
        return jsonify({'error': 'Transcrição não fornecida'}), 400
    
    transcription = data['transcription']
    
    try:
        # Usar a API da OpenAI para analisar a transcrição e extrair insights usando o cliente
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """
                Você é um assistente especializado em analisar transcrições de reuniões de equipes comerciais.
                Extraia os seguintes elementos da transcrição:
                1. Um resumo executivo da reunião
                2. Menções a pessoas da equipe e seu desempenho/estado
                3. Ações a serem tomadas (curto e médio prazo)
                4. Prazos e datas importantes mencionados
                5. Problemas ou desafios identificados
                
                Formate sua resposta como um objeto JSON com as seguintes chaves:
                - resumo: string com resumo executivo
                - pessoas: array de objetos {nome, contexto}
                - acoes: array de objetos {descricao, prazo}
                - prazos: array de objetos {evento, data}
                - desafios: array de objetos {descricao, responsavel}
                """},
                {"role": "user", "content": transcription}
            ],
            response_format={"type": "json_object"}
        )
        
        # Extrair e retornar os insights
        insights = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'insights': insights
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Usar Gunicorn para produção, esta parte é mais para debug local
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)), debug=False)

