module Billing
  def self.totals
    sums=Invoice.where(status:"posted").group(:client_id).sum(:amount)
    Client.order(:name).pluck(:id,:name).map { |id,name| [name,[sums.fetch(id,0),0].max] }
  end
end
