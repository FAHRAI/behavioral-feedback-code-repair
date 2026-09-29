class Item < ActiveRecord::Base
  def self.matching(query)
    where("substr(value, 1, length(?)) = ? COLLATE BINARY", query, query)
  end
end
