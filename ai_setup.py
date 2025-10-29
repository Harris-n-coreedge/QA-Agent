"""
AI API Setup Helper

This script helps you set up API keys for different AI providers
and test the AI-powered QA agent.
"""
import os
import asyncio
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def setup_api_keys():
    """Help user set up API keys for different AI providers."""
    print("🔑 AI API Setup Helper")
    print("=" * 25)
    print("This will help you set up API keys for different AI providers.")
    print()
    
    # Check current environment variables
    print("📋 Current API Keys:")
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    
    print(f"   OpenAI: {'✅ Set' if openai_key else '❌ Not set'}")
    print(f"   Anthropic: {'✅ Set' if anthropic_key else '❌ Not set'}")
    print(f"   Google: {'✅ Set' if google_key else '❌ Not set'}")
    print()
    
    # Ask which provider to set up
    print("Which AI provider would you like to set up?")
    print("1. OpenAI (GPT-3.5, GPT-4)")
    print("2. Anthropic (Claude)")
    print("3. Google (Gemini)")
    print("4. All of them")
    print("5. Skip setup")
    
    choice = input("Enter choice (1-5): ").strip()
    
    if choice == "1" or choice == "4":
        setup_openai()
    
    if choice == "2" or choice == "4":
        setup_anthropic()
    
    if choice == "3" or choice == "4":
        setup_google()
    
    if choice == "5":
        print("⏭️ Skipping setup")
        return
    
    print("\n✅ Setup complete!")
    print("\n💡 To use these API keys:")
    print("   1. Set them as environment variables")
    print("   2. Or enter them manually when running the agent")
    print("\n🚀 Run the AI agent with:")
    print("   python ai_powered_qa_agent.py")
    print("   python multi_ai_qa_agent.py")


def setup_openai():
    """Set up OpenAI API key."""
    print("\n🔑 OpenAI Setup")
    print("-" * 15)
    print("1. Go to https://platform.openai.com/api-keys")
    print("2. Create a new API key")
    print("3. Copy the key")
    print()
    
    api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Save to .env file
        with open(".env", "a") as f:
            f.write(f"\nOPENAI_API_KEY={api_key}\n")
        print("✅ OpenAI API key saved to .env file")
        
        # Set environment variable for current session
        os.environ["OPENAI_API_KEY"] = api_key
        print("✅ OpenAI API key set for current session")
    else:
        print("⏭️ Skipped OpenAI setup")


def setup_anthropic():
    """Set up Anthropic API key."""
    print("\n🔑 Anthropic Setup")
    print("-" * 17)
    print("1. Go to https://console.anthropic.com/")
    print("2. Create a new API key")
    print("3. Copy the key")
    print()
    
    api_key = input("Enter your Anthropic API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Save to .env file
        with open(".env", "a") as f:
            f.write(f"\nANTHROPIC_API_KEY={api_key}\n")
        print("✅ Anthropic API key saved to .env file")
        
        # Set environment variable for current session
        os.environ["ANTHROPIC_API_KEY"] = api_key
        print("✅ Anthropic API key set for current session")
    else:
        print("⏭️ Skipped Anthropic setup")


def setup_google():
    """Set up Google API key."""
    print("\n🔑 Google Setup")
    print("-" * 13)
    print("1. Go to https://makersuite.google.com/app/apikey")
    print("2. Create a new API key")
    print("3. Copy the key")
    print()
    
    api_key = input("Enter your Google API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Save to .env file
        with open(".env", "a") as f:
            f.write(f"\nGOOGLE_API_KEY={api_key}\n")
        print("✅ Google API key saved to .env file")
        
        # Set environment variable for current session
        os.environ["GOOGLE_API_KEY"] = api_key
        print("✅ Google API key set for current session")
    else:
        print("⏭️ Skipped Google setup")


def test_ai_connection():
    """Test AI API connections."""
    print("\n🧪 Testing AI Connections")
    print("-" * 25)
    
    # Test OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            import openai
            openai.api_key = openai_key
            print("✅ OpenAI connection successful")
        except Exception as e:
            print(f"❌ OpenAI connection failed: {e}")
    else:
        print("⏭️ OpenAI not configured")
    
    # Test Anthropic
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            print("✅ Anthropic connection successful")
        except Exception as e:
            print(f"❌ Anthropic connection failed: {e}")
    else:
        print("⏭️ Anthropic not configured")
    
    # Test Google
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=google_key)
            print("✅ Google connection successful")
        except Exception as e:
            print(f"❌ Google connection failed: {e}")
    else:
        print("⏭️ Google not configured")


def show_usage_examples():
    """Show usage examples for the AI agent."""
    print("\n💡 Usage Examples")
    print("-" * 16)
    print("Once you have API keys set up, you can use the AI agent like this:")
    print()
    print("🤖 Basic Commands:")
    print("   - 'log in'")
    print("   - 'sign up'")
    print("   - 'search for python'")
    print("   - 'scroll down'")
    print("   - 'click the menu'")
    print()
    print("🧠 Advanced AI Commands:")
    print("   - 'find all the buttons on this page'")
    print("   - 'navigate to the tutorials section'")
    print("   - 'what can I do here?'")
    print("   - 'click on the first link that says learn'")
    print("   - 'scroll to the bottom and click contact'")
    print()
    print("🚀 Run the agent:")
    print("   python ai_powered_qa_agent.py")
    print("   python multi_ai_qa_agent.py")


if __name__ == "__main__":
    print("🤖 AI-Powered QA Agent Setup")
    print("=" * 35)
    print()
    
    print("Choose an option:")
    print("1. Set up API keys")
    print("2. Test AI connections")
    print("3. Show usage examples")
    print("4. All of the above")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1" or choice == "4":
        setup_api_keys()
    
    if choice == "2" or choice == "4":
        test_ai_connection()
    
    if choice == "3" or choice == "4":
        show_usage_examples()
    
    print("\n🎉 Setup complete! You're ready to use the AI-powered QA agent!")
