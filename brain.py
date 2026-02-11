from google import genai
from google.genai import types
import json
from config import GEMINI_API_KEY, PLAYLIST_LIMIT
from pydantic import BaseModel, Field

class MusicItem(BaseModel):
    artist: str = Field(description="Nome do Artista")
    song: str = Field(description="Nome da Música")

class PlaylistResponse(BaseModel):
    playlist: list[MusicItem]

class PlaylistBrain:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_id = "gemini-2.5-flash"

    def generate_list(self, user_request, user_profile):
        prompt = f"""
        Atue como um Curador Musical de Alta Performance (DJ & Music Critic).
        
        CONTEXTO DO USUÁRIO:
        - Artistas Favoritos: {user_profile['artists']}
        - Gêneros Favoritos: {user_profile['genres']}
        
        PEDIDO ATUAL: "{user_request}"
        
        SUA LÓGICA DE CURADORIA:
        1. ANÁLISE DE INTENÇÃO:
           - O pedido é um GÊNERO (ex: "Sertanejo") ou um MOOD (ex: "Jantar Romântico")?
           
        2. O FATOR "MATCH":
           - Verifique se o histórico do usuário (Artistas/Gêneros) combina com o PEDIDO.
           - SIM (Combina): Use os artistas favoritos dele como BASE e adicione novidades do mesmo estilo.
           - NÃO (Não combina): Ignore o histórico! Se ele pediu "Jazz" e só ouve "Funk", entregue os maiores clássicos do Jazz. Não force misturas bizarras.

        3. REGRAS DE OURO:
           - Se for um MOOD (ex: "Academia"), foque na ENERGIA (BPM alto), independente do gênero, mas priorizando o gosto dele se couber.
           - Se for GÊNERO (ex: "Trap"), mantenha a pureza do estilo.
           - Evite repetir o mesmo artista mais de 2 vezes, a menos que o pedido seja específico sobre ele.
        
        OBJETIVO:
        Gerar uma lista de exatamente {PLAYLIST_LIMIT} músicas.
        """

        try:
            # Formato da resposta
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=PlaylistResponse
                )
            )
            
            data = response.parsed
            
            # Converte para lista
            return [{"artist": item.artist, "song": item.song} for item in data.playlist]

        except Exception as e:
            print(f"Erro na IA: {e}")
            return []