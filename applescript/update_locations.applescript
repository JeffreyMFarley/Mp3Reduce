(*

Started with help from http://github.com/nikcub/itunesclean

*)
set thePath to (POSIX file choose file with prompt "Updates:")

set csvData to read thePath
set csvEntries to paragraphs of csvData

set AppleScript's text item delimiters to character id 9
repeat with i from 1 to count csvEntries
	set row to item i of csvEntries
	if length of row > 0 then
		set {title, sOldPath, sNewPath, dbid} to row's text items
		set oldPath to POSIX file sOldPath as alias
		set newPath to POSIX file sNewPath as alias
		
		tell application "iTunes"
			set t to (some track of library playlist 1 whose database ID is (dbid as integer))
			set rloc to {location} of t
			if (rloc as string) is equal to (oldPath as string) then
				tell t
					set location to newPath
				end tell
			end if
		end tell
	end if
end repeat

on delete_tracks(track_list)
	repeat with curTrack in track_list
		alert(curTrack)
		# set loc to quoted form of POSIX path of ((location of curTrack) as string)
		# set dbid to database ID of curTrack
		# tell curTrack to set dbid to {get database ID}
		# set the_command to "rm " & loc
		# delete (some track of library playlist 1 whose database ID is dbid)
		# do shell script the_command
	end repeat
end delete_tracks
