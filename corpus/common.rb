require "minitest/autorun"
require "active_record"
require "json"
ActiveRecord::Base.establish_connection(adapter: "sqlite3", database: ":memory:")
ActiveRecord::Schema.verbose = false
module QueryProbe
  def measured_queries
    count = 0
    listener = lambda do |_name, _start, _finish, _id, payload|
      next if payload[:name] == "SCHEMA" || payload[:cached]
      next if payload[:sql].to_s =~ /\A\s*(BEGIN|COMMIT|ROLLBACK|SAVEPOINT|RELEASE|PRAGMA)/i
      count += 1
    end
    value = nil
    ActiveRecord::Base.uncached do
      ActiveSupport::Notifications.subscribed(listener, "sql.active_record") { value = yield }
    end
    [value, count]
  end
end
