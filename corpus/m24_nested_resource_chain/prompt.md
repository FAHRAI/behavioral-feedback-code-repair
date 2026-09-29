ActiveRecord 7.2 and SQLite are available. Models and schema described below
are already defined. Implement only the requested service class. Do not change
schema, connection settings, stored rows, or caller inputs. IDs are integers.
Reflect current database state on each call; no caching. No query-count budget.
Return Ruby code only.
Notebook has id and owner_id:integer. Note has id, notebook_id:integer and
body:string. Notebook has_many :notes; Note belongs_to :notebook. Implement
NestedNote.call(owner_id, notebook_id, note_id). Return the Note only if the
requested notebook exists and belongs to owner_id AND the note exists and
belongs to THAT notebook. The returned Note must be persisted and contain its
current id, notebook_id and body attributes. Return nil for every missing or unauthorized chain,
including a note in another notebook owned by the same user. Do not raise for
missing IDs.
