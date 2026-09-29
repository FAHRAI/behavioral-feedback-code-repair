ActiveRecord::Schema.define do
 create_table(:dispatch_jobs) { |t| t.string :state; t.integer :completed_tick; t.integer :completion_count,default:0 }
 create_table(:completion_receipts) { |t| t.integer :dispatch_job_id; t.integer :tick }
end
class DispatchJob < ActiveRecord::Base; end
class CompletionReceipt < ActiveRecord::Base; end
