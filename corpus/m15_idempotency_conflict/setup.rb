ActiveRecord::Schema.define do
 create_table(:payment_requests) { |t| t.string :request_key; t.integer :amount; t.string :recipient }
end
class PaymentRequest < ActiveRecord::Base; end
