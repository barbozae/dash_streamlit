import pandas as pd
import streamlit as st


class CarregarTabela:
    @st.cache_data
    def tabela_vendas(self):
        # para usar com pandas, utilizando a função with a conexão é fechada automáticamente
        with self.engine.connect() as connection:
            self.df_vendas = pd.read_sql(("SELECT ID, data_venda, periodo, qtd_rodizio, dinheiro, pix, debito_mastercard, debito_visa,"
                                    " debito_elo, credito_mastercard, credito_visa, credito_elo, hiper, american_express, alelo, dt_atualizado"
                                    " FROM vendas ORDER BY ID DESC"), connection)

        self.conecta_bd()
        # carregamento lista de vendas
        lista = f""" SELECT ID, data_venda, periodo, qtd_rodizio, dinheiro, pix, debito_mastercard, debito_visa, 
            debito_elo, credito_mastercard, credito_visa, credito_elo, hiper, american_express, alelo, dt_atualizado
            FROM vendas ORDER BY ID DESC; """
        
        self.tabelavendas = pd.read_sql(lista, self.conexao)

        # Desconectando da base
        self.desconecta_bd()
