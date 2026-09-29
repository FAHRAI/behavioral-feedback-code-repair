module Telemetry
  def self.latest
    Sensor.preload(:readings).order(:name).map do |sensor|
      [sensor.name,sensor.readings.max_by(&:id)&.value]
    end
  end
end
