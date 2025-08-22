#!/bin/bash

# Setup Monitoring and Logging for Notes App
# This script configures Cloud Monitoring, Logging, and Error Reporting

set -e

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-your-project-id}"
REGION="${REGION:-us-central1}"

echo "📊 Setting up monitoring and logging for Notes App"
echo "Project ID: $PROJECT_ID"

# Set the project
gcloud config set project $PROJECT_ID

echo "📋 Enabling monitoring and logging APIs..."
gcloud services enable \
  monitoring.googleapis.com \
  logging.googleapis.com \
  clouderrorreporting.googleapis.com \
  cloudtrace.googleapis.com \
  cloudprofiler.googleapis.com

echo "📈 Creating custom metrics..."

# Create custom metrics
gcloud logging metrics create notes_created_count \
  --description="Count of notes created" \
  --log-filter='resource.type="cloud_run_revision" AND textPayload:"Note created"' \
  --quiet || echo "Metric notes_created_count already exists"

gcloud logging metrics create tasks_created_count \
  --description="Count of tasks created" \
  --log-filter='resource.type="cloud_run_revision" AND textPayload:"Task created"' \
  --quiet || echo "Metric tasks_created_count already exists"

gcloud logging metrics create ai_requests_count \
  --description="Count of AI requests" \
  --log-filter='resource.type="cloud_run_revision" AND textPayload:"AI request"' \
  --quiet || echo "Metric ai_requests_count already exists"

gcloud logging metrics create error_count \
  --description="Count of application errors" \
  --log-filter='resource.type="cloud_run_revision" AND severity>=ERROR' \
  --quiet || echo "Metric error_count already exists"

echo "🚨 Creating alerting policies..."

# Create notification channel (email)
NOTIFICATION_CHANNEL=$(gcloud alpha monitoring channels create \
  --display-name="Notes App Alerts" \
  --type=email \
  --channel-labels=email_address="${ADMIN_EMAIL:-admin@example.com}" \
  --format="value(name)" \
  --quiet || echo "projects/$PROJECT_ID/notificationChannels/existing")

# High error rate alert
gcloud alpha monitoring policies create \
  --policy-from-file=<(cat <<EOF
displayName: "High Error Rate - Notes App"
conditions:
  - displayName: "Error rate > 5%"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND resource.labels.service_name=~"(user|notes|tasks|ai)-service"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 0.05
      duration: 300s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_RATE
          crossSeriesReducer: REDUCE_MEAN
          groupByFields: ["resource.labels.service_name"]
combiner: OR
notificationChannels: ["$NOTIFICATION_CHANNEL"]
alertStrategy:
  autoClose: 86400s
EOF
) \
  --quiet || echo "Error rate alert policy already exists"

# High latency alert
gcloud alpha monitoring policies create \
  --policy-from-file=<(cat <<EOF
displayName: "High Latency - Notes App"
conditions:
  - displayName: "Request latency > 5s"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_latencies"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 5000
      duration: 180s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_PERCENTILE_95
          crossSeriesReducer: REDUCE_MEAN
          groupByFields: ["resource.labels.service_name"]
combiner: OR
notificationChannels: ["$NOTIFICATION_CHANNEL"]
EOF
) \
  --quiet || echo "Latency alert policy already exists"

# Memory usage alert
gcloud alpha monitoring policies create \
  --policy-from-file=<(cat <<EOF
displayName: "High Memory Usage - Notes App"
conditions:
  - displayName: "Memory usage > 80%"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/container/memory/utilizations"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 0.8
      duration: 300s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_MEAN
          crossSeriesReducer: REDUCE_MEAN
          groupByFields: ["resource.labels.service_name"]
combiner: OR
notificationChannels: ["$NOTIFICATION_CHANNEL"]
EOF
) \
  --quiet || echo "Memory usage alert policy already exists"

echo "📊 Creating dashboard..."

