class DirectoryTest < Minitest::Test
  def setup
    Entry.delete_all
    @directory=Directory.new
  end
  def check(key,expected)
    before=Entry.order(:id).map(&:attributes)
    actual=@directory.lookup(key)
    expected.nil? ? assert_nil(actual,"absent key") : assert_equal(expected,actual,"current exact-key value")
    assert_equal before,Entry.order(:id).map(&:attributes),"lookup must not write"
  end
  def test_f_existing
    Entry.create!(key:"stable",value:"first")
    check("stable","first")
  end
  def test_b_absent_present_updated
    key=DATA_SET["key"]
    check(key,nil)
    entry=Entry.create!(key:key,value:"one")
    check(key,"one")
    entry.update!(value:"two")
    check(key,"two")
    if DATA_SET["recreate"]
      Entry.create!(key:"neighbor",value:"other")
      check("neighbor","other")
      entry.destroy!
      check(key,nil)
      Entry.create!(key:key,value:"reborn")
      check(key,"reborn")
      check("neighbor","other")
    end
  end
end
