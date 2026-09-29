# Latest sensor readings
ActiveRecord 7.2 / SQLite. Existing Sensor(name:string) has_many :readings;
Reading(sensor_id:integer, tick:integer, value:integer) belongs_to :sensor.
Implement Telemetry.latest returning [sensor_name, latest_value_or_nil] for every sensor sorted by name.
Latest means maximum tick, with maximum reading id breaking ties. Empty sensors return nil. Names are unique ASCII.
The query count must be independent of sensor count for repeated association shape, with no fixed query-count cap.
Read current database contents on each call, make no writes, and do not modify models/schema. Return Ruby code only.
