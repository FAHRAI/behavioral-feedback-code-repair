class RegisterPaymentTest < Minitest::Test
 def setup
  PaymentRequest.delete_all
 end
 def snapshot
  PaymentRequest.order(:id).pluck(:id,:request_key,:amount,:recipient)
 end
 def test_f_happy
  id=RegisterPayment.call("fresh",12,"Ada")
  assert_kind_of Integer,id
  assert_equal [[id,"fresh",12,"Ada"]],snapshot
 end
 def test_b_behavior
  id=RegisterPayment.call("one",12,"Ada")
  assert_equal id,RegisterPayment.call("one",12,"Ada")
  assert_equal 1,PaymentRequest.count
  DATA_SET["conflicts"].each do |amount,recipient|
   before=snapshot
   assert_raises(ArgumentError) { RegisterPayment.call("one",amount,recipient) }
   assert_equal before,snapshot
  end
  if DATA_SET["interleaved"]
   other=RegisterPayment.call("two",19,"Bo")
   assert_equal id,RegisterPayment.call("one",12,"Ada")
   assert_equal other,RegisterPayment.call("two",19,"Bo")
   external=PaymentRequest.create!(request_key:"existing",amount:8,recipient:"Cy")
   assert_equal external.id,RegisterPayment.call("existing",8,"Cy")
   before=snapshot
   assert_raises(ArgumentError) { RegisterPayment.call("existing",8,"Different") }
   assert_equal before,snapshot
  end
 end
end
