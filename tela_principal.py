import streamlit as st
import time as time
import datetime as datetime
from streamlit_option_menu import option_menu
from filtro import Filtros
from conexao import Conexao
from noticias import Noticia
from exportacao import Exportacao
import pandas as pd


consulta = Conexao.conecta_bd()
df_compras = consulta[1]
fornecedor = consulta[2]
grupo_produto = consulta[3]
classificacao = consulta[4]
numero_boleto = consulta[5]
produto = consulta[6]
df_cadastro_funcionarios = consulta[8]
nome_funcionario = consulta[9]

class TelaPrincipal:
    def __init__(self):
        self.filtro = Filtros()

    # FILTROS DATA
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
            
    # FILTROS VENDAS
    def varPeriodo(self):
        self.filtro.varPeriodo = st.multiselect(
                'Selecione o Período',
                ('Almoço', 'Jantar'),
                placeholder='Escolha o período')

    # FILTROS COMPRAS
    def varFornecedor(self):
        self.filtro.varFornecedor = st.multiselect(           
            'Selecione o Fornecedor', 
            fornecedor,
            placeholder='Escolha fornecedor')
        
    def varClassificacao(self):
        self.filtro.varClassificacao = st.multiselect(
            'Selecione a Classificação:',
            classificacao,
            placeholder='Escolha uma opção')

    def varGrupoProduto(self):
        self.filtro.varGrupoProduto = st.multiselect(
            'Selecione o Grupo:',
            grupo_produto,
            placeholder='Escolha um grupo')
        
    def varProduto(self):
        # produto_sem_none = [p for p in produto if p is not None]
        self.filtro.varProduto = st.multiselect(
            'Selecione o Produto:',
            produto,
            placeholder='Escolha o produto')
        
    def varNumeroBoleto(self):
        self.filtro.varNumeroBoleto = st.multiselect(
            'Seleciona número do boleto',
            numero_boleto,
            placeholder='Digite número boleto')

    def varFormaPagamento(self):
        # Exclua os valores em branco da coluna 'forma_pagamento'
        forma_pagamento = df_compras.dropna(subset=['forma_pagamento'])

        self.filtro.varFormaPagamento = st.multiselect(
            'Selecione forma de pagamento',
            forma_pagamento['forma_pagamento'].unique()
        )

    def varIDCompra(self):
        self.filtro.varIDCompra = st.multiselect(
            'Selecione ID',
            df_compras['ID'],
            placeholder='Digite número ID')
    
    # FILTROS PESSOAS
    def varNomeFunc(self):
        self.filtro.varNomeFunc = st.multiselect(
            'Nome Funcionário',
            df_cadastro_funcionarios['nome'].unique(),
            placeholder='Selecione Funcionários'
        )
    
    def varCargo(self):
        self.filtro.varCargo = st.multiselect(
            'Cargo',
            df_cadastro_funcionarios['cargo'].unique(),
            default=[]
,            placeholder='Selecione cargo'
        )

    def varSetor(self):
        self.filtro.varSetor = st.multiselect(
            'Setor', 
            df_cadastro_funcionarios['setor'].unique(),
            default=[],
            placeholder='Selecione setor'
        )

    def varDataContratacao(self):
        data = df_cadastro_funcionarios['data_contratacao'] = pd.to_datetime(df_cadastro_funcionarios['data_contratacao'], errors='coerce')
        
        # dropna() eu dropei as linhas nulas    
        data = data.dropna().dt.strftime('%d/%m/%Y').unique()
        self.filtro.varDataContratacao = st.multiselect(
            'Data de Contratação',
            data,
            placeholder='Selecione data contratação'
        )


    # SIDERBAR
    def sidebar_vendas(self):
        with st.sidebar:
            # st.image('logo.jpg', width=None)
            self.varDataInicial()
            self.varDataFinal()
            self.varPeriodo()

            Exportacao.download_vendas(self)
            # Chama o método estático para obter as notícias
            articles = Noticia.get_noticias()
            if articles:
                # Exibe as notícias chamando o método estático para mostrar as notícias
                Noticia.show_news(articles)
            else:
                st.write("Não foi possível carregar as notícias. Tente novamente mais tarde.")

    def sidebar_compras(self):
        with st.sidebar:
            # st.image('logo.jpg')
            self.varDataInicial()
            self.varDataFinal()
            self.varIDCompra()
            self.varFornecedor()
            self.varClassificacao()
            self.varGrupoProduto()
            self.varProduto()
            self.varNumeroBoleto()
            self.varFormaPagamento()
            Exportacao.download_compras(self)
    
    def sidebar_pessoas(self):
        with st.sidebar:
            # st.image('logo.jpg')
            self.varDataInicial()
            self.varDataFinal()
            self.varNomeFunc()
            self.varCargo()
            self.varSetor()
            self.varDataContratacao()
            st.write('---')
            with st.expander(label='Exportar Tabelas', expanded=False):
                Exportacao.download_cadastro(self)
                Exportacao.download_admissao(self)
                Exportacao.download_pg_func(self)

    def sidebar_fechamento(self):
        with st.sidebar:
            # st.image('logo.jpg', width=None)
            self.varDataInicial()
            self.varDataFinal()

    def home(self):
        # Use st.markdown() para adicionar um cabeçalho personalizado com HTML e CSS
        st.markdown(
            f'<h2 style="color:#FF0000;">Vesão Demonstração</h2>',
            unsafe_allow_html=True)
        
        # menu de navegação - é possivel colocar dentro do sideBar
        self.selected = option_menu(
        menu_title = 'Painel de Navegação',
        menu_icon = 'cast', # icone do titulo
        options = ['Vendas', 'Compras', 'Pessoas', 'Fechamento'],
        # link para consultar os nomes dos icones https://icons.getbootstrap.com/
        icons = ['receipt', 'wallet2', 'people-fill', 'bar-chart'],    # bell, grid
        default_index = 0,
        orientation='horizontal')
        
        if self.selected == 'Vendas':
            self.sidebar_vendas()
            self.navegacao_vendas()
        elif self.selected == 'Compras':
            self.sidebar_compras()
            self.navegacao_compras()
        elif self.selected == 'Pessoas':
            self.sidebar_pessoas()
            self.navegacao_funcionarios()
        else:
            self.sidebar_fechamento()
            tab1, tab2, tab3, tab4 = st.tabs(['Resumo', 'Análise Vendas', 'Análise Compras', 'Análise Funcionários'])
            with tab1:
                st.markdown('Resumo das Vendas')
                self.cards_resumo_vendas()
                st.write('---')
                st.markdown('Resumo das Compras')
                self.cards_resumo_compras()
                st.write('---')
                st.markdown('Resumo da Mão de Obra')
                self.card_resumo_Fuc()
            with tab2:
                self.tableau_vendas()
            with tab3:
                self.tableau_compras()
            with tab4:
                self.tableau_pg_funcionario()