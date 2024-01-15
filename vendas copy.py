import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
from millify import millify
from datetime import datetime
from streamlit_metrics import metric # precisei intalar no terminal streamlit_metrics e a biblioteca millify
import calendar
from st_aggrid import AgGrid, GridOptionsBuilder
gb = GridOptionsBuilder()
from filtro import Filtros


class Vendas: 
    def __init__(self) -> None:
        self.filtro = Filtros()

    def navegacao_vendas(self):
        tab1, tab2, tab3 = st.tabs(["Resumo", "Lançamento", "Tabela Dinâmica"])
        with tab1:
            self.cards_resumo()
            self.graficos_vendas()
        with tab2:
            st.subheader("Apontamento das vendas")
            self.lancamento_vendas()
            st.write('----------------')
            st.subheader('A data de modificação esta sendo alterado na tabela inteira')
            self.lancamento_vendas_table()
        with tab3:
            self.tabela_dinamica_vendas()

    def dataframe_vendas(self):
        self.conecta_bd()
        
        # colunas do banco
        # data_venda, dinheiro, pix, debito_mastercard, debito_visa, debito_elo, credito_mastercard, credito_visa, credito_elo, hiper, 
        # american_express, alelo, 'sodexo', 'ticket_rest', 'vale_refeicao', 'dinersclub', qtd_rodizio, socio, periodo, dt_atualizado, ID"
        
        # Filtrando data
        data_inicial = str(self.filtro.data_inicial)     # formato da data'2023-05-01'
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

        # self.valores_vendas = [item for item in np.array(self.df_vendas) if datetime.strptime(item[0], '%d/%m/%Y').month == 7]

        self.df_vendas_valores = self.valores_vendas.drop(['data_venda', 'periodo', 'dt_atualizado', 'ID'], axis=1)
        self.array_vendas = np.array(self.df_vendas_valores)

        # garantir que array esta como string e assim poder aplicar replace
        self.array_vendas = self.array_vendas.astype(str)
        self.array_vendas = np.char.replace(self.array_vendas, ',', '.')
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
        self.outros_cartoes = self.hiper + self.american_express + self.alelo + self.sodexo + self.ticket_rest + self.vale_refeicao + self.dinersclub
        self.total_vendas = self.dinheiro + self.pix + self.debito + self.credito + self.outros_cartoes
        self.ticket_medio = self.total_vendas / self.rodizio

    def cards_resumo_vendas(self):
        self.dataframe_vendas()
        # Cards das vendas
        # a função millify serve para abreviar o valor $8.000 para $8k
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric('Credito', '${}'.format(millify(self.credito)), '{:.4}%'.format(self.credito/self.total_vendas*100))
        col2.metric('Débito', '${}'.format(millify(self.debito)), '{:.4}%'.format(self.debito/self.total_vendas*100))
        col3.metric('Benefício', '${}'.format(millify(self.outros_cartoes)), '{:.4}%'.format(self.outros_cartoes/self.total_vendas*100), 
                    help='Cartões: Hiper - American Express - Alelo, Sodexo - Vale Refeição - Ticket Rest - DinersClub')
        col4.metric('Dinheiro', '${}'.format(millify(self.dinheiro)), '{:.4}%'.format(self.dinheiro/self.total_vendas*100))
        col5.metric('Pix', '${}'.format(millify(self.pix)), '{:.4}%'.format(self.pix/self.total_vendas*100))

        col1, col2, col3 = st.columns([1, 1, 3])
        col1.metric('Total Vendas', '${}'.format(millify(self.total_vendas)), help='Incluir a data do filtro')
        col2.metric('Qtd Rodízio', self.rodizio)
        col3.metric('*Ticket Médio*', '${:.2f}'.format(self.ticket_medio))
        st.write('-------')

    def lancamento_vendas(self):
        # Forms pode ser declarado utilizando a sintaxe 'with'
        with st.form(key='lançar_vendas', clear_on_submit=True):
            # st.title = ('Lançamento de Vendas')
            col1, col2, col3, col4, col5, col6= st.columns(6)
            with col1:
                self.data_venda = st.date_input('Data', format='DD/MM/YYYY')
                self.periodo = st.selectbox('Período', ['Almoço', 'Jantar'])
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
        elif self.periodo == '':
            st.error('O período não foi preenchido!', icon="🚨")
        elif self.rodizio == '':
            st.warning('O período não foi preenchido.', icon="⚠")
        else:            
            self.conecta_mysql()

            dt_atualizo = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
            
            comando = f""" INSERT INTO vendas (data_venda, periodo, qtd_rodizio, dinheiro, pix, debito_mastercard, 
                        debito_visa, debito_elo, credito_mastercard, credito_visa, credito_elo, american_express, alelo,
                        hiper, sodexo, ticket_rest, vale_refeicao, dinersclub, socio, dt_atualizado) 
            VALUES (
                '{self.data_venda}', '{self.periodo}', '{self.rodizio}', '{self.dinheiro}', '{self.pix}', 
                '{self.debito_mastercard}', '{self.debito_visa}', '{self.debito_elo}', '{self.credito_mastercard}', 
                '{self.credito_visa}', '{self.credito_elo}', '{self.american_express}', '{self.alelo}', '{self.hiper}',
                '{self.sodexo}', '{self.ticket_rest}', '{self.vale_refeicao}', '{self.dinersclub}',
                '{self.socio}', '{dt_atualizo}')"""

            self.cursor.execute(comando)
            self.cursor.commit()

            self.desconecta_bd()
            st.success("Lançamento Realizado com Sucesso!")
            # fazer com que apos 5 segundos a mensagem de sucesso apague PENDENTE

    def lancamento_vendas_table(self):
        self.conecta_mysql2()

        # Função para carregar dados do banco de dados
        @st.cache_data
        def load_data():
            query = "SELECT * FROM vendas ORDER BY ID DESC"
            df = pd.read_sql(query, self.conn)
            return df

        # POR ENQUANTO NÃO ESTOU ATUALIZANDO A DATA DE ATUALIZAÇÃO POIS ESTAVA ALTERANDO A COLUNA INTEIRA
        # dt_atualizado = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

        # Função para atualizar dados no banco de dados
        def update_data(df):
            cursor = self.conn.cursor()
            for index, row in df.iterrows():
                query = f"UPDATE vendas SET data_venda = '{row['data_venda']}', periodo = '{row['periodo']}', \
                            qtd_rodizio = '{row['qtd_rodizio']}', dinheiro = '{row['dinheiro']}', pix = '{row['pix']}', \
                            debito_mastercard = '{row['debito_mastercard']}', debito_visa = '{row['debito_visa']}', \
                            debito_elo = '{row['debito_elo']}', credito_mastercard = '{row['credito_mastercard']}', \
                            credito_visa = '{row['credito_visa']}', credito_elo = '{row['credito_elo']}', alelo = '{row['alelo']}', \
                            hiper = '{row['hiper']}', american_express = '{row['american_express']}', sodexo = '{row['sodexo']}', \
                            ticket_rest = '{row['ticket_rest']}', vale_refeicao = '{row['vale_refeicao']}', \
                            dinersclub = '{row['dinersclub']}', socio = '{row['socio']}' WHERE ID = {row['ID']}"
                cursor.execute(query)
            self.conn.commit()
            
            cursor.close()
            self.conn.close()

        # Carregue os dados do banco de dados
        df = load_data()
        
        # Bloquear algumas colunas da edição
        colunas_bloqueadas = {
        'dt_atualizado': {'editable': False},
        'ID': {'editable': False}
        }
        
        # Formatar as colunas como número
        colunas_formatada = {
            'qtd_rodizio': st.column_config.NumberColumn(format='%d', min_value=1, max_value=500),
            'dinheiro': st.column_config.NumberColumn(format='$%d', min_value=0, max_value=25000),
            'pix': st.column_config.NumberColumn(format='$%d', min_value=0, max_value=25000),
            'debito_mastercard': st.column_config.NumberColumn(format='$%d', min_value=0, max_value=25000),
            'debito_visa': st.column_config.NumberColumn(format='$%d', min_value=0, max_value=25000),
            'debito_elo': st.column_config.NumberColumn(format='$%d', min_value=0, max_value=25000),
            'credito_mastercard': st.column_config.NumberColumn(format='$%d', min_value=0, max_value=25000),
            'credito_visa': st.column_config.NumberColumn(format='$%d', min_value=0, max_value=25000),
            'credito_elo': st.column_config.NumberColumn(format='$%d', min_value=0, max_value=25000),
            'alelo': st.column_config.NumberColumn(format='$%d', min_value=0, max_value=25000),
            'hiper': st.column_config.NumberColumn(format='$%d', min_value=0, max_value=25000),
            'american_express': st.column_config.NumberColumn(format='$%d', min_value=0, max_value=25000),
            'sodexo': st.column_config.NumberColumn(format='$%d', min_value=0, max_value=25000),
            'ticket_rest': st.column_config.NumberColumn(format='$%d', min_value=0, max_value=25000),
            'vale_refeicao': st.column_config.NumberColumn(format='$%d', min_value=0, max_value=25000),
            'dinersclub': st.column_config.NumberColumn(format='$%d', min_value=0, max_value=25000),
            'socio': st.column_config.NumberColumn(format='$%d', min_value=0, max_value=2000),
        }
        # num_rows = 'dynamic' é para habilitar a inclusão de linhas
        # disabled = deixa as colunas ineditavel
        tabela_editavel = st.data_editor(df, hide_index=True, disabled=colunas_bloqueadas, column_config=colunas_formatada,
                                            column_order=['ID', 'data_venda', 'periodo', 'qtd_rodizio', 'dinheiro', 'pix', 
                                                            'debito_mastercard', 'debito_visa', 'debito_elo', 'credito_mastercard', 
                                                            'credito_visa', 'credito_elo', 'alelo', 'hiper', 'american_express', 
                                                            'sodexo', 'ticket_rest', 'vale_refeicao', 'dinersclub', 'socio',
                                                            'dt_atualizado'])
        # exibindo a tabela
        tabela_editavel

        if st.button('Salvar Alterações'):
            update_data(tabela_editavel)
            st.success('Alterações salvas com sucesso!')   
        
    def graficos_vendas(self):
        # pegando a coluna data
        self.valores_vendas_np = np.array(self.valores_vendas)
        self.data_vendas = np.array([ts.strftime('%d/%m/%Y') for ts in self.valores_vendas_np[:, 0]])
        # somando total de valores para cada dia (coluna total de uma tabela)
        # somando todas as linhas da coluna 0 até a 14 -> o mesmo que ter uma coluna total de uma tabela
        # total de vendas desconsiderando consumo dos sócios
        self.array_total_vendas = np.nansum(self.array_vendas[:, 0:15], axis=1) 

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
                largura_ideal = 850 / len(df['Data'])

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
        
        with st.expander('Tabela das vendas'):
            st.write(self.valores_vendas)

        with st.expander('Gráfico Mensal'):
            df_ano_mes = self.df_vendas # esse df_vendas não tem filtro na data pega todos os meses
            # df_ano_mes = self.valores_vendas

            # # df_ano_mes['data_venda'] = pd.to_datetime(df_ano_mes['data_venda'], format='%d/%m/%Y')
            df_ano_mes['ano'] = df_ano_mes['data_venda'].dt.year
            df_ano_mes['mes'] = df_ano_mes['data_venda'].dt.month
            df_ano_mes['mes'] = df_ano_mes['data_venda'].dt.month.apply(lambda x: calendar.month_abbr[x])
            
            # Filtro do ano
            df_filtrado = df_ano_mes.loc[(df_ano_mes['data_venda'].dt.year == 2023)]
            df_ano_mes = df_filtrado.drop(['data_venda', 'socio', 'ID', 'periodo', 'qtd_rodizio', 'dt_atualizado', 'ano', 'mes'], axis=1)
            df_ano_mes = np.array(df_ano_mes)

            # garantir que array esta como string e assim poder aplicar replace
            df_ano_mes = df_ano_mes.astype(str)
            df_ano_mes = np.char.replace(df_ano_mes, ',', '.')
            # substiturir valores vazios por nan e assim converter valores para float
            df_ano_mes[df_ano_mes == ''] = 0 #'nan'
            df_ano_mes = df_ano_mes.astype(float)
            
            data = np.array(df_filtrado['mes'])
            valor = np.nansum(df_ano_mes, axis=1)
            
            colunas = ['Meses', 'Valor']
            array_vendas_mes = np.column_stack((data, valor))
            df_vendas_mes = pd.DataFrame(array_vendas_mes, columns=colunas)

            # Gráfico de barras - ticket médio
            graf_vendas_mes = alt.Chart(df_vendas_mes).mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10).encode(
                    x = 'Meses:N', 
                    y = 'sum(Valor):Q',
                    # tooltip = ['Data', 'Valor']
                    ).properties(title= 'Vendas Mensais')
            
            linha = alt.Chart(df_vendas_mes).mark_rule(color='blue').encode(
                    y='mean(Valor):Q')
            
            rotulos_valores = graf_vendas_mes.mark_text(
            align='left',
            baseline='middle',
            dx=-30,  # Ajuste horizontal para posicionar o rótulo
            dy=10,  # Ajuste vertical para posicionar o rótulo
            fontSize = 15,
            color='black',  # Cor do texto
             ).encode(
            text=alt.Text('sum(Valor):Q')  # Use a soma dos valores como texto
            )

            st.altair_chart(graf_vendas_mes + linha + rotulos_valores, use_container_width=True)
        
    def tabela_dinamica_vendas(self):
        st.write('\
                 Em desenvolvimento...')
        # self.conecta_mysql()
        # def lista():
        #     lista = f""" SELECT ID, data_venda, periodo, qtd_rodizio, dinheiro, pix, debito_mastercard, debito_visa, debito_elo, 
        #                         credito_mastercard, credito_visa, credito_elo, hiper, american_express, alelo, sodexo, ticket_rest, 
        #                         vale_refeicao, dinersclub, socio,
        #                     CAST(dinheiro AS DECIMAL) + CAST(pix AS DECIMAL) + 
        #                     CAST(debito_mastercard AS DECIMAL) + CAST(debito_visa AS DECIMAL) + CAST(debito_elo AS DECIMAL) + 
        #                     CAST(credito_mastercard AS DECIMAL) + CAST(credito_visa AS DECIMAL) + CAST(credito_elo AS DECIMAL) + 
        #                     CAST(hiper AS DECIMAL) + CAST(american_express AS DECIMAL) + CAST(alelo AS DECIMAL) + 
        #                     CAST(sodexo AS DECIMAL) + CAST(ticket_rest AS DECIMAL) + CAST(vale_refeicao AS DECIMAL) + 
        #                     CAST(dinersclub AS DECIMAL) + CAST(socio AS DECIMAL) AS total_vendas 
        #                 FROM vendas ORDER BY ID DESC; """
        # lista = lista()
        # tabelavendas = pd.read_sql(lista, self.conexao)
        # self.desconecta_bd()

        # # gerando os dataframe
        # tabelavendas = tabelavendas.drop(['ID'], axis=1)

        # # Conversões
        # tabelavendas['qtd_rodizio'] = pd.to_numeric(tabelavendas['qtd_rodizio'], errors='coerce')
        # tabelavendas['dinheiro'] = pd.to_numeric(tabelavendas['dinheiro'], errors='coerce')
        # tabelavendas['pix'] = pd.to_numeric(tabelavendas['pix'], errors='coerce')
        # tabelavendas['debito_mastercard'] = pd.to_numeric(tabelavendas['debito_mastercard'], errors='coerce')
        # tabelavendas['debito_visa'] = pd.to_numeric(tabelavendas['debito_visa'], errors='coerce')
        # tabelavendas['debito_elo'] = pd.to_numeric(tabelavendas['debito_elo'], errors='coerce')
        # tabelavendas['credito_mastercard'] = pd.to_numeric(tabelavendas['credito_mastercard'], errors='coerce')
        # tabelavendas['credito_visa'] = pd.to_numeric(tabelavendas['credito_visa'], errors='coerce')
        # tabelavendas['credito_elo'] = pd.to_numeric(tabelavendas['credito_elo'], errors='coerce')
        # tabelavendas['hiper'] = pd.to_numeric(tabelavendas['hiper'], errors='coerce')
        # tabelavendas['american_express'] = pd.to_numeric(tabelavendas['american_express'], errors='coerce')
        # tabelavendas['alelo'] = pd.to_numeric(tabelavendas['alelo'], errors='coerce')
        # tabelavendas['sodexo'] = pd.to_numeric(tabelavendas['sodexo'], errors='coerce')
        # tabelavendas['ticket_rest'] = pd.to_numeric(tabelavendas['ticket_rest'], errors='coerce')
        # tabelavendas['vale_refeicao'] = pd.to_numeric(tabelavendas['vale_refeicao'], errors='coerce')
        # tabelavendas['dinersclub'] = pd.to_numeric(tabelavendas['dinersclub'], errors='coerce')
        # tabelavendas['socio'] = pd.to_numeric(tabelavendas['socio'], errors='coerce')

        # # check box
        # shouldDisplayPivoted = st.toggle('Pivotar Coluna')  # st.checkbox("Pivot data on Reference Date") 

        # # torna as colunas redimensionáveis, classificáveis e filtráveis por padrão
        # gb.configure_default_column(
        #     resizable=True,
        #     filterable=True,
        #     sortable=True,
        #     editable=False,)

        # # define se o modo de pivô deve ser ativado ou desativado
        # pivotMode = False # Mode Pivot inicia desativado
        # gb.configure_grid_options(
        #     sideBar={
        #         "toolPanels": [
        #             {
        #                 "id": "columns",
        #                 "labelDefault": "Colunas",
        #                 "labelKey": "columns",                      # rowGroup ou columns
        #                 "iconKey": "columns",                       # rowGroup
        #                 "toolPanel": "agColumnsToolPanel",          # agRowGroupToolPanel ou agColumnsToolPanel
        #                 "toolPanelParams": {
        #                     # Permite que as colunas sejam reordenadas no painel de colunas
        #                     "suppressSyncLayoutWithGrid": True,
        #                     # impede que as colunas sejam movidas do painel de colunas
        #                     "suppressColumnMove": False,
        #                 },
        #             },
        #             {
        #                 "id": "filters",
        #                 "labelDefault": "Filtros",
        #                 "labelKey": "filters",
        #                 "iconKey": "filter",
        #                 "toolPanel": "agFiltersToolPanel",
        #                 "toolPanelParams": {
        #                     # impede que os filtros sejam reordenados no painel de filtros
        #                     "suppressSyncLayoutWithGrid": True,
        #                     # impede que os filtros sejam movidos do painel de filtros
        #                     "suppressFilterMove": True,
        #                 },
        #             },
        #         ],
                        
        #         # define o painel de colunas como padrão
        #         "defaultToolPanel": "", # deixar o filtro aberto quando abrir o sistema (columns ou filter dentro do parantes)
        #         # ativa ou desativa o modo de pivô
        #         "pivotMode": '',
        #     },
        # )

        # # habilite o modo dinâmico quando a caixa de seleção estiver ativada
        # gb.configure_grid_options(
        #     tooltipShowDelay=0,
        #     pivotMode=pivotMode,)

        # # configurar a coluna que exibe a hierarquia do agrupamento
        # gb.configure_grid_options(
        #     autoGroupColumnDef=dict(
        #         minWidth=300, 
        #         pinned="left",
        #         cellRendererParams=dict(suppressCount=True)
        #         )
        # )

        # # Criando colunas virtuais do ano
        # gb.configure_column(
        #     field="virtualYear",
        #     header_name="Ano",
        #     valueGetter="new Date(data.data_venda).getFullYear()",
        #     pivot=True, # allows grid to pivot on this column (o agrupamento altera de linha para coluna de forma automatica)
        #     enablePivot=True, # ao ativar pivotamento a coluna fica disponivel para selecionar
        #     hide=True, # oculta-o quando o modo dinâmico está desativado (check box que habilita)
        #     rowGroup=True if shouldDisplayPivoted else False)

        # # Criando colunas virtuais do mês
        # gb.configure_column(
        #     field="virtualMonth",
        #     header_name="Mês",
        #     valueGetter="new Date(data.data_venda).toLocaleDateString('pt-BR',options={year:'numeric', month:'2-digit'})",
        #     pivot=True, # allows grid to pivot on this column (o agrupamento altera de linha para coluna deforma automatica)
        #     enablePivot=True, # ao ativar pivotamento a coluna fica disponivel para selecionar
        #     hide=True, # oculta-o quando o modo dinâmico está desativado (check box que habilita)
        #     rowGroup=True if shouldDisplayPivoted else False)

        # gb.configure_column(
        #     field="data_venda",
        #     header_name="Data",
        #     valueFormatter="value != undefined ? new Date(value).toLocaleString('pt-BR', {dateStyle:'medium'}): ''",
        #     # flex=1, # padronizar largura da celula
        #     width=180,
        #     pivot=False, # allows grid to pivot on this column (o agrupamento altera de linha para coluna deforma automatica)
        #     enablePivot=True, # ao ativar pivotamento a coluna fica disponivel para selecionar
        #     hide=True,
        #     rowGroup=True if shouldDisplayPivoted else False)

        # gb.configure_column(
        #     field="periodo", 
        #     header_name="Período",
        #     width=110,
        #     pivot=False, # allows grid to pivot on this column (o agrupamento altera de linha para coluna deforma automatica)
        #     enablePivot=True, # ao ativar pivotamento a coluna fica disponivel para selecionar
        #     hide=True,
        #     rowGroup=True if shouldDisplayPivoted else False)

        # gb.configure_column(
        #     field="dinheiro",
        #     header_name="Dinheiro",
        #     type=["numericColumn"],
        #     valueFormatter="value.tolLocaleString()",
        #     aggFunc="sum",
        #     width=110,)

        # gb.configure_column(
        #     field="pix",
        #     header_name="Pix",
        #     type=["numericColumn"],
        #     valueFormatter="value.tolLocaleString()",
        #     aggFunc="sum",
        #     width=110,)
        
        # gb.configure_column(
        #     field="debito_mastercard",
        #     header_name="Debito Master",
        #     type=["numericColumn"],
        #     valueFormatter="value.tolLocaleString()",
        #     aggFunc="sum",
        #     width=110,)

        # gb.configure_column(
        #     field="debito_visa",
        #     header_name="Debito Visa",
        #     type=["numericColumn"],
        #     valueFormatter="value.tolLocaleString()",
        #     aggFunc="sum",
        #     width=110,)
        
        # gb.configure_column(
        #     field="debito_elo",
        #     header_name="Debito Elo",
        #     type=["numericColumn"],
        #     valueFormatter="value.tolLocaleString()",
        #     aggFunc="sum",
        #     width=110,)
        
        # gb.configure_column(
        #     field="credito_mastercard",
        #     header_name="Credito Master",
        #     type=["numericColumn"],
        #     valueFormatter="value.tolLocaleString()",
        #     aggFunc="sum",
        #     width=110,)
        
        # gb.configure_column(
        #     field="credito_visa",
        #     header_name="Credito Visa",
        #     type=["numericColumn"],
        #     valueFormatter="value.tolLocaleString()",
        #     aggFunc="sum",
        #     width=110,)
        
        # gb.configure_column(
        #     field="credito_elo",
        #     header_name="Credito Elo",
        #     type=["numericColumn"],
        #     valueFormatter="value.tolLocaleString()",
        #     aggFunc="sum",
        #     width=110,)
        
        # gb.configure_column(
        #     field="hiper",
        #     header_name="Hiper Card",
        #     type=["numericColumn"],
        #     valueFormatter="value.tolLocaleString()",
        #     aggFunc="sum",
        #     width=110,)
        
        # gb.configure_column(
        #     field="american_express",
        #     header_name="American Express",
        #     type=["numericColumn"],
        #     valueFormatter="value.tolLocaleString()",
        #     aggFunc="sum",
        #     width=110,)
        
        # gb.configure_column(
        #     field="alelo",
        #     header_name="Alelo",
        #     type=["numericColumn"],
        #     valueFormatter="value.tolLocaleString()",
        #     aggFunc="sum",
        #     tooltipField="alelo",
        #     width=110)

        # gb.configure_column(
        #     field="sodexo",
        #     header_name="Sodexo",
        #     type=["numericColumn"],
        #     valueFormatter="value.tolLocaleString()",
        #     aggFunc="sum",
        #     width=110,)
        
        # gb.configure_column(
        #     field="ticket_rest",
        #     header_name="Ticket Rest",
        #     type=["numericColumn"],
        #     valueFormatter="value.tolLocaleString()",
        #     aggFunc="sum",
        #     width=110,)

        # gb.configure_column(
        #     field="vale_refeicao",
        #     header_name="Vale Refeição",
        #     type=["numericColumn"],
        #     valueFormatter="value.tolLocaleString()",
        #     aggFunc="sum",
        #     width=110,)

        # gb.configure_column(
        #     field="dinersclub",
        #     header_name="DinersClub",
        #     type=["numericColumn"],
        #     valueFormatter="value.tolLocaleString()",
        #     aggFunc="sum",
        #     width=110,)

        # gb.configure_column(
        #     field="qtd_rodizio",
        #     header_name="Rodízio",
        #     type=["numericColumn"],
        #     valueFormatter="value.tolLocaleString()",
        #     aggFunc="sum",
        #     width=110,)
        
        # gb.configure_column(
        #     field="socio",
        #     header_name="Socio",
        #     type=["numericColumn"],
        #     valueFormatter="value.tolLocaleString()",
        #     aggFunc="sum",
        #     width=110,)
        
        # gb.configure_column(
        #     field="total_vendas",
        #     header_name="Total",
        #     type=["numericColumn"],
        #     valueFormatter="value.tolLocaleString()",
        #     aggFunc="sum",
        #     width=110,)

        # go = gb.build()

        # AgGrid(tabelavendas, gridOptions=go, height=650)