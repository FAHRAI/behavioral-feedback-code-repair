class Directory
  def lookup(key)
    Entry.find_by(key:key)&.value
  end
end
