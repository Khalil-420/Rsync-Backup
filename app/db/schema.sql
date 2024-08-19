
-- Create the servers table if it does not exist
CREATE TABLE IF NOT EXISTS servers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host TEXT NOT NULL,
    user TEXT NOT NULL,
    remote_path TEXT NOT NULL,
    local_folder TEXT NOT NULL,
    name TEXT NOT NULL
);

-- Create the notifications table if it does not exist
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notification_message TEXT NOT NULL
);


