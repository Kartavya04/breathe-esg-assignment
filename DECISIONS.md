# Product Architectural Decisions & Product Management Resolutions

During development, multiple data standard ambiguities and product requirements gaps were proactively resolved to ensure production readiness.

## 1. Ambiguities Resolved & Strategic Choices Made

### A. Lack of Explicit Emission Factors in Source Payloads
* **Ambiguity:** Source feeds provide consumption quantities (e.g., Liters of Diesel) but omit the specific Emission Factor ($EF$) variable required to calculate carbon intensity.
* **Resolution:** Implemented an internal static compliance lookup engine mapping global statutory standards (e.g., Defra / EPA baseline guidelines). 
    * *Diesel Fuel consumption modifier:* $2.68$ kg $CO_2e$ per Liter.
    * *Natural Gas conversion factor:* $2.02$ kg $CO_2e$ per $M^3$.
    * *Electricity utility grid average:* $0.85$ kg $CO_2e$ per kWh.

### B. High Potential for Source File Bad Formatting
* **Ambiguity:** Real-world enterprise source extracts inevitably contain negative adjustments, blank string values, or unmapped fuel items.
* **Resolution:** Engineered an automated validation layer instead of crashing the ingest thread. Bad data blocks are marked as `has_data_anomaly = True` and flagged with specific explanatory text strings, making it easy for an analyst to spot problems during review without losing data lineage.

### C. Scope 3 Strategy
* **Decision:** For this version of the pipeline, we intentionally omitted automatic classification for complex supply chain Scope 3 line items. The current framework concentrates exclusively on high-certainty operational metrics (Scope 1 Direct Combustion and Scope 2 Purchased Electricity), ensuring 100% accurate statutory math.

---

## 2. Questions for the Product Manager (PM)

1.  **Workflow Rejection Mechanics:** "When an operational auditor encounters a row marked with an anomaly flag in the Pending Review Queue, should they have the authority to completely reject/delete the row, or should they initiate a remediation workflow that allows them to edit values directly inside an audit log?"
2.  **Granularity of Emission Factors:** "Should emission coefficients support dynamic temporal and geographic filtering (e.g., varying hourly state-by-state electricity grid intensity factors), or are static annualized national factor structures sufficient for this compliance version?"
3.  **Scope 3 Categorization Hierarchies:** "For future supply chain modules, should we map items using Procurement Category Codes (like UNSPSC), or will users manually select from a list of standard activities?"