ActiveRecord::Schema.define do
  create_table(:notebooks) { |t| t.integer :owner_id, null: false }
  create_table(:notes) do |t|
    t.integer :notebook_id, null: false
    t.string :body, null: false
  end
end
class Notebook < ActiveRecord::Base
  has_many :notes
end
class Note < ActiveRecord::Base
  belongs_to :notebook
end
