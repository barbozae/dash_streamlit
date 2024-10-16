import streamlit as st
from pygwalker.api.streamlit import StreamlitRenderer
import pandas as pd
import numpy as np
import time
# from millify import millify
from datetime import datetime
from filtro import Filtros
from conexao import Conexao
from sqlalchemy import text, select, insert, Table, MetaData, Column, Integer, String, DateTime


class Compras: 
    def __init__(self) -> None:
        self.filtro = Filtros()

    def atualizar():
        consulta = Conexao.conecta_bd()
        df_compras = consulta[1]
        df_fornecedor = consulta[11]
        classificacao = ['CMV', 'Gasto Fixo', 'Gasto Variável']
        return df_compras, df_fornecedor, classificacao
    
    def navegacao_compras(self):
        consulta = Compras.atualizar()
        self.df_fornecedor = consulta[1]

        df = self.df_fornecedor.rename(columns={
            'nome_empresa': 'Empresa',
            'cnpj': 'CNPJ',
            'nome_contato': 'Contato',
            'telefone': 'Telefone',
            'email': 'E-mail',
            'endereco': 'Endereço',
            'cep': 'CEP',
            'numero': 'Número',
            'bairro': 'Bairro',
            'dt_atualizado': 'Atualizado em:'
        })

        tab1, tab2, tab3 = st.tabs(["Resumo", "Lançamento", "Cadastro Fornecedor"])
        with tab1:
            self.cards_resumo_compras()
            self.caixas_expansivas()

        with tab2:
            with st.expander('Lançamento Compras', expanded=True):
                self.widget_compras()
            with st.expander('Edição Compras', expanded=False):
                self.lancamento_compras_table()
        
        with tab3:
            with st.expander('Cadastro Fornecedor', expanded=True):
                self.widget_cadastro_fornecedor()
            with st.expander('Tabela dos Fornecedores', expanded=False):
                st.dataframe(df)
            with st.expander('Edição do Cadastro do Fornecedor', expanded=False):
                self.lacamento_fornecedor_table()

    def indicadores_compras(self):
        consulta = Compras.atualizar()
        self.df_compras = consulta[0]

        # Utilizado no arquivo resumo
        # Filtrando data
        data_inicial = self.filtro.data_inicial     # formato da data'2023-05-01'
        data_final = self.filtro.data_final
        filtro_data_compras = (self.df_compras['data_compra'] >= data_inicial) & (self.df_compras['data_compra'] <= data_final)
    
        valores_classificacao = self.df_compras[filtro_data_compras]

        # Filtrando as linhas onde a coluna 'classificacao' é igual a 'cmv'
        cmv = valores_classificacao[valores_classificacao['classificacao'] == 'CMV']
        # Drop das colunas desnecessárias
        cmv = cmv.drop(['data_compra', 'data_vencimento', 'data_pagamento', 'valor_pago', 'fornecedor', 'qtd', 
                                        'numero_boleto', 'grupo_produto', 'produto', 'classificacao', 'forma_pagamento', 
                                        'observacao', 'dt_atualizado', 'ID'], axis=1)
        # self.cmv = cmv.astype(float).sum()

        gasto_fixo = valores_classificacao[valores_classificacao['classificacao'] == 'Gasto Fixo']
        # Drop das colunas desnecessárias
        gasto_fixo = gasto_fixo.drop(['data_compra', 'data_vencimento', 'data_pagamento', 'valor_pago', 'fornecedor', 'qtd', 
                                                    'numero_boleto', 'grupo_produto', 'produto', 'classificacao', 'forma_pagamento', 
                                                    'observacao', 'dt_atualizado', 'ID'], axis=1)

        gasto_variavel = valores_classificacao[valores_classificacao['classificacao'] == 'Gasto Variável']
        # Drop das colunas desnecessárias
        gasto_variavel = gasto_variavel.drop(['data_compra', 'data_vencimento', 'data_pagamento', 'valor_pago', 'fornecedor', 'qtd', 
                                                    'numero_boleto', 'grupo_produto', 'produto', 'classificacao', 'forma_pagamento', 
                                                    'observacao', 'dt_atualizado', 'ID'], axis=1)
        array_cmv = np.array(cmv)
        array_gasto_fixo = np.array(gasto_fixo)
        array_gasto_variavel = np.array(gasto_variavel)
        
        # substiturir valores vazios por nan e assim converter valores para float
        array_cmv[array_cmv == ''] = 0
        array_cmv = array_cmv.astype(float) 

        array_gasto_fixo[array_gasto_fixo == ''] = 0
        array_gasto_fixo = array_gasto_fixo.astype(float)

        array_gasto_variavel[array_gasto_variavel == ''] = 0
        array_gasto_variavel = array_gasto_variavel.astype(float)

        # Somando todas as linhas por colunas
        # somando cada coluna da array -> exemplo [279, 1548, 1514, 4848...] -> cada valor é o total de cada coluna
        self.cmv = np.nansum(array_cmv, axis=0)
        self.gasto_fixo = np.nansum(array_gasto_fixo, axis=0)
        self.gasto_variavel = np.nansum(array_gasto_variavel, axis=0)

    def dataframe_compras(self):
        tabela = Compras.atualizar()
        self.df_compras = tabela[0]

        # Filtrando data
        data_inicial = self.filtro.data_inicial     # formato da data'2023-05-01'
        data_final = self.filtro.data_final
        filtro_data_compras = (self.df_compras['data_compra'] >= data_inicial) & (self.df_compras['data_compra'] <= data_final)
   
        # filtrando fornecedor
        # Verificar se a lista 'self.filtro.varFornecedor' está vazia
        if self.filtro.varFornecedor:
            filtro_fornecedor = self.df_compras['fornecedor'].isin(self.filtro.varFornecedor)
        else:
            filtro_fornecedor = pd.Series([True] * len(self.df_compras)) # se a lista estiver vazia, considera todos os valores como verdadeiros  
      
        if self.filtro.varClassificacao:
            filtro_classificacao = self.df_compras['classificacao'].isin(self.filtro.varClassificacao)
        else:
            filtro_classificacao = pd.Series([True] * len(self.df_compras)) # se a lista estiver vazia, considera todos os valores como verdadeiros

        if self.filtro.varGrupoProduto:
            filtro_grupo_produto = self.df_compras['grupo_produto'].isin(self.filtro.varGrupoProduto)
        else:
            filtro_grupo_produto = pd.Series([True] * len(self.df_compras)) # se a lista estiver vazia, considera todos os valores como verdadeiros
        
        if self.filtro.varProduto:
            filtro_produto = self.df_compras['produto'].isin(self.filtro.varProduto)
        else:
            filtro_produto = pd.Series([True] * len(self.df_compras))

        if self.filtro.varNumeroBoleto:
            filtro_boleto = self.df_compras['numero_boleto'].isin(self.filtro.varNumeroBoleto)
        else:
            filtro_boleto = pd.Series([True] * len(self.df_compras)) 

        if self.filtro.varIDCompra:
            filtro_ID_compra = self.df_compras['ID'].isin(self.filtro.varIDCompra)
        else:
            filtro_ID_compra = pd.Series([True] * len(self.df_compras)) # se a lista estiver vazia, considera todos os valores como verdadeiros

        if self.filtro.varFormaPagamento:
            filtro_forma_pagamento = self.df_compras['forma_pagamento'].isin(self.filtro.varFormaPagamento)
        else:
            filtro_forma_pagamento = pd.Series([True] * len(self.df_compras))
                   
        # TABELAS COMPRAS - aplicando os filtros data e fornecedor
        self.valores_compras = self.df_compras[filtro_data_compras & filtro_fornecedor & filtro_classificacao & 
                                          filtro_grupo_produto & filtro_produto & filtro_boleto & filtro_ID_compra &
                                          filtro_forma_pagamento]
 
        df_compras_valores = self.valores_compras.drop(['data_compra', 'data_vencimento', 'data_pagamento','fornecedor', 'qtd', 
                                                        'numero_boleto', 'grupo_produto', 'produto', 'classificacao','forma_pagamento', 
                                                        'observacao', 'dt_atualizado', 'ID'], axis=1)
       
        array_compra = np.array(df_compras_valores)

        # garantir que array esta como string e assim poder aplicar replace
        array_compra = array_compra.astype(str)
        array_compra = np.char.replace(array_compra, ',', '.') 
        
        # substiturir valores vazios por nan e assim converter valores para float
        array_compra[array_compra == ''] = 0
        # Substituir 'None' por np.nan
        array_compra = array_compra.astype(float)

        # Somando todas as linhas por colunas
        # somando cada coluna da array -> exemplo [279, 1548, 1514, 4848...] -> cada valor é o total de cada coluna
        self.valor_compras = np.nansum(array_compra, axis=0)
  
    def dataframe_pagamentos(self):
        tabela = Compras.atualizar()
        self.df_compras = tabela[0]
    
        # Filtrando data
        data_inicial = self.filtro.data_inicial     # formato da data'2023-05-01'
        data_final = self.filtro.data_final
        df_pagamentos = self.df_compras

        filtro_data_pagamentos = (df_pagamentos['data_pagamento'] >= data_inicial) & (df_pagamentos['data_pagamento'] <= data_final)
        
        # filtrando fornecedor
        # Verificar se a lista 'self.filtro.varFornecedor' está vazia
        if self.filtro.varFornecedor:
            filtro_fornecedor = df_pagamentos['fornecedor'].isin(self.filtro.varFornecedor)
        else:
            filtro_fornecedor = pd.Series([True] * len(df_pagamentos)) # se a lista estiver vazia, considera todos os valores como verdadeiros  
        
        if self.filtro.varClassificacao:
            filtro_classificacao = df_pagamentos['classificacao'].isin(self.filtro.varClassificacao)
        else:
            filtro_classificacao = pd.Series([True] * len(df_pagamentos)) # se a lista estiver vazia, considera todos os valores como verdadeiros

        if self.filtro.varGrupoProduto:
            filtro_grupo_produto = df_pagamentos['grupo_produto'].isin(self.filtro.varGrupoProduto)
        else:
            filtro_grupo_produto = pd.Series([True] * len(df_pagamentos)) # se a lista estiver vazia, considera todos os valores como verdadeiros
        
        if self.filtro.varProduto:
            filtro_produto = df_pagamentos['produto'].isin(self.filtro.varProduto)
        else:
            filtro_produto = pd.Series([True] * len(df_pagamentos))

        if self.filtro.varNumeroBoleto:
            filtro_boleto = df_pagamentos['numero_boleto'].isin(self.filtro.varNumeroBoleto)
        else:
            filtro_boleto = pd.Series([True] * len(df_pagamentos)) # se a lista estiver vazia, considera todos os valores como verdadeiros

        if self.filtro.varIDCompra:
            filtro_ID_compra = df_pagamentos['ID'].isin(self.filtro.varIDCompra)
        else:

            filtro_ID_compra = pd.Series([True] * len(self.df_compras))

        if self.filtro.varFormaPagamento:
            filtro_forma_pagamento = self.df_compras['forma_pagamento'].isin(self.filtro.varFormaPagamento)
        else:
            filtro_forma_pagamento = pd.Series([True] * len(self.df_compras))
    
        # TABELAS DE PAGAMENTOS - aplicando os filtros
        self.valores_pagamentos = df_pagamentos[filtro_data_pagamentos & filtro_fornecedor & filtro_classificacao & 
                                                filtro_grupo_produto & filtro_produto & filtro_boleto & filtro_ID_compra &
                                                filtro_forma_pagamento]

        # total de pagamentos
        df_pagamentos_valores = self.valores_pagamentos.drop(['data_compra', 'data_vencimento', 'data_pagamento','fornecedor', 'qtd', 
                                                           'numero_boleto', 'grupo_produto', 'produto', 'classificacao','forma_pagamento', 
                                                           'observacao', 'dt_atualizado', 'ID', 'valor_compra'], axis=1)
    
        self.array_pagamentos = np.array(df_pagamentos_valores)

        # garantir que array esta como string e assim poder aplicar replace
        self.array_pagamentos = self.array_pagamentos.astype(str)
        self.array_pagamentos = np.char.replace(self.array_pagamentos, ',', '.')    
        
        # substiturir valores vazios por nan e assim converter valores para float
        self.array_pagamentos[self.array_pagamentos == ''] = 0
        self.array_pagamentos = self.array_pagamentos.astype(float)

        # Somando todas as linhas por colunas
        # somando cada coluna da array -> exemplo [279, 1548, 1514, 4848...] -> cada valor é o total de cada coluna
        self.valor_pagamentos = np.nansum(self.array_pagamentos, axis=0)

    def dataframe_vencimento(self):
        # Filtrando data
        data_inicial = self.filtro.data_inicial     # formato da data'2023-05-01'
        data_final = self.filtro.data_final

        filtro_data_vencimento = (self.df_compras['data_vencimento'] >= data_inicial) & (self.df_compras['data_vencimento'] <= data_final)
   
        # filtrando fornecedor
        # Verificar se a lista 'self.filtro.varFornecedor' está vazia
        if self.filtro.varFornecedor:
            filtro_fornecedor = self.df_compras['fornecedor'].isin(self.filtro.varFornecedor)
        else:
            filtro_fornecedor = pd.Series([True] * len(self.df_compras)) # se a lista estiver vazia, considera todos os valores como verdadeiros  
        
        if self.filtro.varClassificacao:
            filtro_classificacao = self.df_compras['classificacao'].isin(self.filtro.varClassificacao)
        else:
            filtro_classificacao = pd.Series([True] * len(self.df_compras)) # se a lista estiver vazia, considera todos os valores como verdadeiros

        if self.filtro.varGrupoProduto:
            filtro_grupo_produto = self.df_compras['grupo_produto'].isin(self.filtro.varGrupoProduto)
        else:
            filtro_grupo_produto = pd.Series([True] * len(self.df_compras)) # se a lista estiver vazia, considera todos os valores como verdadeiros

        if self.filtro.varProduto:
            filtro_produto = self.df_compras['produto'].isin(self.filtro.varProduto)
        else:
            filtro_produto = pd.Series([True] * len(self.df_compras))

        if self.filtro.varNumeroBoleto:
            filtro_boleto = self.df_compras['numero_boleto'].isin(self.filtro.varNumeroBoleto)
        else:
            filtro_boleto = pd.Series([True] * len(self.df_compras)) # se a lista estiver vazia, considera todos os valores como verdadeiros

        if self.filtro.varIDCompra:
            filtro_ID_compra = self.df_compras['ID'].isin(self.filtro.varIDCompra)
        else:
            filtro_ID_compra = pd.Series([True] * len(self.df_compras)) # se a lista estiver vazia, considera todos os valores como verdadeiros

        if self.filtro.varFormaPagamento:
            filtro_forma_pagamento = self.df_compras['forma_pagamento'].isin(self.filtro.varFormaPagamento)
        else:
            filtro_forma_pagamento = pd.Series([True] * len(self.df_compras))
                                             
        # TABELAS COMPRAS - aplicando os filtros data e fornecedor
        self.df_vencimento = self.df_compras[filtro_data_vencimento & filtro_fornecedor & filtro_classificacao & 
                                          filtro_grupo_produto & filtro_produto & filtro_boleto & filtro_ID_compra &
                                          filtro_forma_pagamento]
 
        df_pg_vencido = self.df_vencimento.drop(['data_compra', 'data_vencimento', 'data_pagamento','fornecedor', 'qtd', 
                                                        'numero_boleto', 'grupo_produto', 'produto', 'classificacao','forma_pagamento', 
                                                        'observacao', 'dt_atualizado', 'ID'], axis=1)
       
        array_pg_vencimento = np.array(df_pg_vencido)

        # garantir que array esta como string e assim poder aplicar replace
        array_pg_vencimento = array_pg_vencimento.astype(str)
        array_pg_vencimento = np.char.replace(array_pg_vencimento, ',', '.') 
        
        # substiturir valores vazios por nan e assim converter valores para float
        array_pg_vencimento[array_pg_vencimento == ''] = 0
        array_pg_vencimento = array_pg_vencimento.astype(float) 

        # Somando todas as linhas por colunas
        # somando cada coluna da array -> exemplo [279, 1548, 1514, 4848...] -> cada valor é o total de cada coluna
        self.valores_vencimento = np.nansum(array_pg_vencimento, axis=0)
        # self.valor_pagamentos = np.nansum(self.array_pagamentos, axis=0

    def dataframe_vencido(self):
        # Filtrando data
        data_inicial = self.filtro.data_inicial     # formato da data'2023-05-01'
        data_final = self.filtro.data_final

        filtro_data_vencida = (
            (self.df_compras['data_vencimento'] >= data_inicial) & \
                (self.df_compras['data_vencimento'] <= data_final) & \
                    (self.df_compras['data_pagamento'].isnull() | (self.df_compras['data_pagamento'] == ''))
                         )
        # filtrando fornecedor
        # Verificar se a lista 'self.filtro.varFornecedor' está vazia
        if self.filtro.varFornecedor:
            filtro_fornecedor = self.df_compras['fornecedor'].isin(self.filtro.varFornecedor)
        else:
            filtro_fornecedor = pd.Series([True] * len(self.df_compras)) # se a lista estiver vazia, considera todos os valores como verdadeiros  
        
        if self.filtro.varClassificacao:
            filtro_classificacao = self.df_compras['classificacao'].isin(self.filtro.varClassificacao)
        else:
            filtro_classificacao = pd.Series([True] * len(self.df_compras)) # se a lista estiver vazia, considera todos os valores como verdadeiros

        if self.filtro.varGrupoProduto:
            filtro_grupo_produto = self.df_compras['grupo_produto'].isin(self.filtro.varGrupoProduto)
        else:
            filtro_grupo_produto = pd.Series([True] * len(self.df_compras)) # se a lista estiver vazia, considera todos os valores como verdadeiros

        if self.filtro.varProduto:
            filtro_produto = self.df_compras['produto'].isin(self.filtro.varProduto)
        else:
            filtro_produto = pd.Series([True] * len(self.df_compras))

        if self.filtro.varNumeroBoleto:
            filtro_boleto = self.df_compras['numero_boleto'].isin(self.filtro.varNumeroBoleto)
        else:
            filtro_boleto = pd.Series([True] * len(self.df_compras)) # se a lista estiver vazia, considera todos os valores como verdadeiros

        if self.filtro.varIDCompra:
            filtro_ID_compra = self.df_compras['ID'].isin(self.filtro.varIDCompra)
        else:
            filtro_ID_compra = pd.Series([True] * len(self.df_compras))
        
        if self.filtro.varFormaPagamento:
            filtro_forma_pagamento = self.df_compras['forma_pagamento'].isin(self.filtro.varFormaPagamento)
        else:
            filtro_forma_pagamento = pd.Series([True] * len(self.df_compras))

        # TABELAS COMPRAS - aplicando os filtros data e fornecedor
        self.df_compra_vencida = self.df_compras[filtro_data_vencida & filtro_fornecedor & filtro_classificacao & 
                                          filtro_grupo_produto & filtro_produto & filtro_boleto & filtro_ID_compra &
                                          filtro_forma_pagamento]
 
        df_pg_vencido = self.df_compra_vencida.drop(['data_compra', 'data_vencimento', 'data_pagamento','fornecedor', 'qtd', 
                                                        'numero_boleto', 'grupo_produto', 'produto', 'classificacao','forma_pagamento', 
                                                        'observacao', 'dt_atualizado', 'ID'], axis=1)
       
        array_pg_vencido = np.array(df_pg_vencido)

        # garantir que array esta como string e assim poder aplicar replace
        array_pg_vencido = array_pg_vencido.astype(str)
        array_pg_vencido = np.char.replace(array_pg_vencido, ',', '.') 
        
        # substiturir valores vazios por nan e assim converter valores para float
        array_pg_vencido[array_pg_vencido == ''] = 0
        array_pg_vencido = array_pg_vencido.astype(float) 

        # Somando todas as linhas por colunas
        # somando cada coluna da array -> exemplo [279, 1548, 1514, 4848...] -> cada valor é o total de cada coluna
        self.valor_vencido = np.nansum(array_pg_vencido, axis=0)
        # self.valor_pagamentos = np.nansum(self.array_pagamentos, axis=0

    def card_conta_vencida(self):
        # Divide a tela em 4 colunas
        col1, col2, col3, col4 = st.columns(4)

        #BAD2DE
        #CBE2DA
        #E5F0EC
        #f5f5f5 - light gray
        #4CAF50 - green
        #3498db - blue
        #FF0004 - red
        
        # Define card styles
        card_style = """
        <style>
        .card {
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
            padding: 1px;
            text-align: center;
            background-color: #FF0004;   
            margin: 8px;
            max-width: 230px; /* Largura máxima do card */
            width: 100%; /* Largura total do card */
        }

        .riders {
            background-color: #BAD2DE;
            color: gray;
        }

        .spatial-data {
            background-color: #CBE2DA;
            color: white;
        }
        </style>
        """

        # Aplica o estilo dos cards
        st.markdown(card_style, unsafe_allow_html=True)

        # Exibe os cards nas colunas
        for index, row in self.df_compra_vencida.iterrows():
            card = f"""
            <div class="card conta em aberto">
                <h2>{row['data_vencimento']}</h2>
                <p>Fornecedor: <i> {row['fornecedor']} <i> </p>
                <p>Grupo: <i> {row['grupo_produto']} <i> </p>
                <p>Valor: <i> {row['valor_compra']} <i> </p>
                <p>ID: <i> {row['ID']} <i> </p>
            </div>
            """
            # Adiciona os cards nas colunas
            if index % 4 == 0:
                col1.write(card, unsafe_allow_html=True)
            elif index % 4 == 1:
                col2.write(card, unsafe_allow_html=True)
            elif index % 4 == 2:
                col3.write(card, unsafe_allow_html=True)
            elif index % 4 == 3:
                col4.write(card, unsafe_allow_html=True)
            
    def cards_resumo_compras(self):
        self.dataframe_compras()
        self.dataframe_pagamentos()
        self.dataframe_vencimento()
        self.dataframe_vencido()
        self.indicadores_compras()
        # Cards das vendas
        # a função millify serve para abreviar o valor $8.000 para $8k
        col1, col2, col3, col4, col5, col6  = st.columns(6)
        # col1.metric('Valor de Compra', '${}'.format(millify(self.valor_compras[0])))
        # col2.metric('Valor Pago', '${}'.format(millify(self.valor_pagamentos if np.isscalar(self.valor_pagamentos) 
        #                                                else self.valor_pagamentos[0])))
        # col3.metric('Valor a Pagar', '${}'.format(millify(self.valor_vencido if np.isscalar(self.valor_vencido)
        #                                                     else self.valor_vencido[0])))
        # # Calcule o percentual - o if esta tratando se o valor for vazio
        # percentual_cmv = (float(self.cmv) / float(self.valor_compras[0]) * 100) if self.valor_compras.any() else 0
        # percentual_gasto_fixo = (float(self.gasto_fixo) / float(self.valor_compras[0]) * 100) if self.valor_compras.any() else 0
        # percentual_gasto_variavel = (float(self.gasto_variavel) / float(self.valor_compras[0]) * 100) if self.valor_compras.any() else 0

        # col4.metric('CMV', '${}'.format(millify(self.cmv)), '{:.4}%'.format(percentual_cmv))
        # col5.metric('Gasto Fixo', '${}'.format(millify(self.gasto_fixo)), '{:.3}%'.format(percentual_gasto_fixo))
        # col6.metric('Gasto Variável', '${}'.format(millify(self.gasto_variavel)), '{:.4}%'.format(percentual_gasto_variavel))

        # dataframe pg_funcionario
        self.dataframe_pg_funcionario()
        df_funcionarios = self.valores_pg_func
        df_funcionarios['valor_pago'] = pd.to_numeric(df_funcionarios['valor_pago'])
        self.pg_funcionarios = df_funcionarios['valor_pago'].sum()

        # Verifica se 'self.valor_compras' é uma lista/array e não está vazio antes de acessar o índice 0 pois caso o índice seja zero obtenho um erro logo eu converto para 0
        valor_compra = self.valor_compras[0] if isinstance(self.valor_compras, (list, np.ndarray)) and len(self.valor_compras) > 0 else self.valor_compras if np.isscalar(self.valor_compras) else 0
        col1.metric('Valor de Compra', '${:,.2f}'.format(valor_compra))

        # Verifica se 'self.valor_pagamentos' é escalar ou tem um valor no índice 0
        valor_pagamento = self.valor_pagamentos if np.isscalar(self.valor_pagamentos) else (self.valor_pagamentos[0] if isinstance(self.valor_pagamentos, (list, np.ndarray)) and len(self.valor_pagamentos) > 0 else 0)
        col2.metric('Valor Pago', '${:,.2f}'.format(valor_pagamento))

        # Verifica se 'self.valor_vencido' é escalar ou tem um valor no índice 0
        valor_vencido = self.valor_vencido if np.isscalar(self.valor_vencido) else (self.valor_vencido[0] if isinstance(self.valor_vencido, (list, np.ndarray)) and len(self.valor_vencido) > 0 else 0)
        col3.metric('Valor a Pagar', '${:,.2f}'.format(valor_vencido))

        # Calcule os percentuais, garantindo que os valores existam
        percentual_cmv = (float(self.cmv) / float(valor_compra + self.pg_funcionarios) * 100) if valor_compra != 0 else 0.0
        percentual_gasto_fixo = (float(self.gasto_fixo) / float(valor_compra + self.pg_funcionarios) * 100) if valor_compra != 0 else 0.0
        percentual_gasto_variavel = (float(self.gasto_variavel) / float(valor_compra + self.pg_funcionarios) * 100) if valor_compra != 0 else 0.0

        # Garantir que os percentuais são float e formatar corretamente
        col4.metric('CMV', '${:,.2f}'.format(float(self.cmv)), '{:.2f}%'.format(percentual_cmv))
        col5.metric('Gasto Fixo', '${:,.2f}'.format(float(self.gasto_fixo)), '{:.2f}%'.format(percentual_gasto_fixo))
        col6.metric('Gasto Variável', '${:,.2f}'.format(float(self.gasto_variavel)), '{:.2f}%'.format(percentual_gasto_variavel))

    def widget_compras(self):
        tabela = Compras.atualizar()
        self.df_fornecedor = tabela[1]
        classificacao = tabela[2]
        # Forms pode ser declarado utilizando a sintaxe 'with'
        with st.form(key='lançar_compra', clear_on_submit=False):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                self.data_compra = st.date_input('Data da Compra', format='DD/MM/YYYY')
                self.data_vencimento = st.date_input('Data Vencimento', value=None, format='DD/MM/YYYY')
                self.data_pagamento = st.date_input('Data Pagamento', format='DD/MM/YYYY', value=None)
                self.observacao = st.text_input(label='Observação')
            with col2:
                self.fornecedor = st.selectbox('Fornecedor', self.df_fornecedor['nome_empresa'].unique(), index=None, 
                                               placeholder='Escolha Fornecedor')
                self.numero_boleto = st.text_input(label='Número Boleto', placeholder='Digite número do Boleto')
                self.tipo_pagamento = ['Dinheiro', 'Cartão de Crédito', 'Cartão Débito', 'Pix', 'Cheque',
                                       'Transferência', 'Boleto', 'Débito Automático']
                self.forma_pagamento = st.selectbox('Forma de Pagamento', self.tipo_pagamento, index=None, 
                                                    placeholder='Escolha o Pagamento')
                self.qtd = st.text_input('Qtde', placeholder='Quantidade comprada')
            with col3:
                self.valor_compra = st.number_input(label='Valor Compra', value=float('0.00'), step=10.00,
                                                    min_value=0.00, max_value=25000.00)
                self.valor_pago = st.number_input(label='Valor Pago', value=float('0.00'), step=10.00, min_value=0.00,
                                                  max_value=25000.00)
                self.classificacao = st.selectbox('Classificação', classificacao, index=None, placeholder='Escolha a classificação')
            with col4:
                self.inclui_novo_grupo_produto = st.text_input('Novo Grupo Produto', placeholder='Insira Novo Grupo Produto')
                self.grupo_produto = st.selectbox('Grupo Produto', self.df_compras['grupo_produto'].unique(), index=None,
                                                  placeholder='Escolha o grupo')
                self.inclui_novo_produto = st.text_input('Novo Produto', placeholder='Insira Novo Produto')
                self.produto = st.selectbox('Produto', self.df_compras['produto'].unique(), index=None, placeholder='Escolha o produto')
                
                if self.grupo_produto != None:
                    self.grupo_produto = self.grupo_produto
                else:
                    self.grupo_produto = self.inclui_novo_grupo_produto
            
                if self.produto != None:
                    self.produto = self.produto
                else:
                    self.produto = self.inclui_novo_produto

            submit_button = st.form_submit_button(label='Enviar')
                
        if submit_button:
            self.salvar_compras()

    def salvar_compras(self):
        if self.data_compra == '':
            st.error('Data da compra não é válida!', icon="🚨")
        elif self.fornecedor in (None, ''):
            st.error('Fornecedor não foi preenchido!', icon="🚨")
        elif self.data_vencimento in (None, ''):
            st.error('Data do vencimento não é válida!', icon="🚨")
        elif self.valor_compra <= 0:
            st.error('Informe valor da compra!', icon="🚨")
        elif self.classificacao in (None, ''):
            st.error('Informe classificação da compra!', icon="🚨") #⚠
        elif self.grupo_produto in (None, ''):
            st.error('Informe grupo do produto!', icon="🚨")
        elif self.produto in (None, ''):
            st.error('Informe produto da compra!', icon="🚨")
        else:            
            self.conecta_mysql()
            dt_atualizo = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
            
            comando = text(""" INSERT INTO compras (data_compra, data_vencimento, data_pagamento, fornecedor, valor_compra, 
                                                valor_pago, qtd, numero_boleto, grupo_produto, produto, classificacao, 
                                                forma_pagamento, observacao, dt_atualizado, ID_fornecedor) 
                                VALUES (:data_compra, :data_vencimento, :data_pagamento, :fornecedor, :valor_compra, 
                                        :valor_pago, :qtd, :numero_boleto, :grupo_produto, :produto, :classificacao,
                                        :forma_pagamento, :observacao, :dt_atualizado, :ID_fornecedor)""")
            query = text(f"SELECT c.ID FROM cadastro_fornecedor c WHERE c.nome_empresa = :fornecedor")
            result = self.session.execute(query, {'fornecedor': self.fornecedor})
            ID_fornecedor = result.scalar()  # Assumindo que o ID é um único valor
            
            # Crie um dicionário com os valores a serem substituídos nos placeholders
            valores = {
                'data_compra': self.data_compra,
                'data_vencimento': self.data_vencimento,
                'data_pagamento': self.data_pagamento,
                'fornecedor': self.fornecedor,
                'valor_compra': self.valor_compra,
                'valor_pago': self.valor_pago,
                'qtd': self.qtd,
                'numero_boleto': self.numero_boleto,
                'grupo_produto': self.grupo_produto,
                'produto': self.produto,
                'classificacao': self.classificacao,
                'forma_pagamento': self.forma_pagamento,
                'observacao': self.observacao,
                'ID_fornecedor': ID_fornecedor,
                'dt_atualizado': dt_atualizo
            }

            # Execute a instrução SQL usando os valores e placeholders seguros
            self.session.execute(comando, valores)

            # Comite as mudanças e feche a sessão
            self.session.commit()
            self.session.close()
            
            msg_lancamento = st.empty()
            msg_lancamento.success("Lançamento Realizado com Sucesso!")
            time.sleep(5)
            msg_lancamento.empty()
            # fazer com que apos 5 segundos a mensagem de sucesso apague PENDENTE
        
    def lancamento_compras_table(self):
        df = self.valores_compras
        df['data_compra'] = pd.to_datetime(df['data_compra'], errors='coerce')
        df['data_vencimento'] = pd.to_datetime(df['data_vencimento'], errors='coerce')
        df.loc[:, 'data_pagamento'] = pd.to_datetime(df['data_pagamento'], errors='coerce')
        
        col1, col2, col3, col4 = st.columns([1.5, 1.5, 1, 3])
        with col1: 
            filtro_ID_compras = st.multiselect('Selecione ID para edição', df['ID'], placeholder='Escolha um ID')
            if filtro_ID_compras:
                df = df[df['ID'].isin(filtro_ID_compras)]
        with col2:
            filtro_datas = df['data_compra'].unique()
            filtro_data_compras = st.selectbox('Filtrar data', filtro_datas, 
                                                index=None, 
                                                placeholder='Escolha uma data') if len(filtro_datas) > 0 else None
            if filtro_data_compras:
                df = df[df['data_compra'] == filtro_data_compras]  

        # pegando o nome das colunas
        coluna_compra = self.valores_compras.columns.tolist()

        # alterei nome das colunas para o widget
        coluna_compra = ['ID', 'Data Compra', 'Data Vencimento', 'Data Pagamento', 'Fornecedor', 'Valor Compra',
                        'Valor Pago', 'Qtde', 'Número Boleto', 'Grupo', 'Produto', 'Classificação', 'Forma Pagamento',
                        'Observação', 'Atualizado']
        # witdget
        excluir_coluna = st.multiselect('Excluir coluna', coluna_compra, placeholder='Selecione a coluna', key='excluir_coluna_compras')
        
        # necessário voltar para o nome da coluna original, para tabela a seguir
        nomes_alterados = {
            'ID': 'ID', 'Data Compra': 'data_compra', 'Data Vencimento': 'data_vencimento', 'Data Pagamento': 'data_pagamento', 
            'Fornecedor': 'fornecedor', 'Valor Compra': 'valor_compra', 'Valor Pago': 'valor_pago', 'Qtde': 'qtd',
            'Número Boleto': 'numero_boleto', 'Grupo': 'grupo_produto', 'Produto': 'produto' ,'Classificação': 'classificacao',
            'Forma Pagamento': 'forma_pagamento', 'Observação': 'observacao', 'Atualizado': 'dt_atualizado'
            }

        # excluir as colunas selecionadas no widget
        excluir_coluna = [nomes_alterados[coluna] if coluna in nomes_alterados else coluna for coluna in excluir_coluna]

        df = self.valores_compras.drop(excluir_coluna, axis=1)
        if len(filtro_ID_compras) > 0: # Se houver IDs filtrados, aplique o filtro
            df = df[df['ID'].isin(filtro_ID_compras)]

        if filtro_data_compras:
            df = df[df['data_compra'].isin(filtro_data_compras)]
                
        # Bloquear algumas colunas da edição
        colunas_bloqueadas = {
        'dt_atualizado': {'editable': False},
        'fornecedor': {'editable': False},
        'ID': {'editable': False}
        }

        colunas_formatada = {
                'ID': st.column_config.NumberColumn('ID', format='%d'),
                'data_compra': st.column_config.DateColumn('Data Compra', format='DD/MM/YYYY'),
                'data_vencimento': st.column_config.DateColumn('Data Vencimento', format='DD/MM/YYYY'),
                'data_pagamento': st.column_config.DateColumn('Data Pagamento', format='DD/MM/YYYY'),
                'fornecedor': st.column_config.SelectboxColumn('Fornecedor', options=self.df_fornecedor['nome_empresa'].unique(), required=True),
                'valor_compra': st.column_config.NumberColumn('Valor Compra', format='$%f', min_value=0, max_value=25000), 
                'valor_pago': st.column_config.NumberColumn('Valor Pago', format='$%f', min_value=0, max_value=25000),
                'qtd': st.column_config.TextColumn('Qtde'),
                'numero_boleto': st.column_config.TextColumn('Número Boleto'),
                'grupo_produto': st.column_config.SelectboxColumn('Grupo', options=self.df_compras['grupo_produto'], required=True),
                'produto': st.column_config.SelectboxColumn('Produto', options=self.df_compras['produto'], required=True),
                'classificacao': st.column_config.SelectboxColumn('Classificação', options=self.df_compras['classificacao'].unique(), required=True),
                'forma_pagamento': st.column_config.SelectboxColumn('Forma Pagamento', options=self.tipo_pagamento, required=True),
                'observacao': st.column_config.TextColumn('Observação'),
                'dt_atualizado':st.column_config.DatetimeColumn('Atualizado', format='DD/MM/YYYY- h:mm A')}
        
        # Aplicando a formatação apenas nas colunas que ainda existem
        colunas_formatadas_existem = {key: value for key, value in colunas_formatada.items() if key in df.columns}

        # num_rows = 'dynamic' é um parametro para habilitar a inclusão de linhas
        # disabled = deixa as colunas ineditavel
        tabela_editavel = st.data_editor(df, 
                                            disabled=colunas_bloqueadas, 
                                            column_config=colunas_formatadas_existem, 
                                            column_order=['ID', 'data_compra', 'data_vencimento', 'data_pagamento', 
                                                          'fornecedor', 'valor_compra', 'valor_pago', 'qtd', 
                                                          'numero_boleto', 'grupo_produto', 'produto', 'classificacao',
                                                          'forma_pagamento', 'observacao', 'dt_atualizado'],
                                            hide_index=True)

        def update_data_compras(df):
            # atualização acontece apenas nas colunas disponivel
            self.conecta_mysql2()
            cursor = self.conn.cursor()
            data_atual = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
            
            # Obter as colunas disponíveis
            colunas_disponiveis = df.columns.tolist()

            for index, row in df.iterrows():
                query = "UPDATE compras SET "
                valores = []
                for coluna in colunas_disponiveis:
                    # Verificar se a coluna está presente no índice da linha atual
                    if coluna in row.index:
                        # Tratar valores None ou NaT para SQL NULL
                        valor = row[coluna]
                        if pd.isnull(valor):
                            valor = 'NULL'
                        else:
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
            
            st.rerun(scope='fragment')
            self.conn.commit()
            cursor.close()
            self.conn.close()

        with col3:
            if st.button('Salvar Alterações'):
                if len(filtro_ID_compras) > 0 or filtro_data_compras is not None:
                    update_data_compras(tabela_editavel)
                    with col4:
                        # precisei criar uma mensagem vazia para depois deixa-la vazia novamente depois de utiliza-la
                        msg_lancamento = st.empty()
                        msg_lancamento.success("Edição realizada com Sucesso!")
                        time.sleep(10)
                        msg_lancamento.empty() 
                else:
                    with col4:
                        msg_lancamento = st.empty()
                        msg_lancamento.warning('Selecione uma data ou ID que deseja editar!', icon="🚨")
                        time.sleep(10)
                        msg_lancamento.empty()

    def caixas_expansivas(self):
        # pegando o nome das colunas
        coluna_compra = self.valores_compras.columns.tolist()

        # alterei nome das colunas para o widget
        coluna_compra = ['ID', 'Data Compra', 'Data Vencimento', 'Data Pagamento', 'Fornecedor', 'Valor Compra',
                        'Valor Pago', 'Qtde', 'Número Boleto', 'Grupo', 'Produto', 'Classificação', 'Forma Pagamento',
                        'Observação', 'Atualizado']
        # witdget
        excluir_coluna = st.multiselect('Excluir coluna', coluna_compra, placeholder='Selecione a coluna')
        
        # necessário voltar para o nome da coluna original, para tabela a seguir
        nomes_alterados = {
            'ID': 'ID', 'Data Compra': 'data_compra', 'Data Vencimento': 'data_vencimento', 'Data Pagamento': 'data_pagamento', 
            'Fornecedor': 'fornecedor', 'Valor Compra': 'valor_compra', 'Valor Pago': 'valor_pago', 'Qtde': 'qtd',
            'Número Boleto': 'numero_boleto', 'Grupo': 'grupo_produto', 'Produto': 'produto' ,'Classificação': 'classificacao',
            'Forma Pagamento': 'forma_pagamento', 'Observação': 'observacao', 'Atualizado': 'dt_atualizado'
            }

        # excluir as colunas selecionadas no widget
        excluir_coluna = [nomes_alterados[coluna] if coluna in nomes_alterados else coluna for coluna in excluir_coluna]

        colunas_formatada = {
                'ID': st.column_config.NumberColumn('ID', format='%d'),
                'data_compra': st.column_config.DateColumn('Data Compra', format='DD/MM/YYYY'),
                'data_vencimento': st.column_config.DateColumn('Data Vencimento', format='DD/MM/YYYY'),
                'data_pagamento': st.column_config.DateColumn('Data Pagamento', format='DD/MM/YYYY'),
                'fornecedor': st.column_config.TextColumn('Fornecedor'),
                'valor_compra': st.column_config.NumberColumn('Valor Compra', format='$%f'), 
                'valor_pago': st.column_config.NumberColumn('Valor Pago', format='$%f'),
                'qtd': st.column_config.TextColumn('Qtde'),
                'numero_boleto': st.column_config.TextColumn('Número Boleto'),
                'grupo_produto': st.column_config.TextColumn('Grupo'),
                'produto': st.column_config.TextColumn('Produto'),
                'classificacao': st.column_config.TextColumn('Classificação'),
                'forma_pagamento': st.column_config.TextColumn('Forma Pagamento'),
                'observacao': st.column_config.TextColumn('Observação'),
                'dt_atualizado':st.column_config.DatetimeColumn('Atualizado', format='DD/MM/YYYY- h:mm A')}
        
        order_column = ['ID', 'data_compra', 'data_vencimento', 'data_pagamento', 'fornecedor', 'valor_compra',
                        'valor_pago', 'qtd', 'numero_boleto', 'grupo_produto', 'produto', 'classificacao',
                        'forma_pagamento', 'observacao', 'dt_atualizado']
        
        df_tabela_compras = self.valores_compras.drop(excluir_coluna, axis=1)
        df_vencimento = self.df_vencimento.drop(excluir_coluna, axis=1)
        df_pagamentos = self.valores_pagamentos.drop(excluir_coluna, axis=1)
        df_vencidas = self.df_compra_vencida.drop(excluir_coluna, axis=1)

        
        # Aplicando a formatação apenas nas colunas que ainda existem
        colunas_formatadas_existem_compras = {key: value for key, value in colunas_formatada.items() if key in df_tabela_compras.columns}
        colunas_formatadas_existem_vencimento = {key: value for key, value in colunas_formatada.items() if key in df_vencimento.columns}
        colunas_formatadas_existem_pagamentos = {key: value for key, value in colunas_formatada.items() if key in df_pagamentos.columns}
        colunas_formatadas_existem_vencidas = {key: value for key, value in colunas_formatada.items() if key in df_vencidas.columns}

        with st.expander('Tabela Compras', expanded=True):
            # excluir_coluna = st.multiselect('Excluir coluna', coluna_compra, placeholder='Selecione a coluna')
            st.dataframe(df_tabela_compras, column_config= colunas_formatadas_existem_compras,
                                                hide_index=True, 
                                                column_order=order_column)

        with st.expander('Cards dos pagamentos vencidos'):
            self.card_conta_vencida()
            
        with st.expander('Tabela Vencimentos'): 
            st.dataframe(df_vencimento, column_config=colunas_formatadas_existem_vencimento, 
                                             column_order=order_column, 
                                             hide_index=True)

        with st.expander('Tabela Pagamentos'):
            st.dataframe(df_pagamentos, column_config=colunas_formatadas_existem_pagamentos,
                                                    column_order=order_column,
                                                    hide_index=True)

        with st.expander('Tabela Vencidos'):
            # self.df_vencimento
            st.dataframe(df_vencidas, column_config=colunas_formatadas_existem_vencidas, 
                                                 column_order=order_column, 
                                                 hide_index=True)
            
    def widget_cadastro_fornecedor(self):
        with st.form(key='cadastrar_fornecedor', clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                self.nome_fornecedor = st.text_input(label='Fornecedor', placeholder='Digite nome da Empresa')
                self.cnpj = st.text_input(label='CNPJ', placeholder='Digite CNPJ')
                # TODO from validate_docbr import CNPJ criar logica para validar cnpj
                self.nome_contato_fornecedor = st.text_input(label='Nome do Fornecedor', placeholder='Digite Nome do Contato')
                self.telefone_fornecedor = st.text_input(label='Telefone', placeholder='Digite telefone ou celular')
            with col2:
                # TODO validar telefone, email e cep do fornecedor
                self.email_fornecedor = st.text_input(label='E-mail', placeholder='Digite e-mail do Fornecedor')
                self.endereco_fornecedor = st.text_input(label='Endereço', placeholder='Digite o Endereço')
                self.cep_fornecedor = st.text_input(label='CEP', placeholder='Digite o CEP')
            with col3:
                self.numero_fornecedor = st.text_input(label='Número', placeholder='Digite o Número do Endereço')
                self.bairro_fornecedor = st.text_input(label='Bairro', placeholder='Digite o Bairro')
                self.cidade_fornecedor = st.text_input(label='Cidade', placeholder='Digite a Cidade')

            submit_button = st.form_submit_button(label='Enviar')
                
        if submit_button:
            self.salvar_cadastro_fornecedor()
            # Atualizar as tabelas

    def salvar_cadastro_fornecedor(self):
        if self.nome_fornecedor == '':
            st.error('Preencha nome do fornecedor!', icon="🚨")
        else:            
            self.conecta_mysql()

            dt_atualizo = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

            metadata = MetaData()
            fornecedor_table = Table('cadastro_fornecedor', metadata,
                Column('ID', Integer, primary_key=True),
                Column('nome_empresa', String),
                Column('cnpj', String),
                Column('nome_contato', String),
                Column('telefone', String),
                Column('email', String),
                Column('endereco', String),
                Column('cep', String),
                Column('numero', String),
                Column('bairro', String),
                Column('cidade', String),
                Column('dt_atualizado', DateTime)
            )

            # Definindo os valores para inserção
            valores = {
                'nome_empresa': self.nome_fornecedor,
                'cnpj': self.cnpj,
                'nome_contato': self.nome_contato_fornecedor,
                'telefone': self.telefone_fornecedor,
                'email': self.email_fornecedor,
                'endereco': self.endereco_fornecedor,
                'cep': self.cep_fornecedor,
                'numero': self.numero_fornecedor,
                'bairro': self.bairro_fornecedor,
                'cidade': self.cidade_fornecedor,
                'dt_atualizado': dt_atualizo
            }

            # Verificar se o nome do funcionário já existe na tabela
            stmt_select = select(fornecedor_table).where(fornecedor_table.c.nome_empresa == self.nome_fornecedor)
            resultado = self.session.execute(stmt_select)
            existe_nome = resultado.fetchone() is not None

            if not existe_nome:    
                # Criando uma instrução de INSERT
                stmt = insert(fornecedor_table).values(valores)
                # Executando a instrução de INSERT
                self.session.execute(stmt)
                # Confirmar a transação
                self.session.commit()

                # precisei criar uma mensagem vazia para depois deixa-la vazia novamente depois de utiliza-la
                msg_lancamento = st.empty()
                msg_lancamento.success("Lançamento Realizado com Sucesso!")
                time.sleep(5)
                msg_lancamento.empty()
                # fazer com que apos 5 segundos a mensagem de sucesso apague PENDENTE
            else:
                msg_lancamento = st.empty()
                msg_lancamento.error("Empresa já cadastrada", icon="🚨")
                time.sleep(5)
                msg_lancamento.empty()
                # fazer com que apos 5 segundos a mensagem de sucesso apague PENDENTE
                
            # Fechando a sessão
            self.session.close()
    
    def lacamento_fornecedor_table(self):
        col1, col2, col3, col4 = st.columns([1.5, 1.5, 1, 3])
        with col1: 
            filtro_ID_fornecedor = st.multiselect('Selecione ID para edição', self.df_fornecedor['ID'], placeholder='Escolha um ID', key='Seleção ID para edição')
            if filtro_ID_fornecedor:
                df = self.df_fornecedor[self.df_fornecedor['ID'].isin(filtro_ID_fornecedor)]

        with col2:
            filtro_nome_fornecedor = st.multiselect('Selecione a empresas para edição', self.df_fornecedor['nome_empresa'].unique(), placeholder='Escolha os fornecedores')
            if filtro_nome_fornecedor:
                df = self.df_fornecedor[self.df_fornecedor['nome_empresa'].isin(filtro_nome_fornecedor)]

        # pegando o nome das colunas
        coluna_fornecedor = self.df_fornecedor.columns.tolist()

        # alterei nome das colunas para o widget
        coluna_fornecedor = ['ID', 'Empresa', 'CNPJ', 'Contato', 'Telefone', 'E-mail', 'Endereço', 'CEP', 'Número', 'Bairro', 'Atualizado']
        # witdget
        excluir_coluna = st.multiselect('Excluir coluna', coluna_fornecedor, placeholder='Selecione a coluna', key='excluir_coluna_fornecedor')
        
        # necessário voltar para o nome da coluna original, para tabela a seguir
        nomes_alterados = {'ID': 'ID', 'Empresa': 'nome_empresa', 'CNPJ': 'CNPJ', 'Contato': 'nome_contato', 'Telefone': 'telefone',
                           'E-mail': 'email', 'Endereço': 'endereco', 'CEP': 'cep', 'Número': 'numero', 'Bairro': 'bairro', 
                           'Atualizado': 'dt_atualizado'}

        # excluir as colunas selecionadas no widget
        excluir_coluna = [nomes_alterados[coluna] if coluna in nomes_alterados else coluna for coluna in excluir_coluna]

        df = self.df_fornecedor.drop(excluir_coluna, axis=1)
        if len(filtro_ID_fornecedor) > 0: # Se houver IDs filtrados, aplique o filtro
            df = self.df_fornecedor[self.df_fornecedor['ID'].isin(filtro_ID_fornecedor)]

        if filtro_nome_fornecedor:
            df = self.df_fornecedor[self.df_fornecedor['nome_empresa'].isin(filtro_nome_fornecedor)]
                
        # Bloquear algumas colunas da edição
        colunas_bloqueadas = {
        'dt_atualizado': {'editable': False},
        'ID': {'editable': False}
        }

        colunas_formatada = {
                'ID': st.column_config.NumberColumn('ID', format='%d'),
                'nome_empresa': st.column_config.TextColumn('Empresa'),
                'cnjp': st.column_config.TextColumn('CNPJ'),
                'nome_contato': st.column_config.TextColumn('Contato'),
                'telefone': st.column_config.TextColumn('Telefone'),
                'email': st.column_config.TextColumn('E-mail'), 
                'endereco': st.column_config.TextColumn('Endereço'),
                'cep': st.column_config.TextColumn('CEP'),
                'numero': st.column_config.TextColumn('Número'),
                'bairro': st.column_config.TextColumn('Bairro'),
                'dt_atualizado':st.column_config.DatetimeColumn('Atualizado', format='DD/MM/YYYY- h:mm A')}
        
        # Aplicando a formatação apenas nas colunas que ainda existem
        colunas_formatadas_existem = {key: value for key, value in colunas_formatada.items() if key in df.columns}

        # num_rows = 'dynamic' é um parametro para habilitar a inclusão de linhas
        # disabled = deixa as colunas ineditavel
        tabela_editavel = st.data_editor(df, 
                                            disabled=colunas_bloqueadas, 
                                            column_config=colunas_formatadas_existem, 
                                            column_order=['ID', 'nome_empresa', 'cnpj', 'nome_contato', 
                                                          'telefone', 'email', 'endereco', 'cep', 
                                                          'numero', 'bairro', 'dt_atualizado'], 
                                            hide_index=True)

        def update_data_compras(df):
            # atualização acontece apenas nas colunas disponivel
            self.conecta_mysql2()
            cursor = self.conn.cursor()
            data_atual = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
            
            # Obter as colunas disponíveis
            colunas_disponiveis = df.columns.tolist()

            for index, row in df.iterrows():
                query = "UPDATE cadastro_fornecedor SET "
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
            if st.button('Salvar Alterações', key='edição_cadastro_fornecedor'):
                # if len(filtro_ID_fornecedor) > 0 or filtro_nome_fornecedor is not None:
                if len(filtro_ID_fornecedor) > 0 or (filtro_nome_fornecedor is not None and len(filtro_nome_fornecedor) > 0):
                    update_data_compras(tabela_editavel)
                    with col4:
                        # precisei criar uma mensagem vazia para depois deixa-la vazia novamente depois de utiliza-la
                        msg_lancamento = st.empty()
                        msg_lancamento.success("Edição realizada com Sucesso!")
                        time.sleep(10)
                        msg_lancamento.empty()
                else:
                    with col4:
                        msg_lancamento = st.empty()
                        msg_lancamento.warning('Selecione ID ou fornecedor que deseja editar!', icon="🚨")
                        time.sleep(10)
                        msg_lancamento.empty()

    def tableau_compras(self):
        df = self.valores_compras.drop(['ID', 'dt_atualizado'], axis=1)
        df['valor_compra'] = pd.to_numeric(df['valor_compra'], errors='coerce')
        df['valor_pago'] = pd.to_numeric(df['valor_pago'], errors='coerce')

        # Calcula o valor total da coluna 'valor_compra'
        valor_total = df['valor_compra'].sum() + self.pg_funcionarios

        # Cria a nova coluna com a porcentagem de cada valor em relação ao total
        df['Porcentagem'] = ((df['valor_compra'] / valor_total) * 100).round(2)
        
        # Lista das colunas de data que você deseja converter
        colunas_de_data = ['data_compra', 'data_vencimento', 'data_pagamento']

        # Converter as colunas de data para o formato de data do Pandas
        for coluna in colunas_de_data:
            df[coluna] = pd.to_datetime(df[coluna])
        
        df = df.drop(['qtd', 'numero_boleto', 'observacao'], axis=1)

        df = df.rename(columns={
            'data_compra': 'Data Compra',
            'data_vencimento': 'Data Vencimento',
            'data_pagamento': 'Data Pagamento',
            'fornecedor': 'Fornecedor',
            'valor_compra': 'Valor Compra',
            'valor_pago': 'Valor Pago',
            'grupo_produto': 'Grupo',
            'produto': 'Produto',
            'classificacao': 'Classificação',
            'forma_pagamento': 'Forma Pagamento'
        })

        if df.empty:
            st.warning('A tabela está vazia. Verifique os dados de entrada.')
            st.write(df)
        else:
            grafico_dinamico = StreamlitRenderer(df, spec="./json/compras.json", spec_io_mode="rw")
            renderer = grafico_dinamico
            renderer.explorer()
