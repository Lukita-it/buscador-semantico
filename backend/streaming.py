import requests

# ⚠️ IMPORTANTE: No compartas tu API Key en foros públicos. 
# Regenerala si es posible, ya que la imagen la expuso.
RAPID_HOST = "streaming-availability.p.rapidapi.com"
RAPID_KEY = "d66bbe94ccmsh6e1441bd133994ap100558jsn335204ad5322" 

def get_streaming_availability(title_es: str, title_en: str):
    """
    Busca la disponibilidad de una película por título.
    """
    # Usamos el título en inglés preferentemente, ya que la API busca mejor en inglés
    title = title_en or title_es
    if not title:
        return ["No disponible"]

    # 1. CORRECCIÓN DE URL: Usar el endpoint 'title' según tu imagen
    url = "https://streaming-availability.p.rapidapi.com/shows/search/title"

    # Definimos el país donde buscar (en la imagen dice que 'country' es obligatorio)
    target_country = "us" 

    # 2. PARÁMETROS: Ajustados a lo que pide la documentación en la imagen
    params = {
        "title": title,           # Requerido
        "country": target_country, # Requerido (ISO 3166-1 alpha-2)
        "show_type": "movie",     # Opcional, pero bueno para filtrar
        "output_language": "en"
    }

    headers = {
        "x-rapidapi-key": RAPID_KEY,
        "x-rapidapi-host": RAPID_HOST,
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        # Debug para ver qué devuelve la API
        # print(f"DEBUG API: {data}") 

    except Exception as e:
        print("Streaming API ERROR:", e)
        return ["No disponible"]

    # 3. PARSEO DE LA RESPUESTA
    # La API devuelve una lista de resultados bajo la llave variable (a veces solo es una lista directa)
    # Pero según la documentación de v4 suele ser una lista directa de objetos.
    
    # Validamos si data es una lista (formato común en v4 para search/title)
    if isinstance(data, list):
        results = data
    elif "results" in data: # Formato alternativo
        results = data["results"]
    else:
        return ["No disponible"]

    if not results:
        return ["No disponible"]

    # Tomamos la primera coincidencia
    item = results[0]

    # Verificamos si tiene opciones de streaming
    if "streamingOptions" not in item:
        return ["No disponible"]

    options = item["streamingOptions"]

    # Verificamos si hay opciones para el país solicitado (us)
    if target_country not in options:
        return ["No disponible"]

    # Extraemos los servicios
    entries = options[target_country]
    plataformas = set()

    for entry in entries:
        # La estructura suele ser entry -> service -> name
        if "service" in entry and "name" in entry["service"]:
            plataformas.add(entry["service"]["name"])

    if not plataformas:
        return ["No disponible"]

    return list(plataformas)