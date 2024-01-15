import streamlit as st
import time as time

class LancamentoVendas:
    def lancamento_vendas(self):
        # Forms pode ser declarado utilizando a sintaxe 'with'
        with st.form(key='lançar_vendas', clear_on_submit=True):
            # st.title = ('Lançamento de Vendas')
            col1, col2, col3, col4, col5, col6= st.columns(6)
            with col1:
                datainicial = st.date_input('Data')
                periodo = st.selectbox('Período', ['Almoço', 'Jantar'])
                rodizio = st.text_input(label='Qtd Rodízio')
            with col2:
                socio = st.text_input('Sócio')
                dinheiro = st.text_input(label='Dinheiro')
                pix = st.text_input(label='Pix')
            with col3:
                debito_visa = st.text_input(label='Débito Visa')
                debito_master = st.text_input(label='Débito Master')
                debito_elo = st.text_input(label='Débito Elo')
            with col4:
                credito_visa = st.text_input(label='Crédito Visa')
                credito_master = st.text_input(label='Crédito Master')
                credito_elo = st.text_input(label='Crédito Elo')
            with col5:
                vale_refeicao = st.text_input(label='Vale Refeição')
                sodexo = st.text_input(label='Sodexo')
                alelo = st.text_input(label='Alelo')
            with col6:
                ticket_rest = st.text_input(label='Ticket Rest')
                american_express = st.text_input(label='American Express')
                dinersclub = st.text_input(label='DinersClub')  
            submit_button = st.form_submit_button(label='Enviar')
            
        if submit_button:
            st.success("Lançamento Realizado com Sucesso!")
            socio = st.empty()

            # fazer com que apos 5 segundos a mensagem de sucesso apague

