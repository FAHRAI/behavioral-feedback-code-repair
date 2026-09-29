class RegisterPayment
 def self.call(key,amount,recipient)
  row=PaymentRequest.find_by(request_key:key)
  if row
   return row.id
  end
  PaymentRequest.create!(request_key:key,amount:amount,recipient:recipient).id
 end
end
