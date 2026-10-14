# Analyzing Data and Enabling Machine Learning

## 1. Analysis / BI Tools
- **Looker Studio** (formerly Data Studio): free, lightweight dashboards/reports, connects to BigQuery, Sheets, GA, etc.
- **Looker**: enterprise BI platform, semantic modeling layer (LookML), governed self-service analytics.
- **BigQuery BI Engine**: in-memory layer for sub-second dashboard queries.
- **Connected Sheets**: analyze billions of rows of BigQuery data directly from Google Sheets.
- **Jupyter/Colab Enterprise & Vertex AI Workbench**: notebook environments for data scientists.

## 2. Vertex AI (Unified ML Platform)
- Consolidates AI Platform, AutoML, and other legacy ML products into one platform.
- Key components:
  - **Vertex AI Workbench**: managed Jupyter notebooks.
  - **AutoML**: train high-quality models (tabular, image, text, video) with minimal ML expertise — no custom code needed.
  - **Custom Training**: bring your own TensorFlow/PyTorch/scikit-learn code, run on managed infrastructure (supports distributed training, GPUs/TPUs).
  - **Vertex AI Pipelines**: orchestrate ML workflows (based on Kubeflow Pipelines/TFX) — reproducible, versioned ML pipelines.
  - **Feature Store**: centralized repository for ML features, ensures consistency between training and serving (avoids training/serving skew).
  - **Model Registry & Endpoints**: version models, deploy for online (real-time) or batch prediction.
  - **Vertex AI Model Monitoring**: detects training/serving skew and data drift in production models.
  - **Explainable AI**: feature attribution for model predictions (important for compliance/trust).

## 3. BigQuery ML
- Train/deploy models using SQL directly on BigQuery data — no data movement required.
- Supported models: linear/logistic regression, k-means clustering, matrix factorization (recommendations), time-series (ARIMA_PLUS), boosted trees (XGBoost), deep neural networks, AutoML tables (via `CREATE MODEL ... OPTIONS(model_type='AUTOML_...')`), and importing TensorFlow/ONNX models for prediction.
- Best when: team is SQL-strong, data already in BigQuery, want fast iteration without export/import overhead.

## 4. Pre-trained APIs (no training needed)
- **Vision AI**: image labeling, OCR, face/object detection.
- **Natural Language AI**: entity/sentiment/syntax analysis.
- **Translation AI**, **Speech-to-Text**, **Text-to-Speech**.
- **Document AI**: parse structured data from forms/invoices/receipts.
- Use these when the task matches a common pattern — don't build custom models for solved problems (exam favorite: "minimize ML expertise/time to market" → pick a pre-trained API or AutoML over custom training).

## 5. ML Workflow Concepts Tested
- **Training/serving skew**: when feature engineering differs between training and inference — avoid via Feature Store / shared pipeline code.
- **Data drift / concept drift**: monitor production input distributions vs training distribution; retrain when drift detected.
- **Train/validation/test split**: typical rule — don't let same entity leak across splits (e.g., split by user_id, not by random row, to avoid leakage).
- **Imbalanced classes**: use techniques like class weighting, resampling, or appropriate metrics (precision/recall/F1, AUC-PR) instead of plain accuracy.
- **Overfitting**: regularization, dropout, more data, simpler model, early stopping.
- **Pipeline reproducibility**: use Vertex AI Pipelines / TFX to version data, code, and models together.

## 6. Choosing Between Options (exam logic)
| Scenario | Best choice |
|---|---|
| Need sentiment analysis on reviews, no ML team | Natural Language AI (pre-trained) |
| Tabular data, want best accuracy with no ML expertise | Vertex AI AutoML Tables / BigQuery ML AUTOML |
| Data science team wants full control of architecture (custom TF model), needs GPUs/TPUs | Vertex AI Custom Training |
| Need to query + model in one SQL workflow | BigQuery ML |
| Need consistent features across training & serving at scale | Vertex AI Feature Store |
| Need to detect production model degrading over time | Vertex AI Model Monitoring |
