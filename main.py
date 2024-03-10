import streamlit as st
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
from streamlit_option_menu import option_menu
import time as time
import datetime as datetime
from conexao import Conexao
from filtro import Filtros
from tela_principal import TelaPrincipal
from vendas import Vendas
from compras import Compras
from funcionarios import FuncNavegacao, FuncCadastro, FuncAdmissao, FuncPagamento, FuncRescisao, FuncResumo


# class Aplication(Conexao, TelaPrincipal, Vendas, Compras, FuncNavegacao, FuncCadastro, FuncAdmissao, FuncPagamento, FuncRescisao): 
#     def configurar_page():
#     page_configured = False

#     @classmethod
#     def configure_page(cls):
#         if not cls.page_configured:
#             st.set_page_config(
#                 page_title="Restaurante Fictício",
#                 page_icon="🍣",
#                 layout='wide',
#                 initial_sidebar_state='collapsed'
#                 # menu_items={
#                 # 'Get Help': "http://www.google.com.br",
#                 # 'Report a Bug': "edsonbarboza2006@hotmail.com",
#                 # 'About': "# Esse aplicativo foi desenvolvido por Edson Barboza ..."
#                 # }
#             )  
#             cls.page_configured = True
#         pass
    
#     def login():
#         names = ['Edson Barboza', 'Matheus Barboza', 'Daniela Bonopera']
        # usernames = ['barbozae', 'barbozam', 'bonoperad']
        
        # file_path = Path(__file__).parent / 'hashed_pw.pkl'
        # with file_path.open('rb') as file:
        #     hashed_passwords = pickle.load(file)

        # authenticator = stauth.Authenticate(names, usernames, hashed_passwords, 'main', cookie_expiry_days=30)
        
        # name, authenticator_status, username = authenticator.login('Login', 'main')

        # if authenticator_status == False:
        #     st.error('Usuário ou senha esta incorreto')

        # if authenticator_status == None:
        #     st.warning('Por favor faça login utilizando usuário e senha')

        # if authenticator_status:



# # Configura a página do Streamlit
# st.set_page_config(
#     page_title="Restaurante Fictício",
#     page_icon="🍣",
#     layout='wide',
#     initial_sidebar_state='collapsed')
# with st.sidebar:
#     # self.varDataInicial()
#     # self.varDataFinal()
#     varClientes = st.radio(
#         'Selecione o Cliente',
#         ('Iphone', 'Samsung', 'LG'))
#     varClientes

class Aplication(Conexao, TelaPrincipal, Vendas, Compras, FuncNavegacao, FuncCadastro, FuncAdmissao, FuncPagamento, FuncRescisao, FuncResumo):
    def __init__(self):
        self.filtro = Filtros()
        # self.page_configured = False
        # self.authenticator_status = None
        # self.name = None
        # self.username = None

        # self.configurar_page()
        # self.sidebar()
        self.home()
        # self.login()

    # def configurar_page(self):
    #     if not self.page_configured:
    #         st.set_page_config(
    #             page_title="Restaurante Fictício",
    #             page_icon="🍣",
    #             layout='wide',
    #             initial_sidebar_state='collapsed'
    #         )
    #         self.page_configured = True

    # def login(self):
    #     names = ['Edson Barboza', 'Matheus Barboza', 'Daniela Bonopera']
    #     usernames = ['barbozae', 'barbozam', 'bonoperad']

    #     file_path = Path(__file__).parent / 'hashed_pw.pkl'
    #     with file_path.open('rb') as file:
    #         hashed_passwords = pickle.load(file)

    #     authenticator = stauth.Authenticate(names, usernames, hashed_passwords, 'main', cookie_expiry_days=30)

    #     self.name, self.authenticator_status, self.username = authenticator.login('Login', 'main')

    #     if self.authenticator_status == False:
    #         st.error('Usuário ou senha está incorreto')

    #     if self.authenticator_status == None:
    #         st.warning('Por favor faça login utilizando usuário e senha')

if __name__ == "__main__":
    Aplication()