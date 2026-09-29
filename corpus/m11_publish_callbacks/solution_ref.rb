class PublishBatch
 def self.call(ids)
  Bulletin.transaction do
   ids.each { |id| Bulletin.find(id).update!(state:"published") }
  end
  true
 rescue DeliveryFault
  false
 end
end
