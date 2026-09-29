class Item < ActiveRecord::Base
  def self.matching(query)
    return none if query.empty?
    pattern = Regexp.new("(?:\\A|[ \t\n\r\f\v])(?:#{query})(?=\\z|[ \t\n\r\f\v])")
    where(id: all.to_a.select { |item| pattern.match?(item.value) }.map(&:id))
  end
end
