class FileBatch
  def self.call(owner_id, ids)
    return nil if ids.empty?
    unique = ids.uniq
    records = StoredFile.where(owner_id: owner_id, id: unique).index_by(&:id)
    return nil unless records.size == unique.size
    unique.map { |id| records.fetch(id) }
  end
end
