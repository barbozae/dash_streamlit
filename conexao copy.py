import streamlit as st
import pyodbc
import mysql.connector
from sqlalchemy import create_engine
import pandas as pd


class Conexao:
    
    def conecta_bd(self): # utilizando sqlalchemy
        # usuario -> : -> senha -> @ -> host -> / -> banco de dados
        # substitua 'mysql_user', 'mysql_pwd', 'mysql_host', 'mysql_db' pelos seus dados
        #engine = create_engine('mysql+mysqlconnector://mysql_user:mysql_pwd@mysql_host/mysql_db')
        engine = create_engine('''mysql+mysqlconnector://
                                    yxvnub0tjz2q91z2:qn452lhidcwsv3a0@
                                    grp6m5lz95d9exiz.cbetxkdyhwsb.us-east-1.rds.amazonaws.com/
                                    z8308a2l1w09zs3e''')
        
        # para usar com pandas, utilizando a função with a conexão é fechada automáticamente
        with engine.connect() as connection:
            self.df_vendas = pd.read_sql(("SELECT data_venda, dinheiro, pix, debito_mastercard, debito_visa, debito_elo, credito_mastercard,"
                                            "credito_visa, credito_elo, hiper, american_express, alelo, sodexo, ticket_rest," 
                                            "vale_refeicao, dinersclub, qtd_rodizio, socio, periodo, dt_atualizado, ID"
                                            " FROM vendas ORDER BY ID DESC"), connection)
        return self.df_vendas
    
    
    def conecta_mysql(self):
        self.dados_conexao = ("DRIVER={MySQL ODBC 8.0 Unicode Driver};"
                        "SERVER=grp6m5lz95d9exiz.cbetxkdyhwsb.us-east-1.rds.amazonaws.com;"  #host
                        "DATABASE=z8308a2l1w09zs3e;"     #banco de dados 
                        "UID=yxvnub0tjz2q91z2;"                  #usuario
                        "PASSWORD=qn452lhidcwsv3a0;")                  #senha
        
        self.conexao = pyodbc.connect(self.dados_conexao)
        self.cursor = self.conexao.cursor()


    def conecta_mysql2(self): # 
        self.conn = mysql.connector.connect(
        host= 'grp6m5lz95d9exiz.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',
        user='yxvnub0tjz2q91z2',
        password='qn452lhidcwsv3a0',
        database='z8308a2l1w09zs3e')


    def desconecta_bd(self):
        self.cursor.close()
        self.conexao.close()