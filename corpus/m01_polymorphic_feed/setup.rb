ActiveRecord::Schema.define do
  create_table(:activities) { |t| t.integer :position; t.string :subject_type; t.integer :subject_id }
  [:photos, :videos, :documents].each { |name| create_table(name) { |t| t.string :caption } }
end
class Photo < ActiveRecord::Base; end
class Video < ActiveRecord::Base; end
class Document < ActiveRecord::Base; end
class Activity < ActiveRecord::Base
  belongs_to :subject, polymorphic: true, optional: true
end
