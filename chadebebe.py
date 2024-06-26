import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from gspread_dataframe import set_with_dataframe
import os
import json

credentials_json = st.secrets["GOOGLE_CREDENTIALS"]

# Substituir a chave privada por uma versão com quebras de linha corretas
credentials_dict = json.loads(credentials_json)

# Reformatar as credenciais como JSON
# formatted_credentials_json = json.dumps(credentials_dict)
# credentials = json.loads(formatted_credentials_json)
# # Escopo das APIs que você quer acessar
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Crie as credenciais usando o dict
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(credentials)

# Função para carregar os dados da planilha
def load_data(sheet_name):
    sheet = client.open(sheet_name).sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# Função para atualizar os dados na planilha
def update_data (df):
    spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1kJebujh-B7TcsQFqSbEwOMB45MVrEEW8tAseRYaQaMQ')
    worksheet = spreadsheet.worksheet("Itens")
    worksheet.clear()
    set_with_dataframe(worksheet, df, include_index=False, resize=False)

# Função para enviar email
def escrever_mensagem(nome,msg):
    spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1kJebujh-B7TcsQFqSbEwOMB45MVrEEW8tAseRYaQaMQ')
    worksheet = spreadsheet.worksheet("Mensagens")
    worksheet.append_row([nome, msg])


# Carregar dados da planilha
sheet_name = 'Chá de bebê'
df = load_data(sheet_name)

data_evento = datetime.datetime(2024, 12, 2)
data_atual = datetime.datetime.now()
diferenca = data_evento - data_atual
dias_restantes = diferenca.days


# Configuração do dashboard
st.title('Chá de bebê da Cecília')

st.markdown('> Os filhos são herança do Senhor, uma recompensa que Ele dá. - _Salmo 127:3_')
st.write('\n')
st.write("**Data e local:** ⏰ 27 de julho de 2024 | 📍 Rua João Dranka, 66 - Cristo Rei, Curitiba - PR")
st.write('\n')
st.write(f"""
    Olá, queridos amigos e familiares! Estamos muito felizes em compartilhar com vocês a chegada da nossa bebê Cecília. Faltam {dias_restantes} dias para o nascimento previsto do nosso amor!
""")

st.write("""
    Obrigado por participar do chá de bebê! Escolha um item na barra lateral, indique a quantidade que deseja presentear, 
    escreva uma mensagem carinhosa para a bebê e clique em "Confirmar". Sua mensagem será enviada para o email dos pais, que guardarão com muito carinho, para que ela leve de lembrança a vida toda.
""")

col1, col2 = st.columns(2)

nome_comprador = st.text_input('Seu Nome')
item_selecionado = col1.selectbox('Item', df['Item'].tolist())
quantidade_selecionada = col2.number_input('Quantidade', min_value=1, max_value=int(df[df['Item'] == item_selecionado]['Quantidade Disponível'].values[0]), value=1)

# # Seleção de itens e quantidade na barra lateral
# st.sidebar.image('https://res.cloudinary.com/dipzskced/image/upload/v1718218109/kaa7aid0y4rpfcosksl8.png')
# st.sidebar.header('Selecione o item que deseja presentear')
# item_selecionado = st.sidebar.selectbox('Item', df['Item'].tolist())
# quantidade_selecionada = st.sidebar.number_input('Quantidade', min_value=1, max_value=int(df[df['Item'] == item_selecionado]['Quantidade Disponível'].values[0]), value=1)
# nome_comprador = st.sidebar.text_input('Seu Nome')

# Caixa de texto para mensagem carinhosa
mensagem_carinhosa = st.text_area('Mensagem Carinhosa')

if st.button('Confirmar'):
    if nome_comprador and mensagem_carinhosa:
        df['Quantidade Comprada'] = df['Quantidade Comprada'].replace('', '0')
        df['Quantidade Disponível'] = df['Quantidade Disponível'].replace('', '0')
        
        df['Quantidade Comprada'] = df['Quantidade Comprada'].astype(int)
        df['Quantidade Disponível'] = df['Quantidade Disponível'].astype(int)
        
        df.loc[df['Item'] == item_selecionado, 'Quantidade Comprada'] += quantidade_selecionada
        df.loc[df['Item'] == item_selecionado, 'Quantidade Disponível'] -= quantidade_selecionada
        update_data(df)
        escrever_mensagem(nome_comprador,mensagem_carinhosa)
        if escrever_mensagem:
            st.success('Obrigado pelo presente, {}! Sua mensagem foi enviada com sucesso.'.format(nome_comprador))
    else:
        st.error('Por favor, preencha todos os campos.')

st.write('\n')

df_mensagem = pd.DataFrame({'nome_comprador': [nome_comprador], 'mensagem_carinhosa': [mensagem_carinhosa]})

col1, col2 = st.columns(2)

col1.image('https://res.cloudinary.com/dipzskced/image/upload/v1718197968/yzxmhv6cec0jruhxsprl.jpg', caption='Primeira foto da nossa bebê', use_column_width=True)
col2.image('https://i.pinimg.com/originals/c7/10/c1/c710c11985c3a64f9ab0d1a0a2224a04.jpg', caption='Santa Cecília, padroeira dos músicos e dos poetas', use_column_width=True)
col1.image('https://res.cloudinary.com/dipzskced/image/upload/v1718197969/a64fkfofdu5ytxrnbfts.jpg', caption='Pais sortudos', use_column_width=True)
col2.image('https://res.cloudinary.com/dipzskced/image/upload/v1718198410/mfm0fbzo3bsfjajylwky.jpg', caption='Primeiro ursinho da Ceci', use_column_width=True)

st.write('\n')
st.subheader('Oração a Santa Cecília')
st.markdown(""">_Ó gloriosa Santa Cecília, que escolheste morrer em vez de negar teu Rei,
rogai por nós para que possamos suportar as dificuldades da nossa fé._
>
>_Querida Santa Cecília, admirável padroeira dos músicos,
pedimos tua intercessão para que, através da música,
nossos corações possam se elevar ao divino e ao amor de Deus._
>
>_Concede-nos a graça de entender a música como um instrumento de paz e alegria,
e que através dela possamos louvar e glorificar a Deus._
>
>_Santa Cecília, que com tua música atraíste muitos corações para Cristo,
intercede por nós para que, como tu, possamos ser testemunhas da fé com alegria e coragem._
>
>_Amém._""")

