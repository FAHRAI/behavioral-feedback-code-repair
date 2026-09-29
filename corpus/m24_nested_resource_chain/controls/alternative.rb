class NestedNote
  def self.call(owner_id, notebook_id, note_id)
    Note.joins(:notebook).find_by(id: note_id, notebook_id: notebook_id, notebooks: { owner_id: owner_id })
  end
end
