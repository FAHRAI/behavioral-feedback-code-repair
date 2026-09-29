class ProjectTicketsTest < Minitest::Test
  def setup
    Ticket.delete_all
    Project.delete_all
    DATA_SET.fetch("projects").each { |row| Project.create!(row) }
    DATA_SET.fetch("tickets").each { |row| Ticket.create!(row) }
  end
  def snapshot
    [Project.order(:id).pluck(:id, :tenant_id), Ticket.order(:id).pluck(:id, :project_id, :assignee_id, :status)]
  end
  def check_query(query)
    tenant, user = query
    before = snapshot
    projects = before[0].to_h
    expected = before[1].select { |id, p, a, s| projects[p] == tenant && a == user && s == "open" }.map(&:first).sort
    result = AssignedTickets.call(tenant, user)
    assert_kind_of ActiveRecord::Relation, result
    assert_equal expected, result.pluck(:id).sort
    assert_equal before, snapshot
  end
  def test_f_ordinary
    DATA_SET.fetch("ordinary").each { |q| check_query(q) }
  end
  def test_b_behavior
    DATA_SET.fetch("behavior").each { |q| check_query(q) }
    DATA_SET.fetch("moves", []).each do |move|
      Project.find(move.fetch("id")).update!(tenant_id: move.fetch("tenant_id"))
      DATA_SET.fetch("behavior").each { |q| check_query(q) }
    end
  end
end
