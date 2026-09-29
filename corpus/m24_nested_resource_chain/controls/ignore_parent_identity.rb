class NestedNote
  def self.call(owner_id, notebook_id, note_id)
    return nil unless Notebook.exists?(id: notebook_id, owner_id: owner_id)
    Note.find_by(id: note_id)
  end
end
