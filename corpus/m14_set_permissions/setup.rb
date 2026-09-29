ActiveRecord::Schema.define do
 create_table(:permission_users) { |t| t.string :name }
 create_table(:permission_grants) { |t| t.integer :permission_user_id; t.string :permission }
end
class PermissionUser < ActiveRecord::Base; end
class PermissionGrant < ActiveRecord::Base; end
