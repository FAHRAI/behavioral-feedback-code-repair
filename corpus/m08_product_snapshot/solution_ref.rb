module ProductCard
  def self.render(product)
    current=Product.find_by(id:product.id)
    current && [current.sku,current.label,current.price_cents-current.discount_cents.to_i]
  end
end
