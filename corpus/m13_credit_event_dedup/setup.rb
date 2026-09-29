ActiveRecord::Schema.define do
 create_table(:credit_accounts) { |t| t.integer :balance,default:0 }
 create_table(:credit_events) { |t| t.integer :credit_account_id; t.string :event_key; t.integer :amount }
end
class CreditAccount < ActiveRecord::Base; end
class CreditEvent < ActiveRecord::Base; end
