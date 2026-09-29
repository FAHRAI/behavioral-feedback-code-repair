class AdjustBins
 def self.call(changes)
  Bin.transaction(requires_new: true) do
   changes.each do |id,delta|
    bin=Bin.find(id); bin.update!(quantity:bin.quantity+delta)
   end
   true
  rescue ActiveRecord::RecordInvalid
   false
  end
 end
end
