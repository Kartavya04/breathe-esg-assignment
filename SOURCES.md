# Data Source Deep-Dive, Extraction Specifications & Vulnerability Analyses

Our system is engineered to absorb unstructured information from three distinct operational source categories typical of modern enterprise resource environments.

## 1. Analyzed Data Sources Profile

### Source A: Core Enterprise Resource Planning (ERP) Ingestion Stream (e.g., SAP / Oracle Extracts)
* **Real-World Format Researched:** Standard enterprise transactional log files, usually exported as tab-separated or comma-separated flat files directly from modules like SAP ERP Materials Management (MM).
* **Sample Data Structure Applied:**
    ```csv
    line_id,activity_type,quantity,unit,date
    SAP-TXN-9011,Diesel Fuel Consumption,4500.50,Liters,2026-05-15
    SAP-TXN-9012,Natural Gas Pipeline Feed,2100.00,M3,2026-05-14
    ```
* **What Breaks in Real Production Deploys:** ERP exports frequently lack clean encoding (e.g., using UTF-16 instead of UTF-8) or include trailing summary balance headers that cause CSV parsing scripts to fail.

### Source B: Utility Supplier Infrastructure APIs (e.g., Direct Power Grid Data Feeds)
* **Real-World Format Researched:** Standardized utility billing datasets, structured interval meter profiles, or green-button JSON/CSV telemetry exports from providers like PG&E, National Grid, or Schneider EcoStruxure platforms.
* **Sample Data Structure Applied:**
    ```csv
    line_id,activity_type,quantity,unit,date
    METER-ELEC-442,Electricity Grid,14200.75,kWh,2026-05-10
    ```
* **What Breaks in Real Production Deploys:** Utility portals frequently update their column headers unexpectedly or mix different interval granularities (e.g., combining 15-minute smart meter intervals with monthly aggregate billing loops). This can break static index parsers.

### Source C: Unstructured Facilities Logbook Feeds (Manual Log Tracker Data)
* **Real-World Format Researched:** Ad-hoc spreadsheet logs compiled manually by factory floor workers or facilities coordinators, often containing unvalidated text fields.
* **Sample Data Structure Applied:**
    ```csv
    line_id,activity_type,quantity,unit,date
    ERR-ROW-99,Unknown Material Reversal,-60.00,Nos,2026-05-01
    ```
* **What Breaks in Real Production Deploys:** Manual spreadsheets are highly prone to formatting errors, such as spelling mistakes in activity names (e.g., "Dizet Fuel"), missing dates, or entering text descriptions in numeric quantity columns.

---

## 2. Robust Fault Ingestion Engine Handling Demonstration
The backend architecture prevents system failures by routing unmapped inputs, negative values, or unrecognized units into a designated anomaly hold pattern (`has_data_anomaly = True`), rather than rejecting the file outright. This ensures the ingestion pipeline remains resilient and reliable.