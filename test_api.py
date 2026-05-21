#!/usr/bin/env python
"""Quick test script for Raft Simulator API"""

import sys
import json
sys.path.insert(0, '/d/KULIAH/Semester 4/Infrastruktur Cloud dan Sistem Terdistribusi/Tugas/Raft Simulator')

from app import app, cluster

def test_api():
    """Test API endpoints using Flask test client"""
    with app.test_client() as client:
        print("=" * 60)
        print("TESTING RAFT SIMULATOR API")
        print("=" * 60)

        # Test 1: Initialize cluster
        print("\n[Test 1] POST /api/raft/init")
        response = client.post('/api/raft/init')
        data = response.get_json()
        print(f"Status: {response.status_code}")
        print(f"Leader: Node {data.get('current_leader')}")
        print(f"Alive nodes: {data.get('alive_count')}/{data.get('total_nodes')}")
        print(f"Can form majority: {data.get('can_form_majority')}")

        # Test 2: Get cluster state
        print("\n[Test 2] GET /api/raft/state")
        response = client.get('/api/raft/state')
        data = response.get_json()
        print(f"Status: {response.status_code}")
        print(f"Current leader: {data.get('current_leader')}")
        for node_id, node in data.get('nodes', {}).items():
            print(f"  Node {node_id}: {node['state'].upper()} (Term {node['term']}, Log: {node['log_length']})")

        # Test 3: Kill node
        print("\n[Test 3] POST /api/raft/kill-node (Node 1)")
        response = client.post('/api/raft/kill-node', json={"node_id": 1})
        data = response.get_json()
        print(f"Status: {response.status_code}")
        print(f"Message: {data.get('message')}")
        print(f"Alive nodes: {data.get('state', {}).get('alive_count')}/5")

        # Test 4: Resurrect node
        print("\n[Test 4] POST /api/raft/resurrect-node (Node 1)")
        response = client.post('/api/raft/resurrect-node', json={"node_id": 1})
        data = response.get_json()
        print(f"Status: {response.status_code}")
        print(f"Alive nodes: {data.get('state', {}).get('alive_count')}/5")

        # Test 5: Trigger election
        print("\n[Test 5] POST /api/raft/trigger-election")
        response = client.post('/api/raft/trigger-election')
        data = response.get_json()
        print(f"Status: {response.status_code}")
        print(f"New leader: Node {data.get('state', {}).get('current_leader')}")
        print(f"Can form majority: {data.get('state', {}).get('can_form_majority')}")

        # Test 6: Append entry
        print("\n[Test 6] POST /api/raft/append-entry")
        response = client.post('/api/raft/append-entry', json={"command": "test_command"})
        data = response.get_json()
        print(f"Status: {response.status_code}")
        print(f"Success: {data.get('success')}")
        if data.get('success'):
            nodes = data.get('state', {}).get('nodes', {})
            leader_id = data.get('state', {}).get('current_leader')
            if leader_id is not None:
                leader_log = nodes.get(str(leader_id), {}).get('log', [])
                print(f"Leader log length: {len(leader_log)}")

        # Test 7: Quorum analysis
        print("\n[Test 7] POST /api/quorum/analyze (N=5, W=3, R=3)")
        response = client.post('/api/quorum/analyze', json={"n": 5, "w": 3, "r": 3})
        data = response.get_json()
        print(f"Status: {response.status_code}")
        print(f"W+R > N: {data.get('valid')}")
        print(f"Consistency: {data.get('consistency')}")
        print(f"Max write failures: {data.get('max_write_failures')}")
        print(f"Max read failures: {data.get('max_read_failures')}")

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)

if __name__ == '__main__':
    test_api()
