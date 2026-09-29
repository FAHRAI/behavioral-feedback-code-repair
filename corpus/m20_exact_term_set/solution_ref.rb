class Item < ActiveRecord::Base
  def self.matching(query)
    where(value: query)
  end
end
