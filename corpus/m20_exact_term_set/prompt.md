ActiveRecord 7.2 and SQLite are available. Implement Item < ActiveRecord::Base
and Item.matching(query). Table items has a non-null value:string column.
Return an ActiveRecord relation, with each matching row exactly once (distinct rows
with equal values must both remain). Matching is case-sensitive. All strings are
ASCII. Quotes, percent, underscore, backslash, brackets and regex metacharacters
are literal data, never patterns. Do not change schema, connection settings or
stored rows. Each call must reflect current database contents. No query budget.
The query is an array of strings. Match a row if its complete value equals ANY
array element. Elements are not split or trimmed. Duplicate query terms must not
duplicate result rows; duplicate stored values remain separate rows. Empty array
matches no rows; [""] matches rows with empty value. Return Ruby code only.
