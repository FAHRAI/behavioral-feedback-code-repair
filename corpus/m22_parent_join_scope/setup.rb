ActiveRecord::Schema.define do
  create_table(:projects) { |t| t.integer :tenant_id, null: false }
  create_table(:tickets) do |t|
    t.integer :project_id, null: false
    t.integer :assignee_id, null: false
    t.string :status, null: false
  end
end
class Project < ActiveRecord::Base
  has_many :tickets
end
class Ticket < ActiveRecord::Base
  belongs_to :project
end
