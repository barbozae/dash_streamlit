import streamlit as st
from pygwalker.api.streamlit import StreamlitRenderer
from sqlalchemy import text, select, insert, update, Table, MetaData, Column, Integer, String, DateTime
from datetime import datetime
from filtro import Filtros
from conexao import Conexao
import pandas as pd
import numpy as np
import time


class FuncNavegacao:
    def navegacao_funcionarios(self):
        tab1, tab2, tab3, tab4 = st.tabs(['Cadastro', 'Contratação', 'Pagamento', 'Rescisão'])
    
        with tab1:
            with st.expander('Cadastro de funcionário', expanded=True):
                self.widget_cadastro()
            with st.expander('Edição do cadastro'):
                self.edicao_cadastro_table()     
        with tab2:
            with st.expander('Admissão de funcionário', expanded=True):
                self.widget_admissao()
            with st.expander('Edição da admissão'):
                self.edicao_admissao_table()
        with tab3:
            with st.expander('Pagamento de funcionário', expanded=True):
                self.widget_pagamento()
            with st.expander('Edição de pagamento dos funcionários'):
                self.edicao_pg_func_table()
        with tab4:
            with st.expander('Rescisão de funcionário', expanded=True):
                self.widget_rescisao()
            with st.expander('Edição da rescisão dos funcionários'):
                self.edicao_rescisao_table()

class FuncCadastro: 
    def __init__(self) -> None:
        self.filtro = Filtros()

    @staticmethod
    def atualizar_func_cadastro():
        consulta = Conexao.conecta_bd()
        # print('Conectado ao banco, atualizar_cadastro')
        df_cadastro = consulta[8]
        return df_cadastro

    def widget_cadastro(self):
        self.lista_banco = ['Bradesco', 'Itau', 'Santander', 'Nubank', 'Banco do Brasil',
                               'Caixa Econômica', 'Inter', 'C6 Bank', 'Neon', 'Next', 'Banco Original']
        # Forms pode ser declarado utilizando a sintaxe 'with'
        with st.form(key='func_cadastro', clear_on_submit=False):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                self.nome_funcionario = st.text_input(label='Nome', placeholder='Nome do funcionário')
                self.rg = st.text_input(label='RG', placeholder='RG do funcionário')
                self.cpf = st.text_input(label='CPF', placeholder='CPF do funcionário')
            with col2:
                self.carteira_trabalho = st.text_input(label='Carteira de Trabalho', placeholder='Número da CTPS')
                self.cidade = st.text_input(label='Cidade', placeholder='Digite Cidade')
                self.bairro = st.text_input(label='Bairro', placeholder='Digite o Bairro')
            with col3:
                self.endereco = st.text_input(label='Endereço', placeholder='Digite endereço')
                self.numero = st.text_input(label='Número', placeholder='Número do endereço')
                self.telefone = st.text_input(label='Contato', placeholder='Telefone')
            with col4:
                self.banco = st.selectbox('Banco', self.lista_banco, index=None, placeholder='Selecione o banco')
                self.agencia = st.text_input(label='Agencia', placeholder='Agencia do Banco')
                self.conta = st.text_input(label='Conta', placeholder='Número da conta')

            submit_button = st.form_submit_button(label='Enviar')
                
        if submit_button:
            self.salvar_cadastro()

    def salvar_cadastro(self):
        if self.nome_funcionario == '':
            st.error('Nome de funcionário não é válido!', icon="🚨")
        else:
            dt_atualizo = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
            self.conecta_mysql()

            metadata = MetaData()
            cadastro_func_table = Table('cadastro_funcionario', metadata,
                Column('ID', Integer, primary_key=True),
                Column('nome', String),
                Column('rg', String),
                Column('cpf', String),
                Column('carteira_trabalho', String),
                Column('endereco', String),
                Column('numero', String),
                Column('bairro', String),
                Column('cidade', String),
                Column('telefone', String),
                Column('banco', String),
                Column('agencia',  String),
                Column('conta', String),
                Column('dt_atualizado', DateTime)
            )

            # Definindo os valores para inserção
            valores = {
                'nome': self.nome_funcionario,
                'rg': self.rg,
                'cpf': self.cpf,
                'carteira_trabalho': self.carteira_trabalho,
                'endereco': self.endereco,
                'numero': self.numero,
                'bairro': self.bairro,
                'cidade': self.cidade,
                'telefone': self.telefone,
                'banco': self.banco,
                'agencia': self.agencia,
                'conta': self.conta,
                'dt_atualizado': dt_atualizo
            }
           
            # Verificar se o nome do funcionário já existe na tabela
            stmt_select = select(cadastro_func_table).where(cadastro_func_table.c.nome == self.nome_funcionario)
            resultado = self.session.execute(stmt_select)
            existe_nome = resultado.fetchone() is not None

            # Se o nome não existir, então inserir o novo registro
            if not existe_nome:
                stmt = insert(cadastro_func_table).values(valores)
                # Executando a instrução de INSERT
                self.session.execute(stmt)
                # Confirmar a transação
                self.session.commit()

                # precisei criar uma mensagem vazia para depois deixa-la vazia novamente depois de utiliza-la
                msg_lancamento = st.empty()
                msg_lancamento.success("Lançamento Realizado com Sucesso!", icon='✅')
                time.sleep(10)
                msg_lancamento.empty()
                # fazer com que apos 5 segundos a mensagem de sucesso apague PENDENTE
            else:
                msg_lancamento = st.empty()
                msg_lancamento.error("Nome já cadastrado", icon="🚨")
                time.sleep(5)
                msg_lancamento.empty()
                # fazer com que apos 5 segundos a mensagem de sucesso apague PENDENTE

            # Fechar a sessão
            self.session.close()
            print('Fechou conexão')

    def dataframe_cadastro(self):
        consulta = FuncCadastro.atualizar_func_cadastro()
        df_cadastro = consulta
        # chamando a classe FiltrosFuncionarios e o metodo filtros_funcionarios
        FiltrosFuncionarios.filtros_funcionarios(self)

        # TABELAS DE CADASTRO - aplicando os filtros
        self.valores_cadastro = df_cadastro[self.filtro_nome_func & self.filtro_cargo & self.filtro_setor & self.filtro_data_contratacao]
        
        # total de pagamentos
        self.df_cadastro = self.valores_cadastro.drop(['setor', 'cargo','salario', 'documentacao_admissional',
                                                           'data_exame_admissional', 'contabilidade_admissional', 'observacao_admissional',
                                                           'data_desligamento','devolucao_uniforme', 'data_exame_demissional',
                                                           'data_homologacao', 'tipo_desligamento', 'contabilidade_rescisao',
                                                           'observacao_demissional', 'status_admissao', 'status_rescisao'], axis=1)

    def edicao_cadastro_table(self):
        self.dataframe_cadastro()
        col1, col2, col3, col4 = st.columns([1, 1, 1, 3])        
        with col1:
            df = self.df_cadastro
            filtro_ID = st.multiselect('ID', df['ID'], placeholder='Escolha ID')
        with col2:
            filtro_nome = st.multiselect('Nome', df['nome'], placeholder='Funcionário')

            if filtro_ID:
                df_filtrado = df[df['ID'].isin(filtro_ID)]
            else:
                df_filtrado = df
            df = df_filtrado

            if filtro_nome:
                df_filtrado = df[df['nome'].isin(filtro_nome)]
            else:
                df_filtrado = df
            df = df_filtrado

        # Bloquear algumas colunas da edição
        colunas_bloqueadas = {
        'dt_atualizado': {'editable': False},
        'ID': {'editable': False}
        }
        
        colunas_formatada = {
            'ID': st.column_config.NumberColumn('ID', format='%d'),
            'nome': st.column_config.TextColumn('Nome'),
            'rg': st.column_config.TextColumn('RG'),
            'cpf': st.column_config.TextColumn('CPF'),
            'carteira_trabalho': st.column_config.TextColumn('Carteira de Trabalho'),
            'cidade': st.column_config.TextColumn('Cidade'),
            'bairro': st.column_config.TextColumn('Bairro'),
            'endereco': st.column_config.TextColumn('Endereço'),
            'numero': st.column_config.TextColumn('Número'),
            'telefone': st.column_config.TextColumn('Telefone'),
            'banco': st.column_config.SelectboxColumn('Banco', options=self.lista_banco, required=True),
            'agencia': st.column_config.TextColumn('Agencia'),
            'conta': st.column_config.TextColumn('Conta'),
            'dt_atualizado': st.column_config.DatetimeColumn('Atualizado', format='DD/MM/YYYY- h:mm A'),
        }
        # num_rows = 'dynamic' é um parametro para habilitar a inclusão de linhas
        # disabled = deixa as colunas ineditavel
        tabela_editavel = st.data_editor(df, 
                                         disabled=colunas_bloqueadas, 
                                         column_config=colunas_formatada, 
                                         column_order=['ID', 'nome', 'rg', 'cpf', 'carteira_trabalho', 'cidade', 'bairro' 
                                                            'endereco', 'numero', 'telefone', 'banco', 'agencia', 'conta',
                                                            'dt_atualizado'], 
                                        hide_index=True)
        # Função para atualizar dados no banco de dados
        def update_data(df):
            self.conecta_mysql2()
            cursor = self.conn.cursor()
            data_atual = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
            for index, row in df.iterrows():
                query = f"UPDATE cadastro_funcionario \
                            SET nome = '{row['nome']}', rg = '{row['rg']}', cpf = '{row['cpf']}', \
                                carteira_trabalho = '{row['carteira_trabalho']}', cidade = '{row['cidade']}', \
                                bairro = '{row['bairro']}', endereco = '{row['endereco']}', numero = '{row['numero']}', \
                                telefone = '{row['telefone']}', banco = '{row['banco']}', agencia = '{row['agencia']}', \
                                conta = '{row['conta']}', dt_atualizado = '{data_atual}' \
                                WHERE ID = {row['ID']}"
                cursor.execute(query)
            self.conn.commit()
            
            cursor.close()
            self.conn.close()

        with col3:
            if st.button('Salvar Alterações'):
                if filtro_ID or filtro_nome or self.filtro.varNomeFunc:
                    update_data(tabela_editavel)
                    with col4:
                        # precisei criar uma mensagem vazia para depois deixa-la vazia novamente depois de utiliza-la
                        msg_lancamento = st.empty()
                        msg_lancamento.success("Edição realizada com Sucesso!", icon='✅')
                        time.sleep(10)
                        msg_lancamento.empty()
                else:
                    with col4:
                        msg_lancamento = st.empty()
                        msg_lancamento.error('Selecione ID ou funcionário que deseja editar!', icon="🚨")
                        time.sleep(10)
                        msg_lancamento.empty()

