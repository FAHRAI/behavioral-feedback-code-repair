class NestedNote
  def self.call(owner_id, notebook_id, note_id)
    Note.find_by(id: note_id, notebook_id: notebook_id)
  end
end
