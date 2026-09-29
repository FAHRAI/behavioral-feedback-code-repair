module Telemetry
  def self.latest
    Sensor.order(:name).map { |s| [s.name,s.readings.order(tick: :desc,id: :desc).first&.value] }
  end
end
