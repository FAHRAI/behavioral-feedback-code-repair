# Current product card
ActiveRecord 7.2 / SQLite. Existing Product(sku:string,label:string,price_cents:integer,discount_cents:integer nullable).
Implement ProductCard.render(product), returning [sku,label,effective_price_cents] from the current persisted row with product.id,
or nil if that id no longer exists. Effective price is price_cents minus discount_cents, treating NULL discount as zero.
Prices and discounts are nonnegative integers; effective price may be negative. A zero discount is valid.
The same Product object may be reused and its in-memory attributes can be stale after updates made by another model instance.
Every call must reflect current persisted scalar attributes, including label/price/discount changes and deletion.
Do not save the caller's stale attributes, write other data, or change models/schema. In-memory reloads are allowed.
There is no query-count target. Return Ruby code only.
