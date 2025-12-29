#!/usr/bin/env python3
"""
Bridge Integration for Self-Evolving AI Framework
================================================

Connects the Evolution Framework with the Bridge API for unified system operation.
Handles event synchronization, status updates, and cross-system communication.

Features:
- Real-time event publishing to Bridge API
- Health monitoring and status reporting
- Automatic reconnection and error recovery
- Type-safe communication using shared types
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable
import aiohttp
import websockets
from websockets.exceptions import ConnectionClosed, InvalidURI

from shared_types import (
    CrossSystemEvent, EventType, UnifiedSystemStatus, ApiResponse,
    BridgeAPIError, IntegrationError
)
from type_validation import TypeValidator, validate_cross_system_event


class BridgeIntegration:
    """
    Integration service for connecting Evolution Framework with Bridge API.
    
    Provides bidirectional communication, event synchronization, and
    health monitoring between the Evolution Framework and Bridge API.
    """
    
    def __init__(self, bridge_url: str = "http://localhost:3001", websocket_url: str = "ws://localhost:3001"):
        self.bridge_url = bridge_url.rstrip('/')
        self.websocket_url = websocket_url
        self.logger = logging.getLogger(__name__)
        
        # Connection state
        self.connected = False
        self.websocket = None
        self.session = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 5  # seconds
        
        # Event handlers
        self.event_handlers: Dict[EventType, Callable] = {}
        self.status_callback: Optional[Callable] = None
        
        # Health monitoring
        self.last_health_check = None
        self.health_check_interval = 30  # seconds
        
        # Background tasks
        self.background_tasks = set()
    
    async def initialize(self) -> bool:
        """Initialize the bridge integration"""
        try:
            self.logger.info("🌉 Initializing Bridge Integration...")
            
            # Create HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'Content-Type': 'application/json'}
            )
            
            # Test connection to Bridge API
            await self._test_connection()
            
            # Start WebSocket connection
            await self._connect_websocket()
            
            # Start background tasks
            self._start_background_tasks()
            
            self.logger.info("✅ Bridge Integration initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Bridge Integration initialization failed: {e}")
            return False
    
    async def _test_connection(self):
        """Test HTTP connection to Bridge API"""
        try:
            async with self.session.get(f"{self.bridge_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    self.logger.info(f"✅ Bridge API connection successful: {data.get('data', {}).get('bridge', {}).get('status', 'unknown')}")
                else:
                    raise IntegrationError(f"Bridge API health check failed: {response.status}", 'evolution')
        except aiohttp.ClientError as e:
            raise IntegrationError(f"Failed to connect to Bridge API: {e}", 'evolution')
    
    async def _connect_websocket(self):
        """Connect to Bridge API WebSocket"""
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            self.connected = True
            self.reconnect_attempts = 0
            
            self.logger.info("🔌 WebSocket connected to Bridge API")
            
            # Start WebSocket message handler
            task = asyncio.create_task(self._websocket_handler())
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)
            
        except (ConnectionClosed, InvalidURI, OSError) as e:
            self.logger.error(f"❌ WebSocket connection failed: {e}")
            self.connected = False
            await self._schedule_reconnect()
    
    async def _websocket_handler(self):
        """Handle incoming WebSocket messages"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._handle_websocket_message(data)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid WebSocket message: {e}")
                except Exception as e:
                    self.logger.error(f"Error handling WebSocket message: {e}")
        except ConnectionClosed:
            self.logger.warning("WebSocket connection closed")
            self.connected = False
            await self._schedule_reconnect()
        except Exception as e:
            self.logger.error(f"WebSocket handler error: {e}")
            self.connected = False
            await self._schedule_reconnect()
    
    async def _handle_websocket_message(self, data: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        message_type = data.get('type')
        payload = data.get('payload', {})
        
        if message_type == 'event':
            # Handle cross-system events
            try:
                event = validate_cross_system_event(payload)
                await self._handle_cross_system_event(event)
            except ValueError as e:
                self.logger.error(f"Invalid event format: {e}")
        
        elif message_type == 'status':
            # Handle status updates
            if self.status_callback:
                await self.status_callback(payload)
        
        elif message_type == 'error':
            self.logger.error(f"Bridge API error: {payload}")
    
    async def _handle_cross_system_event(self, event: CrossSystemEvent):
        """Handle cross-system events from Bridge API"""
        if event.target in ['evolution', 'both']:
            handler = self.event_handlers.get(event.type)
            if handler:
                try:
                    await handler(event)
                except Exception as e:
                    self.logger.error(f"Error handling event {event.type}: {e}")
            else:
                self.logger.debug(f"No handler for event type: {event.type}")
    
    async def _schedule_reconnect(self):
        """Schedule WebSocket reconnection"""
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            delay = self.reconnect_delay * (2 ** (self.reconnect_attempts - 1))  # Exponential backoff
            
            self.logger.info(f"🔄 Scheduling reconnect attempt {self.reconnect_attempts}/{self.max_reconnect_attempts} in {delay}s")
            
            await asyncio.sleep(delay)
            await self._connect_websocket()
        else:
            self.logger.error("❌ Max reconnection attempts reached")
    
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        # Health check task
        task = asyncio.create_task(self._health_check_loop())
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)
    
    async def _health_check_loop(self):
        """Background health check loop"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_check()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
    
    async def _perform_health_check(self):
        """Perform health check with Bridge API"""
        try:
            async with self.session.get(f"{self.bridge_url}/health") as response:
                if response.status == 200:
                    self.last_health_check = datetime.now()
                    self.logger.debug("✅ Health check successful")
                else:
                    self.logger.warning(f"⚠️ Health check failed: {response.status}")
        except Exception as e:
            self.logger.error(f"❌ Health check error: {e}")
    
    # Public API Methods
    
    async def publish_event(self, event_type: EventType, payload: Dict[str, Any], 
                          target: str = 'both', priority: str = 'medium') -> bool:
        """Publish event to Bridge API"""
        try:
            event_data = {
                'id': f"evo_{int(time.time() * 1000)}",
                'type': event_type.value,
                'source': 'evolution',
                'target': target,
                'payload': payload,
                'timestamp': datetime.now().isoformat(),
                'priority': priority
            }
            
            # Send via HTTP API
            async with self.session.post(f"{self.bridge_url}/api/events", json=event_data) as response:
                if response.status == 200:
                    self.logger.debug(f"✅ Event published: {event_type.value}")
                    return True
                else:
                    self.logger.error(f"❌ Failed to publish event: {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"❌ Error publishing event: {e}")
            return False
    
    async def update_evolution_status(self, status: Dict[str, Any]) -> bool:
        """Update evolution system status in Bridge API"""
        try:
            async with self.session.post(f"{self.bridge_url}/api/evolution/status", json=status) as response:
                if response.status == 200:
                    self.logger.debug("✅ Evolution status updated")
                    return True
                else:
                    self.logger.error(f"❌ Failed to update status: {response.status}")
                    return False
        except Exception as e:
            self.logger.error(f"❌ Error updating status: {e}")
            return False
    
    async def request_workflow_optimization(self, workflow_id: str, metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Request workflow optimization from Bridge API"""
        try:
            optimization_data = {
                'workflow_id': workflow_id,
                'evolution_metrics': metrics,
                'timestamp': datetime.now().isoformat()
            }
            
            async with self.session.post(f"{self.bridge_url}/api/optimize/workflow/{workflow_id}", 
                                       json=optimization_data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"✅ Workflow optimization received for {workflow_id}")
                    return result.get('data')
                else:
                    self.logger.error(f"❌ Workflow optimization failed: {response.status}")
                    return None
        except Exception as e:
            self.logger.error(f"❌ Error requesting optimization: {e}")
            return None
    
    def register_event_handler(self, event_type: EventType, handler: Callable):
        """Register handler for specific event type"""
        self.event_handlers[event_type] = handler
        self.logger.info(f"📝 Registered handler for {event_type.value}")
    
    def set_status_callback(self, callback: Callable):
        """Set callback for status updates"""
        self.status_callback = callback
        self.logger.info("📝 Status callback registered")
    
    async def shutdown(self):
        """Shutdown bridge integration"""
        self.logger.info("🔄 Shutting down Bridge Integration...")
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Close WebSocket
        if self.websocket:
            await self.websocket.close()
        
        # Close HTTP session
        if self.session:
            await self.session.close()
        
        self.connected = False
        self.logger.info("✅ Bridge Integration shutdown complete")


