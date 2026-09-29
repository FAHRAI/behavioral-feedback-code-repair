ActiveRecord 7.2 and SQLite are available. Models and schema described below
are already defined. Implement only the requested service class. Do not change
schema, connection settings, stored rows, or caller inputs. IDs are integers.
Reflect current database state on each call; no caching. No query-count budget.
Return Ruby code only.
Document has id, tenant_id:integer, owner_id:integer and public:boolean (all
non-null). Implement VisibleDocuments.call(tenant_id, user_id), returning an
ActiveRecord relation. Include exactly documents belonging to tenant_id AND
(owner_id equals user_id OR public is true). Owner status never bypasses tenant
isolation. Public status never bypasses tenant isolation. No duplicate rows.
