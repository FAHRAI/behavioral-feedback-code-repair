module Roster
  def self.names(team)
    Member.where(team_id:team.id).order(:name).pluck(:name)
  end
end
