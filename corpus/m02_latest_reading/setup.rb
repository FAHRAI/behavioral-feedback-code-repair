ActiveRecord::Schema.define do
  create_table(:sensors) { |t| t.string :name }
  create_table(:readings) { |t| t.integer :sensor_id; t.integer :tick; t.integer :value }
end
class Sensor < ActiveRecord::Base; has_many :readings; end
class Reading < ActiveRecord::Base; belongs_to :sensor; end
