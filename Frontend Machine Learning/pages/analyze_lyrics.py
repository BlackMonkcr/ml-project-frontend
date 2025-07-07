"""
Página para analizar letras personalizadas
"""

import streamlit as st
from utils.api_client import analyze_words_safe, predict_lyrics_safe, format_confidence, get_confidence_description

def show_analyze_page():
    """Mostrar la página de análisis de letras personalizadas"""
    
    st.title("📝 Analizar Letras")
    st.markdown("Escribe o pega las letras de una canción para analizar si contiene contenido explícito")
    
    # Formulario de análisis
    with st.form("analyze_form"):
        # Campos opcionales para metadatos
        col1, col2 = st.columns(2)
        
        with col1:
            song_title = st.text_input(
                "🎵 Título de la canción (opcional)",
                placeholder="Ej: My Song Title",
                help="Opcional: ayuda a contextualizar el análisis"
            )
        
        with col2:
            artist_name = st.text_input(
                "🎤 Artista (opcional)",
                placeholder="Ej: Artist Name",
                help="Opcional: ayuda a contextualizar el análisis"
            )
        
        # Área de texto para las letras
        lyrics_text = st.text_area(
            "📜 Letras de la canción",
            placeholder="Escribe o pega aquí las letras de la canción que quieres analizar...",
            height=200,
            help="Escribe las letras completas para un mejor análisis"
        )
        
        # Botones de acción
        col_a, col_b, col_c = st.columns([1, 1, 2])
        
        with col_a:
            analyze_button = st.form_submit_button("🔬 Analizar Contenido", use_container_width=True)
        
        with col_b:
            analyze_words_button = st.form_submit_button("🔍 Análisis Detallado", use_container_width=True)
    
    # Procesar análisis
    if analyze_button or analyze_words_button:
        if not lyrics_text.strip():
            st.error("⚠️ Por favor, escribe las letras de la canción para analizar.")
        elif len(lyrics_text.strip()) < 10:
            st.warning("⚠️ Las letras parecen muy cortas. Escribe más texto para un mejor análisis.")
        else:
            if analyze_words_button:
                perform_detailed_analysis(lyrics_text, song_title, artist_name)
            else:
                perform_basic_analysis(lyrics_text, song_title, artist_name)
    
    # Mostrar ejemplos si no hay análisis
    if not (analyze_button or analyze_words_button):
        show_examples()

def perform_basic_analysis(lyrics: str, title: str = "", artist: str = ""):
    """
    Realizar análisis básico de las letras
    
    Args:
        lyrics: Letras de la canción
        title: Título opcional
        artist: Artista opcional
    """
    st.markdown("---")
    st.markdown("### 🎯 Resultado del Análisis")
    
    with st.spinner("Analizando contenido..."):
        result = predict_lyrics_safe(lyrics, title or None, artist or None)
    
    if result:
        # Mostrar resultado principal
        col1, col2 = st.columns(2)
        
        with col1:
            if result['is_explicit']:
                st.error("🔥 **CONTENIDO EXPLÍCITO DETECTADO**")
                st.markdown("El modelo ha identificado que estas letras contienen contenido explícito.")
            else:
                st.success("✅ **CONTENIDO LIMPIO**")
                st.markdown("El modelo considera que estas letras no contienen contenido explícito.")
        
        with col2:
            confidence = result['confidence']
            confidence_text, confidence_class = format_confidence(confidence)
            confidence_desc = get_confidence_description(confidence)
            
            st.metric(
                "Confianza del Modelo",
                confidence_text,
                help=f"El modelo está {confidence_desc.lower()} de esta predicción"
            )
        
        # Mostrar probabilidades
        st.markdown("#### 📊 Probabilidades Detalladas")
        
        prob_explicit = result['probabilities']['explicit'] * 100
        prob_not_explicit = result['probabilities']['not_explicit'] * 100
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.metric("Probabilidad Explícito", f"{prob_explicit:.1f}%")
        
        with col_b:
            st.metric("Probabilidad Limpio", f"{prob_not_explicit:.1f}%")
        
        # Barra de progreso visual
        st.markdown("**Visualización:**")
        st.progress(prob_explicit / 100, text=f"Contenido Explícito: {prob_explicit:.1f}%")
        
        # Metadatos
        metadata = result.get('metadata', {})
        with st.expander("ℹ️ Información del Análisis"):
            col_i, col_ii, col_iii = st.columns(3)
            
            with col_i:
                st.metric("Caracteres", metadata.get('lyrics_length', 0))
            
            with col_ii:
                st.metric("Palabras", metadata.get('word_count', 0))
            
            with col_iii:
                if title and artist:
                    st.write(f"**Canción:** {title}")
                    st.write(f"**Artista:** {artist}")
        
        # Sugerencia para análisis detallado
        if not result['is_explicit']:
            st.info("💡 Para ver qué palabras específicas influyeron en esta decisión, usa el **Análisis Detallado**.")
        
    else:
        st.error("❌ Error al analizar las letras. Verifica que la API esté funcionando correctamente.")

