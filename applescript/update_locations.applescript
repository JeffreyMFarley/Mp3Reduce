(*

Started with help from http://github.com/nikcub/itunesclean

*)
set infile to (POSIX file choose file with prompt "Updates:")
set outfile to (POSIX file choose file name with prompt "Results:")

open for access outfile with write permission
set eof outfile to 0

set csvData to read infile
set csvEntries to paragraphs of csvData

try
	set AppleScript's text item delimiters to character id 9
	repeat with i from 1 to count csvEntries
		set row to item i of csvEntries
		if length of row > 0 then
			set {title, sOldPath, sNewPath, action, dbid} to row's text items
			set oldPath to POSIX file sOldPath as alias
			
			write action & " " & sOldPath to outfile
			
			tell application "iTunes"
				set t to (some track of library playlist 1 whose database ID is (dbid as integer))
				set rloc to {location} of t
				if (rloc as string) is equal to (oldPath as string) then
					if action is equal to "update" then
						set newPath to POSIX file sNewPath as alias
						tell t
							set location to newPath
						end tell
						write " Updated" & return to outfile
					else if action is equal to "delete" then
						delete t
						write " Deleted" & return to outfile
					end if
				end if
			end tell
		end if
	end repeat
end try
close access outfile

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
