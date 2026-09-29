class Item < ActiveRecord::Base
  def self.matching(query)
    where("value GLOB ?", query + "*")
  end
end
