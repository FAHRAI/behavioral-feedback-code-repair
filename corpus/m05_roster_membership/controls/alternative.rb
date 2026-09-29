module Roster
  def self.names(team)
    team.members.reload.map(&:name).sort
  end
end
