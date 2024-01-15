import pandas as pd
import pyodbc 
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
gb = GridOptionsBuilder()


dados_conexao = ("DRIVER={MySQL ODBC 8.0 Unicode Driver};"
                "SERVER=grp6m5lz95d9exiz.cbetxkdyhwsb.us-east-1.rds.amazonaws.com;"  #host
                "DATABASE=z8308a2l1w09zs3e;"     #banco de dados 
                "UID=yxvnub0tjz2q91z2;"                  #usuario
                "PASSWORD=qn452lhidcwsv3a0;")  

conexao = pyodbc.connect(dados_conexao)
cursor = conexao.cursor()

lista = f""" SELECT ID, data_venda, periodo, qtd_rodizio, dinheiro, pix, debito_mastercard, debito_visa, 
            debito_elo, credito_mastercard, credito_visa, credito_elo, hiper, american_express, alelo, 
                CAST(dinheiro AS DECIMAL) + CAST(pix AS DECIMAL) + 
                CAST(debito_mastercard AS DECIMAL) + CAST(debito_visa AS DECIMAL) + CAST(debito_elo AS DECIMAL) + 
                CAST(credito_mastercard AS DECIMAL) + CAST(credito_visa AS DECIMAL) + CAST(credito_elo AS DECIMAL) + 
                CAST(hiper AS DECIMAL) + CAST(american_express AS DECIMAL) + CAST(alelo AS DECIMAL) AS total_vendas 
            FROM vendas ORDER BY ID DESC; """
tabelavendas = pd.read_sql(lista, conexao)

# Desconectando do banco
cursor.close()
conexao.close()

# gerando os dataframe
tabelavendas = tabelavendas.drop(['ID'], axis=1)
vendas_periodo = tabelavendas.groupby(['periodo']).sum() #ainda não estou utilizando
# vendas_periodo

# Calculos
# convertendo para númerotabelavendas tabelavendas['dinheiro'] = pd.to_numeric(tabelavendtabelavendas['dinheiro'], errors="coerce")
tabelavendas['dinheiro'] = pd.to_numeric(tabelavendas['dinheiro'], errors='coerce')
tabelavendas['qtd_rodizio'] = pd.to_numeric(tabelavendas['qtd_rodizio'], errors='coerce')
tabelavendas['pix'] = pd.to_numeric(tabelavendas['pix'], errors='coerce')
tabelavendas['debito_mastercard'] = pd.to_numeric(tabelavendas['debito_mastercard'], errors='coerce')
tabelavendas['debito_visa'] = pd.to_numeric(tabelavendas['debito_visa'], errors='coerce')
tabelavendas['debito_elo'] = pd.to_numeric(tabelavendas['debito_elo'], errors='coerce')
tabelavendas['credito_mastercard'] = pd.to_numeric(tabelavendas['credito_mastercard'], errors='coerce')
tabelavendas['credito_visa'] = pd.to_numeric(tabelavendas['credito_visa'], errors='coerce')
tabelavendas['credito_elo'] = pd.to_numeric(tabelavendas['credito_elo'], errors='coerce')
tabelavendas['alelo'] = pd.to_numeric(tabelavendas['alelo'], errors='coerce')
tabelavendas['american_express'] = pd.to_numeric(tabelavendas['american_express'], errors='coerce')
tabelavendas['hiper'] = pd.to_numeric(tabelavendas['hiper'], errors='coerce')

# tabelavendas['total_vendas'] = total_vendas
st.write("tabela de vendas")

# torna as colunas redimensionáveis, classificáveis e filtráveis por padrão
gb.configure_default_column(
    resizable=True,
    filterable=True,
    sortable=True,
    editable=False,
)

# check box
shouldDisplayPivoted = st.toggle("Pivot data on Reference Date")     #podemos utilizar tanto o toggle quanto o checkbox

# Menu de filtro DataFrame Vendas
st.write(shouldDisplayPivoted)

