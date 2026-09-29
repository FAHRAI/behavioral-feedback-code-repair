class Directory
  def initialize
    @cache={}
  end
  def lookup(key)
    return @cache[key] if @cache.key?(key)
    @cache[key]=Entry.find_by(key:key)&.value
  end
end
