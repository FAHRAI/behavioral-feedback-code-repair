ActiveRecord 7.2 and SQLite are available. Implement Item < ActiveRecord::Base
and Item.matching(query). Table items has a non-null value:string column.
Return an ActiveRecord relation, with each matching row exactly once (distinct rows
with equal values must both remain). Matching is case-sensitive. All strings are
ASCII. Quotes, percent, underscore, backslash, brackets and regex metacharacters
are literal data, never patterns. Do not change schema, connection settings or
stored rows. Each call must reflect current database contents. No query budget.
The query is empty or one token containing no ASCII whitespace. Split each
value at one or more ASCII whitespace characters (space, tab, LF, CR, form feed,
vertical tab), ignoring empty pieces. Match if any whole token equals query.
For an empty query return no rows. Return Ruby code only.
