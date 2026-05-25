# Data Architecture & Multi-Tenant ESG Schema Specification

## 1. Entity-Relationship Diagram & Database Schema
Our database is engineered for strict enterprise compliance, handling multi-tenancy isolation, carbon accounting calculations (Scope 1/2/3), audit data lineage, and an immutable double-entry ledger-style lock system.

### Schema Overview:

#### A. `CompanyClient` (Tenant Model)
* `id` (BigAutoField, Primary Key)
* `company_name` (CharField, Unique)
* `created_at` (DateTimeField, auto_now_add=True)

#### B. `DataUploadBatch` (Source-of-Truth Data Lineage)
* `id` (BigAutoField, Primary Key)
* `client` (ForeignKey -> CompanyClient, On Delete Cascade)
* `source_system` (CharField) e.g., 'SAP', 'Utility Portal', 'Manual'
* `uploaded_by` (ForeignKey -> User, Nullable)
* `original_file_name` (CharField)
* `uploaded_at` (DateTimeField, auto_now_add=True)

#### C. `CarbonDataRow` (Granular Operational Journal Ledger)
* `id` (BigAutoField, Primary Key)
* `client` (ForeignKey -> CompanyClient)
* `upload_batch` (ForeignKey -> DataUploadBatch)
* `review_status` (CharField: 'PENDING' | 'APPROVED')
* `ghg_scope` (IntegerField: 1 | 2 | 3)
* `is_finalized_and_locked` (BooleanField, Default False)
* `has_data_anomaly` (BooleanField, Default False)
* `anomaly_explanation` (TextField)
* `source_system_line_id` (CharField)
* `unmodified_data_snapshot` (TextField) -> Store raw JSON/String format of the original payload for non-repudiation audit trails.
* `emission_activity_type` (CharField)
* `raw_quantity_entered` (DecimalField, max_digits=18, decimal_places=4)
* `raw_unit_entered` (CharField)
* `normalized_quantity` (DecimalField, max_digits=18, decimal_places=4)
* `normalized_unit` (CharField)
* `calculated_carbon_footprint_kg` (DecimalField, max_digits=18, decimal_places=4)
* `accounting_date` (DateField)

---

## 2. Architectural Justifications for Core Requirements

### A. Multi-Tenancy Isolation
Every data-bearing model (`DataUploadBatch`, `CarbonDataRow`) implements a foreign key restriction pointing straight to a `CompanyClient` tenant record. Database queries are strictly filtered by this identifier. This guarantees absolute logical isolation between discrete enterprise entities, fully mitigating cross-tenant leak vectors.

### B. GHG Scope 1 & Scope 2 Categorization Engine
A programmatic ingestion business-rules runtime classifies the activity signatures directly during row pipeline evaluation:
* **Scope 1 (Direct Emissions):** Triggered automatically by stationary/mobile combustion elements like "Diesel" or "Natural Gas".
* **Scope 2 (Indirect Emissions):** Triggered by utility consumption grids like "Electricity".

### C. Source-of-Truth Tracking & Immutability
Data lineage tracking is handled natively via the `DataUploadBatch` pointer. The exact immutable footprint raw packet is preserved inside `unmodified_data_snapshot`. Once an item changes its workflow status token to `APPROVED`, the database flips `is_finalized_and_locked` to `True`. The engine treats this as an absolute transactional lock, guarding audited numbers from retroactive modification.

### D. Unit Normalization Architecture
Raw numbers ingested are parsed into standardized global reporting metrics at the intake tier using high-precision SQL `DecimalField` tokens (to completely avoid floating-point binary inaccuracies). Units are normalized into standardized operational anchors:
* Volume values shift to **Liters** or **M3**
* Power configurations shift to **kWh**
* Footprint outcomes are computed into absolute mass kilograms of $CO_2e$ values ($calculated\_carbon\_footprint\_kg$).

### E. Advanced Audit Trails
The layout maintains full observability records: who uploaded a set (`uploaded_by`), what file produced it (`original_file_name`), when it took place (`uploaded_at`), and whether automated pipeline data validation flagged irregularities (`has_data_anomaly`).