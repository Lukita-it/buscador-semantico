import requests
from bs4 import BeautifulSoup

def get_trailer_id(title: str):
    """Busca el primer video de YouTube para '<title> trailer'"""

    query = f"{title} trailer"
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"

    response = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0"
    })

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Buscar dentro de los scripts donde YouTube guarda los datos
    for script in soup.find_all("script"):
        text = script.text

        if "videoId" in text:
            # Extraer el primer videoId que aparezca
            start = text.find('"videoId":"') + len('"videoId":"')
            end = text.find('"', start)
            video_id = text[start:end]

            if len(video_id) >= 8:  # Validación básica
                return video_id

    return None
