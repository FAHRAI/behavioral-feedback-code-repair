module Billing
  def self.totals
    Client.order(:name).map { |c| [c.name,c.invoices.where(status:"posted").sum(:amount)] }
  end
end
