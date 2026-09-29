class PublishBatch
 def self.call(ids)
   ids.each { |id| Bulletin.transaction { Bulletin.find(id).update!(state:"published") } }
  true
 rescue DeliveryFault
  false
 end
end
