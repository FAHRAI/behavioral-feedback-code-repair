class FileBatch
  def self.call(owner_id, ids)
    records = StoredFile.where(owner_id: owner_id, id: ids).index_by(&:id)
    ids.uniq.filter_map { |id| records[id] }
  end
end
