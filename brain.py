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
        Atue como um Curador Musical de Elite (DJ & Music Critic). Sua missão é criar a playlist perfeita para o pedido abaixo.

        --- PEDIDO DO USUÁRIO (PRIORIDADE TOTAL) ---
        "{user_request}"

        --- PERFIL DO USUÁRIO (USE APENAS COMO DIREÇÃO/ESTILO) ---
        - Músicas recentes: {user_profile['recent_vibe']}
        - Artistas que gosta: {user_profile['top_artists']}
        - Gêneros predominantes: {user_profile['genres']}

        LÓGICA DE CURADORIA:
        1. O PEDIDO É A REGRA: Se o usuário pediu "Trap para Academia", entregue Trap real e pesado. Não importa se ele ouve "MPB" no perfil dele, foque no Trap.
        2. PERFIL COMO FILTRO DE ESTILO: Use o perfil dele apenas para entender se ele prefere algo mais moderno, clássico, "underground" ou comercial.
        3. PROIBIDO ALUCINAR: Não invente nomes de artistas ou músicas. Use apenas artistas reais, verificados e influentes no gênero solicitado.
        4. DESCOBERTA MUSICAL: Misture artistas que ele conhece (30%) com excelentes sugestões novas que ele provavelmente amaria dentro do tema (70%).
        5. DIVERSIDADE: Limite de no máximo 2 faixas por artista.

        OBJETIVO:
        Gerar uma lista de exatamente {PLAYLIST_LIMIT} músicas reais em JSON.
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