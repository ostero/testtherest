import whisper
import os

directory = 'przesluchania'

def transcribe_audio(audio_path):
    #audio_file = "./przesluchania/monika.m4a"  # Replace with your audio file path
    audio = whisper.load_audio(audio_path)
    global model
    result = model.transcribe(audio)
    return result["text"]

def append_transcription(tag: str, text: str) -> None:
    with open("transcription.txt", "a+", encoding="utf-8") as transcription_file:
        transcription_file.write(f"{tag}:\n")
        transcription_file.write(text + "\n\n")

def main() -> None:
    # Load the model (choose a size)
    global model
    model = whisper.load_model("base")
    #model = whisper.load_model("SpeakLeash/bielik-7b-instruct-v0.1-gguf:latest")
    
    for filename in os.listdir(directory):
        if filename.lower().endswith('.m4a'):
            filepath = os.path.join(directory, filename)
            tag = os.path.splitext(filename)[0].capitalize().replace('l', 'ł')  # Use the filename without extension as tag
            print(tag)
            result = transcribe_audio(filepath)
            print(result)
            append_transcription(tag, result)

if __name__ == "__main__":
    main()

