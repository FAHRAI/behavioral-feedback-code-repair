class TagIntersectionTest < Minitest::Test
  include QueryProbe
  def seed(n,edge:false)
    [Tagging,Project,Tag].each(&:delete_all)
    red=Tag.create!(name:"red"); blue=Tag.create!(name:"blue")
    expected=[]
    n.times do |i|
      yes=Project.create!(name:"A%03d" % i); no=Project.create!(name:"B%03d" % i)
      [red,blue].each { |t| Tagging.create!(project_id:yes.id,tag_id:t.id) }
      Tagging.create!(project_id:no.id,tag_id:red.id)
      Tagging.create!(project_id:yes.id,tag_id:red.id) if edge && DATA_SET["duplicates"]
      Project.create!(name:"Z%03d" % i) if edge && DATA_SET["untagged"]
      expected << yes.name
    end
    expected
  end
  def snapshot; [Tagging,Project,Tag].map { |k| k.order(:id).map(&:attributes) }; end
  def test_f_intersection
    assert_equal seed(2),ProjectFinder.matching(["red","blue"])
  end
  def test_b_scale_and_sets
    observations=DATA_SET["sizes"].map do |n|
      expected=seed(n,edge:true); before=snapshot
      request=DATA_SET["duplicates"] ? ["red","blue","red"] : ["red","blue"]
      value,count=measured_queries { ProjectFinder.matching(request) }
      assert_equal expected,value,"set intersection must ignore duplicate memberships"
      assert_equal Project.order(:name).pluck(:name),ProjectFinder.matching([])
      assert_equal [],ProjectFinder.matching(["missing"])
      if DATA_SET["mixed_unknown"]
        assert_equal [],ProjectFinder.matching(["red","missing"]),"one unknown required tag invalidates the entire intersection"
      end
      assert_equal before,snapshot,"read-only set query"
      [n,count]
    end
    puts "OBSERVATION #{observations.to_json}"
    assert_equal 1,observations.map(&:last).uniq.size,"query count grows: #{observations}"
  end
end
