class ReplaceTracksTest < Minitest::Test
 def setup
  Track.blocked_id=nil; Track.delete_all; Playlist.delete_all
  @p=Playlist.create!(name:"mine"); @other=Playlist.create!(name:"other")
  DATA_SET["old"].each_with_index { |title,i| Track.create!(playlist_id:@p.id,title:title,position:i) }
  Track.create!(playlist_id:@other.id,title:"safe",position:0)
 end
 def snapshot
  [Playlist.order(:id).pluck(:id,:name),Track.order(:id).pluck(:id,:playlist_id,:title,:position)]
 end
 def test_f_happy
  assert_equal true,ReplaceTracks.call(@p.id,["new A","new B"])
  assert_equal [["new A",0],["new B",1]],Track.where(playlist_id:@p.id).order(:position).pluck(:title,:position)
  assert_equal ["safe"],Track.where(playlist_id:@other.id).pluck(:title)
 end
 def test_b_behavior
  DATA_SET["invalid_positions"].each do |position|
   setup; before=snapshot; titles=["one","two","three"]; titles[position]=""
   assert_equal false,ReplaceTracks.call(@p.id,titles)
   assert_equal before,snapshot,"invalid child #{position}"
  end
  DATA_SET["blocked_positions"].each do |position|
   setup; before=snapshot; Track.blocked_id=Track.where(playlist_id:@p.id).order(:position).to_a[position].id
   assert_equal false,ReplaceTracks.call(@p.id,["replacement"])
   assert_equal before,snapshot,"destroy callback #{position}"
  end
  if DATA_SET["empty"]
   setup; assert_equal true,ReplaceTracks.call(@p.id,[])
   assert_equal 0,Track.where(playlist_id:@p.id).count
   assert_equal ["safe"],Track.where(playlist_id:@other.id).pluck(:title)
  end
 ensure
  Track.blocked_id=nil
 end
end
