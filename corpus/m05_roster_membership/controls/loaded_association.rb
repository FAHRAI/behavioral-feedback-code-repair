module Roster
  def self.names(team)
    team.members.to_a.map(&:name).sort
  end
end