# Create monitoring dashboard
gcloud monitoring dashboards create \
  --config-from-file=<(cat <<EOF
displayName: "Notes App Dashboard"
mosaicLayout:
  tiles:
    - width: 6
      height: 4
      widget:
        title: "Request Rate"
        xyChart:
          dataSets:
            - timeSeriesQuery:
                timeSeriesFilter:
                  filter: 'resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count"'
                  aggregation:
                    alignmentPeriod: 60s
                    perSeriesAligner: ALIGN_RATE
                    crossSeriesReducer: REDUCE_SUM
                    groupByFields: ["resource.labels.service_name"]
          yAxis:
            scale: LINEAR
    - width: 6
      height: 4
      xPos: 6
      widget:
        title: "Error Rate"
        xyChart:
          dataSets:
            - timeSeriesQuery:
                timeSeriesFilter:
                  filter: 'resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count" AND metric.labels.response_code_class!="2xx"'
                  aggregation:
                    alignmentPeriod: 60s
                    perSeriesAligner: ALIGN_RATE
                    crossSeriesReducer: REDUCE_SUM
                    groupByFields: ["resource.labels.service_name"]
    - width: 6
      height: 4
      yPos: 4
      widget:
        title: "Response Latency (95th percentile)"
        xyChart:
          dataSets:
            - timeSeriesQuery:
                timeSeriesFilter:
                  filter: 'resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_latencies"'
                  aggregation:
                    alignmentPeriod: 60s
                    perSeriesAligner: ALIGN_PERCENTILE_95
                    crossSeriesReducer: REDUCE_MEAN
                    groupByFields: ["resource.labels.service_name"]
    - width: 6
      height: 4
      xPos: 6
      yPos: 4
      widget:
        title: "Memory Utilization"
        xyChart:
          dataSets:
            - timeSeriesQuery:
                timeSeriesFilter:
                  filter: 'resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/container/memory/utilizations"'
                  aggregation:
                    alignmentPeriod: 60s
                    perSeriesAligner: ALIGN_MEAN
                    crossSeriesReducer: REDUCE_MEAN
                    groupByFields: ["resource.labels.service_name"]
EOF
) \
  --quiet || echo "Dashboard already exists"

echo "🔍 Setting up logging..."

# Create log-based metrics for custom application events
gcloud logging sinks create notes-app-sink \
  bigquery.googleapis.com/projects/$PROJECT_ID/datasets/notes_app_logs \
  --log-filter='resource.type="cloud_run_revision" AND resource.labels.service_name=~"(user|notes|tasks|ai)-service"' \
  --quiet || echo "Log sink already exists"

echo "🔐 Setting up security monitoring..."

# Create security event alerts
gcloud alpha monitoring policies create \
  --policy-from-file=<(cat <<EOF
displayName: "Security Events - Notes App"
conditions:
  - displayName: "Authentication failures"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND textPayload:"authentication failed"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 10
      duration: 300s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_RATE
          crossSeriesReducer: REDUCE_SUM
combiner: OR
notificationChannels: ["$NOTIFICATION_CHANNEL"]
EOF
) \
  --quiet || echo "Security alert policy already exists"

echo "✅ Monitoring and logging setup complete!"
echo ""
echo "📊 Monitoring Dashboard: https://console.cloud.google.com/monitoring/dashboards"
echo "📝 Logs Explorer: https://console.cloud.google.com/logs/query"
echo "🚨 Alerting: https://console.cloud.google.com/monitoring/alerting"
echo "❌ Error Reporting: https://console.cloud.google.com/errors"
echo ""
echo "🔔 Notification Channel: $NOTIFICATION_CHANNEL"
echo ""
echo "⚠️ Important:"
echo "1. Update the ADMIN_EMAIL variable to receive alerts"
echo "2. Configure BigQuery dataset for log exports if needed"
echo "3. Review and adjust alert thresholds based on your requirements"