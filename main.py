import json
import logging
from concurrent import futures

import functions_framework
from google.cloud import pubsub_v1

logging.basicConfig(level=logging.INFO)

# Set your Pub/Sub topic
PROJECT_ID = ""
TOPIC_ID = ""

batch_settings = pubsub_v1.types.BatchSettings(
    max_messages=10,
    max_bytes=1024,
    max_latency=1,
)

publisher = pubsub_v1.PublisherClient(batch_settings)
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)


def callback(future: pubsub_v1.publisher.futures.Future) -> None:
    """Handles the result of a published message."""
    try:
        message_id = future.result()
        logging.info(f"Message published with ID: {message_id}")
    except Exception as e:
        logging.error(f"Failed to publish message: {e}")


@functions_framework.http
def publish_bq_results(request):
    """Cloud Function to receive BigQuery results and publish to Pub/Sub."""

    try:
        request_json = request.get_json(silent=True)
        if not request_json or "calls" not in request_json:
            return {"error": "Invalid request format"}

        calls = request_json.get("calls", [])
        publish_futures = []
        replies = []
        for call in calls:
            if not isinstance(call, list) or not call:
                continue  # Skip invalid data format
            bq_result = call[0]
            try:
                data = bq_result.encode("utf-8")
                json_data = json.loads(bq_result)
                replies.append(json_data)
                publish_future = publisher.publish(topic_path, data)
                publish_future.add_done_callback(callback)
                publish_futures.append(publish_future)
            except json.JSONDecodeError:
                logging.warning(f"Invalid JSON format: {bq_result}")
                replies.append({"error": "Invalid JSON format"})

        futures.wait(publish_futures, return_when=futures.ALL_COMPLETED)
        return {"replies": replies}
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return {"error": "Internal server error"}
