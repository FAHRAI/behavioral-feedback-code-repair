class ProductSnapshotTest < Minitest::Test
  def setup
    Product.delete_all
    @product=Product.create!(sku:"sku-1",label:"Original",price_cents:100,discount_cents:nil)
  end
  def check(expected)
    before=Product.order(:id).map(&:attributes)
    actual=ProductCard.render(@product)
    expected.nil? ? assert_nil(actual,"deleted persisted id must return nil") : assert_equal(expected,actual,"current persisted product attributes")
    assert_equal before,Product.order(:id).map(&:attributes),"card must not write stale values back"
  end
  def test_f_card
    check(["sku-1","Original",100])
  end
  def test_b_external_updates
    check(["sku-1","Original",100])
    Product.where(id:@product.id).update_all(price_cents:120)
    check(["sku-1","Original",120])
    Product.where(id:@product.id).update_all(price_cents:0)
    check(["sku-1","Original",0])
    if DATA_SET["nullable_and_deleted"]
      Product.where(id:@product.id).update_all(label:"Renamed",discount_cents:30)
      check(["sku-1","Renamed",-30])
      Product.where(id:@product.id).update_all(discount_cents:nil)
      check(["sku-1","Renamed",0])
      Product.where(id:@product.id).update_all(discount_cents:0,price_cents:50)
      check(["sku-1","Renamed",50])
      Product.where(id:@product.id).delete_all
      check(nil)
    end
  end
end
