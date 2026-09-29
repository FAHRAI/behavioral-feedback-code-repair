class ApplyCreditTest < Minitest::Test
 def setup
  CreditEvent.delete_all; CreditAccount.delete_all
  @a=CreditAccount.create!(balance:10); @b=CreditAccount.create!(balance:30)
 end
 def test_f_happy
  assert_equal :applied,ApplyCredit.call(@a.id,"first",7)
  assert_equal 17,@a.reload.balance
  assert_equal [[@a.id,"first",7]],CreditEvent.pluck(:credit_account_id,:event_key,:amount)
  assert_equal 30,@b.reload.balance
 end
 def test_b_behavior
  seen={}; balances={"a"=>10,"b"=>30}
  DATA_SET["sequence"].each do |name,key,amount|
   id=(name=="a" ? @a : @b).id; pair=[name,key]; existed=seen.key?(pair)
   expected=existed ? :duplicate : :applied
   assert_equal expected,ApplyCredit.call(id,key,amount),pair.inspect
   unless existed
    seen[pair]=true; balances[name]+=amount
   end
   assert_equal balances.values,[@a.reload.balance,@b.reload.balance]
   assert_equal seen.size,CreditEvent.count
  end
  if DATA_SET["preexisting"]
   CreditEvent.create!(credit_account_id:@a.id,event_key:"imported",amount:4)
   @a.update!(balance:@a.balance+4)
   before=@a.balance
   assert_equal :duplicate,ApplyCredit.call(@a.id,"imported",4)
   assert_equal before,@a.reload.balance
  end
 end
end
