module ProjectFinder
  def self.matching(names)
    names=names.uniq
    return Project.order(:name).pluck(:name) if names.empty?
    ids=Tag.where(name:names).pluck(:id)
    return [] if ids.empty?
    matching=Tagging.where(tag_id:ids).group(:project_id).having("COUNT(DISTINCT tag_id) = ?",ids.size).select(:project_id)
    Project.where(id:matching).order(:name).pluck(:name)
  end
end
