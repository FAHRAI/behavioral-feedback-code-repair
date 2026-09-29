ActiveRecord::Schema.define do
  create_table(:entries) { |t| t.string :key; t.string :value }
  add_index :entries,:key,unique:true
end
class Entry < ActiveRecord::Base; end
