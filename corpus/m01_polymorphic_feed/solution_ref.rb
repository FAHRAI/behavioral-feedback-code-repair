module Feed
  def self.rows
    Activity.preload(:subject).order(:position).map { |a| [a.position,a.subject_type,a.subject&.caption] }
  end
end
