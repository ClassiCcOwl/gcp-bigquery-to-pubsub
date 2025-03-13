# GCP BigQuery to Pub/Sub  

This repository contains a **Google Cloud Function** that retrieves query results from **BigQuery** and publishes them to a **Pub/Sub topic**. It is designed for **real-time data processing**, enabling seamless integration between BigQuery and Pub/Sub for **event-driven architectures, data pipelines, and streaming analytics**. The function is optimized with **batch settings, error handling, and logging** for reliability and scalability.  


## 🚀 Getting Started

### 1️⃣ Deploying the Cloud Function  
To use this function, you need to **deploy it to Google Cloud Run**.  
1. **Create a new Cloud Run function**.  
2. **Upload the following files** to the deployment:  
   - `main.py` (the function script)  
   - `requirements.txt` (dependencies)  
    - **Update** the following variables in `main.py` with your ***Google Cloud Project ID*** and ***Pub/Sub Topic***:  
     ```python
     PROJECT_ID = ""
     TOPIC_ID = ""
     ```
3. **Set the entry point** to:  
   ```plaintext
   publish_bq_results
4. **Follow the official guide** to build and deploy the function:  
👉 [See the guide on how to build and deploy the code](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service).  


### 2️⃣ Setting Up BigQuery Remote Function  

To allow BigQuery to **call the Cloud Run function**, follow these steps:  

1. **Create an external remote connection** in BigQuery.  
2. **Configure the connection** to authenticate with Cloud Run.  

    For detailed instructions, follow the **official guide**:  
👉 [See how to create a connection and use a remote function](https://cloud.google.com/bigquery/docs/remote-functions#create_a_connection).  
3. **Creating the BigQuery Remote Function**  

    Once the **external connection** is set up, you can create a **BigQuery function** that sends query results to Pub/Sub via the Cloud Run function.  

    Use the following SQL template to create the function (**replace placeholders** with your values):  

    ```sql
    CREATE OR REPLACE FUNCTION
        `PROJECT_ID.DATASET_ID.TO_PUBSUB`(query_result STRING) RETURNS JSON
    REMOTE WITH CONNECTION `PROJECT_ID.LOCATION.CONNECTION_NAME`
    OPTIONS (endpoint = 'ENDPOINT_URL');

### 3️⃣ Modifying Your Query to Use the New Function  

To send query results to Pub/Sub using the created BigQuery function, you need to modify your existing SQL queries.
Wrap your query with the following code to invoke the **TO_PUBSUB** function:

```sql

SELECT `dataset.TO_PUBSUB`(TO_JSON_STRING(STRUCT(couloumn)))
FROM `your_project.your_dataset.your_table`;
```

## For example, if you have a query like this:    

```sql
SELECT id, name, status 
FROM `your_project.your_dataset.your_table`
```

## You would modify it to:
```sql

SELECT `dataset.TO_PUBSUB`(TO_JSON_STRING(STRUCT(id, name, status)))
FROM `your_project.your_dataset.your_table`;
```