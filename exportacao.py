import streamlit as st
import pandas as pd
from io import BytesIO

class Exportacao:
    def download_vendas(self):
        st.write('')
        st.write('')
        st.write('---')
        self.dataframe_vendas()
        # Crie um buffer BytesIO para armazenar o arquivo Excel
        output = BytesIO()
        # Crie um escritor de Excel do Pandas
        writer = pd.ExcelWriter(output, engine='xlsxwriter')

        df = self.valores_vendas.copy()
        df['pix'] = pd.to_numeric(df['pix'], errors='coerce')
        df['dinheiro'] = pd.to_numeric(df['dinheiro'], errors='coerce')

        # Escreva o DataFrame no arquivo Excel
        df.to_excel(writer, index=False, sheet_name='Vendas')
        # Obtenha os objetos (workbook) e de planilha (worksheet)
        workbook = writer.book
        worksheet = writer.sheets['Vendas']

        # Defina os formatos numéricos para as colunas
        formato_data = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        formato_float = workbook.add_format({'num_format': '0.00'})
        # formato_inteiro = workbook.add_format({'num_format': '0'})
        worksheet.set_column('A:A', None, formato_data)
        worksheet.set_column('B:R', None, formato_float)
        # worksheet.set_column('U:U', None, formato_inteiro)

        # Feche o escritor para finalizar o arquivo
        writer.close()
        # Obtenha os dados processados do buffer BytesIO
        processed_data = output.getvalue()

        # crie o botão de download
        st.download_button(label='💾 Resultado Vendas',
                            use_container_width=True,
                            data=processed_data,
                            help='Click para iniciar o Download',
                            file_name='Vendas.xlsx')

    def download_compras(self):
        st.write('---')
        self.dataframe_compras()
        # Crie um buffer BytesIO para armazenar o arquivo Excel
        output = BytesIO()
        # Crie um escritor de Excel do Pandas
        writer = pd.ExcelWriter(output, engine='xlsxwriter')

        df = self.valores_compras.copy()

        df['valor_compra'] = pd.to_numeric(df['valor_compra'], errors='coerce')
        df['valor_pago'] = pd.to_numeric(df['valor_pago'], errors='coerce')
        df['data_compra'] = pd.to_datetime(df['data_compra'])
        df['data_vencimento'] = pd.to_datetime(df['data_vencimento'])

        # Escreva o DataFrame no arquivo Excel
        df.to_excel(writer, index=False, sheet_name='Compras')
        # Obtenha os objetos (workbook) e de planilha (worksheet)
        workbook = writer.book
        worksheet = writer.sheets['Compras']

        # Defina os formatos numéricos para as colunas
        formato_data = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        formato_float = workbook.add_format({'num_format': '#,##0.00'})
        worksheet.set_column('A:C', None, formato_data)
        worksheet.set_column('E:F', None, formato_float)

        # Feche o escritor para finalizar o arquivo
        writer.close()
        # Obtenha os dados processados do buffer BytesIO
        processed_data = output.getvalue()

        # crie o botão de download
        st.download_button(label='💾 Resultado Compras',
                            use_container_width=True,
                            data=processed_data,
                            help='Click para iniciar o Download',
                            file_name='Compras.xlsx')

    def download_cadastro(self):
        self.dataframe_cadastro()
        # Crie um buffer BytesIO para armazenar o arquivo Excel
        output = BytesIO()
        # Crie um escritor de Excel do Pandas
        writer = pd.ExcelWriter(output, engine='xlsxwriter')

        df = self.df_cadastro.copy()

        # Escreva o DataFrame no arquivo Excel
        df.to_excel(writer, index=False, sheet_name='Cadastro dos Funcionários')

        # Feche o escritor para finalizar o arquivo
        writer.close()
        # Obtenha os dados processados do buffer BytesIO
        processed_data = output.getvalue()

        # crie o botão de download
        st.download_button(label='💾 Cadastro',
                            use_container_width=True,
                            data=processed_data,
                            help='Click para iniciar o Download',
                            file_name='Cadastro.xlsx')

    def download_admissao(self):
        self.dataframe_admissao()
        output = BytesIO()
        # Crie um escritor de Excel do Pandas
        writer = pd.ExcelWriter(output, engine='xlsxwriter')

        df = self.df_admissao.copy()

        # Escreva o DataFrame no arquivo Excel
        df.to_excel(writer, index=False, sheet_name='Admissão dos Funcionários')

        # Feche o escritor para finalizar o arquivo
        writer.close()
        # Obtenha os dados processados do buffer BytesIO
        processed_data = output.getvalue()

        # crie o botão de download
        st.download_button(label='💾 Admissão',
                            use_container_width=True,
                            data=processed_data,
                            help='Click para iniciar o Download',
                            file_name='Admissão.xlsx')

    def download_pg_func(self):
        self.dataframe_pg_funcionario()

        output = BytesIO()
        # Crie um escritor de Excel do Pandas
        writer = pd.ExcelWriter(output, engine='xlsxwriter')

        # Escreva o DataFrame no arquivo Excel
        df = self.valores_pg_func.copy()

        df['data_pagamento'] = pd.to_datetime(df['data_pagamento'])
        df['valor_pago'] = pd.to_numeric(df['valor_pago'], errors='coerce')

        df.to_excel(writer, index=False, sheet_name='Pagamentos dos Funcionários')

        # Feche o escritor para finalizar o arquivo
        writer.close()
        # Obtenha os dados processados do buffer BytesIO
        processed_data = output.getvalue()

        # crie o botão de download
        st.download_button(label='💾 Pagamentos',
                            use_container_width=True,
                            data=processed_data,
                            help='Click para iniciar o Download',
                            file_name='Pagamentos Funcionários.xlsx')