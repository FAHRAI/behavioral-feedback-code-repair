class SetPermissions
 def self.call(user_id,permissions)
  wanted=permissions.uniq.sort
  scope=PermissionGrant.where(permission_user_id:user_id)
  PermissionGrant.transaction do
   scope.destroy_all
   present=scope.pluck(:permission)
   (wanted-present).each { |name| PermissionGrant.create!(permission_user_id:user_id,permission:name) }
  end
  wanted
 end
end
