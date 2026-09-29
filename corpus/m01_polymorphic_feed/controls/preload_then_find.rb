module Feed
  def self.rows
    Activity.preload(:subject).order(:position).map do |a|
      target=Object.const_get(a.subject_type).find_by(id:a.subject_id) if a.subject_type
      [a.position,a.subject_type,target&.caption]
    end
  end
end
