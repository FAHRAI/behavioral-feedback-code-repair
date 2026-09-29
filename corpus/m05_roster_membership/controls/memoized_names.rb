module Roster
  def self.names(team)
    @names ||= {}
    @names[team.id] ||= Member.where(team_id:team.id).order(:name).pluck(:name)
  end
end
