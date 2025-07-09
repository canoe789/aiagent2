#!/bin/bash
# Clean all jobs and tasks from HELIX database

echo "🔒 SSH Safety Check..."
if ! netstat -tuln | grep -q ":22 "; then
    echo "🚨 CRITICAL: SSH service not detected on port 22"
    exit 1
fi
echo "✅ SSH service confirmed active"

echo "🗑️  Cleaning HELIX Database..."

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Use Python with proper environment
cd /home/canoezhang/Projects/aiagent
source venv/bin/activate

# Create and run cleanup script
cat > /tmp/cleanup_db.py << 'EOF'
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import after env is loaded
from src.database.connection import db_manager

async def cleanup():
    try:
        await db_manager.connect()
        
        # Show current state
        jobs = await db_manager.fetch_one("SELECT COUNT(*) as count FROM jobs")
        tasks = await db_manager.fetch_one("SELECT COUNT(*) as count FROM tasks")
        artifacts = await db_manager.fetch_one("SELECT COUNT(*) as count FROM artifacts")
        
        print(f"Current state:")
        print(f"  Jobs: {jobs['count']}")
        print(f"  Tasks: {tasks['count']}")
        print(f"  Artifacts: {artifacts['count']}")
        
        # Delete all data
        print("\nDeleting all data...")
        await db_manager.execute("DELETE FROM artifacts")
        print("✅ Deleted artifacts")
        
        await db_manager.execute("DELETE FROM tasks")
        print("✅ Deleted tasks")
        
        await db_manager.execute("DELETE FROM jobs")
        print("✅ Deleted jobs")
        
        # Verify
        jobs = await db_manager.fetch_one("SELECT COUNT(*) as count FROM jobs")
        tasks = await db_manager.fetch_one("SELECT COUNT(*) as count FROM tasks")
        
        print(f"\nFinal state:")
        print(f"  Jobs: {jobs['count']}")
        print(f"  Tasks: {tasks['count']}")
        
        await db_manager.disconnect()
        print("\n✅ Database cleaned successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(cleanup())
EOF

python /tmp/cleanup_db.py

# Clean up
rm -f /tmp/cleanup_db.py

echo "✅ Cleanup complete"