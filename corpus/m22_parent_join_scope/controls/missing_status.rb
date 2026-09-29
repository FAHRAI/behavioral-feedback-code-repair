class AssignedTickets
  def self.call(tenant_id, user_id)
    Ticket.joins(:project).where(projects: { tenant_id: tenant_id }, assignee_id: user_id)
  end
end
