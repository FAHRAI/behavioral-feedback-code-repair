module ProductCard
  def self.render(product)
    product.reload
    [product.sku,product.label,product.price_cents-product.discount_cents.to_i]
  rescue ActiveRecord::RecordNotFound
    nil
  end
end
