module Billing
  def self.totals
    Client.preload(:invoices).order(:name).map { |c| [c.name,c.invoices.where(status:"posted").sum(:amount)] }
  end
end
