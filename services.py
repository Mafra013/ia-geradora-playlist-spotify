import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import *

class SpotifyService:
    def __init__(self):
        # Escopos necessários para ler perfil e criar playlist pública/privada
        scope = "playlist-modify-public playlist-modify-private user-top-read"
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=scope,
            cache_path=".cache-spotify"
        ))
        self.user_id = self.sp.current_user()["id"]

    def get_profile_summary(self):
        try:
            # Pega top artistas (médio prazo)
            top = self.sp.current_user_top_artists(limit=15, time_range='medium_term')
            artists = [item['name'] for item in top['items']]
            
            # Extrai gêneros desses artistas
            genres = set()
            for item in top['items']:
                genres.update(item.get('genres', []))
            
            return {
                "artists": ", ".join(artists),
                "genres": ", ".join(list(genres)[:10])
            }
        except:
            return {"artists": "Indefinido", "genres": "Indefinido"}

    def search_track_uri(self, artist, song):
        # 1. Busca
        q = f"track:{song} artist:{artist}"
        res = self.sp.search(q=q, type="track", limit=1, market="BR")
        if res['tracks']['items']:
            return res['tracks']['items'][0]['uri']
        
        # 2. Fallback
        q2 = f"{artist} {song}"
        res = self.sp.search(q=q2, type="track", limit=1, market="BR")
        if res['tracks']['items']:
            return res['tracks']['items'][0]['uri']
            
        return None

    def create_playlist_direct(self, name, description, uris):
        if not uris: return None
        
        pl = self.sp.user_playlist_create(self.user_id, name, public=True, description=description)
        
        # limite
        self.sp.playlist_add_items(pl['id'], uris)
        return pl['external_urls']['spotify']