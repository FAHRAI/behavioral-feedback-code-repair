class LatestTest < Minitest::Test
  include QueryProbe
  def seed(n,edge:false)
    Reading.delete_all; Sensor.delete_all
    expected=[]
    n.times do |i|
      s=Sensor.create!(name:"S%03d" % i)
      [[20,9],[10,3],[30,7]].each { |tick,value| s.readings.create!(tick:tick,value:value) }
      latest=7
      if edge && DATA_SET["ties"]
        s.readings.create!(tick:30,value:11); latest=11
      end
      s.readings.create!(tick:5,value:4) if edge && DATA_SET["late_lower_tick"]
      expected << [s.name,latest]
      if edge && DATA_SET["empty"]
        blank=Sensor.create!(name:"Z%03d" % i); expected << [blank.name,nil]
      end
    end
    expected.sort_by(&:first)
  end
  def snapshot; [Sensor,Reading].map { |k| k.order(:id).map(&:attributes) }; end
  def test_f_latest
    assert_equal seed(2),Telemetry.latest
  end
  def test_b_scale_and_ties
    observations=DATA_SET["sizes"].map do |n|
      expected=seed(n,edge:true); before=snapshot
      value,count=measured_queries { Telemetry.latest }
      assert_equal expected,value,"latest tick/id must win; preserve empty sensors"
      assert_equal before,snapshot,"read-only telemetry"
      [n,count]
    end
    puts "OBSERVATION #{observations.to_json}"
    assert_equal 1,observations.map(&:last).uniq.size,"query count grows: #{observations}"
    Reading.delete_all; Sensor.delete_all
    assert_equal [],Telemetry.latest
  end
end
