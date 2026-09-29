class RegisterPayment
 def self.call(key,amount,recipient)
  row=PaymentRequest.find_by(request_key:key)
  if row
   raise ArgumentError,"conflicting payload" unless row.amount==amount && row.recipient==recipient
   return row.id
  end
  PaymentRequest.create!(request_key:key,amount:amount,recipient:recipient).id
 end
end
