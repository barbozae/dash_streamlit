import streamlit as st
import requests
from datetime import datetime

class Noticia:
    # Função para buscar notícias de restaurantes usando a API News API
    @staticmethod
    def get_noticias():
        api_key = "68b226a1179b48a7ac5bb607b0ff0af0"
        url = f"https://newsapi.org/v2/everything?q='comida japonesa'&sortBy=publishedAt&language=pt&apiKey={api_key}"
        response = requests.get(url)
        data = response.json()
        if "articles" in data:  # Verifica se há artigos na resposta
            return data["articles"][:3]  # Retorna apenas os dois primeiros artigos
        else:
            return None

    # Função para exibir as notícias na interface Streamlit
    @staticmethod
    def show_news(articles):
        st.markdown('')
        st.markdown('---')
        # hashtag para tamanho da letra, * para deixar italico
        st.markdown('''### *:red[Últimas notícias] :red[..] :red[.]*''')
        st.write('')
        for article in articles:
            if 'urlToImage' in article and article['urlToImage']:  # Verifica se a imagem existe
                st.image(article['urlToImage'], caption=article['title'], width=270)
            st.markdown("##### " + article["description"])
            st.write("Fonte:", article["source"]["name"])
            # st.write("Publicado em:", article["publishedAt"])
            published_date = datetime.strptime(article["publishedAt"], '%Y-%m-%dT%H:%M:%SZ')  # Converte para datetime
            formatted_date = published_date.strftime('%d/%m/%Y')  # Formata como dia/mês/ano
            st.markdown(f"Publicado em: {formatted_date}")  # Mostra a data formatada
            st.write("[Leia mais](" + article["url"] + ")")
            st.write("---")

def main():
    st.title("Notícias de Restaurantes")
    st.write("Aqui estão as últimas notícias.")
    
    # Buscar e exibir notícias
    articles = Noticia.get_noticias()  # Use o método estático diretamente
    if articles:
        Noticia.show_news(articles)  # Use o método estático diretamente
    else:
        st.write("Não foi possível carregar as notícias. Tente novamente mais tarde.")

if __name__ == "__main__":
    main()

