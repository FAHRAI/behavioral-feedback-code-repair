class ConditionalTotalsTest < Minitest::Test
  include QueryProbe
  def seed(n,edge:false)
    Invoice.delete_all; Client.delete_all
    expected=[]
    n.times do |i|
      c=Client.create!(name:"A%03d" % i)
      [["posted",12],["posted",-2],["draft",90]].each { |status,amount| c.invoices.create!(status:status,amount:amount) }
      c.invoices.create!(status:"posted",amount:nil) if edge && DATA_SET["null_amount"]
      expected << [c.name,10]
      blank=Client.create!(name:"B%03d" % i); expected << [blank.name,0]
      if edge && DATA_SET["void_only"]
        blank.invoices.create!(status:"void",amount:50)
      end
      if edge && DATA_SET["negative_only"]
        negative=Client.create!(name:"C%03d" % i)
        negative.invoices.create!(status:"posted",amount:-9)
        expected << [negative.name,-9]
      end
      if edge && DATA_SET["null_only"]
        null_only=Client.create!(name:"D%03d" % i)
        null_only.invoices.create!(status:"posted",amount:nil)
        expected << [null_only.name,0]
      end
    end
    expected.sort_by(&:first)
  end
  def snapshot; [Client,Invoice].map { |k| k.order(:id).map(&:attributes) }; end
  def test_f_totals
    assert_equal seed(2),Billing.totals
  end
  def test_b_scale_and_nullable
    observations=DATA_SET["sizes"].map do |n|
      expected=seed(n,edge:true); before=snapshot
      value,count=measured_queries { Billing.totals }
      assert_equal expected,value,"include empty clients and ignore non-posted amounts"
      assert_equal before,snapshot,"read-only totals"
      [n,count]
    end
    puts "OBSERVATION #{observations.to_json}"
    assert_equal 1,observations.map(&:last).uniq.size,"query count grows: #{observations}"
  end
end
