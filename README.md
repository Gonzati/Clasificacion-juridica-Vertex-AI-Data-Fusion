#  Clasificación jurídica automatizada con Vertex AI y orquestación ETL en Google Cloud

Este proyecto implementa un **pipeline completo de análisis y clasificación de resoluciones judiciales** utilizando herramientas nativas de Google Cloud.  
Combina **IA generativa (Gemini 2.0)**, procesamiento en **Cloud Data Fusion**, almacenamiento en **BigQuery** y visualización en **Looker Studio**, para crear un flujo de datos **end-to-end**, escalable y automatizado.

##  Tecnologías utilizadas

| Capa | Herramienta | Función |
|------|--------------|---------|
| **IA / Clasificación** | Vertex AI (Gemini 2.0 Flash / Pro) | Análisis semántico completo de sentencias |
| **Almacenamiento RAW** | Cloud Storage  | Ficheros `.txt` originales |
| **Orquestación / ETL** | Cloud Data Fusion | Unión, limpieza y carga en BigQuery |
| **Transformación** | Wrangler + Joiner | Normalización y fusión de CSVs |
| **Data Warehouse** | BigQuery | Tabla final `sentenciasmerged` |
| **Visualización** | Looker Studio | Dashboards de motivos y resultados |
| **Entorno de desarrollo** | Vertex AI Workbench (Jupyter Notebooks) | Ejecución y experimentación |


---

## Lógica de clasificación

###  Notebook: **Clasificación de motivos**
- Lee archivos `.txt` del bucket origen.
- Envía cada sentencia completa a Gemini 2.0 (Vertex AI)
- Extrae un JSON con los **motivos jurídicos** más relevantes (hasta 4)
- Guarda el resultado incrementalmente en el bucket de destino.


### Notebook: **Clasificación de resultado y parte demandada**
- Analiza la sentencia completa y determina:
- `demandado`: `"eos"` o `"contrario"`
- `resultado`: `"favorable"` o `"desfavorable"`
- Salida incremental en bucket de destino.


---

## Pipeline de integración (Cloud Data Fusion)

### 🔹 Componentes:
- **GCS Source (1):** lee `sentencias_motivos_vertex.csv`
- **GCS Source (2):** lee `sentencias_resultado_vertex.csv`
- **Joiner:** une ambos datasets por la columna `nombre`
- **Wrangler:** limpia y ordena las columnas
- **BigQuery Sink:** inserta los datos en la tabla final:`Sentencias.sentenciasmerged

##  Visualización (Looker Studio)

El dataset final (`sentenciasmerged`) alimenta un dashboard interactivo con:
- **Distribución de motivos jurídicos** por tipo de resultado
- **Porcentaje global** de sentencias favorables/desfavorables

## Habilidades demostradas
- Orquestación de pipelines **end-to-end** en **Google Cloud**.  
- Uso avanzado de **Vertex AI Generative Models (Gemini 2.0)**.  
- Modelado y carga incremental de datos en **BigQuery**.  
- Creación de dashboards **interactivos en Looker Studio**.  
- Automatización de procesos legales mediante IA aplicada.

## Próximos pasos (roadmap)
- Integrar **Cloud Functions trigger** para ejecutar los notebooks al subir nuevas sentencias.  
- Añadir análisis de **confianza promedio** por motivo.  
- Automatizar la ejecución diaria del pipeline mediante **Cloud Composer (Airflow)**.

---

##  Autor
**Ángel Argibay**  
📍 Data Engineer | Legal-Tech Developer  
💼 Proyecto desarrollado como parte del laboratorio de IA Jurídica en Vertex AI  
🔗 [LinkedIn](https://www.linkedin.com/in/angelargibay) · [GitHub](https://github.com/Gonzati)

