#  Clasificación jurídica automatizada con Vertex AI y orquestación ETL en Google Cloud

Este proyecto implementa un **pipeline completo de análisis y clasificación de resoluciones judiciales** utilizando herramientas nativas de Google Cloud.  
Combina **IA generativa (Gemini 2.0)**, procesamiento en **Cloud Data Fusion**, almacenamiento en **BigQuery** y visualización en **Looker Studio**, para crear un flujo de datos **end-to-end**, escalable y automatizado.

---

## Arquitectura general

📂 Google Cloud Storage (rag-legal-corpus)
│
▼
🤖 Vertex AI (Gemini 2.0 - Full Text Classification)
│ ├── Extracción de motivos jurídicos
│ └── Clasificación de resultado y parte demandada
▼
📂 Google Cloud Storage 
│
▼
🧩 Cloud Data Fusion (ETL Pipeline)
├── GCS → Joiner → Wrangler → BigQuery
│
▼
🗃️ BigQuery Dataset: Sentencias.sentenciasmerged
│
▼
📊 Looker Studio Dashboard
├── Distribución de motivos
└── Tasa de sentencias favorables vs desfavorables

