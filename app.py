import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from zipfile import ZipFile

# Función para convertir el DataFrame a un archivo Excel en memoria
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

# Traducción de los días de la semana al español
days_translation = {
    'Monday': 'Lunes',
    'Tuesday': 'Martes',
    'Wednesday': 'Miércoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

# Función para crear el reparto para acuerdo
def create_reparto_para_acuerdo(df, codes_df, config_df):
    # Extracción del último código de despacho y la lista de códigos del archivo de configuración
    ultimo_codigo_despacho = config_df['ultimo_codigo_despacho'].iloc[0]
    lista_codigos = config_df['lista_codigos'].iloc[0].split(',')

    # Establecer el orden de los códigos de despacho
    orden_despacho = {codigo: idx + 1 for idx, codigo in enumerate(lista_codigos)}

    # Asegurar que el último código del despacho esté al principio
    if ultimo_codigo_despacho in orden_despacho:
        del orden_despacho[ultimo_codigo_despacho]
        orden_despacho = {ultimo_codigo_despacho: 1} | orden_despacho

    # Mapear 'Codigo del Despacho' con 'Despacho o Dependencia' para obtener el nombre del despacho
    dict_codigos_despachos = dict(zip(codes_df['Código'].astype(str), codes_df['Despacho o Dependencia']))
    df['Despacho o Dependencia'] = df['Codigo del Despacho'].map(dict_codigos_despachos)

    # Asignar 'Orden del Despacho' basado en el código del despacho
    df['Orden del Despacho'] = df['Codigo del Despacho'].map(orden_despacho)

    # Ordenar el DataFrame basado en 'Orden del Despacho' y 'Fecha'
    reparto_ordenado = df.sort_values(['Orden del Despacho', 'Fecha'])

    return reparto_ordenado[['Orden del Despacho', 'Fecha', 'Día de la Semana', 'Despacho o Dependencia']]

# Función para crear los archivos Excel y comprimirlos en un archivo ZIP
def create_zip_file(reparto_df, reparto_acuerdo_df):
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'a') as zf:
        reparto_excel = to_excel(reparto_df)
        zf.writestr('Reparto_Horas_Habiles.xlsx', reparto_excel.getvalue())
        
        reparto_acuerdo_excel = to_excel(reparto_para_acuerdo_df)
        zf.writestr('Reparto_Para_Acuerdo.xlsx', reparto_acuerdo_excel.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

# Título y descripción en la ventana inicial
st.title('Generador de Reparto de Horas Hábiles')
st.write('Carga el archivo de configuración del reparto, el archivo de festivos y el archivo de códigos de despachos para generar el nuevo reparto.')

# Cargar archivos necesarios
uploaded_file_config = st.file_uploader("Cargar el archivo de configuración (CSV)", type=['csv'])
uploaded_file_festivos = st.file_uploader("Cargar el archivo de festivos (CSV)", type=['csv'])
uploaded_file_codigos = st.file_uploader("Cargar archivo de códigos de despachos (XLSX)", type=['xlsx'])

# Botón de procesamiento
if st.button('Generar Reparto'):
    if uploaded_file_config and uploaded_file_festivos and uploaded_file_codigos:
        try:
            config_df = pd.read_csv(uploaded_file_config)
            festivos_df = pd.read_csv(uploaded_file_festivos)
            codes_despachos_df = pd.read_excel(uploaded_file_codigos)
        except Exception as e:
            st.error(f"Error al leer los archivos: {e}")
            st.stop()

        # Configuración inicial
        fecha_inicio = pd.to_datetime(config_df['fecha_inicio'].iloc[0])
        fecha_fin = pd.to_datetime(config_df['fecha_fin'].iloc[0])
        ultimo_codigo = config_df['ultimo_codigo_despacho'].iloc[0]
        lista_codigos = config_df['lista_codigos'].iloc[0].split(',')
        festivos_df['fecha'] = pd.to_datetime(festivos_df['fecha'])

        # Generar fechas hábiles excluyendo festivos
        all_weekdays = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='B')
        weekdays_without_festivos = all_weekdays[~all_weekdays.isin(festivos_df['fecha'])]
        new_reparto_df = pd.DataFrame({'Fecha': weekdays_without_festivos})
        new_reparto_df['Codigo del Despacho'] = None

        # Rotar los códigos de despacho, comenzando por el siguiente al último usado
        if ultimo_codigo in lista_codigos:
            start_index = lista_codigos.index(ultimo_codigo) + 1
            lista_codigos = lista_codigos[start_index:] + lista_codigos[:start_index]

        code_index = 0
        for index, row in new_reparto_df.iterrows():
            codigo_actual = lista_codigos[code_index]
            new_reparto_df.at[index, 'Codigo del Despacho'] = codigo_actual
            code_index = (code_index + 1) % len(lista_codigos)

        # Mapear 'Codigo del Despacho' con 'Despacho o Dependencia'
        dict_codigos_despachos = dict(zip(codes_despachos_df['Código'].astype(str), codes_despachos_df['Despacho o Dependencia']))
        new_reparto_df['Despacho o Dependencia'] = new_reparto_df['Codigo del Despacho'].map(dict_codigos_despachos)

        # Agregar la columna 'Día de la Semana'
        new_reparto_df['Día de la Semana'] = new_reparto_df['Fecha'].dt.day_name().map(days_translation)

        try:
            reparto_para_acuerdo_df = create_reparto_para_acuerdo(new_reparto_df, codes_despachos_df, config_df)
        except Exception as e:
            st.error(f"Error al crear el reparto para acuerdo: {e}")
            st.stop()

        try:
            zip_file = create_zip_file(new_reparto_df, reparto_para_acuerdo_df)
        except Exception as e:
            st.error(f"Error al crear el archivo ZIP: {e}")
            st.stop()

        # Descargar archivo ZIP
        st.download_button(
            label="Descargar archivo ZIP con repartos",
            data=zip_file,
            file_name="repartos.zip",
            mime="application/zip"
        )
        st.success('El reparto ha sido generado y comprimido con éxito.')
    else:
        st.error('Por favor, carga todos los archivos necesarios para proceder con el reparto.')