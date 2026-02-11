from rich.console import Console
from rich.progress import track
from services import SpotifyService
from brain import PlaylistBrain

console = Console()

def main():
    sp = SpotifyService()
    brain = PlaylistBrain()
    
    console.print("\n[bold green]♫ Spotify AI Generator[/]")
    
    pedido = console.input("\n[bold yellow]O que vamos ouvir?[/] ").strip()
    if not pedido: return

    with console.status("[bold cyan]Consultando seu histórico e gerando lista...[/]"):
        perfil = sp.get_profile_summary()
        dados_musicas = brain.generate_list(pedido, perfil)

    if not dados_musicas:
        console.print("[red]Erro ao gerar lista.[/]")
        return

    uris_finais = []
    uris_vistas = set()   
    nomes_vistos = set()
    
    for item in track(dados_musicas, description="[green]Filtrando e Sincronizando...[/]"):
        # 1. Filtro de Nome (Evita que a IA mande a mesma string duas vezes)
        chave_nome = f"{item['artist']} - {item['song']}".lower()
        if chave_nome in nomes_vistos:
            continue
        nomes_vistos.add(chave_nome)

        # 2. Busca no Spotify
        uri = sp.search_track_uri(item['artist'], item['song'])
        
        # 3. Filtro de URI (Evita que buscas diferentes levem à mesma música)
        if uri and uri not in uris_vistas:
            uris_finais.append(uri)
            uris_vistas.add(uri)
            
    
    if uris_finais:
        nome_pl = f"AI: {pedido.title()}"
        desc_pl = f"Playlist única gerada via IA. Tema: {pedido}"
        
        link = sp.create_playlist_direct(nome_pl, desc_pl, uris_finais)
        
        console.print(f"\n[bold green]✓ Playlist Criada com {len(uris_finais)} músicas únicas![/]")
        console.print(f"[link={link}]Clique aqui para ouvir: {nome_pl}[/link]\n")
    else:
        console.print("[red]Nenhuma música válida encontrada.[/]")

if __name__ == "__main__":
    main()