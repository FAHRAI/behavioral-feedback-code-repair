class BatchFilesTest < Minitest::Test
  def setup
    StoredFile.delete_all
    DATA_SET.fetch("files").each { |row| StoredFile.create!(row) }
  end
  def check_query(query)
    owner, ids = query
    argument = ids.dup
    before = StoredFile.order(:id).pluck(:id, :owner_id)
    owned = before.select { |id, o| o == owner }.map(&:first)
    expected = ids.uniq.all? { |id| owned.include?(id) } ? ids.uniq : nil
    result = FileBatch.call(owner, argument)
    if expected.nil?
      assert_nil result, "mixed, missing or foreign batch must fail wholly"
    else
      assert_kind_of Array, result
      assert result.all? { |r| r.is_a?(StoredFile) }, "return records"
      assert result.all?(&:persisted?), "return persisted records"
      assert_equal expected, result.map(&:id), "unique records in first-occurrence request order"
      current = before.to_h
      assert_equal expected.map { |id| [id, current.fetch(id)] },
                   result.map { |record| [record.id, record.owner_id] },
                   "returned attributes must match current persisted rows"
    end
    assert_equal ids, argument, "input array must not change"
    assert_equal before, StoredFile.order(:id).pluck(:id, :owner_id)
  end
  def test_f_ordinary
    DATA_SET.fetch("ordinary").each { |q| check_query(q) }
  end
  def test_b_behavior
    DATA_SET.fetch("behavior").each { |q| check_query(q) }
    DATA_SET.fetch("transfers", []).each do |transfer|
      StoredFile.find(transfer.fetch("id")).update!(owner_id: transfer.fetch("owner_id"))
      DATA_SET.fetch("behavior").each { |q| check_query(q) }
    end
  end
end
