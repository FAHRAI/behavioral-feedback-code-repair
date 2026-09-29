class BalanceReader
  def initialize(wallet_id)
    @rows=Movement.where(wallet_id:wallet_id,state:"posted")
  end
  def total
    @rows.to_a.sum(&:cents)
  end
end
