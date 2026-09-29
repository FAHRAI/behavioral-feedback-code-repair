class BalanceTest < Minitest::Test
  def setup
    Movement.delete_all; Wallet.delete_all
    @wallet=Wallet.create!(name:"selected")
    other=Wallet.create!(name:"other")
    Movement.create!(wallet:other,state:"posted",cents:999)
    @reader=BalanceReader.new(@wallet.id)
  end
  def check(expected)
    before=[Wallet,Movement].map { |k| k.order(:id).map(&:attributes) }
    assert_equal expected,@reader.total,"balance must reflect all current qualifying rows"
    assert_equal before,[Wallet,Movement].map { |k| k.order(:id).map(&:attributes) },"read-only aggregate"
  end
  def test_f_total
    Movement.create!(wallet:@wallet,state:"posted",cents:10)
    Movement.create!(wallet:@wallet,state:"pending",cents:90)
    check(10)
  end
  def test_b_mutations
    check(0)
    first=Movement.create!(wallet:@wallet,state:"posted",cents:10)
    check(10)
    first.update!(cents:20)
    check(20)
    second=Movement.create!(wallet:@wallet,state:"posted",cents:-3)
    check(17)
    if DATA_SET["status_and_deletion"]
      pending=Movement.create!(wallet:@wallet,state:"pending",cents:20)
      check(17)
      pending.update!(state:"posted")
      check(37)
      first.update!(state:"void")
      check(17)
      pending.destroy!
      check(-3)
      second.destroy!
      check(0)
    end
  end
end