# define se o modo de pivô deve ser ativado ou desativado
pivotMode = False # Mode Pivot inicia desativado
gb.configure_grid_options(
    sideBar={
        "toolPanels": [
            {
                "id": "columns",
                "labelDefault": "Colunas",
                "labelKey": "columns",                      # rowGroup ou columns
                "iconKey": "columns",                       # rowGroup
                "toolPanel": "agColumnsToolPanel",          # agRowGroupToolPanel ou agColumnsToolPanel
                "toolPanelParams": {
                    # Permite que as colunas sejam reordenadas no painel de colunas
                    "suppressSyncLayoutWithGrid": True,
                    # impede que as colunas sejam movidas do painel de colunas
                    "suppressColumnMove": False,
                },
            },
            {
                "id": "filters",
                "labelDefault": "Filtros",
                "labelKey": "filters",
                "iconKey": "filter",
                "toolPanel": "agFiltersToolPanel",
                "toolPanelParams": {
                    # impede que os filtros sejam reordenados no painel de filtros
                    "suppressSyncLayoutWithGrid": True,
                    # impede que os filtros sejam movidos do painel de filtros
                    "suppressFilterMove": True,
                },
            },
        ],
                
        # define o painel de colunas como padrão
        "defaultToolPanel": "columns", # essa linha serve para deixar o filtro aberto quando abrir o sistema
        # ativa ou desativa o modo de pivô
        "pivotMode": '',
    },
)

# habilite o modo dinâmico quando a caixa de seleção estiver ativada
gb.configure_grid_options(
    tooltipShowDelay=0,
    pivotMode=pivotMode,
)

# configurar a coluna que exibe a hierarquia do agrupamento
gb.configure_grid_options(
    autoGroupColumnDef=dict(
        minWidth=300, 
        pinned="left",
        cellRendererParams=dict(suppressCount=True)
    )
)

# Criando colunas virtuais do ano
gb.configure_column(
    field="virtualYear",
    header_name="Ano",
    valueGetter="new Date(data.data_venda).getFullYear()",
    pivot=True, # allows grid to pivot on this column (o agrupamento altera de linha para coluna de forma automatica)
    enablePivot=True, # ao ativar pivotamento a coluna fica disponivel para selecionar
    hide=True, # oculta-o quando o modo dinâmico está desativado (check box que habilita)
    rowGroup=True if shouldDisplayPivoted else False
)

# Criando colunas virtuais do mês
gb.configure_column(
    field="virtualMonth",
    header_name="Mês",
    valueGetter="new Date(data.data_venda).toLocaleDateString('pt-BR',options={year:'numeric', month:'2-digit'})",
    pivot=False, # allows grid to pivot on this column (o agrupamento altera de linha para coluna deforma automatica)
    enablePivot=True, # ao ativar pivotamento a coluna fica disponivel para selecionar
    hide=True, # oculta-o quando o modo dinâmico está desativado (check box que habilita)
    rowGroup=True if shouldDisplayPivoted else False
)

gb.configure_column(
    field="data_venda",
    header_name="Data",
    valueFormatter="value != undefined ? new Date(value).toLocaleString('pt-BR', {dateStyle:'medium'}): ''",
    # flex=1, # padronizar largura da celula
    width=180,
    pivot=False, # allows grid to pivot on this column (o agrupamento altera de linha para coluna deforma automatica)
    enablePivot=True, # ao ativar pivotamento a coluna fica disponivel para selecionar
    hide=True,
    rowGroup=True if shouldDisplayPivoted else False
)

gb.configure_column(
    field="periodo", 
    header_name="Período",
    width=110,
    pivot=False, # allows grid to pivot on this column (o agrupamento altera de linha para coluna deforma automatica)
    enablePivot=True, # ao ativar pivotamento a coluna fica disponivel para selecionar
    hide=True,
    rowGroup=True if shouldDisplayPivoted else False
)

gb.configure_column(
    field="pix",
    header_name="Pix",
    type=["numericColumn"],
    valueFormatter="value.tolLocaleString()",
    aggFunc="sum",
    width=110,
)

gb.configure_column(
    field="alelo",
    header_name="Alelo",
    type=["numericColumn"],
    valueFormatter="value.tolLocaleString()",
    aggFunc="sum",
    tooltipField="alelo",
    width=110
)

gb.configure_column(
    field="hiper",
    header_name="Hiper",
    type=["numericColumn"],
    valueFormatter="value.tolLocaleString()",
    aggFunc="sum",
    width=110,
)

gb.configure_column(
    field="dinheiro",
    header_name="Dinheiro",
    type=["numericColumn"],
    valueFormatter="value.tolLocaleString()",
    aggFunc="sum",
    width=110,
)

gb.configure_column(
    field="total_vendas",
    header_name="Total",
    type=["numericColumn"],
    valueFormatter="value.tolLocaleString()",
    aggFunc="sum",
    width=110,
)

go = gb.build()

AgGrid(tabelavendas, gridOptions=go, height=500)