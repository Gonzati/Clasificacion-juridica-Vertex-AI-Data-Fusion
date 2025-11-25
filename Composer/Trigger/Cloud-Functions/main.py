import os, json, time
import functions_framework
from cloudevents.http import CloudEvent

from google.auth import default
from google.auth.transport.requests import AuthorizedSession

PROJECT  = os.environ["GCP_PROJECT"]
LOCATION = os.environ["LOCATION"]         # us-east4 
ENV      = os.environ["COMPOSER_ENV"]     # composer-rag
DAG_ID   = os.environ["DAG_ID"]           # run_notebooks_and_datafusion

def _authed_session():
    creds, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    return AuthorizedSession(creds)

def _composer_base():
    return f"https://composer.googleapis.com/v1/projects/{PROJECT}/locations/{LOCATION}/environments/{ENV}"

@functions_framework.cloud_event
def trigger_dag(event: CloudEvent):
    data = event.data or {}
    bucket = data.get("bucket")
    name   = data.get("name")
    if not bucket or not name:
        print("Evento sin bucket/name; nada que hacer.")
        return "OK", 204

    # Pasamos el objeto como conf al DAG (opcional)
    dag_conf = {"bucket": bucket, "name": name}

    session = _authed_session()
    base = _composer_base()

    # 1) Ejecuta: airflow CLI -> dags trigger <DAG_ID> --conf '<json>'
    body = {
        "command": "dags",
        "subcommand": "trigger",
        "parameters": [DAG_ID, "--conf", json.dumps(dag_conf)]
    }
    r = session.post(f"{base}:executeAirflowCommand", json=body)
    print("executeAirflowCommand:", r.status_code, r.text)
    if r.status_code >= 300:
        raise RuntimeError(f"Composer API error (execute): {r.text}")

    exec_id = r.json().get("executionId")
    if not exec_id:
        print("Sin executionId (posible éxito rápido).")
        return "OK", 200

    # 2) Poll corto (opcional) para registrar estado del CLI
    for _ in range(6):  # ~30s máx
        pr = session.post(f"{base}:pollAirflowCommand", json={"executionId": exec_id})
        print("pollAirflowCommand:", pr.status_code, pr.text)
        if pr.status_code >= 300:
            break
        jr = pr.json()
        if jr.get("done"):
            print("Airflow CLI done:", jr.get("output", ""))
            break
        time.sleep(5)

    return "OK", 200
