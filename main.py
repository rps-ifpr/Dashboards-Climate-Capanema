import pandas as pd
import streamlit as st
from datetime import datetime

# Leitura dos dados
data = pd.read_csv("./dados/dados.csv", delimiter=";", low_memory=False, encoding="UTF-8")

# Função para renomear a direção do vento
def rename_wind_direction(direction):
    mapping = {
        "N": "Norte", "NNE": "Norte-Nordeste", "NE": "Nordeste", "ENE": "Leste-Nordeste",
        "E": "Leste", "ESE": "Leste-Sudeste", "SE": "Sudeste", "SSE": "Sul-Sudeste",
        "S": "Sul", "SSW": "Sul-Sudoeste", "SW": "Sudoeste", "WSW": "Oeste-Sudoeste",
        "W": "Oeste", "WNW": "Oeste-Noroeste", "NW": "Noroeste", "NNW": "Norte-Noroeste",
    }
    return mapping.get(direction.strip(), direction)

# Configuração da página
st.set_page_config(page_title="Estação Meteorológica IFPR", page_icon=":partly_sunny:")

# Seleção da data
min_n = data["n"].min()
max_n = data["n"].max()
tempo_final = st.sidebar.date_input(
    "Data",
    value=datetime.strptime(data[data["n"] == max_n]["Time"].values[0].strip(), "%d/%m/%Y %H:%M:%S").date(),
    min_value=datetime.strptime(data[data["n"] == min_n]["Time"].values[0].strip(), "%d/%m/%Y %H:%M:%S").date(),
    max_value=datetime.strptime(data[data["n"] == max_n]["Time"].values[0].strip(), "%d/%m/%Y %H:%M:%S").date(),
    format="DD/MM/YYYY"
)
st.sidebar.write("Última atualização:", data[data["n"] == max_n]["Time"].values[0])

# Filtragem dos dados
data_filtrada = data[(data["Time"] >= f" {tempo_final.strftime('%d/%m/%Y')} 00:00:00") & (data["Time"] <= f" {tempo_final.strftime('%d/%m/%Y')} 23:59:59")]

# Criação de cópia dos dados filtrados
data_filtrada_copy = data_filtrada.copy()

# Formatação da coluna de tempo
data_filtrada_copy["Time"] = pd.to_datetime(data_filtrada["Time"], dayfirst=True)
data_filtrada_copy["Time"] = data_filtrada_copy["Time"].dt.strftime("%H:%M")

# Aplicação da função de renomear direção do vento
data_filtrada_copy["Wind Direction"] = data_filtrada["Wind Direction"].apply(rename_wind_direction)

# Conversão de colunas para tipos numéricos
numeric_columns = ["Outdoor Temperature(°C)", "Indoor Temperature(°C)", "Wind Speed(km/h)"]
data_filtrada_copy[numeric_columns] = data_filtrada[numeric_columns].astype(float)

# Renomeação de colunas
column_mapping = {
    "Time": "Horário",
    "Outdoor Temperature(°C)": "Temperatura Externa (ºC)",
    "Indoor Temperature(°C)": "Temperatura Interna (ºC)",
    "Wind Speed(km/h)": "Velocidade do Vento (km/h)",
    "Wind Direction": "Direção do Vento",
    "Hour Rainfall(mm)": "Chuva por Hora (mm)",
    "24 Hour Rainfall(mm)": "Chuva do dia (mm)"
}
chart_data = data_filtrada_copy.rename(columns=column_mapping)

# Exibição dos gráficos
st.write("### Temperatura:")
st.line_chart(chart_data.set_index("Horário"), y=["Temperatura Externa (ºC)", "Temperatura Interna (ºC)"])

st.write("### Velocidade do Vento:")
st.line_chart(chart_data.set_index("Horário"), y="Velocidade do Vento (km/h)")

st.write("### Frequência da direção do vento:")
direction_counts = chart_data["Direção do Vento"].value_counts()
direction_counts_df = pd.DataFrame({"Direção do Vento": direction_counts.index, "Contagem": direction_counts.values})
st.bar_chart(direction_counts_df.set_index("Direção do Vento"), y="Contagem")

st.write("### Precipitação ao Longo do Tempo:")
st.line_chart(chart_data.set_index("Horário"), y=["Chuva por Hora (mm)", "Chuva do dia (mm)"])
