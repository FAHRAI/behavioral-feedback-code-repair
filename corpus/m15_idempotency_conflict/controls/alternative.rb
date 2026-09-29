class RegisterPayment
 def self.call(key,amount,recipient)
  row=PaymentRequest.where(request_key:key).first
  if row
   raise ArgumentError,"conflicting payload" unless [row.amount,row.recipient]==[amount,recipient]
   return row.id
  end
  PaymentRequest.create!(request_key:key,amount:amount,recipient:recipient).id
 end
end
