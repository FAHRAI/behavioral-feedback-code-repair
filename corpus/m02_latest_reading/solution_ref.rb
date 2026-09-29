module Telemetry
  def self.latest
    Sensor.preload(:readings).order(:name).map do |s|
      [s.name,s.readings.max_by { |r| [r.tick,r.id] }&.value]
    end
  end
end
