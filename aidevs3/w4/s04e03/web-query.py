#!venv3/bin/python3

import requests
import html2text
import json
import logging
from config import Config
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

import os
import re
import sqlite3

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

def get_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.error(f"Error downloading page: {e}")
        return None

def html_to_markdown(html):
    return html2text.html2text(html)

def ask_llm_if_answer(system_prompt, page_md, question, llm):
    prompt = (
        f"{system_prompt}\n"
        f"---\n"
        f"Treść strony:\n{page_md}\n"
        f"---\n"
        f"Pytanie: {question}\n"
        "Czy na podstawie powyższej treści możesz jednoznacznie odpowiedzieć na pytanie? "
        "Jeśli tak, podaj odpowiedź. Jeśli nie, odpowiedz tylko słowem NIE.\n"
        "Odpowiedź powinna być krótka i zwięzła, bez dodatkowych informacji."
    )
    logging.info(f"LLM question: {question}")
    messages = [SystemMessage(content=prompt)]
    response = llm.invoke(messages)
    logging.info(f"LLM response: {response.content.strip()}")
    return response.content.strip()

def ask_llm_which_link(system_prompt, links, question, llm):
    prompt = (
        f"{system_prompt}\n"
        f"---\n"
        f"Pytanie: {question}\n"
        f"Dostępne linki (w formacie markdown):\n" +
        "\n".join(links) +
        "\nKtóry z powyższych linków najbardziej prawdopodobnie prowadzi do odpowiedzi na pytanie? "
        "Podaj dokładny adres wybranego linku. Odpowiedź powinna zawierać tylko adres."
    )
    messages = [SystemMessage(content=prompt)]
    response = llm.invoke(messages)
    logging.info(f"LLM link response: {response.content.strip()}")
    return response.content.strip()
def find_markdown_links(page_md):
    """
    Zwraca listę wszystkich markdownowych linków (jako pełne dopasowania) z tekstu markdown.
    """
    # Pomija obrazy ![alt](src)
    page_md = re.sub(r'!\[.*?\]\(.*?\)', '', page_md)
    # Zwraca pełne dopasowania, np. [Tekst](adres "Tytuł") lub [Tekst][ref]
    return re.findall(r'\[[^\]]+\]\([^)]+\)|\[[^\]]+\]\[[^\]]+\]', page_md)
def parse_markdown_link(md_link):
    """
    Przyjmuje pojedynczy markdownowy link i zwraca krotkę (tekst, adres/ref, tytuł).
    Obsługuje zarówno [tekst](adres "tytuł"), jak i [tekst][referencja].
    """
    # Inline link: [tekst](adres "tytuł")
    match_inline = re.match(r'\[([^\]]+)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)', md_link)
    if match_inline:
        link_text = match_inline.group(1)
        link_address = match_inline.group(2)
        link_title = match_inline.group(3) if match_inline.lastindex == 3 else None
        return (link_text, link_address, link_title)
    # Reference link: [tekst][referencja]
    match_ref = re.match(r'\[([^\]]+)\]\[([^\]]+)\]', md_link)
    if match_ref:
        link_text = match_ref.group(1)
        link_ref = match_ref.group(2)
        return (link_text, link_ref, None)
    return (None, None, None)

def resolve_url(base, link):
    from urllib.parse import urljoin
    return urljoin(base, link)

def save_page_to_db(link, page_md, db_path="pages.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            link TEXT PRIMARY KEY,
            content TEXT
        )
    """)
    c.execute("""
        INSERT OR REPLACE INTO pages (link, content) VALUES (?, ?)
    """, (link, page_md))
    conn.commit()
    conn.close()

def get_page_from_db(link, db_path="pages.db"):
    if not os.path.exists(db_path):
        return None
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Check if table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pages'")
    if not c.fetchone():
        conn.close()
        return None
    c.execute("SELECT content FROM pages WHERE link = ?", (link,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

def search_for_answer(start_link, start_url, question, llm, system_prompt, max_depth=15):
    visited = set()
    link = start_link
    url = start_url
    for depth in range(max_depth):
        if url in visited:
            break
        visited.add(url)

        # Use the new function to check if page is in db
        page_md = get_page_from_db(link)
        if page_md:
            logging.info(f"Loaded page for link [{link}] from sqlite db.")
        else:
            html = get_html(url)
            if not html:
                return None
            page_md = html_to_markdown(html)
            save_page_to_db(link, page_md)  # Save markdown to sqlite3 by link

        answer = ask_llm_if_answer(system_prompt, page_md, question, llm)
        if answer.strip().upper() != "NIE":
            return answer
        links = find_markdown_links(page_md)
        if not links:
            break
        logging.info(f"Available links: {links}")
        chosen = ask_llm_which_link(system_prompt, links, question, llm)
        logging.info(f"LLM chose link: [{chosen}]")
        for l in links:
            (text, href, title) = parse_markdown_link(l)
            if not href:
                continue
            logging.info(f"Checking link: [{chosen}] with href: [{href}]")
            if chosen in href:
                logging.info(f"Resolved URL: {href}")
                link = href
                url = resolve_url(url, href)
                logging.info(f"Next URL to visit: {url}")
                logging.info(f"Link name: {link}")
                break
        else:
            break  # LLM nie wskazał żadnego istniejącego linku
    return None

def talk_to_robot(url: str, data: dict) -> dict | None:
    """Send a POST request with JSON data and return the response as a dict."""
    try:
        response = requests.post(url, json=data, headers=CONTENT_TYPE_HEADER)
        logging.info(response)
        logging.info(response.text)
        save_data(response.text, "robot_response.txt")
        response.raise_for_status()
        return response.text
    except (requests.RequestException, ValueError) as e:
        logging.error(f"Error communicating with robot: {e}")
        return None

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

    queries_txt = get_html(config.src.replace("YOUR-KEY", config.apikey))
    queries = json.loads(queries_txt)
    save_data(json.dumps(queries,ensure_ascii=False, indent=4), "queries.json")

    llm = ChatOpenAI(openai_api_key=config.llmkey, model_name=config.openai_model)
    system_prompt = (
        "Jesteś inteligentnym agentem przeszukującym stronę internetową, aby znaleźć odpowiedzi na pytania użytkownika. "
        "Twoim zadaniem jest analizować treść strony i wskazywać, czy można już odpowiedzieć na pytanie, "
        "lub który link wybrać, by znaleźć odpowiedź."
    )
    answers = {}
    for key, question in queries.items():
        answer = search_for_answer("/",config.page, question, llm, system_prompt)
        answers[key] = answer if answer else "Nie znaleziono odpowiedzi."
        print(f"{key}: {answers[key]}\n")
    # Zapisz odpowiedzi do pliku
    with open("answers.json", "w", encoding="utf-8") as f:
        json.dump(answers, f, ensure_ascii=False, indent=2)

    # --- REPORT TO ROBOT ---
    # Prepare report data
    report_data = {
        "task": "softo",
        "apikey": config.apikey,
        "answer": answers
    }
    # Send report to robot
    talk_to_robot(config.dest, report_data)

if __name__ == "__main__":
    main()
