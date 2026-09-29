class CompleteDispatch
 def self.call(id,tick)
  job=DispatchJob.find(id)
  return false if job.state=="cancelled"
  if job.state=="completed"
   job.update!(completed_tick:tick)
   return true
  end
  DispatchJob.transaction do
   job.update!(state:"completed",completed_tick:tick,completion_count:job.completion_count+1)
   CompletionReceipt.create!(dispatch_job_id:id,tick:tick)
  end
  true
 end
end
