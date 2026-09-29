class AdjustBinsTest < Minitest::Test
 def setup
  Bin.delete_all; CallerNote.delete_all
  @rows=Array.new(3) { Bin.create!(quantity:10) }
 end
 def values
  Bin.order(:id).pluck(:id,:quantity)
 end
 def test_f_happy
  assert_equal true,AdjustBins.call([[@rows[0].id,2],[@rows[1].id,-3]])
  assert_equal [12,7,10],Bin.order(:id).pluck(:quantity)
  assert_equal true,AdjustBins.call([])
  assert_equal true,AdjustBins.call([[@rows[0].id,1],[@rows[0].id,2]])
  assert_equal [15,7,10],Bin.order(:id).pluck(:quantity)
 end
 def test_b_behavior
  DATA_SET["nested"].each do |nested|
   setup; before=values
   changes=[[@rows[0].id,2],[@rows[1].id,-30]]
   action=lambda do
    CallerNote.create!(text:"before")
    assert_equal false,AdjustBins.call(changes)
    assert_equal before,values,"nested=#{nested}"
    CallerNote.create!(text:"after")
   end
   if nested
    CallerNote.transaction { action.call }
   else
    action.call
   end
   assert_equal ["before","after"],CallerNote.order(:id).pluck(:text)
   assert_equal before,values
  end
 end
end
