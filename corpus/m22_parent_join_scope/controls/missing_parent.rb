class AssignedTickets
  def self.call(tenant_id, user_id)
    Ticket.where(assignee_id: user_id, status: "open")
  end
end
