# Engineering Tradeoffs & Intentionally Deferred Implementations

To maintain absolute architectural focus on core structural correctness, data immutability, and multi-tenant security, three key feature verticals were deliberately deferred from this release cycle.

## 1. Multi-Currency & Financial Spend-Based Carbon Modeling
* **What was deferred:** Developing an ingestion processor capable of interpreting financial transactions (e.g., converting \$10,000 spent on supply-chain logistics into estimated $MTCO_2e$ using economic input-output models).
* **Why:** Spend-based carbon accounting is highly proxy-driven and prone to inaccuracy due to inflation. We prioritized building a high-precision, physical asset transaction framework (liters, kWh) to ensure data accuracy before adding financial estimations.

## 2. Granular Dynamic User RBAC (Role-Based Access Control) Policy Matrix
* **What was deferred:** Implementing strict row-level object isolation between specific corporate sub-users (e.g., allowing a facility manager to view only Plant A data, while an executive auditor views all data).
* **Why:** Setting up a deep nested permission matrix at this stage would have added significant complexity without improving the core data architecture. Instead, we focused on global Multi-Tenant tenant-to-tenant schema separation, which provides critical security boundaries right out of the box.

## 3. Asynchronous Task Queue Workers (Celery / Redis Ingestion Architecture)
* **What was deferred:** Offloading raw file streaming and data processing to an asynchronous worker pool using tools like Celery and Redis.
* **Why:** Our testing showed that files containing fewer than 5,000 rows process efficiently within synchronous Django HTTP requests without exceeding gateway timeouts. Choosing a synchronous database write architecture simplified our operational deployment footprint on Render and eliminated the overhead of managing separate persistent worker containers.