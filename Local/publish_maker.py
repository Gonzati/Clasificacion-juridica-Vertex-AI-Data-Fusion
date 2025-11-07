# ~/jupyter_env/trabajo/pipeline/publish_marker.py

from google.cloud import pubsub_v1

project_id = "xxxx"
topic_id = "notebook-finished"
message = "done"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

future = publisher.publish(topic_path, message.encode("utf-8"))
print(f"✅ Marker publicado en Pub/Sub: {future.result()}")
