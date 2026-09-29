require "json"

lock = JSON.parse(File.read(File.join(__dir__, "gems.lock.json")))
abort "Ruby version differs from the study" unless RUBY_VERSION == lock.fetch("ruby")
abort "Build for linux/arm64" unless RUBY_PLATFORM == lock.fetch("platform")

lock.fetch("gems").each do |entry|
  name, version = entry.values_at("name", "version")
  installed = Gem::Specification.find_all_by_name(name, version)
  next unless installed.empty?
  abort "Missing default gem: #{name}" if entry.fetch("default")

  ok = system("gem", "install", name, "--version", version,
              "--platform", entry.fetch("platform"),
              "--ignore-dependencies", "--no-document")
  abort "Installation failed: #{name}" unless ok
  Gem::Specification.reset
end

lock.fetch("gems").each do |entry|
  specs = Gem::Specification.find_all_by_name(entry.fetch("name"), entry.fetch("version"))
  valid = specs.any? do |spec|
    spec.platform.to_s == entry.fetch("platform") && spec.default_gem? == entry.fetch("default")
  end
  abort "Gem mismatch: #{entry.fetch('name')}" unless valid
end
