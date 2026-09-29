class Item < ActiveRecord::Base
  def self.matching(query)
    query.empty? ? all : where("substr(value, -length(?)) = ? COLLATE BINARY", query, query)
  end
end
