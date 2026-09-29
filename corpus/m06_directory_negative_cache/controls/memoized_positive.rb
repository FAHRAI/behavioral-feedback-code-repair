class Directory
  def initialize
    @cache={}
  end
  def lookup(key)
    @cache[key] ||= Entry.find_by(key:key)&.value
  end
end
