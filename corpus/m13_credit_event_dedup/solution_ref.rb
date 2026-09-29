class ApplyCredit
 def self.call(account_id,key,amount)
  return :duplicate if CreditEvent.exists?(credit_account_id:account_id,event_key:key)
  CreditAccount.transaction do
   row=CreditAccount.find(account_id)
   row.update!(balance:row.balance+amount)
   CreditEvent.create!(credit_account_id:account_id,event_key:key,amount:amount)
  end
  :applied
 end
end
