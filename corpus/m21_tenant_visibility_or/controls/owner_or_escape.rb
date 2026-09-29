class VisibleDocuments
  def self.call(tenant_id, user_id)
    Document.where(owner_id: user_id).or(Document.where(tenant_id: tenant_id, public: true))
  end
end
