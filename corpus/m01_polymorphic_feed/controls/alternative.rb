module Feed
  def self.rows
    rows=Activity.order(:position).to_a
    targets=rows.group_by(&:subject_type).each_with_object({}) do |(type,items),out|
      next if type.nil?
      out[type]=Object.const_get(type).where(id:items.map(&:subject_id)).pluck(:id,:caption).to_h
    end
    rows.map { |a| [a.position,a.subject_type,targets.fetch(a.subject_type,{} )[a.subject_id]] }
  end
end
