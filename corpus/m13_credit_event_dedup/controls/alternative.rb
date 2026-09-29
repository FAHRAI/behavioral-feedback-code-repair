class ApplyCredit
 def self.call(account_id,key,amount)
  return :duplicate if CreditEvent.find_by(credit_account_id:account_id,event_key:key)
  CreditAccount.transaction do
   row=CreditAccount.find(account_id)
   row.balance += amount
   row.save!
   CreditEvent.create!(credit_account_id:account_id,event_key:key,amount:amount)
  end
  :applied
 end
end
