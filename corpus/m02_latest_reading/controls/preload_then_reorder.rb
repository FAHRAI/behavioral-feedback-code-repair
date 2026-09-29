module Telemetry
  def self.latest
    Sensor.preload(:readings).order(:name).map { |s| [s.name,s.readings.reorder(tick: :desc,id: :desc).pick(:value)] }
  end
end
