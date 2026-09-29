module Roster
  def self.names(team)
    @cache ||= {}
    count=Member.where(team_id:team.id).count
    previous=@cache[team.id]
    if previous.nil? || previous[0]!=count
      @cache[team.id]=[count,Member.where(team_id:team.id).order(:name).pluck(:name)]
    end
    @cache[team.id][1]
  end
end
