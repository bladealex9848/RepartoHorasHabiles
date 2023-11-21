# Reparto de Horas Hábiles

Este proyecto se desarrolló siguiendo los lineamientos de los Acuerdos No. 3399 de 2006 de la entonces Sala Administrativa del Consejo Superior de la Judicatura y PSA-CSJS 001 de 10 de enero de 2013 de este Consejo Seccional modificado por el Acuerdo CSJSUA18-5 del 17 de enero de 2018, en consideración a los Acuerdo PCSJA20-11652 y Acuerdo CSJSUA20-70 del 4 de diciembre de 2020.

## Descripción

El programa tiene como finalidad automatizar el proceso de reparto de horas hábiles, de acuerdo a los criterios establecidos por el Consejo Superior de la Judicatura. Utiliza un conjunto de archivos de configuración y códigos de despachos para generar un nuevo reparto, asegurando la correcta asignación y distribución de horas entre los diferentes despachos.

## Instalación y Ejecución

Para instalar y ejecutar este proyecto, siga los siguientes pasos:

1. Clone el repositorio o descargue el código fuente.
2. Instale las dependencias ejecutando `pip install -r requirements.txt`.
3. Ejecute la aplicación con `streamlit run app.py`.

## Archivos Requeridos

- Archivo de configuración (CSV): Contiene la configuración inicial para el reparto, incluyendo fechas y códigos de despacho.
- Archivo de festivos (CSV): Lista de días festivos a excluir del reparto.
- Archivo de códigos de despachos (XLSX): Información detallada de los despachos, incluyendo códigos y nombres.

## Funcionalidades

- Generación de reparto de horas hábiles excluyendo días festivos.
- Ordenamiento y asignación de despachos según la configuración establecida.
- Creación de archivos Excel para la visualización y descarga del reparto.

## Contribuciones

Las contribuciones a este proyecto son bienvenidas. Por favor, asegúrese de seguir las normativas y lineamientos establecidos por el Consejo Superior de la Judicatura al realizar modificaciones o mejoras.