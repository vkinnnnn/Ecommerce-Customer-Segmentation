"""
Customer Segmentation Data Pipeline DAG

This DAG orchestrates the complete data processing pipeline for customer segmentation,
from data acquisition through feature engineering.

Schedule: Daily at 2:00 AM UTC
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup

# Import processing modules
import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'modules'))

from modules import (
    fetchDataset,
    extractArchive,
    loadDataset,
    processMissingValues,
    eliminateDuplicates,
    classifyTransactionStatus,
    detectCodeAnomalies,
    cleanDescriptions,
    validatePricing,
    analyzeCustomerValue,
    aggregateProductData,
    analyzeBehaviorPatterns,
    buildLocationFeatures,
    analyzeCancellations,
    extractTemporalPatterns,
    removeOutliers
)


# Default arguments for the DAG
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email': ['data-team@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}

# Create the DAG
dag = DAG(
    'customer_segmentation_pipeline',
    default_args=default_args,
    description='End-to-end customer segmentation data pipeline',
    schedule_interval='0 2 * * *',  # Daily at 2 AM UTC
    catchup=False,
    tags=['customer-segmentation', 'data-pipeline', 'ml'],
    max_active_runs=1,
)


# Task wrapper functions
def fetch_dataset_task(**context):
    """Download dataset from UCI repository."""
    result = fetchDataset()
    context['task_instance'].xcom_push(key='archive_path', value=result)
    return result


def extract_archive_task(**context):
    """Extract downloaded archive."""
    archive_path = context['task_instance'].xcom_pull(
        task_ids='data_acquisition.fetch_dataset',
        key='archive_path'
    )
    result = extractArchive(archiveFilePath=archive_path)
    context['task_instance'].xcom_push(key='excel_path', value=result)
    return result


def load_dataset_task(**context):
    """Load dataset into pickle format."""
    result = loadDataset()
    context['task_instance'].xcom_push(key='data_path', value=result)
    return result


# Data Acquisition Task Group
with TaskGroup('data_acquisition', dag=dag) as data_acquisition_group:
    
    start_acquisition = EmptyOperator(
        task_id='start',
        dag=dag
    )
    
    fetch_data = PythonOperator(
        task_id='fetch_dataset',
        python_callable=fetch_dataset_task,
        provide_context=True,
        dag=dag
    )
    
    extract_data = PythonOperator(
        task_id='extract_archive',
        python_callable=extract_archive_task,
        provide_context=True,
        dag=dag
    )
    
    load_data = PythonOperator(
        task_id='load_dataset',
        python_callable=loadDataset,
        dag=dag
    )
    
    end_acquisition = EmptyOperator(
        task_id='end',
        dag=dag
    )
    
    start_acquisition >> fetch_data >> extract_data >> load_data >> end_acquisition


# Data Cleaning Task Group
with TaskGroup('data_cleaning', dag=dag) as data_cleaning_group:
    
    start_cleaning = EmptyOperator(
        task_id='start',
        dag=dag
    )
    
    process_nulls = PythonOperator(
        task_id='process_missing_values',
        python_callable=processMissingValues,
        dag=dag
    )
    
    remove_duplicates = PythonOperator(
        task_id='eliminate_duplicates',
        python_callable=eliminateDuplicates,
        dag=dag
    )
    
    classify_transactions = PythonOperator(
        task_id='classify_transaction_status',
        python_callable=classifyTransactionStatus,
        dag=dag
    )
    
    detect_anomalies = PythonOperator(
        task_id='detect_code_anomalies',
        python_callable=detectCodeAnomalies,
        dag=dag
    )
    
    clean_desc = PythonOperator(
        task_id='clean_descriptions',
        python_callable=cleanDescriptions,
        dag=dag
    )
    
    validate_prices = PythonOperator(
        task_id='validate_pricing',
        python_callable=validatePricing,
        dag=dag
    )
    
    end_cleaning = EmptyOperator(
        task_id='end',
        dag=dag
    )
    
    (start_cleaning >> process_nulls >> remove_duplicates >> 
     classify_transactions >> detect_anomalies >> clean_desc >> 
     validate_prices >> end_cleaning)


# Feature Engineering Task Group
with TaskGroup('feature_engineering', dag=dag) as feature_engineering_group:
    
    start_features = EmptyOperator(
        task_id='start',
        dag=dag
    )
    
    rfm_analysis = PythonOperator(
        task_id='analyze_customer_value',
        python_callable=analyzeCustomerValue,
        dag=dag
    )
    
    product_agg = PythonOperator(
        task_id='aggregate_product_data',
        python_callable=aggregateProductData,
        dag=dag
    )
    
    behavior_analysis = PythonOperator(
        task_id='analyze_behavior_patterns',
        python_callable=analyzeBehaviorPatterns,
        dag=dag
    )
    
    location_features = PythonOperator(
        task_id='build_location_features',
        python_callable=buildLocationFeatures,
        dag=dag
    )
    
    cancellation_analysis = PythonOperator(
        task_id='analyze_cancellations',
        python_callable=analyzeCancellations,
        dag=dag
    )
    
    temporal_patterns = PythonOperator(
        task_id='extract_temporal_patterns',
        python_callable=extractTemporalPatterns,
        dag=dag
    )
    
    end_features = EmptyOperator(
        task_id='end',
        dag=dag
    )
    
    (start_features >> rfm_analysis >> product_agg >> behavior_analysis >> 
     location_features >> cancellation_analysis >> temporal_patterns >> end_features)


# Advanced Analytics Task Group
with TaskGroup('advanced_analytics', dag=dag) as advanced_analytics_group:
    
    start_analytics = EmptyOperator(
        task_id='start',
        dag=dag
    )
    
    remove_outlier_records = PythonOperator(
        task_id='remove_outliers',
        python_callable=removeOutliers,
        dag=dag
    )
    
    end_analytics = EmptyOperator(
        task_id='end',
        dag=dag
    )
    
    start_analytics >> remove_outlier_records >> end_analytics


# Pipeline start and end
pipeline_start = EmptyOperator(
    task_id='pipeline_start',
    dag=dag
)

pipeline_end = EmptyOperator(
    task_id='pipeline_complete',
    dag=dag,
    trigger_rule='all_success'
)

# Define task dependencies
(pipeline_start >> data_acquisition_group >> data_cleaning_group >> 
 feature_engineering_group >> advanced_analytics_group >> pipeline_end)
