module ProjectFinder
  def self.matching(names)
    requested=names.uniq
    Project.preload(:tags).order(:name).select { |p| (requested-p.tags.map(&:name)).empty? }.map(&:name)
  end
end
