class Item < ActiveRecord::Base
  def self.matching(query)
    query.empty? ? all : where(value: query)
  end
end
