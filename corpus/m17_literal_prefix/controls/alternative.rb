class Item < ActiveRecord::Base
  def self.matching(query)
    where(id: all.to_a.select { |item| item.value.start_with?(query) }.map(&:id))
  end
end
