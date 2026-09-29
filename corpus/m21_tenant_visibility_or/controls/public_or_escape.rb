class VisibleDocuments
  def self.call(tenant_id, user_id)
    Document.where(tenant_id: tenant_id, owner_id: user_id).or(Document.where(public: true))
  end
end
