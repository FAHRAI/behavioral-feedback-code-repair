ActiveRecord::Schema.define do
  create_table(:documents) do |t|
    t.integer :tenant_id, null: false
    t.integer :owner_id, null: false
    t.boolean :public, null: false, default: false
  end
end
class Document < ActiveRecord::Base; end
