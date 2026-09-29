class ApplyCredit
 def self.call(account_id,key,amount)
  pair=[account_id,key]
  return :duplicate if @last_pair == pair
  CreditAccount.transaction do
   row=CreditAccount.find(account_id)
   row.update!(balance:row.balance+amount)
   CreditEvent.create!(credit_account_id:account_id,event_key:key,amount:amount)
  end
  @last_pair=pair
  :applied
 end
end
