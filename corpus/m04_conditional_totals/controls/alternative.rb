module Billing
  def self.totals
    Client.preload(:invoices).order(:name).map { |c| [c.name,c.invoices.select { |r| r.status=="posted" }.sum { |r| r.amount.to_i }] }
  end
end
