from flask import Flask, request, jsonify, render_template
import os
from pydub import AudioSegment
import whisper

app = Flask(__name__)

# Load Whisper model
model = whisper.load_model("base")  # You can choose 'small', 'base', 'medium', 'large' based on your needs

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    audio_path = os.path.join('uploads', audio_file.filename)
    audio_file.save(audio_path)

    converted_audio_path = os.path.join('uploads', 'converted.wav')
    transcription = ""

    try:
        # Convert the audio to WAV format using pydub
        audio = AudioSegment.from_file(audio_path)
        audio.export(converted_audio_path, format='wav')

        # Transcribe the entire audio using Whisper
        result = model.transcribe(converted_audio_path, language="id")
        transcription = result['text']
    except Exception as e:
        transcription = f"[Error: {str(e)}] "
    finally:
        # Clean up the uploaded and converted files
        os.remove(audio_path)
        if os.path.exists(converted_audio_path):
            os.remove(converted_audio_path)

    return jsonify({'transcription': transcription.strip()})

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)

