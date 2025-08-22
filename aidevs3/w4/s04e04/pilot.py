#!./venv3/bin/python3
from flask import Flask, request, jsonify
from config import Config
import logging
import openai

app = Flask(__name__)

def init_map():
    global terrain_map
    w, h = 4, 4
    terrain_map = [["" for x in range(w)] for y in range(h)] 
    terrain_map[0][0] = "start"
    terrain_map[0][1] = "trawa"
    terrain_map[0][2] = "drzewo"
    terrain_map[0][3] = "dom"
    terrain_map[1][0] = "trawa"
    terrain_map[1][1] = "wiatrak"
    terrain_map[1][2] = "trawa"
    terrain_map[1][3] = "trawa"
    terrain_map[2][0] = "trawa"
    terrain_map[2][1] = "trawa"
    terrain_map[2][2] = "skały"
    terrain_map[2][3] = "dwa drzewa"
    terrain_map[3][0] = "skały"
    terrain_map[3][1] = "skały"
    terrain_map[3][2] = "samochód"
    terrain_map[3][3] = "jaskinia"

def validate_llm_response(response: str) -> tuple[int, int] | None:
    """
    Sprawdza, czy odpowiedź LLM to dwie liczby z zakresu 0-3 oddzielone przecinkiem.
    Jeśli tak, zwraca krotkę (wiersz, kolumna), w przeciwnym razie None.
    """
    if not isinstance(response, str):
        return None
    parts = response.strip().split(",")
    if len(parts) != 2:
        return None
    try:
        row = int(parts[0].strip())
        col = int(parts[1].strip())
        if 0 <= row <= 3 and 0 <= col <= 3:
            return (row, col)
        else:
            return None
    except ValueError:
        return None

@app.route('/pilot', methods=['POST'])
def pilot():
    if not request.is_json:
        return jsonify({"error": "Żądanie musi być w formacie JSON"}), 400

    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Nieprawidłowy JSON"}), 400

    instruction = data.get("instruction")
    if not instruction or not isinstance(instruction, str):
        return jsonify({"error": "Brak lub nieprawidłowe pole 'instruction'"}), 400
    logging.info(f"Received instruction: {instruction}") 
    global config
    system_prompt = (
        "Mapa to siatka 4x4 (wiersze i kolumny liczone od 0 do 3). "
        "Startujesz z pozycji 0,0. "
        f"Na podstawie instrukcji podanej przez użytkownika podaj współrzędne końcowe drona w formacie nr_wiersza, nr_kolumny. "
        "Odpowiedz tylko współrzędnymi, bez dodatkowych słów."
    )
    llm_response = ask_openai(system_prompt, instruction)
    if not llm_response:
        return jsonify({"error": "Nie udało się uzyskać odpowiedzi od LLM"}), 500
    logging.info(f"LLM response: {llm_response}")   
    row, col = validate_llm_response(llm_response)
    if row  is None or col is None:
        return jsonify({"error": "Nieprawidłowa odpowiedź LLM", "llm_response": llm_response}), 400
    logging.info(f"description at ({row}, {col}): {terrain_map[row][col]}")
    return jsonify({"status": "OK", "llm_response": llm_response, "description": terrain_map[row][col]}), 200

def ask_openai(system_prompt: str, user_prompt: str) -> str | None:
    global config
    try:        
        openai.api_key = config.llmkey
        response = openai.chat.completions.create(
            model = config.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=10,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error getting LLM answer: {e}")
        return None

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    global config
    config = Config.load_from_yaml()
    if not config.is_valid():
        logging.error("Invalid configuration. HTTP server will not start.")
    else:
        init_map()
        app.run(host='0.0.0.0', port=config.port)