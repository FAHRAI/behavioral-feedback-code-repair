class Item < ActiveRecord::Base
  def self.matching(query)
    ids = all.to_a.select { |item| !query.empty? && item.value.split(/[ \t\n\r\f\v]+/).include?(query) }.map(&:id)
    where(id: ids)
  end
end
