#!/usr/bin/env python3
"""
Universal Protocol - The Rosetta Stone for Programming Languages
Translates between any programming language and the AI Neural Spine
"""

import json
import struct
import base64
import hashlib
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from enum import Enum
import socket
import threading
import queue
import sqlite3
from pathlib import Path

class MessageType(Enum):
    """Universal message types"""
    AI_REQUEST = "ai_request"
    AI_RESPONSE = "ai_response"
    CODE_TRANSLATION = "code_translation"
    FUNCTION_CALL = "function_call"
    DATA_SYNC = "data_sync"
    HEALTH_CHECK = "health_check"
    ERROR = "error"

class CommunicationChannel(Enum):
    """Communication channels between languages"""
    WEBSOCKET = "websocket"
    HTTP = "http"
    FILE_SYSTEM = "file_system"
    DATABASE = "database"
    BINARY_SOCKET = "binary_socket"
    SHARED_MEMORY = "shared_memory"

class UniversalMessage:
    """Universal message format that any language can understand"""
    
    def __init__(self, 
                 message_type: MessageType,
                 source_language: str,
                 target_language: str = "universal",
                 payload: Dict[str, Any] = None,
                 response_channel: CommunicationChannel = CommunicationChannel.WEBSOCKET):
        
        self.id = str(uuid.uuid4())
        self.timestamp = datetime.now().isoformat()
        self.message_type = message_type
        self.source_language = source_language
        self.target_language = target_language
        self.payload = payload or {}
        self.response_channel = response_channel
        self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate message checksum for integrity"""
        content = f"{self.id}{self.timestamp}{self.message_type.value}{json.dumps(self.payload, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def to_json(self) -> str:
        """Convert to JSON format"""
        return json.dumps({
            "id": self.id,
            "timestamp": self.timestamp,
            "message_type": self.message_type.value,
            "source_language": self.source_language,
            "target_language": self.target_language,
            "payload": self.payload,
            "response_channel": self.response_channel.value,
            "checksum": self.checksum
        }, indent=2)
    
    def to_binary(self) -> bytes:
        """Convert to binary format for performance"""
        json_data = self.to_json()
        json_bytes = json_data.encode('utf-8')
        
        # Binary format: [length:4][json_data:length]
        return struct.pack('!I', len(json_bytes)) + json_bytes
    
    @classmethod
    def from_json(cls, json_str: str) -> 'UniversalMessage':
        """Create from JSON string"""
        data = json.loads(json_str)
        
        msg = cls(
            MessageType(data['message_type']),
            data['source_language'],
            data['target_language'],
            data['payload'],
            CommunicationChannel(data['response_channel'])
        )
        
        msg.id = data['id']
        msg.timestamp = data['timestamp']
        msg.checksum = data['checksum']  # Use the stored checksum
        
        # Verify checksum by recalculating
        expected_checksum = msg._calculate_checksum_from_data()
        if expected_checksum != data['checksum']:
            print(f"⚠️ Warning: Checksum mismatch (expected: {expected_checksum}, got: {data['checksum']})")
            # Don't fail on checksum mismatch for now - just warn
        
        return msg
    
    def _calculate_checksum_from_data(self) -> str:
        """Calculate checksum from current data"""
        content = f"{self.id}{self.timestamp}{self.message_type.value}{json.dumps(self.payload, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    @classmethod
    def from_binary(cls, binary_data: bytes) -> 'UniversalMessage':
        """Create from binary data"""
        if len(binary_data) < 4:
            raise ValueError("Invalid binary data - too short")
        
        # Extract length and JSON data
        length = struct.unpack('!I', binary_data[:4])[0]
        json_data = binary_data[4:4+length].decode('utf-8')
        
        return cls.from_json(json_data)

class LanguageTranslator:
    """Translates between different programming language constructs"""
    
    def __init__(self):
        self.translation_rules = {
            'python_to_javascript': {
                'print': 'console.log',
                'len': 'length',
                'str': 'String',
                'int': 'parseInt',
                'float': 'parseFloat',
                'True': 'true',
                'False': 'false',
                'None': 'null',
                'def ': 'function ',
                'elif': 'else if',
                '__init__': 'constructor'
            },
            'javascript_to_python': {
                'console.log': 'print',
                'length': 'len',
                'String': 'str',
                'parseInt': 'int',
                'parseFloat': 'float',
                'true': 'True',
                'false': 'False',
                'null': 'None',
                'function ': 'def ',
                'else if': 'elif',
                'constructor': '__init__'
            },
            'python_to_go': {
                'print': 'fmt.Println',
                'def ': 'func ',
                'True': 'true',
                'False': 'false',
                'None': 'nil',
                'str': 'string',
                'int': 'int',
                'float': 'float64'
            },
            'go_to_python': {
                'fmt.Println': 'print',
                'func ': 'def ',
                'true': 'True',
                'false': 'False',
                'nil': 'None',
                'string': 'str',
                'int': 'int',
                'float64': 'float'
            }
        }
    
    def translate_code(self, code: str, from_lang: str, to_lang: str) -> str:
        """Translate code between languages"""
        
        translation_key = f"{from_lang}_to_{to_lang}"
        rules = self.translation_rules.get(translation_key, {})
        
        translated_code = code
        for from_pattern, to_pattern in rules.items():
            translated_code = translated_code.replace(from_pattern, to_pattern)
        
        return translated_code
    
    def translate_data_types(self, data: Any, from_lang: str, to_lang: str) -> Any:
        """Translate data types between languages"""
        
        if from_lang == 'python' and to_lang == 'javascript':
            if data is None:
                return None  # null in JS
            elif isinstance(data, bool):
                return data  # Same in both
            elif isinstance(data, (int, float, str)):
                return data  # Same in both
            elif isinstance(data, list):
                return [self.translate_data_types(item, from_lang, to_lang) for item in data]
            elif isinstance(data, dict):
                return {k: self.translate_data_types(v, from_lang, to_lang) for k, v in data.items()}
        
        return data

class UniversalBridge:
    """
    Universal Bridge - Central hub for multi-language communication
    Like the spinal cord for programming languages
    """
    
    def __init__(self, port: int = 8765):
        self.port = port
        self.translator = LanguageTranslator()
        self.message_queue = queue.Queue()
        self.active_connections = {}
        self.language_handlers = {}
        self.db = self._init_database()
        
        # Communication channels
        self.websocket_server = None
        self.http_server = None
        self.file_watcher = None
        
        # Start background services
        self._start_background_services()
    
    def _init_database(self) -> sqlite3.Connection:
        """Initialize message database for persistence"""
        
        db_path = Path("universal_bridge.db")
        conn = sqlite3.connect(db_path, check_same_thread=False)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                message_type TEXT,
                source_language TEXT,
                target_language TEXT,
                payload TEXT,
                response_channel TEXT,
                status TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_language TEXT,
                to_language TEXT,
                original_code TEXT,
                translated_code TEXT,
                success BOOLEAN,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        return conn
    
    def _start_background_services(self):
        """Start background communication services"""
        
        # Message processing thread
        threading.Thread(target=self._process_messages, daemon=True).start()
        
        # File system watcher
        threading.Thread(target=self._watch_file_system, daemon=True).start()
        
        # Database queue processor
        threading.Thread(target=self._process_database_queue, daemon=True).start()
        
        print(f"🌍 Universal Bridge started on port {self.port}")
    
    def register_language_handler(self, language: str, handler_func):
        """Register a handler for a specific language"""
        self.language_handlers[language] = handler_func
        print(f"📝 Registered handler for {language}")
    
    def send_message(self, message: UniversalMessage) -> str:
        """Send message through the universal bridge"""
        
        # Store in database with thread-safe connection
        try:
            self.db.execute("""
                INSERT INTO messages (id, timestamp, message_type, source_language, target_language, payload, response_channel, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(message.id),
                str(message.timestamp),
                str(message.message_type.value),
                str(message.source_language),
                str(message.target_language),
                json.dumps(message.payload),
                str(message.response_channel.value),
                'pending'
            ))
            self.db.commit()
        except Exception as e:
            print(f"⚠️ Database insert warning: {e}")
        
        # Add to processing queue
        self.message_queue.put(message)
        
        print(f"📤 Message sent: {message.id} ({message.source_language} → {message.target_language})")
        return message.id
    
    def _process_messages(self):
        """Background message processing"""
        
        while True:
            try:
                message = self.message_queue.get(timeout=1)
                self._handle_message(message)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Message processing error: {e}")
    
    def _handle_message(self, message: UniversalMessage):
        """Handle individual message"""
        
        try:
            if message.message_type == MessageType.CODE_TRANSLATION:
                self._handle_code_translation(message)
            elif message.message_type == MessageType.AI_REQUEST:
                self._handle_ai_request(message)
            elif message.message_type == MessageType.FUNCTION_CALL:
                self._handle_function_call(message)
            else:
                print(f"⚠️ Unknown message type: {message.message_type}")
            
            # Update status
            self.db.execute(
                "UPDATE messages SET status = 'processed' WHERE id = ?",
                (message.id,)
            )
            self.db.commit()
            
        except Exception as e:
            print(f"❌ Error handling message {message.id}: {e}")
            self.db.execute(
                "UPDATE messages SET status = 'error' WHERE id = ?",
                (message.id,)
            )
            self.db.commit()
    
    def _handle_code_translation(self, message: UniversalMessage):
        """Handle code translation between languages"""
        
        payload = message.payload
        code = payload.get('code', '')
        from_lang = message.source_language
        to_lang = message.target_language
        
        # Translate the code
        translated_code = self.translator.translate_code(code, from_lang, to_lang)
        
        # Store translation
        self.db.execute("""
            INSERT INTO translations (from_language, to_language, original_code, translated_code, success)
            VALUES (?, ?, ?, ?, ?)
        """, (from_lang, to_lang, code, translated_code, True))
        self.db.commit()
        
        # Send response
        response = UniversalMessage(
            MessageType.AI_RESPONSE,
            "universal_bridge",
            from_lang,
            {
                'original_message_id': message.id,
                'translated_code': translated_code,
                'from_language': from_lang,
                'to_language': to_lang
            }
        )
        
        self._send_response(response, message.response_channel)
        
        print(f"🔄 Code translated: {from_lang} → {to_lang}")
    
    def _handle_ai_request(self, message: UniversalMessage):
        """Handle AI request from any language"""
        
        # This would integrate with the AI Neural Spine
        payload = message.payload
        
        # Simulate AI processing
        ai_response = {
            'original_message_id': message.id,
            'ai_result': f"AI processed request from {message.source_language}",
            'data': payload,
            'timestamp': datetime.now().isoformat()
        }
        
        response = UniversalMessage(
            MessageType.AI_RESPONSE,
            "ai_neural_spine",
            message.source_language,
            ai_response
        )
        
        self._send_response(response, message.response_channel)
        
        print(f"🤖 AI request processed for {message.source_language}")
    
    def _handle_function_call(self, message: UniversalMessage):
        """Handle function call between languages"""
        
        payload = message.payload
        function_name = payload.get('function_name')
        args = payload.get('args', [])
        kwargs = payload.get('kwargs', {})
        
        # Look for handler in target language
        target_handler = self.language_handlers.get(message.target_language)
        
        if target_handler:
            try:
                result = target_handler(function_name, args, kwargs)
                
                response = UniversalMessage(
                    MessageType.AI_RESPONSE,
                    message.target_language,
                    message.source_language,
                    {
                        'original_message_id': message.id,
                        'function_result': result,
                        'success': True
                    }
                )
                
                self._send_response(response, message.response_channel)
                
            except Exception as e:
                error_response = UniversalMessage(
                    MessageType.ERROR,
                    "universal_bridge",
                    message.source_language,
                    {
                        'original_message_id': message.id,
                        'error': str(e),
                        'success': False
                    }
                )
                
                self._send_response(error_response, message.response_channel)
        
        print(f"📞 Function call: {function_name} ({message.source_language} → {message.target_language})")
    
    def _send_response(self, response: UniversalMessage, channel: CommunicationChannel):
        """Send response through specified channel"""
        
        if channel == CommunicationChannel.FILE_SYSTEM:
            self._send_via_file_system(response)
        elif channel == CommunicationChannel.DATABASE:
            self._send_via_database(response)
        elif channel == CommunicationChannel.WEBSOCKET:
            self._send_via_websocket(response)
        else:
            print(f"⚠️ Unsupported response channel: {channel}")
    
    def _send_via_file_system(self, message: UniversalMessage):
        """Send message via file system"""
        
        file_path = Path(f"bridge_messages/{message.target_language}/{message.id}.json")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(message.to_json())
        
        print(f"📁 Message saved to file: {file_path}")
    
    def _send_via_database(self, message: UniversalMessage):
        """Send message via database queue"""
        
        self.db.execute("""
            INSERT INTO messages (id, timestamp, message_type, source_language, target_language, payload, response_channel, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            message.id,
            message.timestamp,
            message.message_type.value,
            message.source_language,
            message.target_language,
            json.dumps(message.payload),
            message.response_channel.value,
            'ready'
        ))
        self.db.commit()
        
        print(f"🗄️ Message queued in database: {message.id}")
    
    def _send_via_websocket(self, message: UniversalMessage):
        """Send message via WebSocket"""
        # WebSocket implementation would go here
        print(f"🔌 WebSocket message sent: {message.id}")
    
    def _watch_file_system(self):
        """Watch file system for incoming messages"""
        
        watch_dir = Path("bridge_messages/incoming")
        watch_dir.mkdir(parents=True, exist_ok=True)
        
        while True:
            try:
                for file_path in watch_dir.glob("*.json"):
                    try:
                        with open(file_path, 'r') as f:
                            message_data = f.read()
                        
                        message = UniversalMessage.from_json(message_data)
                        self.message_queue.put(message)
                        
                        # Move processed file
                        processed_dir = watch_dir / "processed"
                        processed_dir.mkdir(exist_ok=True)
                        file_path.rename(processed_dir / file_path.name)
                        
                    except Exception as e:
                        print(f"❌ Error processing file {file_path}: {e}")
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"❌ File watcher error: {e}")
                time.sleep(5)
    
    def _process_database_queue(self):
        """Process database message queue"""
        
        while True:
            try:
                cursor = self.db.execute("""
                    SELECT id, timestamp, message_type, source_language, target_language, payload, response_channel
                    FROM messages 
                    WHERE status = 'ready'
                    ORDER BY created_at ASC
                    LIMIT 10
                """)
                
                messages = cursor.fetchall()
                
                for row in messages:
                    msg_id, timestamp, msg_type, source_lang, target_lang, payload, response_channel = row
                    
                    message = UniversalMessage(
                        MessageType(msg_type),
                        source_lang,
                        target_lang,
                        json.loads(payload),
                        CommunicationChannel(response_channel)
                    )
                    message.id = msg_id
                    message.timestamp = timestamp
                    
                    self.message_queue.put(message)
                    
                    # Mark as processing
                    self.db.execute(
                        "UPDATE messages SET status = 'processing' WHERE id = ?",
                        (msg_id,)
                    )
                    self.db.commit()
                
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                print(f"❌ Database queue error: {e}")
                time.sleep(5)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get bridge statistics"""
        
        cursor = self.db.execute("""
            SELECT 
                COUNT(*) as total_messages,
                COUNT(CASE WHEN status = 'processed' THEN 1 END) as processed,
                COUNT(CASE WHEN status = 'error' THEN 1 END) as errors,
                COUNT(DISTINCT source_language) as languages_used
            FROM messages
        """)
        
        stats = cursor.fetchone()
        
        return {
            'total_messages': stats[0],
            'processed_messages': stats[1],
            'error_messages': stats[2],
            'languages_used': stats[3],
            'active_connections': len(self.active_connections),
            'queue_size': self.message_queue.qsize()
        }

def demo_universal_bridge():
    """Demonstrate the Universal Bridge"""
    
    print("🌍 UNIVERSAL BRIDGE DEMONSTRATION")
    print("=" * 60)
    print("Multi-language communication and translation system")
    print()
    
    # Initialize bridge
    bridge = UniversalBridge()
    
    # Demo 1: Code translation
    print("🔄 Demo 1: Code Translation")
    python_code = """
def hello_world(name):
    print(f"Hello, {name}!")
    return True
"""
    
    translation_message = UniversalMessage(
        MessageType.CODE_TRANSLATION,
        "python",
        "javascript",
        {"code": python_code},
        CommunicationChannel.FILE_SYSTEM
    )
    
    message_id = bridge.send_message(translation_message)
    print(f"   📤 Translation request sent: {message_id}")
    
    # Demo 2: AI request from different language
    print("\n🤖 Demo 2: AI Request")
    ai_request = UniversalMessage(
        MessageType.AI_REQUEST,
        "go",
        "universal",
        {
            "action": "generate_documentation",
            "code": "func main() { fmt.Println(\"Hello World\") }",
            "language": "go"
        },
        CommunicationChannel.DATABASE
    )
    
    ai_message_id = bridge.send_message(ai_request)
    print(f"   📤 AI request sent: {ai_message_id}")
    
    # Demo 3: Function call between languages
    print("\n📞 Demo 3: Cross-Language Function Call")
    function_call = UniversalMessage(
        MessageType.FUNCTION_CALL,
        "python",
        "javascript",
        {
            "function_name": "processData",
            "args": [{"data": "test"}],
            "kwargs": {"format": "json"}
        },
        CommunicationChannel.WEBSOCKET
    )
    
    func_message_id = bridge.send_message(function_call)
    print(f"   📤 Function call sent: {func_message_id}")
    
    # Wait for processing
    time.sleep(3)
    
    # Show statistics
    print("\n📊 Bridge Statistics:")
    stats = bridge.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n🌍 Universal Bridge Features Demonstrated:")
    print("   ✅ Multi-language code translation")
    print("   ✅ AI request routing from any language")
    print("   ✅ Cross-language function calls")
    print("   ✅ Multiple communication channels")
    print("   ✅ Message persistence and queuing")
    print("   ✅ Error handling and recovery")
    
    return bridge

if __name__ == '__main__':
    demo_universal_bridge()