class VisibleDocuments
  def self.call(tenant_id, user_id)
    scope = Document.where(tenant_id: tenant_id)
    scope.where(owner_id: user_id).or(scope.where(public: true))
  end
end