class FiltrosFuncionarios:
    def filtros_funcionarios(self):
        consulta = FuncCadastro.atualizar_func_cadastro()
        self.df_cadastro = consulta

        if self.filtro.varNomeFunc:
            self.filtro_nome_func = self.df_cadastro['nome'].isin(self.filtro.varNomeFunc)
        else:
            self.filtro_nome_func = pd.Series([True] * len(self.df_cadastro)) # se a lista estiver vazia, considera todos os valores como verdadeiros  
        
        if self.filtro.varCargo:
            self.filtro_cargo = self.df_cadastro['cargo'].isin(self.filtro.varCargo)
        else:
            self.filtro_cargo = pd.Series([True] * len(self.df_cadastro))

        if self.filtro.varSetor:
            self.filtro_setor = self.df_cadastro['setor'].isin(self.filtro.varSetor)
        else:
            self.filtro_setor = pd.Series([True] * len(self.df_cadastro))

        self.df_cadastro['data_contratacao'] = pd.to_datetime(self.df_cadastro['data_contratacao'], errors='coerce')
        if self.filtro.varDataContratacao:
            self.filtro_data_contratacao = self.df_cadastro['data_contratacao'].isin(self.filtro.varDataContratacao)
        else:
            self.filtro_data_contratacao = pd.Series([True] * len(self.df_cadastro))

