module ProductCard
  def self.render(product)
    [product.sku,product.label,product.price_cents-product.discount_cents.to_i]
  end
end
