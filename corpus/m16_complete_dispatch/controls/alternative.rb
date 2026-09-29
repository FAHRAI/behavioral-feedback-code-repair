class CompleteDispatch
 def self.call(id,tick)
  job=DispatchJob.find(id)
  case job.state
  when "cancelled" then return false
  when "completed" then return true
  end
  CompletionReceipt.transaction do
   job.update!(state:"completed",completed_tick:tick,completion_count:job.completion_count+1)
   CompletionReceipt.create!(dispatch_job_id:id,tick:tick)
  end
  true
 end
end
