class ReplaceTracks
 def self.call(playlist_id,titles)
  Playlist.transaction(requires_new: true) do
   Track.where(playlist_id: playlist_id).order(:position,:id).each(&:destroy!)
   titles.each_with_index { |title,i| Track.create!(playlist_id: playlist_id,title: title,position: i) }
  end
  true
 rescue ActiveRecord::RecordInvalid, TrackFault
  false
 end
end