class FuncAdmissao: # Contratação
    def widget_admissao(self):
        consulta = FuncCadastro.atualizar_func_cadastro()
        self.df_cadastro = consulta
        
        with st.form(key='func_admissao', clear_on_submit=False):
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                # Filtrando linhas onde 'data_contratacao' está vazio ou nulo. Para que tenhamos apenas opções de funcionarios não contratados
                funcionario_nao_admitido = self.df_cadastro[self.df_cadastro['data_contratacao'].isna() | self.df_cadastro['data_contratacao'].isnull()]
                self.nome_funcionario = st.selectbox('Nome', funcionario_nao_admitido['nome'].unique(), index=None, placeholder='Funcionário')
                self.salario = st.number_input(label='Salário', value=float('0.00'), step=100.00, min_value=0.00, max_value=25000.00)
            with col2:
                cargos_por_setor = {
                    'Administração': ["Gerente Financeiro", "Auxiliar Adm"],
                    'Cozinha': ["Chef", "Cozinheiro", "Cozinheiro Auxiliar", "Copeiro"],
                    'Limpeza': ["Faxineira(o)"],
                    'Sushi': ["Peixeiro", "Sushiman", "Sushiman Auxiliar"],
                    'Salão': ["Barman", "Caixa", "Cumin", "Garçom", "Gerente Geral", "Maitre", "Recepcionista"]
                    }
                cargos_lists = list(cargos_por_setor.values())
                cargos_values = [value for sublist in cargos_lists for value in sublist]
                self.cargo = st.selectbox('Cargo', cargos_values, index=None, placeholder='Selecione o Cargo', help='Selecione Cargo')
                self.doc_recebidos = st.selectbox('Doc Recebidos', ['Pendente', 'Concluído'], index=None, 
                                                    placeholder='Selecione satatus', help='Todos documentos recebidos')                    
            with col3:
                # Seleção do setor
                self.setor = st.selectbox('Setor', cargos_por_setor.keys(), index=None, placeholder='Selecione o Setor')
                self.status_admissao = st.selectbox('Status Admissão', ['Pendente', 'Concluído'], index=None, placeholder='Escolha uma opção')
            with col4:
                self.exame_admissional = st.date_input('Exame Admissional', format='DD/MM/YYYY', value=None)
                self.doc_contabilidade = st.selectbox('Doc Contabilidade', ['Pendente', 'Concluído'], index=None,
                                                    placeholder='Selecione satatus', help='Documentos enviados para contabilidade')
            with col5:
                self.data_contratacao = st.date_input('Data Contratação', format='DD/MM/YYYY', value=None)
                self.observacao_func_admissao = st.text_input(label='Obeservação')
            submit_button = st.form_submit_button(label='Enviar')

        if submit_button:
            self.salvar_admissao()

    def salvar_admissao(self):
        if self.nome_funcionario == '' or self.nome_funcionario == None:
            msg_lancamento = st.empty()
            msg_lancamento.error('Nome de funcionário não é válido!', icon='🚨')
            time.sleep(10)
            msg_lancamento.empty()
        elif self.data_contratacao == '' or self.data_contratacao == None:
            msg_lancamento = st.empty()
            msg_lancamento.error('Informar data da contratação', icon='🚨')
            time.sleep(10)
            msg_lancamento.empty()
        elif self.setor == '' or self.setor == None:
            msg_lancamento = st.empty()
            msg_lancamento.error('Setor do funcionário não é válido!', icon='🚨')
            time.sleep(10)
            msg_lancamento.empty()
        elif self.cargo == '' or self.cargo == None:
            msg_lancamento = st.empty()
            msg_lancamento.error('Cargo do funcionário não é válido!', icon='🚨')
            time.sleep(10)
            msg_lancamento.empty()
        else:
            dt_atualizo = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
            
            self.conecta_mysql()
            metadata = MetaData()
            admissao_func_table = Table('cadastro_funcionario', metadata,
                Column('ID', Integer, primary_key=True),
                Column('nome', String),
                Column('data_contratacao', String),
                Column('data_exame_admissional', String),
                Column('documentacao_admissional', String),
                Column('setor', String),
                Column('cargo', String),
                Column('contabilidade_admissional', String),
                Column('observacao_admissional', String),
                Column('dt_atualizado', DateTime)
            )

            # Definindo os valores para inserção
            valores = {
                'data_contratacao': self.data_contratacao,
                'data_exame_admissional': self.exame_admissional,
                'documentacao_admissional': self.doc_recebidos,
                'setor': self.setor,
                'cargo': self.cargo,
                'contabilidade_admissional': self.doc_contabilidade,
                'observacao_admissional': self.observacao_func_admissao,
                'dt_atualizado': dt_atualizo
            }

            # Criando uma instrução de INSERT
            stmt = update(admissao_func_table).where(admissao_func_table.c.nome == self.nome_funcionario).values(valores)
            # Executando a instrução de INSERT
            self.session.execute(stmt)
            # Confirmar a transação
            self.session.commit()
            # Fechando a sessão
            self.session.close()
            print('Fechou conexão')

            # precisei criar uma mensagem vazia para depois deixa-la vazia novamente depois de utiliza-la
            msg_lancamento = st.empty()
            msg_lancamento.success("Lançamento Realizado com Sucesso!", icon='✅')
            time.sleep(10)
            msg_lancamento.empty()
            # fazer com que apos 5 segundos a mensagem de sucesso apague PENDENTE

    def dataframe_admissao(self):
        FuncCadastro.atualizar_func_cadastro()
        FiltrosFuncionarios.filtros_funcionarios(self)
        # TABELAS DE CADASTRO - aplicando os filtros
        # estou dropando as linhas em brando da coluna data_contratação
        self.valores_admissao = self.df_cadastro.dropna(subset=['data_contratacao'])[self.filtro_nome_func & self.filtro_cargo & 
                                                                                self.filtro_setor & self.filtro_data_contratacao]        
        # total de pagamentos
        self.df_admissao = self.valores_admissao.drop(['rg', 'cpf','carteira_trabalho', 'endereco', 'numero', 'bairro', 'cidade', 
                                                       'telefone','banco', 'agencia', 'conta', 'data_desligamento', 'devolucao_uniforme',
                                                        'data_exame_demissional', 'data_homologacao', 'tipo_desligamento', 
                                                        'contabilidade_rescisao', 'observacao_demissional', 'status_rescisao'], axis=1)

    def edicao_admissao_table(self):
        self.dataframe_admissao()
        
        col1, col2, col3, col4 = st.columns([1, 1.5, 1, 3])        
        with col1:
            df = self.df_admissao
            filtro_ID = st.multiselect('ID', df['ID'], placeholder='Escolha ID', key=1)
        with col2:
            filtro_nome = st.multiselect('Nome', df['nome'], placeholder='Funcionário', key=2)

            if filtro_ID:
                df_filtrado = df[df['ID'].isin(filtro_ID)]
            else:
                df_filtrado = df
            df = df_filtrado

            if filtro_nome:
                df_filtrado = df[df['nome'].isin(filtro_nome)]
            else:
                df_filtrado = df
            df = df_filtrado

        # Bloquear algumas colunas da edição
        colunas_bloqueadas = {
        'dt_atualizado': {'editable': False},
        'ID': {'editable': False}
        }

        # Convert the data_contratacao column into a date data type
        df['data_contratacao'] = pd.to_datetime(df['data_contratacao'], errors='coerce')
        df['data_exame_admissional'] = pd.to_datetime(df['data_exame_admissional'], errors='coerce')

        lista_setor = ['Administação', 'Cozinha', 'Limpeza', 'Sushi', 'Salão']
        lista_cargo = ['Auxiliar Administrativo', 'Chef', 'Cozinheiro', 'Cozinheiro Auxiliar', 'Copeiro', 'Faxineira(o)', 'Peixeiro', 
                       'Sushiman', 'Sushiman Auxiliar', 'Barman', 'Caixa', 'Cumin', 'Garçom', 'Gerente Geral',
                       'Gerente Financeiro', 'Maitre', 'Recepcionista']
        
        colunas_formatada = {
            'ID': st.column_config.NumberColumn('ID', format='%d'),
            'nome': st.column_config.TextColumn('Nome'),
            'data_contratacao': st.column_config.DateColumn('Data Contratação', format='DD/MM/YYYY'),
            'setor': st.column_config.SelectboxColumn('Setor', options=lista_setor, required=True),
            'cargo': st.column_config.SelectboxColumn('Cargo', options=lista_cargo, required=True),
            'salario': st.column_config.NumberColumn('Salário', format='$ %d'),
            'data_exame_admissional': st.column_config.DateColumn('Exame Admissional', format='DD/MM/YYYY'),
            'documentacao_admissional': st.column_config.SelectboxColumn('Documentação Admissional', options=['Pendente', 'Concluído'], required=True),
            'contabilidade_admissional': st.column_config.SelectboxColumn('Doc Contabilidade', options=['Pendente', 'Concluído'], required=True),
            'status_admissao': st.column_config.SelectboxColumn('Status', options=['Pendente', 'Concluído'], required=True),
            'observacao_admissional': st.column_config.TextColumn('Obervação'),
            'dt_atualizado': st.column_config.DatetimeColumn('Atualizado', format='DD/MM/YYYY- h:mm A'),
        }
        # num_rows = 'dynamic' é um parametro para habilitar a inclusão de linhas
        # disabled = deixa as colunas ineditavel
        tabela_editavel = st.data_editor(df, 
                                         disabled=colunas_bloqueadas, 
                                         column_config=colunas_formatada, 
                                         column_order=['ID', 'nome', 'data_contratacao', 'setor', 'cargo', 'salario', 'data_exame_admissional' 
                                                        'documentacao_admissional', 'contabilidade_admissional', 'status_admissao', 
                                                        'observacao_admissional', 'dt_atualizado'], 
                                        hide_index=True)
        # Função para atualizar dados no banco de dados
        def update_data(df):
            self.conecta_mysql2()
            cursor = self.conn.cursor()
            data_atual = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
            for index, row in df.iterrows():
                query = f"UPDATE cadastro_funcionario \
                            SET nome = '{row['nome']}', data_contratacao = '{row['data_contratacao']}', setor = '{row['setor']}', \
                                cargo = '{row['cargo']}', salario = '{row['salario']}', data_exame_admissional = '{row['data_exame_admissional']}', \
                                documentacao_admissional = '{row['documentacao_admissional']}', contabilidade_admissional = '{row['contabilidade_admissional']}', \
                                status_admissao = '{row['status_admissao']}', observacao_admissional = '{row['observacao_admissional']}', \
                                dt_atualizado = '{data_atual}' \
                                WHERE ID = {row['ID']}"
                cursor.execute(query)

            self.conn.commit() 
            cursor.close()
            self.conn.close()

        with col3:
            if st.button('Salvar Alterações', key=90):
                # if len(filtro_ID) > 0 or filtro_nome is not None:
                if filtro_ID or filtro_nome or self.filtro.varNomeFunc:
                    update_data(tabela_editavel)
                    with col4:
                        # precisei criar uma mensagem vazia para depois deixa-la vazia novamente depois de utiliza-la
                        msg_lancamento = st.empty()
                        msg_lancamento.success("Edição realizada com Sucesso!", icon='✅')
                        time.sleep(10)
                        msg_lancamento.empty()
                else:
                    with col4:
                        msg_lancamento = st.empty()
                        msg_lancamento.error('Selecione ID ou funcionario que deseja editar!', icon="🚨")
                        time.sleep(10)
                        msg_lancamento.empty()

