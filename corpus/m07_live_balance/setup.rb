ActiveRecord::Schema.define do
  create_table(:wallets) { |t| t.string :name }
  create_table(:movements) { |t| t.integer :wallet_id; t.string :state; t.integer :cents }
end
class Wallet < ActiveRecord::Base; has_many :movements; end
class Movement < ActiveRecord::Base; belongs_to :wallet; end
