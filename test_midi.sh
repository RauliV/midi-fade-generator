#!/bin/bash
# Quick test script for MIDI generation

echo "=== Testing MIDI Generation ==="
echo "Testing Python3 with midiutil..."

cd "/Users/raulivirtanen/Documents/valot/midi-fade-generator-electron"

# Test data
TEST_DATA='{"scenes":[{"name":"quick_test","channels":{"1":127,"4":80},"fade_in_duration":2,"fade_out_duration":2,"steps":15}]}'

echo "Input data: $TEST_DATA"
echo ""
echo "Running Python backend..."

echo "$TEST_DATA" | python3 valot_python_backend.py

echo ""
echo "Checking generated files..."
ls -la quick_test_*.mid 2>/dev/null || echo "No MIDI files found"

echo ""
echo "=== Test Complete ==="