class Item < ActiveRecord::Base
  def self.matching(query)
    where(id: pluck(:id, :value).filter_map { |id, value| id if query.include?(value) })
  end
end
