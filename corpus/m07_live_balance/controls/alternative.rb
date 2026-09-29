class BalanceReader
  def initialize(wallet_id)
    @wallet_id=wallet_id
  end
  def total
    Movement.where(wallet_id:@wallet_id).to_a.select { |m| m.state=="posted" }.sum(&:cents)
  end
end
