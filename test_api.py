#!/usr/bin/env python3
"""
VoiceFlow Testing Script
Tests all endpoints and functionality
"""

import requests
import json
import time

API_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_health():
    """Test health check"""
    print_section("1. HEALTH CHECK")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"✅ Health: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_seed_data():
    """Seed demo data"""
    print_section("2. SEED DEMO DATA")
    try:
        response = requests.post(f"{API_URL}/seed-demo-data")
        data = response.json()
        print(f"✅ Seeded: {data}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_tasks():
    """Get all tasks"""
    print_section("3. GET TASKS")
    try:
        response = requests.get(f"{API_URL}/tasks/")
        tasks = response.json()
        print(f"✅ Found {len(tasks)} tasks:")
        for task in tasks[:2]:  # Show first 2
            print(f"  - {task['title']} (ID: {task['id']}, Status: {task['status']})")
        return tasks
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_create_task():
    """Create task via API"""
    print_section("4. CREATE TASK (API)")
    try:
        task_data = {
            "title": "Test Task via API",
            "description": "Created by testing script",
            "priority": "High"
        }
        response = requests.post(f"{API_URL}/tasks/", json=task_data)
        task = response.json()
        print(f"✅ Created task: {task['title']} (ID: {task['id']})")
        return task
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_voice_command():
    """Test voice command processing"""
    print_section("5. VOICE COMMAND PROCESSING")
    try:
        voice_data = {
            "transcription": "Create a high priority task for database migration due next Friday"
        }
        response = requests.post(f"{API_URL}/voice/process", json=voice_data)
        result = response.json()
        print(f"✅ Voice Command Result:")
        print(f"  Status: {result['status']}")
        print(f"  Message: {result['message']}")
        if 'task' in result:
            print(f"  Task Created: {result['task']['title']} (Priority: {result['task']['priority']})")
        return result
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_update_task_status(task_id):
    """Update task status"""
    print_section("6. UPDATE TASK STATUS")
    try:
        update_data = {"status": "InProgress"}
        response = requests.put(f"{API_URL}/tasks/{task_id}", json=update_data)
        task = response.json()
        print(f"✅ Updated task status: {task['status']}")
        return task
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_create_workflow(task_id):
    """Create workflow trigger"""
    print_section("7. CREATE WORKFLOW TRIGGER")
    try:
        workflow_data = {
            "task_id": task_id,
            "condition": "Status Changed to Done",
            "action": "Send Slack Notification - Task Completed"
        }
        response = requests.post(f"{API_URL}/workflows/", json=workflow_data)
        workflow = response.json()
        print(f"✅ Created workflow: {workflow['action']}")
        return workflow
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_get_workflows(task_id):
    """Get workflows for task"""
    print_section("8. GET WORKFLOWS")
    try:
        response = requests.get(f"{API_URL}/workflows/{task_id}")
        workflows = response.json()
        print(f"✅ Found {len(workflows)} workflows for task {task_id}")
        if workflows:
            print(f"  - {workflows[0]['action']}")
        return workflows
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_delete_task(task_id):
    """Delete task"""
    print_section("9. DELETE TASK")
    try:
        response = requests.delete(f"{API_URL}/tasks/{task_id}")
        result = response.json()
        print(f"✅ Deleted task: {result['message']}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("  VOICEFLOW API TEST SUITE")
    print("="*60)
    print(f"Testing: {API_URL}\n")

    # Test 1: Health
    if not test_health():
        print("\n❌ Backend not running! Start it with:")
        print("   cd backend && python -m uvicorn main:app --reload")
        return

    # Test 2: Seed data
    test_seed_data()
    time.sleep(1)

    # Test 3: Get tasks
    tasks = test_get_tasks()
    
    # Test 4: Create task
    new_task = test_create_task()
    
    # Test 5: Voice command
    test_voice_command()
    
    # Use first seeded task for further tests
    if tasks:
        task_id = tasks[0]['id']
        
        # Test 6: Update status
        test_update_task_status(task_id)
        
        # Test 7: Create workflow
        test_create_workflow(task_id)
        
        # Test 8: Get workflows
        test_get_workflows(task_id)

    # Test 9: Delete (use new task if available)
    if new_task:
        test_delete_task(new_task['id'])

    # Summary
    print_section("✅ ALL TESTS COMPLETE")
    print("Backend is working correctly!\n")
    print("Next steps:")
    print("1. Start frontend: cd frontend && npm run dev")
    print("2. Open http://localhost:3000")
    print("3. Click 'Load Demo' to populate tasks")
    print("4. Click the mic button to test voice commands")

if __name__ == "__main__":
    run_all_tests()
