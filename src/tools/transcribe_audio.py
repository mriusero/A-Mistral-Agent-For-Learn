from src.utils.tooling import tool
from pydub import AudioSegment
import os

@tool
def transcribe_audio(file_path: str, language: str = None) -> str:
    """
    Transcribes the content of an audio file into text.
    Args:
        file_path (str): The path to the audio file to transcribe.
        language (str, optional): The language of the audio content. If None, the language will be detected automatically. Defaults to None.
    Returns:
        str: The transcribed text from the audio file.
    """
    try:
        import speech_recognition as sr
    except ImportError as e:
        raise ImportError(
            "You must install the package `SpeechRecognition` to run this tool. For instance, run `pip install SpeechRecognition`."
        ) from e

    if file_path.lower().endswith('.mp3'):                                  # Convert MP3 to WAV if necessary
        wav_file_path = file_path.replace('.mp3', '.wav')
        audio = AudioSegment.from_mp3(file_path)
        audio.export(wav_file_path, format="wav")
        file_path = wav_file_path

    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)

            if language is None:
                try:
                    text = recognizer.recognize_google(audio_data)      # Try to detect the language automatically

                except sr.UnknownValueError:
                    raise Exception("Speech Recognition could not understand the audio.")
            else:
                text = recognizer.recognize_google(audio_data, language=language)

            return f"Transcribed text: '{text}'"

    except sr.UnknownValueError:
        raise Exception("Speech Recognition could not understand the audio.")

    except sr.RequestError as e:
        raise Exception(f"Could not request results from Speech Recognition service; {e}")

    finally:
        if file_path.lower().endswith('.wav') and os.path.exists(file_path):
            os.remove(file_path)
