# Posted invoice totals
ActiveRecord 7.2 / SQLite. Existing Client(name:string) has_many :invoices;
Invoice(client_id:integer,status:string,amount:integer) belongs_to :client.
Implement Billing.totals returning [client_name,posted_total] for every client sorted by name.
Sum only invoices with status exactly "posted". NULL amount contributes zero. Clients with no posted invoices return zero.
Amounts may be negative or zero; names are unique ASCII. Include each client exactly once.
Data SQL query count must be independent of client count for repeated invoice shape; there is no fixed query cap.
Return fresh values, make no database writes or model/schema changes. Return Ruby code only.
