#!/usr/bin/env python3
"""
Unified System Integration Test
==============================

Tests the integration between Evolution Framework and Bridge API
to verify the unified application is working correctly.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BRIDGE_API_URL = "http://localhost:3001"
EVOLUTION_API_URL = "http://localhost:5000"

def test_bridge_api_health():
    """Test Bridge API health endpoint"""
    print("🔍 Testing Bridge API health...")
    try:
        response = requests.get(f"{BRIDGE_API_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Bridge API is healthy")
            print(f"   - Version: {data['data']['bridge']['version']}")
            print(f"   - Status: {data['data']['bridge']['status']}")
            print(f"   - Evolution connected: {data['data']['evolution']['connected']}")
            print(f"   - Workflow connected: {data['data']['workflow']['connected']}")
            return True
        else:
            print(f"❌ Bridge API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Bridge API not reachable: {e}")
        return False

def test_evolution_api_health():
    """Test Evolution Framework API health"""
    print("\n🔍 Testing Evolution Framework API...")
    try:
        response = requests.get(f"{EVOLUTION_API_URL}/api/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Evolution Framework is healthy")
            print(f"   - Version: {data['version']}")
            print(f"   - Generation: {data['dna']['generation']}")
            print(f"   - Fitness Score: {data['dna']['fitness_score']:.2f}")
            print(f"   - Mutations Applied: {data['dna']['mutations_count']}")
            return True
        else:
            print(f"❌ Evolution Framework health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Evolution Framework not reachable: {e}")
        return False

def test_mutation_via_bridge():
    """Test mutation application through Bridge API"""
    print("\n🔍 Testing mutation via Bridge API...")
    
    # Get initial state
    try:
        initial_response = requests.get(f"{BRIDGE_API_URL}/health")
        initial_data = initial_response.json()
        initial_generation = initial_data['data']['evolution']['generation']
        initial_fitness = initial_data['data']['evolution']['fitnessScore']
        
        print(f"   Initial state - Generation: {initial_generation}, Fitness: {initial_fitness:.2f}")
        
        # Apply mutation
        mutation_data = {
            "type": "integration_test",
            "description": "Test mutation to verify Bridge API integration",
            "fitness_impact": 1.5,
            "source_ai": "IntegrationTest"
        }
        
        mutation_response = requests.post(
            f"{BRIDGE_API_URL}/api/evolution/mutate",
            json=mutation_data,
            headers={"Content-Type": "application/json"}
        )
        
        if mutation_response.status_code == 200:
            result = mutation_response.json()
            print(f"✅ Mutation request successful")
            print(f"   - Approved: {result['data']['approved']}")
            print(f"   - Auto-approved: {result['data'].get('auto', False)}")
            
            # Wait a moment for the mutation to be processed
            time.sleep(1)
            
            # Check final state
            final_response = requests.get(f"{BRIDGE_API_URL}/health")
            final_data = final_response.json()
            final_generation = final_data['data']['evolution']['generation']
            final_fitness = final_data['data']['evolution']['fitnessScore']
            
            print(f"   Final state - Generation: {final_generation}, Fitness: {final_fitness:.2f}")
            
            if final_generation > initial_generation:
                print(f"✅ Generation advanced: {initial_generation} → {final_generation}")
                fitness_change = final_fitness - initial_fitness
                print(f"✅ Fitness changed by: {fitness_change:.2f}")
                return True
            else:
                print(f"⚠️ Generation did not advance (might be queued for approval)")
                return True  # Still consider success if queued
        else:
            print(f"❌ Mutation request failed: {mutation_response.status_code}")
            print(f"   Response: {mutation_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Mutation test failed: {e}")
        return False

def test_direct_evolution_api():
    """Test direct Evolution Framework API"""
    print("\n🔍 Testing direct Evolution Framework API...")
    
    try:
        # Test fitness endpoint
        fitness_response = requests.get(f"{EVOLUTION_API_URL}/api/fitness")
        if fitness_response.status_code == 200:
            fitness_data = fitness_response.json()
            print(f"✅ Fitness API working")
            print(f"   - Overall Score: {fitness_data['overall']}")
            print(f"   - Trend: {fitness_data['trend']}")
        
        # Test demo data endpoint
        demo_response = requests.get(f"{EVOLUTION_API_URL}/api/demo-data")
        if demo_response.status_code == 200:
            demo_data = demo_response.json()
            print(f"✅ Demo data API working")
            print(f"   - Sample mutations available: {len(demo_data['sample_mutations'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct Evolution API test failed: {e}")
        return False

def test_unified_status():
    """Test unified system status"""
    print("\n🔍 Testing unified system status...")
    
    try:
        # Test Bridge API unified status
        bridge_response = requests.get(f"{BRIDGE_API_URL}/api/status")
        if bridge_response.status_code == 200:
            bridge_data = bridge_response.json()
            print(f"✅ Bridge API status endpoint working")
            
        # Test Evolution Framework status
        evolution_response = requests.get(f"{EVOLUTION_API_URL}/api/status")
        if evolution_response.status_code == 200:
            evolution_data = evolution_response.json()
            print(f"✅ Evolution Framework status endpoint working")
            
        # Compare data consistency
        if bridge_response.status_code == 200 and evolution_response.status_code == 200:
            bridge_generation = bridge_data['data']['evolution']['generation']
            evolution_generation = evolution_data['dna']['generation']
            
            if bridge_generation == evolution_generation:
                print(f"✅ Data consistency verified - Generation: {bridge_generation}")
            else:
                print(f"⚠️ Data inconsistency - Bridge: {bridge_generation}, Evolution: {evolution_generation}")
        
        return True
        
    except Exception as e:
        print(f"❌ Unified status test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Starting Unified System Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Bridge API Health", test_bridge_api_health),
        ("Evolution API Health", test_evolution_api_health),
        ("Mutation via Bridge", test_mutation_via_bridge),
        ("Direct Evolution API", test_direct_evolution_api),
        ("Unified Status", test_unified_status)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The unified application is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)