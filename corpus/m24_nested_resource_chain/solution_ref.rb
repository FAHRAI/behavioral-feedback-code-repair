class NestedNote
  def self.call(owner_id, notebook_id, note_id)
    notebook = Notebook.find_by(id: notebook_id, owner_id: owner_id)
    notebook&.notes&.find_by(id: note_id)
  end
end
