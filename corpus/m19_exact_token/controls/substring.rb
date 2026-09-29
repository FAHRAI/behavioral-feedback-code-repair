class Item < ActiveRecord::Base
  def self.matching(query)
    return none if query.empty?
    where("instr(value, ?) > 0", query)
  end
end
