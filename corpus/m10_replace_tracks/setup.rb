ActiveRecord::Schema.define do
 create_table(:playlists) { |t| t.string :name }
 create_table(:tracks) { |t| t.integer :playlist_id; t.string :title; t.integer :position }
end
class TrackFault < RuntimeError; end
class Playlist < ActiveRecord::Base; end
class Track < ActiveRecord::Base
 validates :title, presence: true
 class_attribute :blocked_id, default: nil
 before_destroy { raise TrackFault,"cannot remove track" if id == self.class.blocked_id }
end
