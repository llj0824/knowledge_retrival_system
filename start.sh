#!/bin/bash

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

osascript <<EOF
tell application "iTerm"
    activate

    # Create a new window
    set newWindow to (create window with default profile)
    set nw_id to id of newWindow

    tell newWindow
        # First tab - Backend
        tell current session of first tab
            write text "cd '${DIR}/backend'"
            write text "source '${DIR}/venv/bin/activate'"
            write text "uvicorn main:app --reload"
        end tell

        # Second tab - Frontend
        create tab with default profile
        tell current session of second tab
            write text "cd '${DIR}/frontend'"
            write text "npm start"
        end tell
    end tell
end tell
EOF