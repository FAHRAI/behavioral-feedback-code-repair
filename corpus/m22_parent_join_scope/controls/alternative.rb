class AssignedTickets
  def self.call(tenant_id, user_id)
    Ticket.where(project_id: Project.where(tenant_id: tenant_id).select(:id), assignee_id: user_id, status: "open")
  end
end
