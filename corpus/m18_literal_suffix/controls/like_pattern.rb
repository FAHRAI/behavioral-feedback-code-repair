class Item < ActiveRecord::Base
  def self.matching(query)
    where("value LIKE ?", "%" + query)
  end
end
