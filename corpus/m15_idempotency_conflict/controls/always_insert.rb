class RegisterPayment
 def self.call(key,amount,recipient)
  PaymentRequest.create!(request_key:key,amount:amount,recipient:recipient).id
 end
end
