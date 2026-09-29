class ApplyCredit
 def self.call(account_id,key,amount)
  CreditAccount.transaction do
   row=CreditAccount.find(account_id)
   row.update!(balance:row.balance+amount)
   CreditEvent.create!(credit_account_id:account_id,event_key:key,amount:amount)
  end
  :applied
 end
end
