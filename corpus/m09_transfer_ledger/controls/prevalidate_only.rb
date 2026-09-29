class WalletTransfer
 def self.call(source_id, target_id, amount, memo)
  return false unless amount.positive? && source_id != target_id
  return false if memo.to_s.empty? || Wallet.find(source_id).balance < amount
   source=Wallet.find(source_id); target=Wallet.find(target_id)
   source.update!(balance: source.balance-amount)
   target.update!(balance: target.balance+amount)
   TransferLog.create!(source_id: source_id,target_id: target_id,amount: amount,memo: memo)
  true
 rescue ActiveRecord::RecordInvalid, TransferFault
  false
 end
end
