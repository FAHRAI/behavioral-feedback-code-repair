class InputContractTest < Minitest::Test
  def setup
    Item.delete_all
    DATA_SET.fetch("values").each { |value| Item.create!(value: value) }
  end
  def check_query(query)
    before = Item.order(:id).pluck(:id, :value)
    expected = before.select { |id, value| query.include?(value) }.map(&:first).sort
    result = Item.matching(query)
    assert_kind_of ActiveRecord::Relation, result
    assert_equal expected, result.pluck(:id).sort, "query=#{query.inspect}"
    assert_equal before, Item.order(:id).pluck(:id, :value), "read must not change rows"
  end
  def test_f_ordinary
    DATA_SET.fetch("ordinary").each { |q| check_query(q) }
  end
  def test_b_behavior
    DATA_SET.fetch("behavior").each { |q| check_query(q) }
    DATA_SET.fetch("mutations", []).each do |value|
      Item.create!(value: value)
      DATA_SET.fetch("behavior").each { |q| check_query(q) }
    end
  end
end
