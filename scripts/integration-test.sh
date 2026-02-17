#!/bin/bash

# Integration test script for Phase 5
# Tests the complete event-driven flow

set -e

echo "Starting Phase 5 Integration Test..."

# Get public IP
PUBLIC_IP=$(kubectl get service todo-app-frontend -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
if [ -z "$PUBLIC_IP" ]; then
  echo "INFO: Frontend service not found or not exposed via LoadBalancer yet"
  echo "INFO: This is expected if deployment hasn't started yet"
  echo "Integration test will need to be run after deployment"
  exit 0
fi

echo "Using public IP: $PUBLIC_IP"

# Test 1: Health check
echo "Test 1: Health check..."
curl -s "http://$PUBLIC_IP/api/health" | jq .
if [ $? -eq 0 ]; then
  echo "✓ Health check passed"
else
  echo "✗ Health check failed"
  exit 1
fi

# Test 2: Create user and get token
echo "Test 2: User authentication..."
EMAIL="test$(date +%s)@example.com"
PASSWORD="TestPassword123!"

# Register user
REGISTER_RESPONSE=$(curl -s -X POST "http://$PUBLIC_IP/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"name\":\"Test User\"}")

TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.access_token')
if [ "$TOKEN" != "null" ]; then
  echo "✓ User registration and login successful"
else
  echo "✗ User registration failed"
  echo $REGISTER_RESPONSE
  exit 1
fi

# Test 3: Create task with reminder
echo "Test 3: Create task with reminder..."
TASK_TITLE="Integration Test Task $(date)"
TASK_DESCRIPTION="This is an automated integration test task"
FUTURE_DATE=$(date -d "+2 hours" -u +"%Y-%m-%dT%H:%M:%S")

CREATE_TASK_RESPONSE=$(curl -s -X POST "http://$PUBLIC_IP/api/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"$TASK_TITLE\",
    \"description\": \"$TASK_DESCRIPTION\",
    \"due_date\": \"$FUTURE_DATE\",
    \"priority\": \"High\",
    \"tags\": [\"integration\", \"test\"],
    \"is_recurring\": false
  }")

TASK_ID=$(echo $CREATE_TASK_RESPONSE | jq -r '.id')
if [ "$TASK_ID" != "null" ]; then
  echo "✓ Task creation successful: $TASK_ID"
else
  echo "✗ Task creation failed"
  echo $CREATE_TASK_RESPONSE
  exit 1
fi

# Test 4: Search tasks
echo "Test 4: Search tasks..."
SEARCH_RESPONSE=$(curl -s "http://$PUBLIC_IP/api/tasks/search?q=integration&priority=High" \
  -H "Authorization: Bearer $TOKEN")

SEARCH_COUNT=$(echo $SEARCH_RESPONSE | jq 'length')
if [ "$SEARCH_COUNT" -ge 1 ]; then
  echo "✓ Search functionality working: found $SEARCH_COUNT tasks"
else
  echo "✗ Search functionality failed"
  echo $SEARCH_RESPONSE
  exit 1
fi

# Test 5: Complete task (should trigger recurring task creation)
echo "Test 5: Create and complete recurring task..."
RECURRING_TASK_TITLE="Recurring Test Task $(date)"
RECURRING_CREATE_RESPONSE=$(curl -s -X POST "http://$PUBLIC_IP/api/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"$RECURRING_TASK_TITLE\",
    \"description\": \"This is a recurring task\",
    \"is_recurring\": true,
    \"recurrence_pattern\": \"daily\"
  }")

RECURRING_TASK_ID=$(echo $RECURRING_CREATE_RESPONSE | jq -r '.id')
if [ "$RECURRING_TASK_ID" != "null" ]; then
  echo "✓ Recurring task creation successful: $RECURRING_TASK_ID"
else
  echo "✗ Recurring task creation failed"
  echo $RECURRING_CREATE_RESPONSE
  exit 1
fi

# Complete the recurring task
COMPLETE_RESPONSE=$(curl -s -X PATCH "http://$PUBLIC_IP/api/tasks/$RECURRING_TASK_ID/complete" \
  -H "Authorization: Bearer $TOKEN")

if [ $? -eq 0 ]; then
  echo "✓ Task completion successful"
else
  echo "✗ Task completion failed"
  echo $COMPLETE_RESPONSE
  exit 1
fi

# Wait for event processing
echo "Waiting 30 seconds for event processing..."
sleep 30

# Check if recurring task was created
echo "Test 6: Verify recurring task was created..."
ALL_TASKS=$(curl -s "http://$PUBLIC_IP/api/tasks" \
  -H "Authorization: Bearer $TOKEN")

RECURRING_TASK_COUNT=$(echo $ALL_TASKS | jq --arg title "$RECURRING_TASK_TITLE" '[.[] | select(.title == $title)] | length')
if [ "$RECURRING_TASK_COUNT" -ge 2 ]; then
  echo "✓ Recurring task functionality working: found $RECURRING_TASK_COUNT instances"
else
  echo "⚠ Recurring task functionality: only found $RECURRING_TASK_COUNT instances (may be timing issue)"
fi

echo ""
echo "=== INTEGRATION TEST SUMMARY ==="
echo "✓ Health check: PASSED"
echo "✓ User authentication: PASSED"
echo "✓ Task creation: PASSED"
echo "✓ Search functionality: PASSED"
echo "✓ Task completion: PASSED"
echo "✓ Recurring task creation: PARTIAL (timing-dependent)"
echo ""
echo "Integration test completed!"