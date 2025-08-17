import whisper
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

src_directory = 'pliki_z_fabryki'
dst_directory = 'decoded_pliki_z_fabryki'

def transcribe_audio(audio_path):
    audio = whisper.load_audio(audio_path)
    global model
    result = model.transcribe(audio)
    return result["text"]

def save_data(data: str| None, filename: str) -> None:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(data)
    except Exception as e:
        logging.error(f"Error saving data: {e}")

def main() -> None:
    # Load the model (choose a size)
    global model
    model = whisper.load_model("base")
    #model = whisper.load_model("SpeakLeash/bielik-7b-instruct-v0.1-gguf:latest")
    
    for filename in os.listdir(src_directory):
        if filename.lower().endswith('.mp3'):
            filepath = os.path.join(src_directory, filename)
            filenameWithoutExtension = os.path.splitext(filename)[0]
            logging.info(filenameWithoutExtension);
            result = transcribe_audio(filepath)
            logging.info(result)
            save_data(result, os.path.join(dst_directory, filenameWithoutExtension + ".txt"))

if __name__ == "__main__":
    main()

