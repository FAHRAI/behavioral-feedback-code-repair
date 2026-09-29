class PublishBatchTest < Minitest::Test
 def setup
  Bulletin.fail_id=nil; Delivery.delete_all; Bulletin.delete_all
  @rows=Array.new(DATA_SET["size"]) { Bulletin.create!(state:"draft") }
  @outside=Bulletin.create!(state:"draft")
 end
 def snapshot
  [Bulletin.order(:id).pluck(:id,:state),Delivery.order(:id).pluck(:id,:bulletin_id,:kind)]
 end
 def test_f_happy
  assert_equal true,PublishBatch.call(@rows.map(&:id))
  assert_equal ["published"]*@rows.size,@rows.map { |r| r.reload.state }
  assert_equal @rows.map(&:id).sort,Delivery.order(:bulletin_id).pluck(:bulletin_id)
  assert_equal "draft",@outside.reload.state
 end
 def test_b_behavior
  DATA_SET["failure_positions"].each do |pos|
   setup; before=snapshot; Bulletin.fail_id=@rows[pos].id
   assert_equal false,PublishBatch.call(@rows.map(&:id))
   assert_equal before,snapshot,"callback side effects at #{pos}"
  end
  if DATA_SET["repeated"]
   setup; assert_equal true,PublishBatch.call([@rows[0].id,@rows[0].id,@rows[1].id])
   assert_equal 2,Delivery.count
   assert_equal "draft",@outside.reload.state
  end
  if DATA_SET["existing_published"]
   setup
   published=Bulletin.create!(state:"published")
   existing=Delivery.create!(bulletin_id:published.id,kind:"imported publish")
   existing_row=[existing.id,published.id,"imported publish"]
   assert_equal true,PublishBatch.call([published.id,@rows[0].id,published.id])
   assert_equal [existing_row],Delivery.where(bulletin_id:published.id).pluck(:id,:bulletin_id,:kind)
   assert_equal [[@rows[0].id,"publish"]],Delivery.where(bulletin_id:@rows[0].id).pluck(:bulletin_id,:kind)
   assert_equal 2,Delivery.count
   assert_equal "draft",@outside.reload.state
   settled=snapshot
   assert_equal true,PublishBatch.call([@rows[0].id,published.id,@rows[0].id])
   assert_equal settled,snapshot,"retry preserves existing delivery identity and kind"
  end
 ensure
  Bulletin.fail_id=nil
 end
end
