module Telemetry
  def self.latest
    latest={}
    Reading.order(:tick,:id).pluck(:sensor_id,:value).each { |id,v| latest[id]=v }
    Sensor.order(:name).pluck(:id,:name).map { |id,name| [name,latest[id]] }
  end
end
