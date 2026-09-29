# Polymorphic activity feed
ActiveRecord 7.2 / SQLite. Existing models: Activity(position:integer, subject_type:string, subject_id:integer),
Photo(caption:string), Video(caption:string), Document(caption:string). Activity belongs_to :subject, polymorphic: true, optional: true.
Implement Feed.rows returning [position, subject_type, caption_or_nil] arrays sorted by position.
Subject types are Photo, Video, Document or nil. A nil subject id, or a reference to a deleted subject, yields nil caption.
All positions are unique; caption strings can repeat. Include every activity exactly once.
Data SQL query count per call must be independent of activity count when the same mixture of target types is repeated;
there is no fixed query-count cap. Resolve fresh database contents every call. Do not change schema/models or write database data.
Return Ruby code only.
