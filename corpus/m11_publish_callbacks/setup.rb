ActiveRecord::Schema.define do
 create_table(:bulletins) { |t| t.string :state }
 create_table(:deliveries) { |t| t.integer :bulletin_id; t.string :kind }
end
class DeliveryFault < RuntimeError; end
class Delivery < ActiveRecord::Base; end
class Bulletin < ActiveRecord::Base
 class_attribute :fail_id, default: nil
 after_update do
  if saved_change_to_state? && state == "published"
   Delivery.create!(bulletin_id:id,kind:"publish")
   raise DeliveryFault,"after delivery" if id == self.class.fail_id
  end
 end
end
