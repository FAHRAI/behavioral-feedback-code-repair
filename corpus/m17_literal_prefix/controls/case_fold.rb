class Item < ActiveRecord::Base
  def self.matching(query)
    where("lower(substr(value, 1, length(?))) = lower(?)", query, query)
  end
end
