import streamlit as st
from millify import millify
from st_aggrid import GridOptionsBuilder
gb = GridOptionsBuilder()
from pygwalker.api.streamlit import StreamlitRenderer
from sqlalchemy import insert, Table, MetaData, Column, Integer, String, DateTime, Float
import altair as alt
import pandas as pd
import numpy as np
from datetime import datetime
import calendar
import time
from filtro import Filtros
from conexao import Conexao
from io import BytesIO
import os


class Vendas: 
    def __init__(self) -> None:
        self.filtro = Filtros()

    def navegacao_vendas(self):            
        tab1, tab2 = st.tabs(["Resumo", "Lançamento"])
        with tab1:
            self.cards_resumo_vendas()
            self.caixas_expansivas_vendas()
        with tab2:
            with st.expander('Lançamento Vendas', expanded=True):
                self.widget_vendas()
            with st.expander('Edição Vendas', expanded=False):
                self.lancamento_vendas_table()

    def cards_resumo_vendas(self):
        self.dataframe_vendas()

        # Cards das vendas
        # a função millify serve para abreviar o valor $8.000 para $8k
        col1, col2, col3, col4 = st.columns(4)
        col1.metric('Credito', '${}'.format(millify(self.credito)), '{:.4}%'.format(self.credito /self.total_vendas * 100))
        col2.metric('Débito', '${}'.format(millify(self.debito)), '{:.4}%'.format(self.debito / self.total_vendas * 100))
        col3.metric('Benefício', '${}'.format(millify(self.outros_cartoes)), '{:.4}%'.format(self.outros_cartoes / self.total_vendas * 100), 
                    help='Cartões: Hiper - American Express - Alelo, Sodexo - Vale Refeição - Ticket Rest - DinersClub')
        col4.metric('Dinheiro', '${}'.format(millify(self.dinheiro)), '{:.4}%'.format(self.dinheiro / self.total_vendas * 100))
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric('Pix', '${}'.format(millify(self.pix)), '{:.4}%'.format(self.pix / self.total_vendas * 100))
        col2.metric('Total Vendas', '${:,.2f}'.format(round(self.total_vendas, 2)), help='Incluir a data do filtro')
        col3.metric('Rodízio', self.rodizio)
        col4.metric('*Ticket Médio*', '${:.2f}'.format(self.ticket_medio))

        col1, col2 = st.columns(2)
        # col1.metric('Lucro', '${:,.2f}'.format(self.lucro), help='Fundamental conhecimento sobre os parametros de cálculo')
        col1.metric('Fundo de Caixa', '${:,.2f}'.format(self.fundo_caixa))

    def dataframe_vendas(self):
        consulta = Conexao.conecta_bd()
        print('Conectado ao banco, dataframe_vendas')
        df_vendas = consulta[0]

        self.df_vendas = df_vendas
        # Filtrando data
        data_inicial = str(self.filtro.data_inicial)
        data_final = str(self.filtro.data_final)
        self.df_vendas['data_venda'] = pd.to_datetime(self.df_vendas['data_venda'], format='%Y-%m-%d')
        
        filtro_data = (self.df_vendas['data_venda'] >= data_inicial) & (self.df_vendas['data_venda'] <= data_final)

        # filtrando periodo
        # Verificar se a lista 'self.filtro.varPeriodo' está vazia
        if self.filtro.varPeriodo:
            filtro_periodo = self.df_vendas['periodo'].isin(self.filtro.varPeriodo)
        else:
            filtro_periodo = pd.Series([True] * len(self.df_vendas)) # se a lista estiver vazia, considera todos os valores como verdadeiros  

        # aplicando os filtros data e periodo
        self.valores_vendas = self.df_vendas[filtro_data & filtro_periodo]

        # Convertendo a coluna 'coluna_string' para números
        self.valores_vendas.loc[:, 'qtd_rodizio'] = pd.to_numeric(self.valores_vendas['qtd_rodizio'], errors='coerce')

        # Converter as colunas para o tipo de dados numérico, tratando valores não numéricos como NaN
        self.valores_vendas.loc[:, 'debito_mastercard'] = pd.to_numeric(self.valores_vendas['debito_mastercard'], errors='coerce')
        self.valores_vendas.loc[:, 'debito_visa'] = pd.to_numeric(self.valores_vendas['debito_visa'], errors='coerce')
        self.valores_vendas.loc[:, 'debito_elo'] = pd.to_numeric(self.valores_vendas['debito_elo'], errors='coerce')
        self.valores_vendas.loc[:, 'credito_mastercard'] = pd.to_numeric(self.valores_vendas['credito_mastercard'], errors='coerce')
        self.valores_vendas.loc[:, 'credito_visa'] = pd.to_numeric(self.valores_vendas['credito_visa'], errors='coerce')
        self.valores_vendas.loc[:, 'credito_elo'] = pd.to_numeric(self.valores_vendas['credito_elo'], errors='coerce')
        self.valores_vendas.loc[:, 'alelo'] = pd.to_numeric(self.valores_vendas['alelo'], errors='coerce')
        self.valores_vendas.loc[:, 'american_express'] = pd.to_numeric(self.valores_vendas['american_express'], errors='coerce')
        self.valores_vendas.loc[:, 'hiper'] = pd.to_numeric(self.valores_vendas['hiper'], errors='coerce')
        self.valores_vendas.loc[:, 'sodexo'] = pd.to_numeric(self.valores_vendas['sodexo'], errors='coerce')
        self.valores_vendas.loc[:, 'ticket_rest'] = pd.to_numeric(self.valores_vendas['ticket_rest'], errors='coerce')
        self.valores_vendas.loc[:, 'vale_refeicao'] = pd.to_numeric(self.valores_vendas['vale_refeicao'], errors='coerce')
        self.valores_vendas.loc[:, 'dinersclub'] = pd.to_numeric(self.valores_vendas['dinersclub'], errors='coerce')
        self.valores_vendas.loc[:, 'socio'] = pd.to_numeric(self.valores_vendas['socio'], errors='coerce')

        # Converter a coluna 'data_venda' para o tipo datetime
        self.valores_vendas.loc[:, 'data_venda'] = pd.to_datetime(self.valores_vendas['data_venda'])

        self.df_vendas_valores = self.valores_vendas.drop(['data_venda', 'periodo', 'dt_atualizado', 'ID'], axis=1)
        self.array_vendas = np.array(self.df_vendas_valores)

        # substiturir valores vazios por nan e assim converter valores para float
        self.array_vendas[self.array_vendas == ''] = 0 #'nan'
        self.array_vendas = self.array_vendas.astype(float)
        
        # Somando todas as linhas por colunas
        # somando cada coluna da array -> exemplo [279, 1548, 1514, 4848...] -> cada valor é o total de cada coluna
        self.total_colunas = np.nansum(self.array_vendas, axis=0)
        
        self.dinheiro = self.total_colunas[0]
        self.pix = self.total_colunas[1]
        self.debito_martercard = self.total_colunas[2]
        self.debito_visa = self.total_colunas[3]
        self.debito_elo = self.total_colunas[4]
        self.credito_mastercard = self.total_colunas[5]
        self.credito_visa = self.total_colunas[6]
        self.credito_elo = self.total_colunas[7]
        self.hiper = self.total_colunas[8]
        self.american_express = self.total_colunas[9]
        self.alelo = self.total_colunas[10]
        self.sodexo = self.total_colunas[11]
        self.ticket_rest = self.total_colunas[12]
        self.vale_refeicao = self.total_colunas[13]
        self.dinersclub = self.total_colunas[14]
        self.rodizio = int(self.total_colunas[15])
        self.socio = self.total_colunas[16]

        self.debito = self.debito_martercard + self.debito_visa + self.debito_elo
        self.credito = self.credito_mastercard + self.credito_visa + self.credito_elo
        self.outros_cartoes = self.american_express + self.alelo + self.sodexo + self.ticket_rest + self.vale_refeicao + self.dinersclub + self.hiper
        self.total_vendas = self.dinheiro + self.pix + self.debito + self.credito + self.outros_cartoes
        self.ticket_medio = self.total_vendas / self.rodizio

        self.taxa = (self.debito * 0.0094) + (self.credito * 0.0299) + (self.alelo * 0.07) + (self.ticket_rest * 0.07) + ((self.sodexo + self.vale_refeicao) * 0.069)

        # dataframe pg_funcionario
        self.dataframe_pg_funcionario()
        df = self.valores_pg_func
        df['valor_pago'] = pd.to_numeric(df['valor_pago'])

        # dataframe contas pagas
        self.dataframe_pagamentos()

        # self.lucro = self.total_vendas - self.taxa - df['valor_pago'].sum() - self.valor_pagamentos[0]
        self.fundo_caixa = self.total_vendas * 0.001

    # estou levando essa tabela para tela_principal.py
    def get_valores_vendas(self):
        return self.valores_vendas

    def widget_vendas(self):
        # Forms pode ser declarado utilizando a sintaxe 'with'
        with st.form(key='lançar_vendas', clear_on_submit=True):
            # st.title = ('Lançamento de Vendas')
            col1, col2, col3, col4, col5, col6= st.columns(6)
            with col1:
                self.data_venda = st.date_input('Data', format='DD/MM/YYYY')
                self.periodo = st.selectbox('Período', ['Almoço', 'Jantar'], index=None, placeholder='')
                self.rodizio = st.number_input(label='Qtd Rodízio', value=int('1'), step=5, min_value=1, max_value=500)
            with col2:
                self.socio = st.number_input('Sócio', value=float(0.00), step=10.00, min_value=0.00, max_value=5000.00)
                self.dinheiro = st.number_input(label='Dinheiro', value=float('0.00'), step=10.00, min_value=0.00, max_value=25000.00)
                self.pix = st.number_input(label='Pix', value=float('0.00'), step=10.00, min_value=0.00, max_value=25000.00)
            with col3:
                self.debito_visa = st.number_input(label='Débito Visa', value=float('0.00'), step=10.00, min_value=0.00, max_value=25000.00)
                self.debito_mastercard = st.number_input(label='Débito Master', value=float('0.00'), step=10.00, min_value=0.00, max_value=25000.00)
                self.debito_elo = st.number_input(label='Débito Elo', value=float('0.00'), step=10.00, min_value=0.00, max_value=25000.00)
            with col4:
                self.credito_visa = st.number_input(label='Crédito Visa', value=float('0.00'), step=10.00, min_value=0.00, max_value=25000.00)
                self.credito_mastercard = st.number_input(label='Crédito Master', value=float('0.00'), step=10.00, min_value=0.00, max_value=25000.00)
                self.credito_elo = st.number_input(label='Crédito Elo', value=float('0.00'), step=10.00, min_value=0.00, max_value=25000.00)
            with col5:
                self.vale_refeicao = st.number_input(label='Vale Refeição', value=float('0.00'), step=10.00, min_value=0.00, max_value=25000.00)
                self.sodexo = st.number_input(label='Sodexo', value=float('0.00'), step=10.00, min_value=0.00, max_value=25000.00)
                self.alelo = st.number_input(label='Alelo', value=float('0.00'), step=10.00, min_value=0.00, max_value=25000.00)
            with col6:
                self.ticket_rest = st.number_input(label='Ticket Rest', value=float('0.00'), step=10.00, min_value=0.00, max_value=25000.00)
                self.american_express = st.number_input(label='American Express', value=float('0.00'), step=10.00, min_value=0.00, max_value=25000.00)
                self.dinersclub = st.number_input(label='DinersClub', value=float('0.00'), step=10.00, min_value=0.00, max_value=25000.00)
            
            submit_button = st.form_submit_button(label='Enviar')
        if submit_button:
            self.salvar_vendas()

    def salvar_vendas(self):
        if self.data_venda == '':
            st.error('A data da venda não foi preenchida!', icon="🚨")
        elif self.periodo == None:
            st.error('O período não foi preenchido!', icon="🚨")
        elif self.rodizio == '':
            st.error('O período não foi preenchido.', icon="🚨") #⚠
        else:
            dt_atualizo = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
            self.conecta_mysql()

            metadata = MetaData()
            vendas_table = Table('vendas', metadata,
                Column('ID', Integer, primary_key=True),
                Column('data_venda', DateTime),
                Column('periodo', String),
                Column('qtd_rodizio', Integer),
                Column('dinheiro', Float),
                Column('pix', Float),
                Column('debito_mastercard', Float),
                Column('debito_visa', Float),
                Column('debito_elo', Float),
                Column('credito_mastercard', Float),
                Column('credito_visa', Float),
                Column('credito_elo', Float),
                Column('american_express', Float),
                Column('alelo', Float),
                # Column('hiper', Float),
                Column('sodexo', Float),
                Column('ticket_rest', Float),
                Column('vale_refeicao', Float),
                Column('dinersclub', Float),
                Column('socio', Float),
                Column('dt_atualizado', DateTime)
            )

            # Definindo os valores para inserção
            valores = {
                'data_venda': self.data_venda,
                'periodo': self.periodo,
                'qtd_rodizio': int(self.rodizio),
                'dinheiro': float(self.dinheiro),
                'pix': float(self.pix),
                'debito_mastercard': float(self.debito_mastercard),
                'debito_visa': float(self.debito_visa),
                'debito_elo': float(self.debito_elo),
                'credito_mastercard': float(self.credito_mastercard),
                'credito_visa': float(self.credito_visa),
                'credito_elo': float(self.credito_elo),
                'american_express': float(self.american_express),
                'alelo': float(self.alelo),
                # 'hiper': float(self.hiper),
                'sodexo': float(self.sodexo),
                'ticket_rest': float(self.ticket_rest),    
                'vale_refeicao': float(self.vale_refeicao),
                'dinersclub': float(self.dinersclub),
                'socio': float(self.socio),
                'dt_atualizado': dt_atualizo
            }

            stmt = insert(vendas_table).values(valores)
            # Executando a instrução de INSERT
            self.session.execute(stmt)
            # Confirmar a transação
            self.session.commit()
            # Fechando a sessão
            self.session.close()

            # precisei criar uma mensagem vazia para depois deixa-la vazia novamente depois de utiliza-la
            msg_lancamento = st.empty()
            msg_lancamento.success("Lançamento Realizado com Sucesso!")
            time.sleep(5)
            msg_lancamento.empty()
            # fazer com que apos 5 segundos a mensagem de sucesso apague PENDENTE

    def lancamento_vendas_table(self):
        df = self.valores_vendas
        df.loc[:, 'data_venda'] = pd.to_datetime(df['data_venda'], errors='coerce')
        
        col1, col2, col3, col4 = st.columns([1.5, 1.5, 1, 3])  
        with col1:
            filtro_ID_vendas = st.multiselect('Selecione ID para edição', df['ID'], placeholder='Escolha um ID')
            if filtro_ID_vendas:
                df = df[df['ID'].isin(filtro_ID_vendas)]
        with col2:
            filtro_datas = df['data_venda'].dt.strftime('%d/%m/%Y').unique()
            filtro_data_vendas = st.selectbox('Filtrar data', filtro_datas, 
                                                            index=None, 
                                                            placeholder='Escolha uma data') if len(filtro_datas) > 0 else None
            if filtro_data_vendas:
                df = df[df['data_venda'] == filtro_data_vendas]

        # pegando o nome das colunas
        coluna_vendas = self.valores_vendas.columns.tolist()

        # alterei nome das colunas para o widget
        coluna_vendas = ['Data Venda', 'Dinheiro', 'Pix', 'Debito Master', 'Debito Visa', 'Debito Elo', 'Credito Master', 
                            'Credito Visa', 'Credito Elo', 'Hiper', 'American Express', 'Alelo', 'Sodexo', 'Ticket Rest', 
                            'Vale Refeição', 'DinersClub', 'Rodízio', 'Sócio', 'Período', 'Data Atualização', 'ID']
        # witdget
        excluir_coluna = st.multiselect('Excluir coluna', coluna_vendas, placeholder='Selecione a coluna', key='excluir_coluna_vendas_edit')
        
        # necessário voltar para o nome da coluna original, para tabela a seguir
        nomes_alterados = {
            'Data Venda': 'data_venda', 'Dinheiro': 'dinheiro', 'Pix': 'pix', 'Debito Master': 'debito_mastercard',
            'Debito Visa': 'debito_visa', 'Debito Elo': 'debito_elo', 'Credito Master': 'credito_mastercard',
            'Credito Visa': 'credito_visa', 'Credito Elo': 'credito_elo', 'Hiper': 'hiper', 'American Express': 'american_express',
            'Alelo': 'alelo', 'Sodexo': 'sodexo', 'Ticket Rest': 'ticket_rest', 'Vale Refeição': 'vale_refeicao',
            'DinersClub': 'dinersclub', 'Rodízio': 'qtd_rodizio', 'Sócio': 'socio', 'Período': 'periodo', 
            'Data Atualização': 'dt_atualizado', 'ID': 'ID'
                }

        # excluir as colunas selecionadas no widget
        excluir_coluna = [nomes_alterados[coluna] if coluna in nomes_alterados else coluna for coluna in excluir_coluna]

        df = self.valores_vendas.drop(excluir_coluna, axis=1)
        if len(filtro_ID_vendas) > 0:  # Se houver IDs filtrados, aplique o filtro
            df = df[df['ID'].isin(filtro_ID_vendas)]
        
        if filtro_data_vendas:
            df = df[df['data_venda'] == filtro_data_vendas]

        # Bloquear algumas colunas da edição
        colunas_bloqueadas = {
        'dt_atualizado': {'editable': False},
        'ID': {'editable': False}
        }
        
        colunas_formatada = {
            'ID': st.column_config.NumberColumn('ID', format='%d'),
            'data_venda': st.column_config.DateColumn('Data Venda', format='DD/MM/YYYY'),   
            'periodo': st.column_config.SelectboxColumn('Período', options=['Almoço', 'Jantar'], required=True),
            'qtd_rodizio': st.column_config.NumberColumn('Rodízio', format='%d', min_value=1, max_value=500),
            'dinheiro': st.column_config.NumberColumn('Dinheiro', format='$%f', min_value=0, max_value=25000),
            'pix': st.column_config.NumberColumn('Pix', format='$%f', min_value=0, max_value=25000),
            'debito_mastercard': st.column_config.NumberColumn('Debito Master', format='$%f', min_value=0, max_value=25000),
            'debito_visa': st.column_config.NumberColumn('Debito Visa', format='$%f', min_value=0, max_value=25000),
            'debito_elo': st.column_config.NumberColumn('Debito Elo', format='$%f', min_value=0, max_value=25000),
            'credito_mastercard': st.column_config.NumberColumn('Credito Master', format='$%f', min_value=0, max_value=25000),
            'credito_visa': st.column_config.NumberColumn('Credito Visa', format='$%f', min_value=0, max_value=25000),
            'credito_elo': st.column_config.NumberColumn('Credito Elo', format='$%f', min_value=0, max_value=25000),
            'alelo': st.column_config.NumberColumn('Alelo', format='$%f', min_value=0, max_value=25000),
            'hiper': st.column_config.NumberColumn('Hiper', format='$%f', min_value=0, max_value=25000),
            'american_express': st.column_config.NumberColumn('American Express', format='$%f', min_value=0, max_value=25000),
            'sodexo': st.column_config.NumberColumn('Sodexo', format='$%f', min_value=0, max_value=25000),
            'ticket_rest': st.column_config.NumberColumn('Ticket Rest', format='$%f', min_value=0, max_value=25000),
            'vale_refeicao': st.column_config.NumberColumn('Vale Refeição', format='$%f', min_value=0, max_value=25000),
            'dinersclub': st.column_config.NumberColumn('DinersClub', format='$%f', min_value=0, max_value=25000),
            'socio': st.column_config.NumberColumn('Sócio', format='$%f', min_value=0, max_value=2000),
            'dt_atualizado': st.column_config.DatetimeColumn('Atualizado', format='DD/MM/YYYY- h:mm A'),
        }
        # Aplicando a formatação apenas nas colunas que ainda existem
        colunas_formatadas_existem = {key: value for key, value in colunas_formatada.items() if key in df.columns}

        # num_rows = 'dynamic' é um parametro para habilitar a inclusão de linhas
        # disabled = deixa as colunas ineditavel
        tabela_editavel = st.data_editor(df, 
                                            disabled=colunas_bloqueadas, 
                                            column_config=colunas_formatadas_existem, 
                                            column_order=['ID', 'data_venda', 'periodo', 'qtd_rodizio', 'dinheiro', 'pix', 
                                                            'debito_mastercard', 'debito_visa', 'debito_elo', 'credito_mastercard', 
                                                            'credito_visa', 'credito_elo', 'alelo', 'hiper', 'american_express', 
                                                            'sodexo', 'ticket_rest', 'vale_refeicao', 'dinersclub', 'socio',
                                                            'dt_atualizado'], 
                                            hide_index=True)
        
        # Função para atualizar dados no banco de dados
        def update_data_vendas(df):
            df = df.drop(['ano', 'mes'], axis=1)

            # atualização acontece apenas nas colunas disponivel
            self.conecta_mysql2()
            cursor = self.conn.cursor()
            data_atual = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
            
            # Obter as colunas disponíveis
            colunas_disponiveis = df.columns.tolist()

            for index, row in df.iterrows():
                query = "UPDATE vendas SET "
                valores = []
                for coluna in colunas_disponiveis:
                    # Verificar se a coluna está presente no índice da linha atual
                    if coluna in row.index:
                        valor = row[coluna]
                        # Se o valor for uma string, adicione aspas simples ao redor dele
                        if isinstance(valor, str):
                            valor = f"'{valor}'"
                        # Se a coluna for uma coluna de data ou hora, formate-a corretamente
                        if 'data' in coluna or 'dt_atualizado' in coluna:
                            valor = f"STR_TO_DATE('{valor}', '%Y-%m-%d %H:%i:%s')"
                        valores.append(f"{coluna} = {valor}")
                # Adicionar a data_atual à lista de valores
                valores.append(f"dt_atualizado = STR_TO_DATE('{data_atual}', '%Y/%m/%d, %H:%i:%s')")
                # Construir a parte SET da query
                query += ', '.join(valores)
                # Adicionar a condição WHERE ID = {row['ID']}
                query += f" WHERE ID = {row['ID']}"
                try:
                    cursor.execute(query)
                except Exception as e:
                    print(f"Erro ao executar a query: {query}")
                    print(f"Erro detalhado: {e}")
                        
            self.conn.commit()
            cursor.close()
            self.conn.close()

        with col3:
            if st.button('Salvar Alterações'):
                if len(filtro_ID_vendas) > 0 or filtro_data_vendas is not None:
                    update_data_vendas(tabela_editavel)
                    with col4:
                        # precisei criar uma mensagem vazia para depois deixa-la vazia novamente depois de utiliza-la
                        msg_lancamento = st.empty()
                        msg_lancamento.success("Edição realizada com Sucesso!")
                        time.sleep(10)
                        msg_lancamento.empty()
                else:
                    with col4:
                        msg_lancamento = st.empty()
                        msg_lancamento.error('Selecione uma data ou ID que deseja editar!', icon="🚨")
                        time.sleep(10)
                        msg_lancamento.empty()

    def caixas_expansivas_vendas(self):
        # pegando a coluna data
        self.valores_vendas_np = np.array(self.valores_vendas)
        self.data_vendas = np.array([ts.strftime('%d/%m/%Y') for ts in self.valores_vendas_np[:, 0]])
        # somando total de valores para cada dia (coluna total de uma tabela)
        # somando todas as linhas da coluna 0 até a 14 -> o mesmo que ter uma coluna total de uma tabela
        # total de vendas desconsiderando consumo dos sócios
        self.array_total_vendas = np.nansum(self.array_vendas[:, 0:15], axis=1)

        with st.expander('Tabela das vendas'):
            # pegando o nome das colunas
            coluna_vendas = self.valores_vendas.columns.tolist()

            # alterei nome das colunas para o widget
            # não inclui a coluna Rodízio pois não posso excluir essa coluna devido o subset na configuração da tabela_vendas que me mostra a max do rodizio
            coluna_vendas = ['Data Venda', 'Dinheiro', 'Pix', 'Debito Master', 'Debito Visa', 'Debito Elo', 'Credito Master', 
                             'Credito Visa', 'Credito Elo', 'Hiper', 'American Express', 'Alelo', 'Sodexo', 'Ticket Rest', 
                             'Vale Refeição', 'DinersClub', 'Sócio', 'Período', 'Data Atualização', 'ID']
            # witdget
            excluir_coluna = st.multiselect('Excluir coluna', coluna_vendas, placeholder='Selecione a coluna')
            
            # necessário voltar para o nome da coluna original, para tabela a seguir
            nomes_alterados = {
                'Data Venda': 'data_venda', 'Dinheiro': 'dinheiro', 'Pix': 'pix', 'Debito Master': 'debito_mastercard', 'Debito Visa': 'debito_visa',
                'Debito Elo': 'debito_elo', 'Credito Master': 'credito_mastercard', 'Credito Visa': 'credito_visa', 'Credito Elo': 'credito_elo', 
                'Hiper': 'hiper', 'American Express': 'american_express', 'Alelo': 'alelo', 'Sodexo': 'sodexo', 'Ticket Rest': 'ticket_rest', 
                'Vale Refeição': 'vale_refeicao', 'DinersClub': 'dinersclub', 'Rodízio': 'qtd_rodizio', 'Sócio': 'socio', 'Período': 'periodo', 
                'Data Atualização': 'dt_atualizado', 'ID': 'ID'
                    }

            # excluir as colunas selecionadas no widget
            excluir_coluna = [nomes_alterados[coluna] if coluna in nomes_alterados else coluna for coluna in excluir_coluna]





            formas_pagamento = ['dinheiro', 'pix', 'debito_mastercard', 'debito_visa', 'debito_elo',
                                'credito_mastercard', 'credito_visa', 'credito_elo', 'alelo', 'american_express',
                                'sodexo', 'ticket_rest', 'vale_refeicao', 'hiper', 'dinersclub', 'socio']

            df = self.valores_vendas.copy()
            # Calcula a coluna de total
            df['total'] = df[formas_pagamento].sum(axis=1).round(2)

            df = df.drop(excluir_coluna, axis=1)






            # df = self.valores_vendas.drop(excluir_coluna, axis=1)

            # df['data_venda'] = pd.to_datetime(df['data_venda']).dt.strftime('%d/%m/%Y')

            colunas_formatada = {
            'ID': st.column_config.NumberColumn('ID', format='%d', min_value=1, max_value=500),
            'data_venda': st.column_config.DateColumn('Data Venda', format='DD/MM/YYYY'),
            'periodo': st.column_config.SelectboxColumn('Período', options=['Almoço', 'Jantar'], required=True),
            'qtd_rodizio': st.column_config.NumberColumn('Rodízio', format='%d', min_value=1, max_value=500),
            'dinheiro': st.column_config.NumberColumn('Dinheiro', format='$%f', min_value=0, max_value=25000),
            'pix': st.column_config.NumberColumn('Pix', format='$%f', min_value=0, max_value=25000),
            'debito_mastercard': st.column_config.NumberColumn('Debito Master', format='$%f', min_value=0, max_value=25000),
            'debito_visa': st.column_config.NumberColumn('Debito Visa', format='$%f', min_value=0, max_value=25000),
            'debito_elo': st.column_config.NumberColumn('Debito Elo', format='$%f', min_value=0, max_value=25000),
            'credito_mastercard': st.column_config.NumberColumn('Credito Master', format='$%f', min_value=0, max_value=25000),
            'credito_visa': st.column_config.NumberColumn('Credito Visa', format='$%f', min_value=0, max_value=25000),
            'credito_elo': st.column_config.NumberColumn('Credito Elo', format='$%f', min_value=0, max_value=25000),
            'alelo': st.column_config.NumberColumn('Alelo', format='$%f', min_value=0, max_value=25000),
            'hiper': st.column_config.NumberColumn('Hiper', format='$%f', min_value=0, max_value=25000),
            'american_express': st.column_config.NumberColumn('American Express', format='$%f', min_value=0, max_value=25000),
            'sodexo': st.column_config.NumberColumn('Sodexo', format='$%f', min_value=0, max_value=25000),
            'ticket_rest': st.column_config.NumberColumn('Ticket Rest', format='$%f', min_value=0, max_value=25000),
            'vale_refeicao': st.column_config.NumberColumn('Vale Refeição', format='$%f', min_value=0, max_value=25000),
            'dinersclub': st.column_config.NumberColumn('DinersClub', format='$%f', min_value=0, max_value=25000),
            'socio': st.column_config.NumberColumn('Sócio', format='$%f', min_value=0, max_value=2000),
            'total': st.column_config.NumberColumn('Total', format='$%f', min_value=0, max_value=2000),
            'dt_atualizado': st.column_config.DatetimeColumn('Atualizando', format='DD/MM/YYYY- h:mm A'),
            }

            # Aplicando a formatação apenas nas colunas que ainda existem
            colunas_formatadas_existem = {key: value for key, value in colunas_formatada.items() if key in df.columns}

            tabela_vendas = st.dataframe(df,
                                         hide_index=True,
                                         column_config=colunas_formatadas_existem,
                                         column_order=['ID', 'data_venda', 'periodo', 'qtd_rodizio', 'dinheiro', 'pix', 
                                                            'debito_mastercard', 'debito_visa', 'debito_elo', 'credito_mastercard', 
                                                            'credito_visa', 'credito_elo', 'alelo', 'hiper', 'american_express', 
                                                            'sodexo', 'ticket_rest', 'vale_refeicao', 'dinersclub', 'total', 'socio',
                                                            'dt_atualizado'])
            
        with st.expander('Gráfico das Vendas - Visão diária e por período'):
            # ([3,1]) -> essa informação é a proporção de 3 para 1 da coluna 1 para a coluna 2
            col1, col2 = st.columns([3,1])
            with col1:    
                # Converta a matriz em um DataFrame
                colunas = ['Data', 'Valor']
                grafico_vendas = np.column_stack((self.data_vendas, self.array_total_vendas))    
                df = pd.DataFrame(grafico_vendas, columns=colunas)

                # Convertendo a coluna de datas para o tipo datetime para que consiga ordenar o eixo x (data) do gráfico
                df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
                # Ordenando o DataFrame pela coluna de datas
                df = df.sort_values(by=['Data'])
                # deixando o ajuste do distanciamento das barras automatico
                if not df['Data'].empty:
                    largura_ideal = 950 / len(df['Data'])
                else:
                    largura_ideal = 950

                # Gráfico de barras - vendas
                graf_vendas = alt.Chart(df).mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10, size=largura_ideal).encode(
                        x = alt.X('Data:T', axis=alt.Axis(title='Data', format='%d/%m/%Y', labelAngle=-90)),
                        # x = 'Data:N', 
                        y = 'Valor:Q',
                        tooltip = ['Data', 'Valor']
                        ).properties(title= 'Vendas diária')
                
                # rotulos = graf_vendas.mark_text(dy= -6, size=17).encode(text='Valor')

                linha_media = alt.Chart(df).mark_rule(color='red').encode(
                    y='mean(Valor):Q')
                
                st.altair_chart(graf_vendas + linha_media, use_container_width=True)

            with col2:
                periodo = self.valores_vendas_np[:, 18]

                # Converta a matriz em um DataFrame
                coluna2 = ['Periodo', 'Valor']
                df_periodo = np.column_stack((periodo, self.array_total_vendas))
                grafico_pizza_venda = pd.DataFrame(df_periodo, columns=coluna2)
            
                grafico_pizza_venda = alt.Chart(grafico_pizza_venda).mark_arc(innerRadius=25, outerRadius=60).encode(
                    theta = alt.Theta(field='Valor', type='quantitative', stack=True),
                    color = alt.Color(field='Periodo', type='nominal') 
                ).properties(title= 'Gráfico por período')  #width=700, height=450, 
                st.altair_chart(grafico_pizza_venda, use_container_width=True)

        with st.expander('Gráfico do Ticket Médio'):
            # incuido coluna ticket medio
            # array_ticket_medio = np.column_stack((np.nansum(self.array_vendas[:, 0:15], axis=1) / self.array_vendas[:, 15]))

            array_ticket_medio = np.column_stack((self.array_vendas, (self.array_vendas[:, 0] + self.array_vendas[:, 1] + self.array_vendas[:, 2] + 
                                                    self.array_vendas[:, 3] + self.array_vendas[:, 4] + self.array_vendas[:, 5] + 
                                                    self.array_vendas[:, 6] + self.array_vendas[:, 7] + self.array_vendas[:, 8] + 
                                                    self.array_vendas[:, 9] + self.array_vendas[:, 10] + self.array_vendas[:, 11] +
                                                    self.array_vendas[:, 12] + self.array_vendas[:, 13] + self.array_vendas[:, 14]
                                                    ) / self.array_vendas[:, 15]))
            # convertendo a coluna ticket media para duas casas decimais
            self.ticket_medio = np.round(array_ticket_medio[:, 17:18], 2)
            
            colunas = ['Data', 'Valor']
            array_ticket_medio = np.column_stack((self.data_vendas, self.ticket_medio))
            df_ticket = pd.DataFrame(array_ticket_medio, columns=colunas)

            # Gráfico de barras - ticket médio
            graf_ticket_medio = alt.Chart(df_ticket).mark_line(strokeWidth=2, interpolate='basis').encode(
                    x = 'Data:N',
                    y = 'Valor:Q',
                    tooltip = ['Data', 'Valor']
                    ).properties(title= 'Ticket Médio')
            
            linha = alt.Chart(df_ticket).mark_rule(color='red').encode(
                    y='mean(Valor):Q')
            
            st.altair_chart(graf_ticket_medio + linha, use_container_width=True)

        with st.expander('Gráfico Mensal'):
            # df_ano_mes = self.df_vendas # esse df_vendas não tem filtro na data pega todos os meses
            df_ano_mes = self.valores_vendas

            # # df_ano_mes['data_venda'] = pd.to_datetime(df_ano_mes['data_venda'], format='%d/%m/%Y')
            df_ano_mes.loc[:, 'ano'] = df_ano_mes['data_venda'].dt.year
            df_ano_mes.loc[:, 'mes'] = df_ano_mes['data_venda'].dt.month
            df_ano_mes.loc[:, 'mes'] = df_ano_mes['data_venda'].dt.month.apply(lambda x: calendar.month_abbr[x])
            
            # Filtro do ano
            df_filtrado = df_ano_mes.loc[(df_ano_mes['data_venda'].dt.year == df_ano_mes['ano'])]
            df_ano_mes = df_filtrado.drop(['data_venda', 'socio', 'ID', 'periodo', 'qtd_rodizio', 'dt_atualizado', 'ano', 'mes'], axis=1)
            df_ano_mes = np.array(df_ano_mes)

            # garantir que array esta como string e assim poder aplicar replace
            df_ano_mes = df_ano_mes.astype(str)
            # substiturir valores vazios por nan e assim converter valores para float
            df_ano_mes[df_ano_mes == ''] = 0 #'nan'
            df_ano_mes = df_ano_mes.astype(float)
            
            data = np.array(df_filtrado['mes'])
            valor = np.nansum(df_ano_mes, axis=1)
            
            colunas = ['Meses', 'Valor']
            array_vendas_mes = np.column_stack((data, valor))
            df_vendas_mes = pd.DataFrame(array_vendas_mes, columns=colunas)

            # Defina a ordem dos meses em uma lista
            ordem_meses = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

            # Converta a coluna 'Meses' para um tipo categórico com a ordem especificada
            df_vendas_mes.loc[:, 'Meses'] = pd.Categorical(df_vendas_mes['Meses'], categories=ordem_meses, ordered=True)

            # Gráfico de barras - ticket médio
            graf_vendas_mes = alt.Chart(df_vendas_mes).mark_bar(
                    cornerRadiusTopLeft=10, cornerRadiusTopRight=10, color='red').encode(
                    x = alt.X('Meses:O', sort=ordem_meses),
                    y = 'sum(Valor):Q',
                    ).properties(title= 'Vendas Mensais')
            
            rotulos_valores = graf_vendas_mes.mark_text(
            align='left',
            baseline='middle',
            dx=-30,  # Ajuste horizontal para posicionar o rótulo
            dy=10,  # Ajuste vertical para posicionar o rótulo
            fontSize = 15,
            color='black    ',  # Cor do texto
             ).encode(
            text=alt.Text('sum(Valor):Q')  # Use a soma dos valores como texto
            )

            st.altair_chart(graf_vendas_mes + rotulos_valores, use_container_width=True)

    def tableau_vendas(self):
        pass
        # df = self.valores_vendas_30dias.drop(['ID', 'dt_atualizado'], axis=1)
        # df['data_venda'] = pd.to_datetime(df['data_venda'], format='%Y-%m-%d')

        # colunas = ['dinheiro', 'pix', 'debito_mastercard', 'debito_visa', 'debito_elo', 'credito_mastercard', 'credito_visa', 'socio',
        #             'credito_elo', 'hiper', 'american_express', 'alelo', 'sodexo', 'ticket_rest', 'vale_refeicao', 'dinersclub'] #, 'valor_total_30']
        
        # for item in colunas:
        #     df[item] = pd.to_numeric(df[item], errors='coerce')

        # df['Total débito'] = df[['debito_mastercard', 'debito_visa', 'debito_elo',]].sum(axis=1)
        # df['Total crédito'] = df[['credito_mastercard', 'credito_visa', 'credito_elo']].sum(axis=1)
        # df['Outros Cartões'] = df[['hiper', 'american_express', 'alelo', 'sodexo', 'ticket_rest', 'vale_refeicao', 'dinersclub']].sum(axis=1)
        # # df['Total'] = df[['dinheiro', 'pix', 'debito_mastercard', 'debito_visa', 'debito_elo', 'credito_mastercard', 'credito_visa', 
        # #                   'credito_elo', 'hiper', 'american_express', 'alelo', 'sodexo', 'ticket_rest', 'vale_refeicao', 'dinersclub']].sum(axis=1)
        # df = df.drop(['debito_mastercard', 'debito_visa', 'debito_elo', 'credito_mastercard', 'credito_visa', 'credito_elo', 
        #               'hiper', 'american_express', 'alelo', 'sodexo', 'ticket_rest', 'vale_refeicao', 'dinersclub'], axis=1)

        # df = df.rename(columns={
        #     'data_venda': 'Data',
        #     'data_30': 'Data -30d',
        #     'dinheiro': 'Dinheiro',
        #     'pix': 'Pix',
        #     'qtd_rodizio': 'Rodízio',
        #     'socio': 'Sócios',
        #     'periodo': 'Período',
        #     'total': 'Total',
        #     'valor_total_30': 'Total -30d'
        # })

        # grafico_dinamico = StreamlitRenderer(df, spec="./json/vendas.json", spec_io_mode="rw")
        # renderer = grafico_dinamico
        # renderer.explorer()
        # df = self.valores_vendas_30dias.drop(['ID', 'dt_atualizado'], axis=1)
        # df['data_venda'] = pd.to_datetime(df['data_venda'], format='%Y-%m-%d')

        # colunas = ['dinheiro', 'pix', 'debito_mastercard', 'debito_visa', 'debito_elo', 'credito_mastercard', 'credito_visa', 'socio',
        #             'credito_elo', 'hiper', 'american_express', 'alelo', 'sodexo', 'ticket_rest', 'vale_refeicao', 'dinersclub', 'valor_total_30']
        
        # for item in colunas:
        #     df[item] = pd.to_numeric(df[item], errors='coerce')

        # df['Total débito'] = df[['debito_mastercard', 'debito_visa', 'debito_elo',]].sum(axis=1)
        # df['Total crédito'] = df[['credito_mastercard', 'credito_visa', 'credito_elo']].sum(axis=1)
        # df['Outros Cartões'] = df[['hiper', 'american_express', 'alelo', 'sodexo', 'ticket_rest', 'vale_refeicao', 'dinersclub']].sum(axis=1)
        # # df['Total'] = df[['dinheiro', 'pix', 'debito_mastercard', 'debito_visa', 'debito_elo', 'credito_mastercard', 'credito_visa', 
        # #                   'credito_elo', 'hiper', 'american_express', 'alelo', 'sodexo', 'ticket_rest', 'vale_refeicao', 'dinersclub']].sum(axis=1)
        # df = df.drop(['debito_mastercard', 'debito_visa', 'debito_elo', 'credito_mastercard', 'credito_visa', 'credito_elo', 
        #               'hiper', 'american_express', 'alelo', 'sodexo', 'ticket_rest', 'vale_refeicao', 'dinersclub'], axis=1)

        # df = df.rename(columns={
        #     'data_venda': 'Data',
        #     'data_30': 'Data -30d',
        #     'dinheiro': 'Dinheiro',
        #     'pix': 'Pix',
        #     'qtd_rodizio': 'Rodízio',
        #     'socio': 'Sócios',
        #     'periodo': 'Período',
        #     'total': 'Total',
        #     'valor_total_30': 'Total -30d'
        # })

        # grafico_dinamico = StreamlitRenderer(df, spec="./json/vendas.json", spec_io_mode="rw")
        # renderer = grafico_dinamico
        # renderer.explorer()