class FuncPagamento:
    def atualizar_df_pg_funcionario(self):
        consulta = Conexao.conecta_bd()
        self.df_pg_funcionario = consulta[10]

    def widget_pagamento(self):
        FuncCadastro.atualizar_func_cadastro()

        self.lista_tipo_pagamento = ['Salário', 'Adiantamento', 'Vale', 'Vale Transporte', 'Extra', 'Rescisão', 'Comissão', 
                                        'Férias', '13° Salário']
        
        with st.form(key='func_pagamento', clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                # Filtrando linhas onde 'data_contratacao' está preenchido, me retornando o dataframe inteiro
                funcionario_contratado = self.df_cadastro[self.df_cadastro['data_contratacao'].notna() | self.df_cadastro['data_contratacao'].notnull()]

                self.nome_funcionario = st.selectbox('Nome', funcionario_contratado['nome'],index=None, placeholder='Selecione o funcionário')
                self.data_pagamento_func = st.date_input('Data Pagamento', format='DD/MM/YYYY', value=None)
                self.tipo_pg_func = st.selectbox('Tipo Pagamento', self.lista_tipo_pagamento, index=None, 
                                                    placeholder='Selecione tipo pagamento')
            with col2:
                lista_forma_pagamento = ['Conta Salário', 'Dinheiro', 'Transferência', 'Pix', 'Cheque', 'Multa Recisória']
                self.forma_pagamento = st.selectbox('Forma de Pagamento', lista_forma_pagamento, index=None,
                                                    placeholder='Forma do pagamento')
                self.pagamento_fuc = st.number_input(label='Valor', value=float('0.00'), step=100.00, min_value=0.00, max_value=25000.00)

            submit_button = st.form_submit_button(label='Enviar')

        if submit_button:
            self.salvar_pg_funcionario()

    def salvar_pg_funcionario(self):
        if self.nome_funcionario == '' or self.nome_funcionario == None:
            # precisei criar uma mensagem vazia para depois deixa-la vazia novamente depois de utiliza-la
            msg_lancamento = st.empty()
            msg_lancamento.error('Nome de funcionário não é válido!', icon='🚨')
            time.sleep(10)
            msg_lancamento.empty()
        elif self.data_pagamento_func == '' or self.data_pagamento_func == None:
            msg_lancamento = st.empty()
            msg_lancamento.error('Data de pagamento inválida!', icon='🚨')
            time.sleep(10)
            msg_lancamento.empty()        
        elif self.pagamento_fuc <= 0:
            msg_lancamento = st.empty()
            msg_lancamento.error('Valor de pagamento inválido!', icon='🚨')
            time.sleep(10)
            msg_lancamento.empty()       
        else:
            dt_atualizo = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
            self.conecta_mysql()

            # nesse INSERT eu tenho um SELECT no final que faz o preenchimento da chave secundária ID_cadastro na tabela pg_funcionario
            # Construir a consulta SQL usando text()
            comando = text("""
                INSERT INTO pg_funcionario (nome, data_pagamento, tipo_pagamento, forma_pagamento,
                                                        valor_pago, ID_cadastro, dt_atualizado) 
                VALUES (
                    :nome, 
                    :data_pagamento_func, 
                    :tipo_pg_func, 
                    :forma_pagamento, 
                    :pagamento_fuc, 
                    (SELECT c.ID FROM cadastro_funcionario c WHERE c.nome = :nome),
                    :dt_atualizado
                )
            """)

            query = text(f"SELECT c.ID FROM cadastro_funcionario c WHERE c.nome = :nome")
            result = self.session.execute(query, {'nome': self.nome_funcionario})
            ID_cadastro = result.scalar()

            valores = {
                'nome': self.nome_funcionario,
                'data_pagamento_func': self.data_pagamento_func,
                'tipo_pg_func': self.tipo_pg_func,
                'forma_pagamento': self.forma_pagamento,
                'pagamento_fuc': self.pagamento_fuc,
                'ID_cadastro': ID_cadastro,
                'dt_atualizado': dt_atualizo
            }

            # Execute a instrução SQL usando os valores e placeholders seguros
            self.session.execute(comando, valores)
            # Confirmar a transação
            self.session.commit()
            # Fechando a sessão
            self.session.close()

            # precisei criar uma mensagem vazia para depois deixa-la vazia novamente depois de utiliza-la
            msg_lancamento = st.empty()
            msg_lancamento.success("Lançamento Realizado com Sucesso!", icon='✅')
            time.sleep(10)
            msg_lancamento.empty()
            # fazer com que apos 5 segundos a mensagem de sucesso apague PENDENTE

    def dataframe_pg_funcionario(self):
        FiltrosFuncionarios.filtros_funcionarios(self)

        self.atualizar_df_pg_funcionario()
        # Filtrando data funcionarios ativos
        data_inicial = str(self.filtro.data_inicial)
        data_final = str(self.filtro.data_final)

        self.df_pg_funcionario['data_pagamento'] = pd.to_datetime(self.df_pg_funcionario['data_pagamento'], format='%Y-%m-%d', errors='coerce')
        filtro_data_pagamento = (self.df_pg_funcionario['data_pagamento'] >= data_inicial) & (self.df_pg_funcionario['data_pagamento'] <= data_final)
        

        # criando filtro dataframe
        # Verificar se a lista 'self.filtro.varNomeFunc' está vazia
        if self.filtro.varNomeFunc:
            filtro_nome_func = self.df_pg_funcionario['nome'].isin(self.filtro.varNomeFunc)
        else:
            filtro_nome_func = pd.Series([True] * len(self.df_pg_funcionario)) # se a lista estiver vazia, considera todos os valores como verdadeiros

        # TABELAS DE CADASTRO - aplicando os filtros
        self.valores_pg_func = self.df_pg_funcionario[filtro_nome_func & filtro_data_pagamento]

    def edicao_pg_func_table(self):
        self.dataframe_pg_funcionario()
        self.lista_forma_pagamento = ['Conta Salário', 'Dinheiro', 'Transferência', 'Pix', 'Cheque', 'Multa Recisória']
        
        col1, col2, col3, col4, col5 = st.columns([1, 1.5, 1.5, 1, 3])        
        with col1:
            df = self.valores_pg_func

            filtro_ID = st.multiselect('ID', df['ID'], placeholder='', key=4)
        with col2:
            filtro_nome = st.multiselect('Nome', df['nome'], placeholder='Funcionário', key=5)
        with col3:
            data = df['data_pagamento'] = pd.to_datetime(df['data_pagamento'], errors='coerce')
            data = data.dt.strftime('%d/%m/%Y').unique()
            filtro_data = st.multiselect('Data Pagamento', df['data_pagamento'], placeholder='Data')

            if filtro_ID:
                df_filtrado = df[df['ID'].isin(filtro_ID)]
            else:
                df_filtrado = df
            df = df_filtrado

            if filtro_nome:
                df_filtrado = df[df['nome'].isin(filtro_nome)]
            else:
                df_filtrado = df
            df = df_filtrado

            if filtro_data:
                df_filtrado = df[df['data_pagamento'].isin(filtro_data)]
            else:
                df_filtrado = df
            df = df_filtrado

        # Bloquear algumas colunas da edição
        colunas_bloqueadas = {
        'dt_atualizado': {'editable': False},
        'ID': {'editable': False}
        }

        # Convert the data_contratacao column into a date data type
        df['data_pagamento'] = pd.to_datetime(df['data_pagamento'], errors='coerce')

        colunas_formatada = {
            'ID': st.column_config.NumberColumn('ID', format='%d'),
            'nome': st.column_config.TextColumn('Nome'),
            'data_pagamento': st.column_config.DateColumn('Data Pagamento', format='DD/MM/YYYY'),   
            'valor_pago': st.column_config.NumberColumn('Valor Pago', format='$ %d'),
            'tipo_pagamento': st.column_config.SelectboxColumn('Tipo de Pagamento', options=self.lista_tipo_pagamento, required=True),
            'forma_pagamento': st.column_config.SelectboxColumn('Forma de Pagamento', options=self.lista_forma_pagamento, required=True),
            'dt_atualizado': st.column_config.DatetimeColumn('Atualizado', format='DD/MM/YYYY- h:mm A'),
        }
        # num_rows = 'dynamic' é um parametro para habilitar a inclusão de linhas
        # disabled = deixa as colunas ineditavel
        tabela_editavel = st.data_editor(df, 
                                         disabled=colunas_bloqueadas, 
                                         column_config=colunas_formatada, 
                                         column_order=['ID', 'nome', 'data_pagamento', 'valor_pago', 'tipo_pagamento',
                                                        'forma_pagamento', 'dt_atualizado'], 
                                         hide_index=True)
        # st.write(df)
        # Função para atualizar dados no banco de dados
        def update_data(df):
            self.conecta_mysql2()
            cursor = self.conn.cursor()
            data_atual = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
            for index, row in df.iterrows():
                query = f"UPDATE pg_funcionario \
                            SET nome = '{row['nome']}', data_pagamento = '{row['data_pagamento']}', valor_pago = '{row['valor_pago']}', \
                                tipo_pagamento = '{row['tipo_pagamento']}', forma_pagamento = '{row['forma_pagamento']}', \
                                dt_atualizado = '{data_atual}' \
                                WHERE ID = {row['ID']}"
                cursor.execute(query)

            self.conn.commit() 
            cursor.close()
            self.conn.close()

        with col4:
            if st.button('Salvar Alterações', key=3):
                if len(filtro_ID) > 0 or len(filtro_nome) > 0 or len(filtro_data) > 0:
                    update_data(tabela_editavel)
                    with col5:
                        # precisei criar uma mensagem vazia para depois deixa-la vazia novamente depois de utiliza-la
                        msg_lancamento = st.empty()
                        msg_lancamento.success("Edição realizada com Sucesso!", icon='✅')
                        time.sleep(10)
                        msg_lancamento.empty()                    
                else:
                    with col5:
                        msg_lancamento = st.empty()
                        msg_lancamento.error('Selecione ID, nome ou data que deseja editar!', icon="🚨")
                        time.sleep(10)
                        msg_lancamento.empty()

    def tableau_pg_funcionario(self):
        # chamando a classe FuncCadastro e o metodo dataframe_cadastro
        FuncCadastro.dataframe_cadastro(self)

        df = self.valores_pg_func
        df = self.valores_pg_func.drop(['ID', 'dt_atualizado'], axis=1)

        df_cadastro_func = self.valores_cadastro.drop(['nome', 'rg', 'cpf', 'carteira_trabalho', 'endereco', 'numero', 'bairro', 'cidade',
                                                       'telefone', 'banco', 'agencia', 'conta', 'data_contratacao', 'salario', 
                                                       'documentacao_admissional', 'data_exame_admissional', 'contabilidade_admissional',
                                                       'observacao_admissional', 'data_desligamento', 'devolucao_uniforme',
                                                       'data_exame_demissional', 'data_homologacao', 'tipo_desligamento',
                                                       'contabilidade_rescisao', 'observacao_demissional', 'status_admissao', 'status_rescisao',
                                                       'dt_atualizado'], axis=1)

        # mesclando pg_funcionarios com cadastro para pegar os pagamentos por setor e cargo
        df_merged = pd.merge(df, df_cadastro_func, left_on='ID_cadastro', right_on='ID', how='left')

        df.loc[:, 'valor_pago'] = pd.to_numeric(df['valor_pago'], errors='coerce')

        df = df_merged.rename(columns={
            'nome': 'Nome',
            'data_pagamento': 'Data Pagamento',
            'valor_pago': 'Valor Pago',
            'tipo_pagamento': 'Tipo Pagamento',
            'forma_pagamento': 'Forma Pagamento',
            'setor': 'Setor',
            'cargo': 'Cargo'
        })

        df = df.drop(['ID', 'ID_cadastro'], axis=1)

        grafico_dinamico = StreamlitRenderer(df, spec="./json/pgfuncionario.json", spec_io_mode="rw")
        renderer = grafico_dinamico
        renderer.explorer()

class FuncRescisao:
    def funcionario_ativo(self):
        df_cadastro = FuncCadastro.atualizar_func_cadastro()

        self.df_funcionario_ativo = df_cadastro[df_cadastro['data_contratacao'].notna() & # valores não nulos
                                    df_cadastro['data_contratacao'].notnull() & # valores que não estão vazios
                                    df_cadastro['data_desligamento'].isna() & # valores nulos
                                    df_cadastro['data_desligamento'].isnull()] # valores vazios
        self.df_funcionario_desligado = df_cadastro[df_cadastro['data_desligamento'].notnull()] # valores que não estão vazios
    
    def widget_rescisao(self):
        lista_forma_desligamento = ['Dispensa sem justa causa', 'Demissão por justa causa', 'Pedido de demissão',
                                             'Término do contrato', 'Rescisão indireta', 'Rescisão por culpa recíproca']
        self.funcionario_ativo()

        with st.form(key='func_rescisao', clear_on_submit=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                # Filtrando linhas onde 'data_contratacao' está preenchido, me retornando o dataframe inteiro
                self.nome_funcionario = st.selectbox('Nome', self.df_funcionario_ativo['nome'],
                                                        index=None, 
                                                        placeholder='Funcionário'
                                                     )
                self.entrega_uniforme = st.selectbox('Uniforme', ['Entregue', 'Pendente'], 
                                                        index=None, 
                                                        placeholder='Escolha uma opção',
                                                        help='Confirmação da entrega do uniforme pelo funcionário'
                                                        )   
                self.exame_demissional = st.date_input('Exame Demissional',
                                                        format='DD/MM/YYYY', 
                                                        value=None,
                                                        help='Data do exame demissinal'
                                                        )
            with col2:
                self.doc_contabilidade = st.selectbox('Documentação Contabilidade', ['Entregue', 'Pendente'],
                                                        index=None,
                                                        placeholder='Selecione Status',
                                                        help='Todos documentos entregue para contabilidade'
                                                        )
                self.data_desligamento = st.date_input('Data desligamento',
                                                       format='DD/MM/YYYY',
                                                       value=None
                                                       )
                self.homologacao = st.date_input('Data homologação',
                                                        format='DD/MM/YYYY',
                                                        value=None)   
            with col3:
                self.forma_desligamento = st.selectbox('Forma Desligamento', lista_forma_desligamento, 
                                                        placeholder='Escolha uma opção',
                                                        index=None)
               
                self.status_rescisao = st.selectbox('Status rescisão', ['Pendente', 'Concluído'],
                                                        index=None,
                                                        placeholder='Escolha uma opção',
                                                        help='Situação da rescisão do funcionário'
                                                        )
                self.observacao_rescisao = st.text_input(label='Obersação')

            submit_button = st.form_submit_button(label='Enviar')

        if submit_button:
            self.salvar_rescisao()
        
    def salvar_rescisao(self):
        # FiltrosFuncionarios.filtros_funcionarios(self)
        if self.nome_funcionario == '' or self.nome_funcionario == None:
            msg_lancamento = st.empty()
            msg_lancamento.error('Nome de funcionário não é válido!', icon='🚨')
            time.sleep(10)
            msg_lancamento.empty()
        elif self.data_desligamento == '' or self.data_desligamento == None:
            msg_lancamento = st.empty()
            msg_lancamento.error('Data de desligamento inválida!', icon="🚨")
            time.sleep(10)
            msg_lancamento.empty()
        else:
            dt_atualizo = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
            self.conecta_mysql()
            
            metadata = MetaData()
            rescisao_func_table = Table('cadastro_funcionario', metadata,
                Column('ID', Integer, primary_key=True),
                Column('nome', String),
                Column('devolucao_uniforme', String),
                Column('data_exame_demissional', String),
                Column('contabilidade_rescisao', String),
                Column('data_desligamento', DateTime),
                Column('data_homologacao', DateTime),
                Column('status_rescisao', String),
                Column('tipo_desligamento', String),
                Column('observacao_demissional', String),
                Column('dt_atualizado', DateTime)
            )

            # Definindo os valores para inserção
            valores = {
                'nome': self.nome_funcionario,
                'devolucao_uniforme': self.entrega_uniforme,
                'data_exame_demissional': self.exame_demissional,
                'contabilidade_rescisao': self.doc_contabilidade,
                'data_desligamento': self.data_desligamento,
                'data_homologacao': self.homologacao,
                'status_rescisao': self.status_rescisao,
                'tipo_desligamento': self.forma_desligamento,
                'observacao_demissional': self.observacao_rescisao,
                'dt_atualizado': dt_atualizo
            }

            # Criando uma instrução de INSERT
            stmt = update(rescisao_func_table).where(rescisao_func_table.c.nome == self.nome_funcionario).values(valores)
            # Executando a instrução de INSERT
            self.session.execute(stmt)
            # Confirmar a transação
            self.session.commit()
            # Fechando a sessão
            self.session.close()
            print('Fechou conexão')

            # precisei criar uma mensagem vazia para depois deixa-la vazia novamente depois de utiliza-la
            msg_lancamento = st.empty()
            msg_lancamento.success("Lançamento Realizado com Sucesso!", icon='✅')
            time.sleep(10)
            msg_lancamento.empty()
            # fazer com que apos 5 segundos a mensagem de sucesso apague PENDENTE

    def dataframe_rescisao(self):
        FiltrosFuncionarios.filtros_funcionarios(self)
        # df = self.df_funcionario_ativo[self.filtro_nome_func & self.filtro_data_contratacao & self.filtro_cargo & self.filtro_setor]
        self.df_rescisao = self.df_funcionario_desligado.drop(['setor', 'rg', 'cpf', 'carteira_trabalho', 'endereco', 'numero',
                                    'bairro', 'cidade', 'telefone', 'banco', 'agencia', 'conta',
                                    'data_contratacao', 'setor', 'cargo','salario', 'documentacao_admissional',
                                    'data_exame_admissional', 'contabilidade_admissional', 
                                    'observacao_admissional'], axis=1)
        
    def edicao_rescisao_table(self):
        self.dataframe_rescisao()
        
        col1, col2, col3, col4 = st.columns([1, 1.5, 1.5, 3])        
        with col1:
            df = self.df_rescisao          
            filtro_ID = st.multiselect('ID', df['ID'], placeholder='', key=6)
        with col2:
            filtro_nome = st.multiselect('Nome', df['nome'], placeholder='Funcionário', key=7)

            if filtro_ID:
                df_filtrado = df[df['ID'].isin(filtro_ID)]
            else:
                df_filtrado = df
            df = df_filtrado

            if filtro_nome:
                df_filtrado = df[df['nome'].isin(filtro_nome)]
            else:
                df_filtrado = df
            df = df_filtrado

        # Bloquear algumas colunas da edição
        colunas_bloqueadas = {
        'dt_atualizado': {'editable': False},
        'ID': {'editable': False}
        }

        # Convert the data_contratacao column into a date data type
        df['data_desligamento'] = pd.to_datetime(df['data_desligamento'], errors='coerce')
        df['data_exame_demissional'] = pd.to_datetime(df['data_exame_demissional'], errors='coerce')
        df['data_homologacao'] = pd.to_datetime(df['data_homologacao'], errors='coerce')

        colunas_formatada = {
            'ID': st.column_config.NumberColumn('ID', format='%d'),
            'data_desligamento': st.column_config.DateColumn('Data Desligamento', format='DD/MM/YYYY'),
            'nome': st.column_config.TextColumn('Nome'),
            'tipo_desligamento': st.column_config.SelectboxColumn('Forma Desligamento', options=self.lista_forma_pagamento, required=True),
            'tipo_pagamento':st.column_config.SelectboxColumn('Pagamento', options=self.lista_tipo_pagamento, required=True),
            'data_exame_demissional': st.column_config.DateColumn('Exame Demissional', format='DD/MM/YYYY'),
            'data_homologacao': st.column_config.DateColumn('Homologação', format='DD/MM/YYYY'),
            'status_rescisao': st.column_config.SelectboxColumn('Status Rescisão', options=['Pendente', 'Concluído'], required=True),
            'devolucao_uniforme': st.column_config.SelectboxColumn('Devolução Uniforme', options=['Entregue', 'Pendente'], required=True),
            'observacao_demissional': st.column_config.TextColumn('Obervação'),
            'dt_atualizado': st.column_config.DatetimeColumn('Atualizado', format='DD/MM/YYYY- h:mm A'),
        }
        # num_rows = 'dynamic' é um parametro para habilitar a inclusão de linhas
        # disabled = deixa as colunas ineditavel
        tabela_editavel = st.data_editor(df, 
                                         disabled=colunas_bloqueadas, 
                                         column_config=colunas_formatada, 
                                         column_order=['ID', 'nome', 'data_desligamento', 'tipo_desligamento', 'tipo_pagamento',
                                                        'data_exame_demissional', 'data_homologacao', 'status_rescisao',
                                                        'devolucao_uniforme', 'observacao_demissional', 'dt_atualizado'], 
                                         hide_index=True)
        # Função para atualizar dados no banco de dados
        def update_data(df):
            self.conecta_mysql2()
            cursor = self.conn.cursor()
            data_atual = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
            for index, row in df.iterrows():
                query = f"UPDATE cadastro_funcionario \
                            SET nome = '{row['nome']}', data_desligamento = '{row['data_desligamento']}', \
                              tipo_desligamento = '{row['tipo_desligamento']}', data_exame_demissional = '{row['data_exame_demissional']}' \
                              data_exame_demissional = '{row['data_exame_demissional']}', data_homologacao = '{row['data_homologacao']}', \
                              status_rescisao = '{row['status_rescisao']}', 'devolucao_uniforme' = '{row['devolucao_uniforme']}', \
                              'observacao_demissional' = '{row['observacao_demissional']}', dt_atualizado = '{data_atual}' \
                            WHERE ID = {row['ID']}"
                cursor.execute(query)

            self.conn.commit() 
            cursor.close()
            self.conn.close()

        with col3:
            if st.button('Salvar Alterações', key=8):
                if len(filtro_ID) > 0:
                    update_data(tabela_editavel)
                    with col4:
                        # precisei criar uma mensagem vazia para depois deixa-la vazia novamente depois de utiliza-la
                        msg_lancamento = st.empty()
                        msg_lancamento.success("Edição realizada com Sucesso!", icon='✅')
                        time.sleep(10)
                        msg_lancamento.empty()
                else:
                    with col4:
                        msg_lancamento = st.empty()
                        msg_lancamento.error('Selecione ID que deseja editar!', icon="🚨")
                        time.sleep(10)
                        msg_lancamento.empty()

class FuncResumo:
    def card_resumo_Fuc(self):
        self.dataframe_vendas()
        self.funcionario_ativo()
        consulta = FuncCadastro.atualizar_func_cadastro()
        self.df_cadastro = consulta
    
        # Filtrando data
        data_inicial = self.filtro.data_inicial
        data_final = self.filtro.data_final

        df_data_func_ativo = (self.df_funcionario_ativo['data_contratacao'] >= data_inicial) & (self.df_funcionario_ativo['data_contratacao'] <= data_final)
        df_data_func_contratado = (self.df_cadastro['data_contratacao'] >= data_inicial) & (self.df_cadastro['data_contratacao'] <= data_final)
        df_data_func_demitido = (self.df_cadastro['data_desligamento'] >= data_inicial) & (self.df_cadastro['data_desligamento'] <= data_final)

        # Aplicando os filtros
        df_ativo_func = self.df_funcionario_ativo[df_data_func_ativo]
        df_contratado_func = self.df_cadastro[df_data_func_contratado]
        df_desliga_func = self.df_cadastro[df_data_func_demitido]
        
        # dataframe pg_funcionario
        self.dataframe_pg_funcionario()
        df = self.valores_pg_func
        df['valor_pago'] = pd.to_numeric(df['valor_pago'])
        pg_funcionarios = df.loc[df['tipo_pagamento'] != 'rescisao', 'valor_pago'].sum()
        rescisao = df.loc[df['tipo_pagamento'] == 'rescisao', 'valor_pago'].sum()

        percentual_mo = (float(pg_funcionarios) / self.total_vendas * 100) if self.total_vendas != 0 else 0.0
        percentual_rescisao = (float(rescisao) / self.total_vendas * 100) if self.total_vendas != 0 else 0.0

        # widgets
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric('Funcionário Ativo', '{}'.format(int(df_ativo_func.shape[0])))
        col2.metric('Funcionário Contratado', '{}'.format(int(df_contratado_func.shape[0])))
        col3.metric('Funcionário Desligado', '{}'.format(int(df_desliga_func.shape[0])))
        col4.metric('Pagamento de Funcionário', '$ {:.2f}'.format(pg_funcionarios), '{:.2f}%'.format(percentual_mo))
        col5.metric('Pagamento de Rescisão', '$ {:.2f}'.format(rescisao), '{:.2f}%'.format(percentual_rescisao))

        
        # Agrupando colunas
        grupo_nome = df.groupby('nome')
        grupo_tipo_pagamento = df.groupby('tipo_pagamento')

        # Calcular a soma de salário para cada grupo de nomes e deixando valor com 2 casas decimais
        pg_funcionario = grupo_nome['valor_pago'].sum().apply(lambda x: '{:.2f}'.format(x))
        pg_tipo_pagamento = grupo_tipo_pagamento['valor_pago'].sum().apply(lambda x: '{:.2f}'.format(x))

        # Renomear as colunas
        pg_funcionario = pg_funcionario.reset_index()  # Resetar o índice para transformar o resultado em DataFrame
        pg_funcionario = pg_funcionario.rename(columns={'nome': 'Nome', 'valor_pago': 'Valor Pago'})

        pg_tipo_pagamento = pg_tipo_pagamento.reset_index()
        pg_tipo_pagamento = pg_tipo_pagamento.rename(columns={'tipo_pagamento': 'Tipo Pagamento', 'valor_pago': 'Valor Pago'})     

        dropar_colunas = ["ID_x", "nome_x", "rg", "cpf", "carteira_trabalho", "endereco", "numero", "bairro", "cidade",
                          "telefone", "banco", "agencia", "conta", "data_contratacao", "salario", "documentacao_admissional",
                          "data_exame_admissional", "contabilidade_admissional", "observacao_admissional", "data_desligamento",
                          "devolucao_uniforme", "data_exame_demissional", "data_homologacao", "tipo_desligamento",
                          "contabilidade_rescisao", "observacao_demissional", "status_admissao", "status_rescisao",
                          "dt_atualizado_x", "ID_y", "nome_y", "data_pagamento", "forma_pagamento", "dt_atualizado_y"]

        # Agrupando tabelas
        # Mesclar os DataFrames com base no ID
        df_merge = pd.merge(df_ativo_func, df, left_on='ID', right_on='ID_cadastro')
        df_merge = pd.merge(self.df_cadastro, df, left_on='ID', right_on='ID_cadastro') #.drop(dropar_colunas, axis=1)

        # Agrupar por setor e calcular a soma dos valores pagos em cada setor
        pagamento_por_setor = df_merge.groupby('setor')['valor_pago'].sum()
        pagamento_por_cargo = df_merge.groupby('cargo')['valor_pago'].sum()

        pagamento_por_setor = pd.DataFrame(pagamento_por_setor)
        pagamento_por_cargo = pd.DataFrame(pagamento_por_cargo)

        # Renomear colunas
        pagamento_por_setor = pagamento_por_setor.reset_index()
        pagamento_por_setor = pagamento_por_setor.rename(columns={'setor': 'Setor', 'valor_pago': 'Valor Pago'})

        pagamento_por_cargo = pagamento_por_cargo.reset_index()
        pagamento_por_cargo = pagamento_por_cargo.rename(columns={'cargo': 'Cargo', 'valor_pago': 'Valor Pago'})
        
        pg_funcionario['Valor Pago'] = pd.to_numeric(pg_funcionario['Valor Pago'])
        pg_tipo_pagamento['Valor Pago'] = pd.to_numeric(pg_tipo_pagamento['Valor Pago'])
        pagamento_por_cargo['Valor Pago'] = pd.to_numeric(pagamento_por_cargo['Valor Pago'])
        pagamento_por_setor['Valor Pago'] = pd.to_numeric(pagamento_por_setor['Valor Pago'])

        coluna_formatada = {'Valor Pago': st.column_config.NumberColumn('Valor Pago', format='$ %f')}

        # tabelas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            # st.write('Funcionário')
            st.dataframe(pg_funcionario, column_config=coluna_formatada)
        with col2:
            # st.write('Cargo')
            st.dataframe(pagamento_por_cargo, column_config=coluna_formatada, hide_index=True)
        with col3:
            # st.write('Tipo de pagamento')
            st.dataframe(pg_tipo_pagamento, column_config=coluna_formatada, hide_index=True)
        with col4:
            # st.write('Setor') 
            st.dataframe(pagamento_por_setor, column_config=coluna_formatada, hide_index=True)