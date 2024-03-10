import streamlit as st
import pyodbc
import mysql.connector
from sqlalchemy import create_engine
import pandas as pd


class Conexao:
    @classmethod
    @st.cache_data
    def conecta_bd(cls): # utilizando sqlalchemy
        # usuario -> : -> senha -> @ -> host -> / -> banco de dados
        # substitua 'mysql_user', 'mysql_pwd', 'mysql_host', 'mysql_db' pelos seus dados
        #engine = create_engine('mysql+mysqlconnector://mysql_user:mysql_pwd@mysql_host/mysql_db')
        engine = create_engine('''mysql+mysqlconnector://
                                    yxvnub0tjz2q91z2:qn452lhidcwsv3a0@
                                    grp6m5lz95d9exiz.cbetxkdyhwsb.us-east-1.rds.amazonaws.com/
                                    z8308a2l1w09zs3e''')
        
        # para usar com pandas, utilizando a função with a conexão é fechada automáticamente
        # with engine.connect() as connection:
            # df_vendas = pd.read_sql(("SELECT data_venda, dinheiro, pix, debito_mastercard, debito_visa, debito_elo, credito_mastercard,"
            #                                 "credito_visa, credito_elo, hiper, american_express, alelo, sodexo, ticket_rest," 
            #                                 "vale_refeicao, dinersclub, qtd_rodizio, socio, periodo, dt_atualizado, ID"
            #                                 " FROM vendas ORDER BY ID DESC"), connection)
            
        # Realizar consulta na tabela vendas
        query_vendas = """
            SELECT data_venda, dinheiro, pix, debito_mastercard, debito_visa, debito_elo, credito_mastercard,
                credito_visa, credito_elo, hiper, american_express, alelo, sodexo, ticket_rest, vale_refeicao,
                dinersclub, qtd_rodizio, socio, periodo, dt_atualizado, ID
            FROM vendas
            ORDER BY ID DESC
        """

        query_compras = """SELECT data_compra, data_vencimento, data_pagamento, fornecedor, valor_compra, valor_pago,
                qtd, numero_boleto, grupo_produto, produto, classificacao, forma_pagamento, observacao, dt_atualizado, ID
                FROM compras 
                ORDER BY ID DESC"""

        query_func_cadastro = """ SELECT ID, nome, rg, cpf, carteira_trabalho, endereco, numero, bairro, cidade, telefone,
                banco, agencia, conta, data_contratacao, setor, cargo, salario, documentacao_admissional, data_exame_admissional,
                contabilidade_admissional, observacao_admissional, data_desligamento, devolucao_uniforme, data_exame_demissional,
                data_homologacao, tipo_desligamento, contabilidade_rescisao, observacao_demissional, status_admissao, status_rescisao,
                dt_atualizado
                FROM cadastro_funcionario
                ORDER BY ID DESC """
        
        query_func_pg_func = """ SELECT ID, nome, data_pagamento, valor_pago, tipo_pagamento, forma_pagamento, dt_atualizado, ID_cadastro
                                FROM pg_funcionario
                                ORDER BY ID DESC """

        # Conectar e executar a consulta
        with engine.connect() as connection:
            df_vendas = pd.read_sql(query_vendas, connection)
        with engine.connect() as connection:
            df_compras = pd.read_sql(query_compras, connection)
        with engine.connect() as connection:
            df_cadastro_funcionarios = pd.read_sql(query_func_cadastro, connection)
        with engine.connect() as connection:
            df_pg_funcionario = pd.read_sql(query_func_pg_func, connection)
            
        fornecedor = df_compras['fornecedor'].unique()
        grupo_produto = df_compras['grupo_produto'].unique()
        classificacao = df_compras['classificacao'].unique()
        numero_boleto = df_compras['numero_boleto'].unique()
        produto = df_compras['produto'].unique()
        id_compra = df_compras['ID'].unique()
        nome_funcionario = df_cadastro_funcionarios['nome'].unique()

        # Mostrar o DataFrame resultante
        return (df_vendas, # df_vendas
                df_compras, fornecedor, grupo_produto, classificacao, numero_boleto, produto, id_compra, # df_compras
                df_cadastro_funcionarios, nome_funcionario, # df_cadastro_funcionarios
                df_pg_funcionario #df_pagamento dos funcionarios
                )
    
    # @classmethod
    # @st.cache_data
    def conecta_mysql(self):
        self.dados_conexao = ("DRIVER={MySQL ODBC 8.0 Unicode Driver};"
                                "SERVER=grp6m5lz95d9exiz.cbetxkdyhwsb.us-east-1.rds.amazonaws.com;"  #host
                                "DATABASE=z8308a2l1w09zs3e;"     #banco de dados 
                                "UID=yxvnub0tjz2q91z2;"                  #usuario
                                "PASSWORD=qn452lhidcwsv3a0;")                  #senha
        
        self.conexao = pyodbc.connect(self.dados_conexao)
        self.cursor = self.conexao.cursor()


    # @classmethod
    # # @st.cache_data
    def conecta_mysql2(self): 
        self.conn = mysql.connector.connect(
        host= 'grp6m5lz95d9exiz.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',
        user='yxvnub0tjz2q91z2',
        password='qn452lhidcwsv3a0',
        database='z8308a2l1w09zs3e')


    def desconecta_bd(self):
        self.cursor.close()
        self.conexao.close()