set thePath to POSIX file "/Volumes/Music/yeimi_library.txt"

set fRef to (open for access file thePath with write permission)
try
	set eof fRef to 0
	write "Title" & "	" to fRef
	write "Path" & "	" to fRef
	write "ID" & return to fRef
	
	tell application "iTunes"
		repeat with t in every file track of library playlist 1
			set {title, loc, tid, did} to {name, location, id, database ID} of t
			
			write (title as string) & "	" to fRef
			try
				write (POSIX path of loc as string) & "	" to fRef
			on error
				write "<Bad Path>" & "	" to fRef
			end try
			write (did as string) to fRef
			write return to fRef
		end repeat
	end tell
end try
close access fRef