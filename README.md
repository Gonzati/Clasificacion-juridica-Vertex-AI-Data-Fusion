Clasificación jurídica automatizada con Vertex AI, Cloud Composer y Data Fusion

Este proyecto implementa un pipeline completo y automatizado para el análisis y clasificación de resoluciones judiciales (anonimizadas y de acceso público), utilizando Vertex AI (Gemini 2.0) junto con un sistema de orquestación y procesamiento ETL basado en Cloud Composer (Airflow) y Cloud Data Fusion.

El flujo permite ejecutar notebooks de análisis en entorno local o on-premise, integrar los resultados mediante Data Fusion y almacenar los datos estructurados en BigQuery para su posterior visualización en Looker Studio.

🧱 Arquitectura general
Capa	Herramienta	Función
IA / Clasificación	Vertex AI (Gemini 2.0 Flash / Pro)	Análisis semántico y extracción de motivos jurídicos
Almacenamiento RAW	Cloud Storage	Archivos .txt originales (resoluciones)
Orquestación	Cloud Composer (Airflow)	Controla la ejecución de notebooks y pipelines
Ejecución notebooks	Entorno local / on-premise + Pub/Sub	Cloud Composer envía comandos vía Pub/Sub y espera confirmación
ETL / Integración	Cloud Data Fusion	Une, limpia y carga los resultados en BigQuery
Transformación	Wrangler + Joiner	Normalización y fusión de CSVs generados por los notebooks
Data Warehouse	BigQuery	Tabla final Sentencias.sentenciasmerged
Archivado	Cloud Storage (bucket procesadas)	Almacena los .txt ya procesados por Data Fusion
Visualización	Looker Studio	Dashboards de motivos, resultados y distribución de casos
Entorno de desarrollo	Vertex AI Workbench / Jupyter Notebooks	Experimentación y desarrollo de lógica IA
🧠 Lógica de clasificación
Notebook 1 — Clasificación de motivos

Lee los archivos .txt desde el bucket de entrada.

Envía el texto completo a Gemini 2.0 (Vertex AI).

Extrae un JSON con los motivos jurídicos más relevantes (hasta 4).

Guarda el resultado incrementalmente en el bucket de destino (sentencias_motivos_vertex.csv).

Notebook 2 — Clasificación de resultado y parte demandada

Analiza la sentencia completa y determina:

demandado: "xxx" o "contrario"

resultado: "favorable" o "desfavorable"

Genera una salida incremental (sentencias_resultado_vertex.csv).

🔄 Orquestación con Cloud Composer (Airflow)

Trigger por Cloud Function:
Cada vez que se sube un .txt al bucket de origen, una Cloud Function ejecuta el DAG run_notebooks_and_datafusion.

Ejecución de notebooks (on-premise):
El DAG envía un mensaje Pub/Sub al runner local, que ejecuta los notebooks y devuelve un evento “done” al DAG.

Pipeline de Data Fusion:
Una vez confirmada la finalización, Composer lanza el pipeline sentenciasmerged en Data Fusion, que:

Fusiona los resultados de ambos CSVs (motivos + resultado).

Inserta los datos en BigQuery (Sentencias.sentenciasmerged).

Mueve los archivos procesados al bucket de archivo (gs://procesadas/).

📊 Visualización en Looker Studio

El dataset final de BigQuery alimenta un dashboard interactivo con:

Distribución de motivos jurídicos por tipo de resultado.

Porcentaje global de sentencias favorables vs desfavorables.

Análisis de frecuencia por motivo y por parte demandada.

🧩 Habilidades demostradas

Orquestación end-to-end con Cloud Composer y Pub/Sub.

Uso avanzado de Vertex AI Generative Models (Gemini 2.0).

Diseño de pipelines ETL en Cloud Data Fusion y carga incremental a BigQuery.

Creación de dashboards interactivos en Looker Studio.

Integración de procesamiento IA on-premise con servicios nativos de Google Cloud.

🚀 Próximos pasos (roadmap)

Añadir control de reintentos y gestión de errores fine-grained en Composer.

Calcular una métrica de confianza media por motivo usando la salida de Gemini.

Extender el pipeline a otros tipos de documentos (autos, decretos y providencias).

Integrar análisis de tendencias temporal en BigQuery y Looker.

👤 Autor


📍 Data Engineer | Legal-Tech Developer
💼 Proyecto desarrollado como parte del laboratorio de IA Jurídica en Vertex AI

