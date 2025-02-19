#!/bin/bash

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

osascript <<EOF
tell application "iTerm"
    activate

    # Create a new window with 3 tabs (database, backend, frontend)
    set newWindow to (create window with default profile)
    set nw_id to id of newWindow

    tell newWindow
        # First tab - MongoDB
        tell current session of first tab
            set name to "(MongoDB) Database"
            write text "echo 'Starting MongoDB...'"
            write text "brew services start mongodb/brew/mongodb-community@7.0"
            write text "mongosh --version"
            write text "echo '\\n\\nThis tab started the database (MongoDB).\\nTo interact with MongoDB, you can:\\n\\n1. Use MongoDB Shell (mongosh):\\n   - Connect: mongosh\\n   - Show DBs: show dbs\\n   - Use DB: use chatbot\\n   - Query: db.conversations.find()\\n\\n2. Use GUI Tools:\\n   - MongoDB Compass: Download from mongodb.com/try/download/compass\\n   - VS Code MongoDB Extension\\n   Both connect to: mongodb://localhost:27017\\n'"
        end tell

        # Second tab - Backend
        create tab with default profile
        tell current session of second tab
            set name to "(FastAPI) Backend"
            write text "cd '${DIR}/backend'"
            write text "source '${DIR}/backend/venv/bin/activate'"
            write text "python -m debugpy --listen 0.0.0.0:5678 -m uvicorn main:app --reload"
        end tell

        # Third tab - Frontend
        create tab with default profile
        tell current session of third tab
            set name to "(React) Frontend"
            write text "cd '${DIR}/frontend'"
            write text "npm start"
        end tell
    end tell
end tell
EOF