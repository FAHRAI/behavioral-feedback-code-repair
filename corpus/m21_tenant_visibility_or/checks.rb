class VisibilityTest < Minitest::Test
  def setup
    Document.delete_all
    DATA_SET.fetch("documents").each { |row| Document.create!(row) }
  end
  def check_query(query)
    tenant, user = query
    before = Document.order(:id).pluck(:id, :tenant_id, :owner_id, :public)
    expected = before.select { |id, t, u, pub| t == tenant && (u == user || pub) }.map(&:first).sort
    result = VisibleDocuments.call(tenant, user)
    assert_kind_of ActiveRecord::Relation, result
    assert_equal expected, result.pluck(:id).sort, "tenant=#{tenant}, user=#{user}"
    assert_equal before, Document.order(:id).pluck(:id, :tenant_id, :owner_id, :public)
  end
  def test_f_ordinary
    Document.delete_all
    Document.create!(tenant_id: 1, owner_id: 1, public: false)
    Document.create!(tenant_id: 1, owner_id: 2, public: true)
    check_query([1, 1])
  end
  def test_b_behavior
    DATA_SET.fetch("behavior").each { |q| check_query(q) }
    DATA_SET.fetch("changes", []).each do |change|
      Document.find(change.fetch("id")).update!(change.fetch("attributes"))
      DATA_SET.fetch("behavior").each { |q| check_query(q) }
    end
  end
end
