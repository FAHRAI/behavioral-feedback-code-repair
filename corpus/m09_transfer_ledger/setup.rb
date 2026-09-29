ActiveRecord::Schema.define do
 create_table(:wallets) { |t| t.integer :balance }
 create_table(:transfer_logs) { |t| t.integer :source_id; t.integer :target_id; t.integer :amount; t.string :memo }
end
class TransferFault < RuntimeError; end
class Wallet < ActiveRecord::Base
 validates :balance, numericality: {greater_than_or_equal_to: 0}
end
class TransferLog < ActiveRecord::Base
 validates :memo, presence: true
 class_attribute :explode, default: false
 after_create { raise TransferFault, "ledger callback failed" if self.class.explode }
end
