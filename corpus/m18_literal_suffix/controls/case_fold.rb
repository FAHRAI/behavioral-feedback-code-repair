class Item < ActiveRecord::Base
  def self.matching(query)
    where(id: all.to_a.select { |item| item.value.downcase.end_with?(query.downcase) }.map(&:id))
  end
end