def perform_detailed_analysis(lyrics: str, title: str = "", artist: str = ""):
    """
    Realizar análisis detallado palabra por palabra
    
    Args:
        lyrics: Letras de la canción
        title: Título opcional
        artist: Artista opcional
    """
    st.markdown("---")
    st.markdown("### 🔬 Análisis Detallado")
    
    with st.spinner("Analizando cada palabra..."):
        analysis = analyze_words_safe(lyrics, title or None, artist or None)
    
    if analysis:
        # Resultado general
        overall = analysis['overall_prediction']
        
        col1, col2 = st.columns(2)
        
        with col1:
            if overall['is_explicit']:
                st.error("🔥 **CONTENIDO EXPLÍCITO DETECTADO**")
            else:
                st.success("✅ **CONTENIDO LIMPIO**")
        
        with col2:
            confidence_text, _ = format_confidence(overall['confidence'])
            st.metric("Confianza", confidence_text)
        
        # Análisis de palabras
        words = analysis.get('words', [])
        
        if words:
            st.markdown("#### 🔍 Análisis por Palabra")
            
            # Filtrar palabras explícitas
            explicit_words = [w for w in words if w['is_explicit']]
            medium_words = [w for w in words if 0.4 <= w['explicit_score'] < 0.6]
            
            # Mostrar palabras explícitas
            if explicit_words:
                st.markdown("**🔥 Palabras Explícitas Detectadas:**")
                
                for word_info in explicit_words:
                    score = word_info['explicit_score']
                    contribution = word_info['contribution']
                    
                    col_word, col_score, col_contrib = st.columns([2, 1, 1])
                    
                    with col_word:
                        st.markdown(f'<span class="explicit-word">{word_info["word"]}</span>', unsafe_allow_html=True)
                    
                    with col_score:
                        st.write(f"Score: {score:.3f}")
                    
                    with col_contrib:
                        if contribution == "high":
                            st.write("🔴 Alto")
                        elif contribution == "medium":
                            st.write("🟡 Medio")
                        else:
                            st.write("🟢 Bajo")
                
                st.markdown("---")
            
            # Mostrar palabras sospechosas
            if medium_words:
                with st.expander("⚠️ Palabras con Score Medio (pueden ser contextuales)"):
                    for word_info in medium_words:
                        score = word_info['explicit_score']
                        st.write(f"**{word_info['word']}** - Score: {score:.3f}")
            
            # Mostrar texto resaltado
            st.markdown("#### 📖 Texto con Palabras Resaltadas")
            highlighted_text = highlight_explicit_words(lyrics, words)
            st.markdown(highlighted_text, unsafe_allow_html=True)
            
            # Estadísticas del análisis
            metadata = analysis.get('metadata', {})
            
            with st.expander("📊 Estadísticas del Análisis"):
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                
                with col_stat1:
                    st.metric("Total Palabras", metadata.get('total_words', 0))
                
                with col_stat2:
                    st.metric("Palabras Analizadas", metadata.get('analyzed_words', 0))
                
                with col_stat3:
                    st.metric("Palabras Explícitas", metadata.get('explicit_words_count', 0))
                
                with col_stat4:
                    explicit_percentage = (metadata.get('explicit_words_count', 0) / 
                                         max(metadata.get('analyzed_words', 1), 1)) * 100
                    st.metric("% Explícitas", f"{explicit_percentage:.1f}%")
        
        else:
            st.warning("No se pudieron analizar las palabras individuales.")
    
    else:
        st.error("❌ Error al realizar el análisis detallado. Verifica que la API esté funcionando.")

def highlight_explicit_words(text: str, words_analysis: list) -> str:
    """
    Resaltar palabras explícitas en el texto
    
    Args:
        text: Texto original
        words_analysis: Lista de análisis de palabras
        
    Returns:
        Texto con palabras resaltadas en HTML
    """
    # Crear diccionario de palabras explícitas
    explicit_words = {
        word_info['word_cleaned'].lower(): word_info 
        for word_info in words_analysis 
        if word_info['is_explicit']
    }
    
    # Procesar palabra por palabra
    words = text.split()
    highlighted_words = []
    
    for word in words:
        word_clean = word.lower().strip('.,!?";:()[]{}')
        
        if word_clean in explicit_words:
            score = explicit_words[word_clean]['explicit_score']
            highlighted_words.append(
                f'<span class="explicit-word" title="Score: {score:.3f}">{word}</span>'
            )
        else:
            highlighted_words.append(word)
    
    return ' '.join(highlighted_words)

def show_examples():
    """Mostrar ejemplos de uso"""
    st.markdown("---")
    st.markdown("### 💡 Ejemplos de Uso")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ Contenido Limpio")
        st.code("""
I love you more than words can say
You make me happy every day
Dancing under stars so bright
Everything will be alright
        """)
        
        if st.button("🔬 Analizar Ejemplo Limpio"):
            example_clean = "I love you more than words can say. You make me happy every day. Dancing under stars so bright. Everything will be alright."
            perform_basic_analysis(example_clean, "Example Clean Song", "Test Artist")
    
    with col2:
        st.markdown("#### ⚠️ Contenido Potencialmente Explícito")
        st.code("""
[Ejemplo censurado por políticas de contenido]
        """)
        
        st.info("ℹ️ Usa tus propias letras para probar el análisis de contenido explícito")
    
    st.markdown("---")
    st.markdown("### 📝 Consejos para Mejores Resultados")
    
    tips_col1, tips_col2 = st.columns(2)
    
    with tips_col1:
        st.markdown("""
        **✅ Mejores Prácticas:**
        - Incluye letras completas
        - Mantén la estructura original
        - Incluye título y artista si los conoces
        - Usa texto en inglés para mejores resultados
        """)
    
    with tips_col2:
        st.markdown("""
        **⚡ Tipos de Análisis:**
        - **Básico**: Predicción rápida (explícito/limpio)
        - **Detallado**: Análisis palabra por palabra
        - **Resaltado**: Visualización de palabras problemáticas
        """)
