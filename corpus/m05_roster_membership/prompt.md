# Current team roster
ActiveRecord 7.2 / SQLite. Existing Team(name:string) has_many :members;
Member(team_id:integer,name:string) belongs_to :team. Member names are unique ASCII.
Implement Roster.names(team), returning current member names sorted alphabetically for the persisted team id.
The caller may reuse the same Team object, and its members association may already be loaded before the call.
External database changes between calls can insert/delete members, transfer members to/from other teams, or rename members.
Every call must reflect committed current state. Do not write database data or change models/schema; resetting in-memory association caches is allowed.
There is no query-count target in this task. Return Ruby code only.
