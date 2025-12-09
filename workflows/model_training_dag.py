"""
Model Training and Evaluation DAG

This DAG handles model training, hyperparameter tuning, evaluation,
and model registry updates.

Schedule: Weekly on Sundays at 3:00 AM UTC
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from airflow.sensors.external_task import ExternalTaskSensor


# Default arguments
default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email': ['ml-team@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
    'execution_timeout': timedelta(hours=4),
}

# Create the DAG
dag = DAG(
    'model_training_pipeline',
    default_args=default_args,
    description='ML model training and evaluation pipeline',
    schedule_interval='0 3 * * 0',  # Weekly on Sunday at 3 AM UTC
    catchup=False,
    tags=['ml', 'training', 'kmeans', 'clustering'],
    max_active_runs=1,
)


# Task functions
def load_features(**context):
    """Load processed features for model training."""
    from pathlib import Path
    import pickle
    
    feature_path = Path('datasets/processed/outliers_removed.pkl')
    
    with open(feature_path, 'rb') as f:
        features = pickle.load(f)
    
    print(f"Loaded {len(features)} customer records")
    context['task_instance'].xcom_push(key='feature_count', value=len(features))
    return str(feature_path)


def scale_features(**context):
    """Scale features using StandardScaler."""
    from sklearn.preprocessing import StandardScaler
    from pathlib import Path
    import pickle
    
    # Load features
    feature_path = Path('datasets/processed/outliers_removed.pkl')
    with open(feature_path, 'rb') as f:
        features = pickle.load(f)
    
    # Scale features (excluding CustomerID)
    scaler = StandardScaler()
    feature_cols = features.columns[1:]  # Exclude CustomerID
    scaled_data = scaler.fit_transform(features[feature_cols])
    
    # Save scaled features
    output_path = Path('datasets/processed/scaled_features.pkl')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'wb') as f:
        pickle.dump({
            'features': scaled_data,
            'customer_ids': features['CustomerID'].values,
            'scaler': scaler
        }, f)
    
    print(f"Scaled {scaled_data.shape[0]} records with {scaled_data.shape[1]} features")
    return str(output_path)


def apply_pca(**context):
    """Apply PCA for dimensionality reduction."""
    from sklearn.decomposition import PCA
    from pathlib import Path
    import pickle
    
    # Load scaled features
    scaled_path = Path('datasets/processed/scaled_features.pkl')
    with open(scaled_path, 'rb') as f:
        data = pickle.load(f)
    
    # Apply PCA
    pca = PCA(n_components=0.95)  # Retain 95% variance
    pca_features = pca.fit_transform(data['features'])
    
    # Save PCA results
    output_path = Path('datasets/processed/pca_features.pkl')
    with open(output_path, 'wb') as f:
        pickle.dump({
            'features': pca_features,
            'customer_ids': data['customer_ids'],
            'pca': pca,
            'explained_variance': pca.explained_variance_ratio_
        }, f)
    
    print(f"PCA reduced to {pca_features.shape[1]} components")
    print(f"Explained variance: {pca.explained_variance_ratio_.sum():.4f}")
    
    return str(output_path)


def train_kmeans(**context):
    """Train K-Means clustering model."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
    from pathlib import Path
    import pickle
    import mlflow
    
    # Load PCA features
    pca_path = Path('datasets/processed/pca_features.pkl')
    with open(pca_path, 'rb') as f:
        data = pickle.load(f)
    
    # MLflow tracking
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("customer_segmentation")
    
    with mlflow.start_run(run_name=f"kmeans_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        # Train K-Means
        n_clusters = 3
        kmeans = KMeans(
            n_clusters=n_clusters,
            init='k-means++',
            n_init=10,
            max_iter=300,
            random_state=42
        )
        
        clusters = kmeans.fit_predict(data['features'])
        
        # Calculate metrics
        silhouette = silhouette_score(data['features'], clusters)
        davies_bouldin = davies_bouldin_score(data['features'], clusters)
        calinski_harabasz = calinski_harabasz_score(data['features'], clusters)
        
        # Log parameters and metrics
        mlflow.log_param("n_clusters", n_clusters)
        mlflow.log_param("init", "k-means++")
        mlflow.log_param("n_init", 10)
        mlflow.log_metric("silhouette_score", silhouette)
        mlflow.log_metric("davies_bouldin_score", davies_bouldin)
        mlflow.log_metric("calinski_harabasz_score", calinski_harabasz)
        
        # Save model
        model_path = Path('models/kmeans_model.pkl')
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': kmeans,
                'clusters': clusters,
                'customer_ids': data['customer_ids'],
                'metrics': {
                    'silhouette': silhouette,
                    'davies_bouldin': davies_bouldin,
                    'calinski_harabasz': calinski_harabasz
                }
            }, f)
        
        # Log model
        mlflow.sklearn.log_model(kmeans, "kmeans_model")
        
        print(f"Model trained with {n_clusters} clusters")
        print(f"Silhouette Score: {silhouette:.4f}")
        print(f"Davies-Bouldin Index: {davies_bouldin:.4f}")
        print(f"Calinski-Harabasz Index: {calinski_harabasz:.4f}")
        
        context['task_instance'].xcom_push(key='silhouette_score', value=silhouette)
        
        return str(model_path)


