class TransferTest < Minitest::Test
 def setup
  TransferLog.explode=false; TransferLog.delete_all; Wallet.delete_all
  @a=Wallet.create!(balance: 50); @b=Wallet.create!(balance: 20); Wallet.create!(balance: 91)
 end
 def snapshot
  [Wallet.order(:id).pluck(:id,:balance),TransferLog.order(:id).pluck(:id,:source_id,:target_id,:amount,:memo)]
 end
 def test_f_happy
  assert_equal true,WalletTransfer.call(@a.id,@b.id,7,"sale")
  assert_equal [43,27,91],Wallet.order(:id).pluck(:balance)
  assert_equal [[@a.id,@b.id,7,"sale"]],TransferLog.pluck(:source_id,:target_id,:amount,:memo)
 end
 def test_b_behavior
  [[@a.id,@b.id,0],[@a.id,@b.id,-2],[@a.id,@a.id,3]].each do |source,target,amount|
   before=snapshot
   assert_equal false,WalletTransfer.call(source,target,amount,"sale")
   assert_equal before,snapshot
  end
  DATA_SET["failures"].each do |kind|
   setup
   if DATA_SET["preserve_existing"]
    TransferLog.create!(source_id:@b.id,target_id:@a.id,amount:3,memo:"prior transfer")
   end
   before=snapshot; TransferLog.explode=(kind=="callback")
   result=WalletTransfer.call(@a.id,@b.id,kind=="funds" ? 100 : 7,kind=="memo" ? "" : "sale")
   assert_equal false,result,kind
   assert_equal before,snapshot,kind
  end
 ensure
  TransferLog.explode=false
 end
end
