class Item < ActiveRecord::Base
  def self.matching(query)
    where(value: query.flat_map { |term| term.split(",") })
  end
end
