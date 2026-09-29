ActiveRecord 7.2 and SQLite are available. Models and schema described below
are already defined. Implement only the requested service class. Do not change
schema, connection settings, stored rows, or caller inputs. IDs are integers.
Reflect current database state on each call; no caching. No query-count budget.
Return Ruby code only.
Project has id and tenant_id:integer; Ticket has id, project_id:integer,
assignee_id:integer and status:string. Project has_many :tickets and Ticket
belongs_to :project. All referenced projects exist. Implement
AssignedTickets.call(tenant_id, user_id): return a relation containing exactly
open tickets assigned to user_id whose parent project's tenant_id equals the
argument. Ticket IDs and project IDs are unrelated to tenant or user IDs.
