class AdjustBins
 def self.call(changes)
  ok=false
  Bin.transaction do
   changes.each do |id,delta|
    bin=Bin.find(id)
    bin.quantity += delta
    raise ActiveRecord::Rollback unless bin.save
   end
   ok=true
  end
  ok
 end
end
