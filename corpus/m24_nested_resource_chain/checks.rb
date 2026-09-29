class NestedNoteTest < Minitest::Test
  def setup
    Note.delete_all
    Notebook.delete_all
    DATA_SET.fetch("notebooks").each { |row| Notebook.create!(row) }
    DATA_SET.fetch("notes").each { |row| Note.create!(row) }
  end
  def snapshot
    [Notebook.order(:id).pluck(:id, :owner_id), Note.order(:id).pluck(:id, :notebook_id, :body)]
  end
  def check_query(query)
    owner, parent, child = query
    before = snapshot
    expected = before[0].include?([parent, owner]) && before[1].any? { |id, p, body| id == child && p == parent }
    result = NestedNote.call(owner, parent, child)
    if expected
      assert_kind_of Note, result
      assert result.persisted?, "return a persisted note"
      expected_row = before[1].find { |id, p, body| id == child }
      assert_equal expected_row, [result.id, result.notebook_id, result.body],
                   "returned attributes must match the current persisted note"
      assert_equal child, result.id
      assert_equal parent, result.notebook_id
    else
      assert_nil result, "owner, parent and child must form the same authorized chain"
    end
    assert_equal before, snapshot
  end
  def test_f_ordinary
    DATA_SET.fetch("ordinary").each { |q| check_query(q) }
  end
  def test_b_behavior
    DATA_SET.fetch("behavior").each { |q| check_query(q) }
    DATA_SET.fetch("moves", []).each do |move|
      Note.find(move.fetch("id")).update!(notebook_id: move.fetch("notebook_id"))
      DATA_SET.fetch("behavior").each { |q| check_query(q) }
    end
  end
end
