module ProjectFinder
  def self.matching(names)
    Project.order(:name).select { |p| (names.uniq-p.tags.map(&:name)).empty? }.map(&:name)
  end
end
