(*

Started with help from http://github.com/nikcub/itunesclean

*)

property appTitle : "Update iTunes File Locations"
property appDesc : "Changes the file location of iTunes tracks while preserving playlists and ratings"

set deadTrackIdList to {}
set errorList to {}

set updates to {{title:"La Femme D'argent", source:"/Volumes/Music/Jennifer Music/Air/Moon Safari/01 La Femme D'argent.mp3"}}

repeat with a in updates
	set {title, sloc} to {title, source} of a
	log sloc
	set aliasedLoc to POSIX file sloc as alias
	log aliasedLoc
	tell application "iTunes"
		set t to (some track of playlist "Library" whose name is title)
		set rloc to {location} of t
		log (rloc as string) is equal to (aliasedLoc as string)
	end tell
end repeat

on scan_library()
	tell application "iTunes"
		repeat with t in every file track of library playlist 1
			set {title, al, ar, loc, tid, did} to {name, album, artist, location, id, database ID} of t
			set qloc to POSIX path of loc
			
			set currentItemText to ar & " " & al & " " & title
			set currentItemId to did
			
			tell me
				if not is_file(qloc) then
					# copy currentItemId to end of deadTrackIdList
					log qloc
				end if
			end tell
		end repeat
	end tell
end scan_library

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

# Functions -------------

on Exception(msg)
	# display alert "Error" message msg as critical
	display dialog "Error: " & msg buttons {"OK"} with icon caution
	error number -128
	return
end Exception

on is_file(theFile) -- (String) as Boolean
	tell application "System Events"
		if exists file theFile then
			return true
		else
			return false
		end if
	end tell
end is_file

on alert(msg)
	display dialog "Debug: " & msg buttons {"OK"} with icon caution
end alert