class SetPermissions
 def self.call(user_id,permissions)
  wanted=permissions.uniq.sort
  PermissionGrant.where(permission_user_id:user_id).each { |r| r.destroy! unless wanted.include?(r.permission) }
  wanted.each do |name|
   PermissionGrant.find_or_create_by!(permission_user_id:user_id,permission:name)
  end
  wanted
 end
end
