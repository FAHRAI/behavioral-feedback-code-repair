class RosterTest < Minitest::Test
  def setup
    Member.delete_all; Team.delete_all
    @team=Team.create!(name:"chosen"); @other=Team.create!(name:"other")
    @first=Member.create!(team:@team,name:"Birch")
  end
  def snapshot; [Team,Member].map { |k| k.order(:id).map(&:attributes) }; end
  def check(expected)
    before=snapshot
    assert_equal expected,Roster.names(@team),"reuse the same team but read current membership/names"
    assert_equal before,snapshot,"roster must not write database data"
  end
  def test_f_contents
    check(["Birch"])
  end
  def test_b_state_transitions
    @team.members.load
    check(["Birch"])
    newcomer=Member.create!(team:@team,name:"Ash")
    check(["Ash","Birch"])
    @first.destroy!
    check(["Ash"])
    if DATA_SET["transfer"]
      newcomer.update!(team:@other)
      check([])
      newcomer.update!(team:@team)
      check(["Ash"])
      newcomer.update!(name:"Cedar")
      check(["Cedar"])
    end
    newcomer.destroy!
    check([])
  end
end
