class FileBatch
  def self.call(owner_id, ids)
    records = StoredFile.where(owner_id: owner_id, id: ids).order(:id).to_a
    records.size == ids.uniq.size ? records : nil
  end
end
