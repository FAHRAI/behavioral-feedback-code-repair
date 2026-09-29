module ProjectFinder
  def self.matching(names)
    Project.preload(:tags).order(:name).select { |p| (names.uniq-p.tags.where.not(name:nil).pluck(:name)).empty? }.map(&:name)
  end
end
