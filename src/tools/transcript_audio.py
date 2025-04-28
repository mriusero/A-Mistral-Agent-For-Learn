from src.utils.tooling import tool

@tool
def transcribe_audio(file_path: str, language: str = 'en') -> str:
    """
    Transcribes the content of an audio file into text.
    Args:
        file_path (str): The path to the audio file to transcribe.
        language (str, optional): The language of the audio content. Defaults to 'en' (English).
    Returns:
        str: The transcribed text from the audio file.
    """
    try:
        import speech_recognition as sr
    except ImportError as e:
        raise ImportError(
            "You must install the package `SpeechRecognition` to run this tool. For instance, run `pip install SpeechRecognition`."
        ) from e

    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language=language)
            return text
    except sr.UnknownValueError:
        raise Exception("Speech Recognition could not understand the audio.")
    except sr.RequestError as e:
        raise Exception(f"Could not request results from Speech Recognition service; {e}")
