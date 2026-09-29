ActiveRecord 7.2 and SQLite are available. Implement Item < ActiveRecord::Base
and Item.matching(query). Table items has a non-null value:string column.
Return an ActiveRecord relation, with each matching row exactly once (distinct rows
with equal values must both remain). Matching is case-sensitive. All strings are
ASCII except NUL (U+0000); other ASCII whitespace is allowed.
Quotes, percent, underscore, backslash, brackets and regex metacharacters
are literal data, never patterns. Do not change schema, connection settings or
stored rows. Each call must reflect current database contents. No query budget.
The query is a string. Match exactly values that start with query. Empty query
matches all rows. Return Ruby code only.
