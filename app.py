from flask import Flask, request, jsonify, render_template
import speech_recognition as sr
import os
from pydub import AudioSegment

app = Flask(__name__)

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

        recognizer = sr.Recognizer()
        audio_length_ms = len(audio)  # Get audio length in milliseconds
        chunk_duration_ms = 5000  # 10 seconds per chunk

        # Iterate over the audio in 10-second chunks
        for start_ms in range(0, audio_length_ms, chunk_duration_ms):
            end_ms = min(start_ms + chunk_duration_ms, audio_length_ms)
            audio_chunk = audio[start_ms:end_ms]
            chunk_path = os.path.join('uploads', f'chunk_{start_ms}.wav')
            audio_chunk.export(chunk_path, format='wav')

            try:
                # Transcribe the chunk
                with sr.AudioFile(chunk_path) as source:
                    audio_data = recognizer.record(source)
                    chunk_transcription = recognizer.recognize_google(audio_data, language='id-ID')
                    transcription += chunk_transcription + " "
            except sr.UnknownValueError:
                transcription += "[Unrecognized speech] "
            except sr.RequestError as e:
                transcription += f"[API error: {e}] "
            finally:
                # Clean up the chunk file
                os.remove(chunk_path)

    except Exception as e:
        transcription += f"[Error: {str(e)}] "
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

