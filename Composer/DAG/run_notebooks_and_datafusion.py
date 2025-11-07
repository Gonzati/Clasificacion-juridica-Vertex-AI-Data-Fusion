from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.google.cloud.sensors.pubsub import PubSubPullSensor
from airflow.providers.google.cloud.operators.datafusion import CloudDataFusionStartPipelineOperator
from google.cloud import pubsub_v1


# -------------------- CONFIG --------------------
PROJECT_ID   = "rag-vertex-477211"
CMD_TOPIC    = "rag-notebook-commands"      # Topic al que publica el DAG
DONE_SUB     = "rag-notebook-done-sub"      # Suscripción donde escucha el sensor
OWNER        = "angel"

# Data Fusion
DATAFUSION_INSTANCE = "df-basic-01"
DATAFUSION_LOCATION = "Location"
DATAFUSION_PIPELINE = "sentenciasmerged"

default_args = {
    "owner": OWNER,
    "retries": 0,
}

with DAG(
    dag_id="run_notebooks_and_datafusion",
    description="Lanza los notebooks vía Pub/Sub y luego ejecuta el pipeline de Data Fusion.",
    start_date=datetime(2025, 11, 6),
    schedule_interval=None,
    catchup=False,
    default_args=default_args,
    tags=["rag", "datafusion"],
) as dag:

    start = EmptyOperator(task_id="start")

    # 1) correlation_id
    def _make_correlation_id(**context):
        corr = f"corr-{uuid.uuid4()}"
        context["ti"].xcom_push(key="correlation_id", value=corr)
        return corr

    make_correlation_id = PythonOperator(
        task_id="make_correlation_id",
        python_callable=_make_correlation_id,
    )

    # 2) Construir body/attrs
    def _build_messages(**context):
        ti = context["ti"]
        corr = ti.xcom_pull(task_ids="make_correlation_id", key="correlation_id")
        body = {"command": "run_notebook_batch", "ts": time.time()}
        attrs = {"correlation_id": corr, "pipeline": "rag-notebooks"}
        ti.xcom_push(key="pubsub_message_body", value=body)
        ti.xcom_push(key="pubsub_message_attrs", value=attrs)

    build_messages = PythonOperator(
        task_id="build_messages",
        python_callable=_build_messages,
    )

    # 3) Publicar mensaje en Pub/Sub (bytestring)
    def _publish_to_pubsub(**context):
        ti = context["ti"]
        body = ti.xcom_pull(task_ids="build_messages", key="pubsub_message_body")
        attrs = ti.xcom_pull(task_ids="build_messages", key="pubsub_message_attrs")

        data = json.dumps(body).encode("utf-8")
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(PROJECT_ID, CMD_TOPIC)

        future = publisher.publish(topic_path, data=data, **attrs)
        mid = future.result(timeout=30)
        ti.xcom_push(key="pubsub_message_id", value=mid)

    publish_to_pubsub = PythonOperator(
        task_id="publish_to_pubsub",
        python_callable=_publish_to_pubsub,
    )

    # 4) Esperar mensaje DONE del runner
    def _messages_callback(messages, context, **kwargs):
        ti = context["ti"]
        corr = ti.xcom_pull(task_ids="make_correlation_id", key="correlation_id")
        for rm in messages:
            msg = rm.message
            attrs = dict(msg.attributes or {})
            if attrs.get("correlation_id") == corr and attrs.get("event") in {"done", "success"}:
                ti.xcom_push(key="done_payload", value=(msg.data or b"").decode("utf-8", "ignore"))
                ti.xcom_push(key="done_event_attrs", value=attrs)
                return True
        return False

    wait_for_marker = PubSubPullSensor(
        task_id="wait_for_marker",
        project_id=PROJECT_ID,
        subscription=DONE_SUB,
        messages_callback=_messages_callback,
        ack_messages=True,
        max_messages=10,
        poke_interval=10,
        timeout=3600,
        mode="reschedule",
    )

    # 5) Lanzar el pipeline de Data Fusion
    start_datafusion_pipeline = CloudDataFusionStartPipelineOperator(
        task_id="start_datafusion_pipeline",
        location=DATAFUSION_LOCATION,
        instance_name=DATAFUSION_INSTANCE,
        pipeline_name=DATAFUSION_PIPELINE,
        pipeline_timeout=1800,
        asynchronous=False,                # espera hasta que termine
        execution_timeout=timedelta(minutes=35),
    )

    # Flow
    start >> make_correlation_id >> build_messages >> publish_to_pubsub >> wait_for_marker >> start_datafusion_pipeline
