import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("🧠 SMARTY - AML Intelligent Assistant")
print("=" * 70)

try:
    from smarty import Assistant, Config
    print("✅ Imports successful!")
    
    config = Config()
    assistant = Assistant(config)
    print("✅ Assistant created!")
    
    if assistant.vector_store.count() == 0:
        print("\n📚 No knowledge base found. Ingesting documents...")
        result = assistant.ingest()
        if result['success']:
            print(f"✅ Ingested {result['documents']} documents")
            print(f"📊 Created {result['chunks']} chunks")
        else:
            print(f"❌ Error: {result['error']}")
    
    status = assistant.status()
    print(f"\n📊 Status: {status['vectors']} vectors from {status['documents']} documents")
    print(f"🔧 Model: {status['model']}")
    print(f"💻 Device: {status['device']}")
    
    print("\n" + "=" * 70)
    print("💬 Commands: 'exit' to quit, 'clear' history, 'status' info, 'reset' all")
    print("=" * 70)
    
    while True:
        try:
            query = input("\n❓ You: ").strip()
            if not query:
                continue
            if query.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye!")
                break
            if query.lower() == 'clear':
                assistant.clear()
                print("🧹 History cleared")
                continue
            if query.lower() == 'status':
                print(assistant.status())
                continue
            if query.lower() == 'reset':
                assistant.reset()
                print("🔄 Assistant reset")
                continue
            print("🤔 Thinking...")
            response = assistant.ask(query)
            print(f"\n🤖 Assistant: {response['response']}")
            if response.get('sources'):
                print(f"\n📎 Sources: {', '.join(response['sources'])}")
            if response.get('confidence'):
                print(f"📊 Confidence: {response['confidence']:.2f}")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            
except Exception as e:
    print(f"❌ Error loading SMARTY: {e}")
    import traceback
    traceback.print_exc()
