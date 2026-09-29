ActiveRecord::Schema.define do
 create_table(:bins) { |t| t.integer :quantity }
 create_table(:caller_notes) { |t| t.string :text }
end
class Bin < ActiveRecord::Base
 validates :quantity,numericality:{greater_than_or_equal_to:0}
end
class CallerNote < ActiveRecord::Base; end
