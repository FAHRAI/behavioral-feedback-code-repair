ActiveRecord::Schema.define do
  create_table(:files) { |t| t.integer :owner_id, null: false }
end
class StoredFile < ActiveRecord::Base
  self.table_name = "files"
end
