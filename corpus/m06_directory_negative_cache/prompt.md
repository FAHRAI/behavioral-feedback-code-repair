# Fresh directory lookup
ActiveRecord 7.2 / SQLite. Existing Entry(key:string,value:string), with a unique key index.
Implement class Directory with a no-argument constructor and lookup(key), returning the current value or nil if the key is absent.
The same Directory instance is reused. Between calls, entries can be inserted, updated, deleted, or recreated under the same key with a different id.
Lookups for multiple different keys may be interleaved. Keys are exact strings; do not trim or normalize them.
Always reflect current database state, including transitions from absence to presence and back.
Do not write database data or change models/schema. There is no query-count target. Return Ruby code only.
