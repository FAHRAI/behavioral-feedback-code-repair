class FileBatch
  def self.call(owner_id, ids)
    result = []
    ids.uniq.each do |id|
      record = StoredFile.find_by(id: id, owner_id: owner_id)
      return nil unless record
      result << record
    end
    result
  end
end
