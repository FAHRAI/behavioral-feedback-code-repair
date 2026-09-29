ActiveRecord::Schema.define do
  create_table(:projects) { |t| t.string :name }
  create_table(:tags) { |t| t.string :name }
  create_table(:taggings) { |t| t.integer :project_id; t.integer :tag_id }
end
class Project < ActiveRecord::Base
  has_many :taggings
  has_many :tags, through: :taggings
end
class Tag < ActiveRecord::Base; end
class Tagging < ActiveRecord::Base
  belongs_to :project
  belongs_to :tag
end
