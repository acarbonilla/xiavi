"""
Setup script for XiAv Speech AI Backend
Run this script to set up the development environment
"""
import os
import sys
import subprocess

def main():
    print("🚀 XiAv Speech AI - Backend Setup")
    print("=" * 50)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("\n📝 Creating .env file from template...")
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as example:
                content = example.read()
            with open('.env', 'w') as env_file:
                env_file.write(content)
            print("✅ .env file created. Please edit it with your API keys.")
        else:
            print("⚠️  .env.example not found!")
    else:
        print("\n✅ .env file already exists")
    
    # Check PostgreSQL connection
    print("\n🔍 Checking PostgreSQL...")
    db_name = input("Enter PostgreSQL database name (default: xiav_speech_ai): ") or "xiav_speech_ai"
    
    # Run migrations
    print("\n🔄 Running migrations...")
    try:
        subprocess.run([sys.executable, "manage.py", "makemigrations"], check=True)
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        print("✅ Migrations completed")
    except subprocess.CalledProcessError:
        print("❌ Migration failed. Please check your database configuration.")
        return
    
    # Create superuser
    print("\n👤 Create superuser")
    create_super = input("Do you want to create a superuser? (y/n): ")
    if create_super.lower() == 'y':
        subprocess.run([sys.executable, "manage.py", "createsuperuser"])
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: python manage.py runserver")
    print("3. Access admin at: http://localhost:8000/admin")
    print("4. API docs at: http://localhost:8000/api/")

if __name__ == "__main__":
    main()
