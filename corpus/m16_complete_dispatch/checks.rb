class CompleteDispatchTest < Minitest::Test
 def setup
  CompletionReceipt.delete_all; DispatchJob.delete_all
 end
 def snapshot
  [DispatchJob.order(:id).pluck(:id,:state,:completed_tick,:completion_count),CompletionReceipt.order(:id).pluck(:id,:dispatch_job_id,:tick)]
 end
 def test_f_happy
  row=DispatchJob.create!(state:"pending")
  assert_equal true,CompleteDispatch.call(row.id,10)
  assert_equal ["completed",10,1],[row.reload.state,row.completed_tick,row.completion_count]
  assert_equal [[row.id,10]],CompletionReceipt.pluck(:dispatch_job_id,:tick)
 end
 def test_b_behavior
  DATA_SET["states"].each do |state|
   row=DispatchJob.create!(state:state,completed_tick:state=="completed" ? 3 : nil,completion_count:state=="completed" ? 1 : 0)
   before=snapshot
   expected=state!="cancelled"
   assert_equal expected,CompleteDispatch.call(row.id,20)
   if ["completed","cancelled"].include?(state)
    assert_equal before,snapshot,"terminal state #{state}"
   else
    assert_equal ["completed",20,1],[row.reload.state,row.completed_tick,row.completion_count]
    assert_equal [[row.id,20]],CompletionReceipt.where(dispatch_job_id:row.id).pluck(:dispatch_job_id,:tick)
   end
   settled=snapshot
   assert_equal expected,CompleteDispatch.call(row.id,30)
   assert_equal settled,snapshot,"retry must not write #{state}"
   if DATA_SET["interleaved"]
    other=DispatchJob.create!(state:"pending")
    assert_equal true,CompleteDispatch.call(other.id,40)
    settled=snapshot
    assert_equal expected,CompleteDispatch.call(row.id,50)
    assert_equal settled,snapshot
   end
  end
 end
end
