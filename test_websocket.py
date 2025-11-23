"""
Test WebSocket connection locally
"""
import asyncio
import websockets
import json
import sys

async def test_websocket():
    # Test without token first
    conversation_id = "69238aa9b76d427d255ecaf8"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjkyMzc2NGZiNzZkNDI3ZDI1NWVjYWY1IiwidXNlcl90eXBlIjoidXNlciIsImVtYWlsIjoiYnV5ZXJAZXhhbXBsZS5jb20iLCJyb2xlIjoiYnV5ZXIiLCJleHAiOjE3NjQwMjM4MDIsImlhdCI6MTc2MzkzNzQwMn0.vtVPx3r9lrmQ04Hd4C3paDA-e3n1XbXPwewNqJ6thLk"
    
    # Test local
    uri_local = f"ws://localhost:8000/ws/chat/{conversation_id}/?token={token}"
    
    # Test production
    uri_prod = f"wss://dolabb-backend-2vsj.onrender.com/ws/chat/{conversation_id}/?token={token}"
    
    print("Testing WebSocket connection...")
    print(f"Local: {uri_local}")
    print(f"Production: {uri_prod}")
    print()
    
    # Test production first
    print("Testing Production WebSocket...")
    try:
        async with websockets.connect(uri_prod) as websocket:
            print("✅ Connected to production WebSocket!")
            
            # Send a test message
            message = {
                "type": "chat_message",
                "senderId": "6923764fb76d427d255ecaf5",
                "receiverId": "6923764fb76d427d255ecaf5",
                "text": "Test message",
                "attachments": [],
                "offerId": None,
                "productId": None
            }
            await websocket.send(json.dumps(message))
            print("✅ Sent test message")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                print(f"✅ Received: {response}")
            except asyncio.TimeoutError:
                print("⚠️ No response received (timeout)")
                
    except Exception as e:
        error_type = type(e).__name__
        print(f"ERROR: Connection failed - {error_type}: {str(e)}")
        if hasattr(e, 'status_code'):
            print(f"   Status code: {e.status_code}")
        if hasattr(e, 'code'):
            print(f"   Close code: {e.code}")
        if hasattr(e, 'reason'):
            print(f"   Reason: {e.reason}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_websocket())

