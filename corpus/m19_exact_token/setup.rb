ActiveRecord::Schema.define do
  create_table(:items) { |t| t.string :value, null: false }
end
