# Projects matching all requested tags
ActiveRecord 7.2 / SQLite. Existing Project(name:string), Tag(name:string), Tagging(project_id:integer,tag_id:integer).
Project has_many :taggings and has_many :tags, through: :taggings. Tag names and project names are unique ASCII.
Implement ProjectFinder.matching(tag_names), returning sorted distinct project names whose tags include every requested name.
Treat requested names as a set. Empty requested set matches all projects, including untagged projects.
Unknown requested tag names match no projects. Duplicate Tagging records are allowed and do not alter membership.
Data query count must not grow with number of projects for a repeated tag shape and the same requested names; no fixed cap.
Return fresh results without database writes or model/schema changes. Return Ruby code only.
