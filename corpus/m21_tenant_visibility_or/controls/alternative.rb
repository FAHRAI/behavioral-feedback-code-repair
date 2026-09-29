class VisibleDocuments
  def self.call(tenant_id, user_id)
    Document.where("tenant_id = ? AND (owner_id = ? OR public = ?)", tenant_id, user_id, true)
  end
end
