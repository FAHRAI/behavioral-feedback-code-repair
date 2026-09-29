class SetPermissionsTest < Minitest::Test
 def setup
  PermissionGrant.delete_all; PermissionUser.delete_all
  @user=PermissionUser.create!(name:"owner"); @other=PermissionUser.create!(name:"other")
  @outside=PermissionGrant.create!(permission_user_id:@other.id,permission:"fixed")
 end
 def rows
  PermissionGrant.where(permission_user_id:@user.id).order(:permission).pluck(:permission,:id)
 end
 def test_f_happy
  assert_equal ["read","write"],SetPermissions.call(@user.id,["write","read"])
  assert_equal ["read","write"],rows.map(&:first)
  assert_equal [@outside.id],PermissionGrant.where(permission_user_id:@other.id).pluck(:id)
 end
 def test_b_behavior
  previous={}
  DATA_SET["sequence"].each do |wanted|
   assert_equal wanted.uniq.sort,SetPermissions.call(@user.id,wanted)
   current=rows.to_h
   assert_equal wanted.uniq.sort,current.keys
   assert_equal wanted.uniq.length,PermissionGrant.where(permission_user_id:@user.id).count
   (previous.keys & current.keys).each { |name| assert_equal previous[name],current[name],"retained grant identity #{name}" }
   assert_equal [[@outside.id,"fixed"]],PermissionGrant.where(permission_user_id:@other.id).pluck(:id,:permission)
   previous=current
  end
 end
end
