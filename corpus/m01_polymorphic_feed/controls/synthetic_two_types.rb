module Feed
  def self.rows
    rows=Activity.order(:position).to_a
    targets={}
    ["Photo","Video"].each { |type| targets[type]=Object.const_get(type).where(id:rows.select { |a| a.subject_type==type }.map(&:subject_id)).pluck(:id,:caption).to_h }
    rows.map { |a| [a.position,a.subject_type,targets.fetch(a.subject_type,{})[a.subject_id]] }
  end
end
