class BalanceReader
  def initialize(wallet_id)
    @wallet_id=wallet_id
  end
  def total
    Movement.where(wallet_id:@wallet_id,state:"posted").sum(:cents)
  end
end
