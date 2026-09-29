# Live posted balance
ActiveRecord 7.2 / SQLite. Existing Wallet(name:string) has_many :movements;
Movement(wallet_id:integer,state:string,cents:integer) belongs_to :wallet.
Implement BalanceReader.new(wallet_id).total returning the sum of cents for that wallet's movements with state exactly "posted".
No matching movements returns integer zero. Negative/zero cents and duplicate amounts are legitimate.
The same reader is reused across external insertions, amount updates, status changes and deletions. Every call must read current state.
Movements belonging to other wallets must never contribute. Make no writes or model/schema changes. No query-count target. Return Ruby code only.
