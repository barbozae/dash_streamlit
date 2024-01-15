import streamlit as st
# import streamlit_authenticator as stauth DESINSTALAR
from streamlit_option_menu import option_menu
import time as time
import datetime as datetime
from conexao import Conexao
from filtro import Filtros
from tela_principal import TelaPrincipal
from vendas import Vendas
from compras import Compras


class Aplication(Conexao, TelaPrincipal, Vendas, Compras): 
    # page_configured = False

    # @classmethod
    # def configure_page(cls):
    #     if not cls.page_configured:
    #         st.set_page_config(
    #             page_title="Restaurante Fictício",
    #             page_icon="🍣",
    #             layout='wide',
    #             initial_sidebar_state='collapsed'
    #             # menu_items={
    #             # 'Get Help': "http://www.google.com.br",
    #             # 'Report a Bug': "edsonbarboza2006@hotmail.com",
    #             # 'About': "# Esse aplicativo foi desenvolvido por Edson Barboza ..."
    #             # }
    #         )  
    #         cls.page_configured = True


    def __init__(self):
        # Aplication.configure_page()
        self.filtro = Filtros()
        self.sidebar()
        self.home()

    @staticmethod
    def page_conf(self):
        st.set_page_config(
        page_title="Restaurante Ficticio",
        page_icon="🍣", # 🍣 ❄ 🥢 
        layout='wide', # ou centered
        initial_sidebar_state='collapsed') # auto, expanded ou collapsed
        # menu_items={
        #     'Get Help': 'http//www.google.com.br',
        #     'Report a Bug': 'http//meuoutrosite.com.br',
        #     'About': 'Esse curso foi desenvolvido por Edson Barboza ...'
        #     }  

if __name__ == "__main__":
    Aplication()


    # with st.spinner('Carregando...'):
    #     time.sleep(2)
    #     st.success('Well Done!')
            
    #     st.caption("""Elaborado por Edson Barboza para contato 11-9696-51094""")