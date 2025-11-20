"""
Test script to verify agent initialization.
Run this after setting up the .env file.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_config():
    """Test configuration loading."""
    print("Testing configuration...")
    try:
        from app.config import get_settings
        settings = get_settings()
        print(f"  ✓ Configuration loaded")
        print(f"  ✓ Database URL: {settings.database_url[:30]}...")
        print(f"  ✓ Agent Model: {settings.agent_model}")
        print(f"  ✓ Session Expire Hours: {settings.session_expire_hours}")
        return True
    except Exception as e:
        print(f"  ✗ Error loading configuration: {e}")
        return False


def test_agent_manager():
    """Test agent manager initialization."""
    print("\nTesting agent manager...")
    try:
        from app.config import get_settings
        from app.agents.manager import AgentManager
        
        settings = get_settings()
        manager = AgentManager(settings)
        
        agents = manager.list_agents()
        print(f"  ✓ Agent manager initialized")
        print(f"  ✓ Available agents: {list(agents.keys())}")
        
        for name, desc in agents.items():
            print(f"    - {name}: {desc}")
            agent = manager.get_agent(name)
            print(f"      ✓ Agent '{name}' loaded successfully")
        
        return True
    except Exception as e:
        print(f"  ✗ Error initializing agent manager: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_connection():
    """Test database connection (basic check)."""
    print("\nTesting database connection...")
    try:
        from app.database.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Try a simple query
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row[0] == 1:
                print("  ✓ Database connection successful")
                return True
            else:
                print("  ✗ Database query returned unexpected result")
                return False
    except Exception as e:
        print(f"  ✗ Database connection failed: {e}")
        print("  ℹ Make sure SQL Server is running and DATABASE_URL is correct")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Multi-Agent Chat System - Verification Tests")
    print("=" * 60)
    
    # Check if .env exists
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        print("\n✗ .env file not found!")
        print("  Please copy .env.example to .env and configure it.")
        return False
    
    results = []
    
    # Run tests
    results.append(("Configuration", test_config()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("Agent Manager", test_agent_manager()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Initialize database schema:")
        print("   sqlcmd -S server -d database -U user -P password -i backend\\app\\database\\init_schema.sql")
        print("2. Start backend: cd backend && uvicorn app.main:app --reload")
        print("3. Start frontend: cd frontend && streamlit run app.py")
    else:
        print("\n⚠ Some tests failed. Please fix the issues before proceeding.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
