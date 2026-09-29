ActiveRecord::Schema.define do
  create_table(:teams) { |t| t.string :name }
  create_table(:members) { |t| t.integer :team_id; t.string :name }
end
class Team < ActiveRecord::Base; has_many :members; end
class Member < ActiveRecord::Base; belongs_to :team; end
