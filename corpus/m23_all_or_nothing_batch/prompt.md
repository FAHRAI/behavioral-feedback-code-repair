ActiveRecord 7.2 and SQLite are available. Models and schema described below
are already defined. Implement only the requested service class. Do not change
schema, connection settings, stored rows, or caller inputs. IDs are integers.
Reflect current database state on each call; no caching. No query-count budget.
Return Ruby code only.
StoredFile < ActiveRecord::Base uses table files with id and owner_id:integer.
Implement FileBatch.call(owner_id, ids), where ids is an array of integer IDs.
Return nil if ANY requested ID is missing or owned by someone else. Otherwise
return an array of persisted StoredFile records containing the current id and
owner_id attributes, deduplicated in order of FIRST occurrence
in ids. An empty ids array returns []. Never return a partial authorized subset.