def evaluate_model(**context):
    """Evaluate model performance and generate reports."""
    from pathlib import Path
    import pickle
    import pandas as pd
    
    # Load model
    model_path = Path('models/kmeans_model.pkl')
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)
    
    # Generate cluster distribution
    unique, counts = pd.Series(model_data['clusters']).value_counts().sort_index().items()
    
    print("Cluster Distribution:")
    for cluster, count in zip(unique, counts):
        percentage = (count / len(model_data['clusters'])) * 100
        print(f"  Cluster {cluster}: {count} customers ({percentage:.2f}%)")
    
    # Check if model meets quality threshold
    silhouette = model_data['metrics']['silhouette']
    threshold = 0.3
    
    if silhouette >= threshold:
        print(f"✓ Model quality acceptable (Silhouette: {silhouette:.4f} >= {threshold})")
        return "approved"
    else:
        print(f"✗ Model quality below threshold (Silhouette: {silhouette:.4f} < {threshold})")
        return "rejected"


# Wait for data pipeline to complete
wait_for_data_pipeline = ExternalTaskSensor(
    task_id='wait_for_data_pipeline',
    external_dag_id='customer_segmentation_pipeline',
    external_task_id='pipeline_complete',
    allowed_states=['success'],
    failed_states=['failed', 'skipped'],
    mode='reschedule',
    timeout=3600,
    dag=dag
)

# Model Training Task Group
with TaskGroup('model_training', dag=dag) as model_training_group:
    
    start_training = EmptyOperator(
        task_id='start',
        dag=dag
    )
    
    load_data = PythonOperator(
        task_id='load_features',
        python_callable=load_features,
        provide_context=True,
        dag=dag
    )
    
    scale_data = PythonOperator(
        task_id='scale_features',
        python_callable=scale_features,
        provide_context=True,
        dag=dag
    )
    
    apply_pca_transform = PythonOperator(
        task_id='apply_pca',
        python_callable=apply_pca,
        provide_context=True,
        dag=dag
    )
    
    train_model = PythonOperator(
        task_id='train_kmeans',
        python_callable=train_kmeans,
        provide_context=True,
        dag=dag
    )
    
    evaluate = PythonOperator(
        task_id='evaluate_model',
        python_callable=evaluate_model,
        provide_context=True,
        dag=dag
    )
    
    end_training = EmptyOperator(
        task_id='end',
        dag=dag
    )
    
    (start_training >> load_data >> scale_data >> apply_pca_transform >> 
     train_model >> evaluate >> end_training)


# Pipeline structure
pipeline_start = EmptyOperator(
    task_id='pipeline_start',
    dag=dag
)

pipeline_end = EmptyOperator(
    task_id='pipeline_complete',
    dag=dag,
    trigger_rule='all_success'
)

# Define dependencies
pipeline_start >> wait_for_data_pipeline >> model_training_group >> pipeline_end
