#!/usr/bin/env python3
"""
Script para probar la lógica de cuándo mostrar acciones en las búsquedas
"""

def should_show_actions(title: str, artist: str, total_results: int) -> bool:
    """
    Determina si mostrar los botones de acción basado en la especificidad de la búsqueda.
    
    Args:
        title: Título de la canción buscada
        artist: Artista buscado
        total_results: Número total de resultados
    
    Returns:
        True si se deben mostrar las acciones, False en caso contrario
    """
    # Si hay tanto título como artista, la búsqueda es específica
    if title and artist:
        return True
    
    # Si solo hay uno de los campos y pocos resultados, mostrar acciones
    if (title or artist) and total_results <= 10:
        return True
    
    # Para búsquedas muy amplias, no mostrar acciones
    return False

def test_search_scenarios():
    """Probar diferentes escenarios de búsqueda"""
    
    print("🧪 Probando lógica de mostrar acciones...")
    print("=" * 50)
    
    # Casos de prueba
    test_cases = [
        # (título, artista, resultados, descripción)
        ("Bohemian Rhapsody", "Queen", 1, "Búsqueda específica - título y artista"),
        ("", "Queen", 50, "Solo artista - muchos resultados"),
        ("", "Queen", 5, "Solo artista - pocos resultados"),
        ("Bohemian Rhapsody", "", 3, "Solo título - pocos resultados"),
        ("Bohemian Rhapsody", "", 25, "Solo título - muchos resultados"),
        ("", "", 100, "Búsqueda vacía"),
        ("Love", "", 500, "Término muy general"),
        ("Love", "Beatles", 12, "Específica pero algunos resultados"),
    ]
    
    for title, artist, results, description in test_cases:
        show_actions = should_show_actions(title, artist, results)
        
        print(f"\n📋 Caso: {description}")
        print(f"   Título: '{title}' | Artista: '{artist}' | Resultados: {results}")
        print(f"   ➜ Mostrar acciones: {'✅ SÍ' if show_actions else '❌ NO'}")
        
        if show_actions:
            print("   💡 El usuario podrá ver botones: Analizar, Similares, Ver Letra")
        else:
            print("   💡 Se mostrará sugerencia para hacer búsqueda más específica")

if __name__ == "__main__":
    test_search_scenarios()
