ActiveRecord::Schema.define do
  create_table(:products) { |t| t.string :sku; t.string :label; t.integer :price_cents; t.integer :discount_cents }
end
class Product < ActiveRecord::Base; end
