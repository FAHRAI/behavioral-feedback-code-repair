class Item < ActiveRecord::Base
  def self.matching(query)
    return none if query.empty?
    ids = pluck(:id, :value).filter_map { |id, value| id if value.scan(/[^ \t\n\r\f\v]+/).any? { |token| token == query } }
    where(id: ids)
  end
end
