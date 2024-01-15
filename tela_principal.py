import streamlit as st
import time as time
import datetime as datetime
from streamlit_option_menu import option_menu
from filtro import Filtros


class TelaPrincipal:
    def __init__(self):
        self.filtro = Filtros()
        
    def sidebar(self):       
        varSideBar = st.sidebar.selectbox(
            "Selecione o modal de Transporte:", ('Página Inicial', 'Lançamento Vendas', 'Lançamento Compras', 'Funcionários'))
        
        self.varDataInicial()
        self.varDataFinal()

        if varSideBar == 'Página Inicial':
            pass
        elif varSideBar == 'Lançamento Vendas':
            pass
        elif varSideBar == 'Funcionários':
            pass

        with st.sidebar:
            varClientes = st.radio(
                'Selecione o Cliente',
                ('Iphone', 'Samsung', 'LG'))
            
            # varPeriodo = st.multiselect(
            #     'Selecione o Período',
            #     ('Almoço', 'Jantar'))
            self.varPerido()
            
            varParcela = st.slider(
                'Quantas parcelas deseja: ', 0, 60, 20)
    
    def varPerido(self):
        self.filtro.varPeriodo = st.multiselect(
                'Selecione o Período',
                ('Almoço', 'Jantar'))

    def varDataInicial(self):
        # datas que inicia o sistema
        tempo = time.time()
        tempo_local = time.localtime(tempo)
        with st.sidebar:
            self.filtro.data_inicial = st.date_input(
                'Data inicial', 
                datetime.date(tempo_local[0], tempo_local[1], 1), format='DD/MM/YYYY') 

    def varDataFinal(self):
        with st.sidebar:
            self.filtro.data_final = st.date_input(
                'Data final', 
                datetime.date.today(), format='DD/MM/YYYY')
            
    def home(self):
        # Sistema
        # st.title('Restaurante Fictício')
        st.header('Restaurante Fictício')
        st.write('---------')
        
        # menu de navegação - é possivel colocar dentro do sideBar
        selected = option_menu(
        menu_title = 'Painel de Navegação',
        menu_icon = 'cast', # icone do titulo
        options = ['Vendas', 'Compra e Pagamento', 'Pessoas', 'Fechamento'],
        # link para consultar os nomes dos icones https://icons.getbootstrap.com/
        icons = ['receipt', 'wallet2', 'grid', 'bar-chart'],    # bell
        default_index = 0,
        orientation='horizontal')
        
        if selected == 'Vendas':
            self.navegacao_vendas()
        elif selected == 'Pagamentos':
            self.navegacao_compras()
        elif selected == 'Pessoas':
            pass
        else:
            pass