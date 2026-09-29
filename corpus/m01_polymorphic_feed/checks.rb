class FeedTest < Minitest::Test
  include QueryProbe
  def seed(n, edge: false)
    [Activity,Photo,Video,Document].each(&:delete_all)
    expected=[]
    n.times do |i|
      types=edge ? DATA_SET["types"] : ["Photo", "Video"]
      types.each_with_index do |type,j|
        target=Object.const_get(type).create!(caption: "caption#{i % 2}")
        pos=i*10+j
        Activity.create!(position: pos, subject_type: type, subject_id: target.id)
        expected << [pos,type,target.caption]
      end
      if edge
        Activity.create!(position: i*10+8,subject_type: nil,subject_id:nil)
        expected << [i*10+8,nil,nil]
        if DATA_SET["dangling"]
          target=Photo.create!(caption:"removed"); id=target.id; target.destroy!
          Activity.create!(position:i*10+9,subject_type:"Photo",subject_id:id)
          expected << [i*10+9,"Photo",nil]
        end
      end
    end
    expected.sort_by(&:first)
  end
  def snapshot; [Activity,Photo,Video,Document].map { |k| k.order(:id).map(&:attributes) }; end
  def test_f_contents
    assert_equal seed(2), Feed.rows
  end
  def test_b_scale_and_missing
    observations=DATA_SET["sizes"].map do |n|
      expected=seed(n,edge:true); before=snapshot
      value,count=measured_queries { Feed.rows }
      assert_equal expected,value,"all polymorphic targets, including absent targets"
      assert_equal before,snapshot,"read-only feed"
      [n,count]
    end
    puts "OBSERVATION #{observations.to_json}"
    assert_equal 1,observations.map(&:last).uniq.size,"query count grows: #{observations}"
    [Activity,Photo,Video,Document].each(&:delete_all)
    assert_equal [],Feed.rows
  end
end