# Convenience functions for Evolution Framework integration

async def create_bridge_integration(bridge_url: str = "http://localhost:3001") -> BridgeIntegration:
    """Create and initialize bridge integration"""
    integration = BridgeIntegration(bridge_url)
    success = await integration.initialize()
    
    if not success:
        raise IntegrationError("Failed to initialize bridge integration", 'evolution')
    
    return integration


async def publish_mutation_event(integration: BridgeIntegration, mutation_data: Dict[str, Any]):
    """Publish mutation event to Bridge API"""
    await integration.publish_event(
        EventType.MUTATION_APPLIED,
        mutation_data,
        target='both',
        priority='high'
    )


async def publish_fitness_update(integration: BridgeIntegration, fitness_data: Dict[str, Any]):
    """Publish fitness calculation event to Bridge API"""
    await integration.publish_event(
        EventType.FITNESS_CALCULATED,
        fitness_data,
        target='workflow',
        priority='medium'
    )


async def publish_system_evolution(integration: BridgeIntegration, evolution_data: Dict[str, Any]):
    """Publish system evolution event to Bridge API"""
    await integration.publish_event(
        EventType.SYSTEM_EVOLVED,
        evolution_data,
        target='both',
        priority='high'
    )


if __name__ == "__main__":
    # Test the bridge integration
    async def test_integration():
        try:
            integration = await create_bridge_integration()
            
            # Test event publishing
            await publish_mutation_event(integration, {
                'mutation_type': 'test_mutation',
                'description': 'Test mutation from Evolution Framework',
                'fitness_impact': 5.0
            })
            
            # Wait a bit for events to process
            await asyncio.sleep(2)
            
            await integration.shutdown()
            print("✅ Bridge integration test completed successfully")
            
        except Exception as e:
            print(f"❌ Bridge integration test failed: {e}")
    
    asyncio.run(test_integration())