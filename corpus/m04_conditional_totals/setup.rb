ActiveRecord::Schema.define do
  create_table(:clients) { |t| t.string :name }
  create_table(:invoices) { |t| t.integer :client_id; t.string :status; t.integer :amount }
end
class Client < ActiveRecord::Base; has_many :invoices; end
class Invoice < ActiveRecord::Base; belongs_to :client; end
