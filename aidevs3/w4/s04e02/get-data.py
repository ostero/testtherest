#!venv3/bin/python3

import logging
import os
import json
from config import Config
import wget
import zipfile

CONTENT_TYPE_HEADER = {'Content-Type': 'application/json;charset=UTF-8'}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def save_data(data: str| None, filename: str) -> None:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(data)
    except Exception as e:
        logging.error(f"Error saving data: {e}")

def get_data(config):
    zipped_data = os.path.basename(config.src)
    if not os.path.exists(zipped_data):
        if not os.path.exists(config.data_dir):
            logging.info(f"Creating data directory: {config.data_dir}")
            os.makedirs(config.data_dir)
        wget.download(config.src)
        with zipfile.ZipFile(zipped_data, 'r') as zip_ref:
            zip_ref.extractall(config.data_dir)

def main() -> None:
    global config
    try:
        config = Config.load_from_yaml()
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        return

    if not config.is_valid():
        logging.error("Invalid configuration.")
        return

    get_data(config)

    teach_data = ""
    teach_line = {}
    teach_line["messages"] = []
    teach_line["messages"].append({"role": "system", "content": "validate data"})
    teach_line["messages"].append({"role": "user", "content": ""})
    teach_line["messages"].append({"role": "assistant", "content": ""})

    with open(config.data_dir + "/correct.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            teach_line["messages"][1]["content"] = line
            teach_line["messages"][2]["content"] = "1"
            teach_data += json.dumps(teach_line, ensure_ascii=False) + "\n"

    with open(config.data_dir + "/incorect.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            teach_line["messages"][1]["content"] = line
            teach_line["messages"][2]["content"] = "0"
            teach_data += json.dumps(teach_line, ensure_ascii=False) + "\n"

    save_data(teach_data.strip(), config.data_dir + "/teach.jsonl")

if __name__ == "__main__":
    main()
