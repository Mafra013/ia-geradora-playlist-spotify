from flask import Flask, render_template, request, jsonify
from services import SpotifyService
from brain import PlaylistBrain

app = Flask(__name__)

sp = SpotifyService()
brain = PlaylistBrain()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_playlist():
    data = request.json
    pedido = data.get("pedido")
    
    if not pedido:
        return jsonify({"error": "Pedido vazio"}), 400

    perfil = sp.get_profile_summary()
    dados_musicas = brain.generate_list(pedido, perfil)
    print(f"Músicas sugeridas pela IA: {dados_musicas}")

    uris_finais = []
    uris_vistas = set()
    nomes_vistos = set()
    
    for item in dados_musicas:
        chave_nome = f"{item["artist"]} - {item["song"]}". lower()
        if chave_nome in nomes_vistos:
            continue
        nomes_vistos.add(chave_nome)
        
        uri = sp.search_track_uri(item["artist"], item["song"])
        
        if uri and uri not in uris_vistas:
            uris_finais.append(uri)
            uris_vistas.add(uri)
            
    if not uris_finais:
        return jsonify({"error": "Nenhuma música encotrada"})
    
    nome_pl = f"AI: {pedido.title()}"
    desc_pl = f"Playlist gerada via IA. Tema: {pedido}"

    link = sp.create_playlist_direct(nome_pl, desc_pl, uris_finais)
    
    return jsonify({
        "link": link,
        "quantidade": len(uris_finais)
    })
    

if __name__ == "__main__":
    app.run(debug=True)