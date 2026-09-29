class Directory
  def lookup(key)
    Entry.where(key:key).pick(:value)
  end
end
