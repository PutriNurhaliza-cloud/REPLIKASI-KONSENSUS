from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from raft.cluster import RaftCluster
from crdt.simulator import CRDTSimulator
from transactions.two_phase_commit import TwoPCCoordinator
from transactions.saga import SagaTransaction
import json

app = Flask(__name__)
CORS(app)

# Global cluster instance
cluster = RaftCluster(5)

# Initialize cluster with random leader
cluster.run_election()

# Global CRDT simulator
crdt_sim = CRDTSimulator(3)

# Global 2PC and Saga coordinators
twopc_coordinator = TwoPCCoordinator(3)
saga_transaction = SagaTransaction(3)


@app.route('/')
def index():
    """Landing page."""
    return render_template('index.html')


@app.route('/lab1')
def lab1():
    """Lab 1: Raft Leader Election."""
    return render_template('lab1-raft.html')


@app.route('/lab2')
def lab2():
    """Lab 2: CRDT G-Counter."""
    return render_template('lab2-crdt.html')


@app.route('/lab3')
def lab3():
    """Lab 3: 2PC Failure Scenario."""
    return render_template('lab3-2pc.html')


@app.route('/lab4')
def lab4():
    """Lab 4: Quorum Configuration Analysis."""
    return render_template('lab4-quorum.html')


# ===== Raft API Routes =====

@app.route('/api/raft/init', methods=['POST'])
def raft_init():
    """Initialize Raft cluster with Node 3 as initial leader."""
    global cluster
    cluster = RaftCluster(5)

    # Force Node 3 to be leader (as per lab specification)
    node3 = cluster.nodes[3]
    node3.become_leader()
    cluster.current_leader = 3

    # Make all other nodes followers with same term
    for node_id in range(5):
        if node_id != 3:
            cluster.nodes[node_id].become_follower(node3.current_term)

    return jsonify(cluster.get_cluster_state())


@app.route('/api/raft/state', methods=['GET'])
def raft_state():
    """Get current cluster state."""
    cluster.simulate_step()
    return jsonify(cluster.get_cluster_state())


@app.route('/api/raft/kill-node', methods=['POST'])
def raft_kill_node():
    """Kill a specific node."""
    data = request.get_json()
    node_id = data.get('node_id')

    if cluster.kill_node(node_id):
        return jsonify({
            "success": True,
            "message": f"Node {node_id} killed",
            "state": cluster.get_cluster_state()
        })
    else:
        return jsonify({"success": False, "message": "Invalid node_id"}), 400


@app.route('/api/raft/resurrect-node', methods=['POST'])
def raft_resurrect_node():
    """Resurrect a specific node."""
    data = request.get_json()
    node_id = data.get('node_id')

    if cluster.resurrect_node(node_id):
        return jsonify({
            "success": True,
            "message": f"Node {node_id} resurrected",
            "state": cluster.get_cluster_state()
        })
    else:
        return jsonify({"success": False, "message": "Invalid node_id"}), 400


@app.route('/api/raft/trigger-election', methods=['POST'])
def raft_trigger_election():
    """Trigger an election."""
    for _ in range(100):  # Simulate multiple steps until election happens
        if cluster.run_election():
            break
        cluster.simulate_step()

    return jsonify({
        "success": True,
        "message": "Election triggered",
        "state": cluster.get_cluster_state()
    })


@app.route('/api/raft/append-entry', methods=['POST'])
def raft_append_entry():
    """Append an entry to the leader's log."""
    data = request.get_json()
    command = data.get('command', f'command_{cluster.simulation_time}')

    if cluster.append_entry(command):
        return jsonify({
            "success": True,
            "message": "Entry appended",
            "state": cluster.get_cluster_state()
        })
    else:
        return jsonify({
            "success": False,
            "message": "No leader available"
        }), 400


# ===== CRDT API Routes (Lab 2) =====

@app.route('/api/crdt/init', methods=['POST'])
def crdt_init():
    """Initialize CRDT simulators."""
    global crdt_sim
    crdt_sim = CRDTSimulator(3)
    return jsonify({
        "message": "CRDT initialized",
        "state": crdt_sim.get_state()
    })


@app.route('/api/crdt/state', methods=['GET'])
def crdt_state():
    """Get current CRDT simulator state."""
    return jsonify(crdt_sim.get_state())


@app.route('/api/crdt/increment', methods=['POST'])
def crdt_increment():
    """Increment G-Counter on a node."""
    data = request.get_json()
    node_id = data.get('node_id', 0)
    counter_type = data.get('counter_type', 'g_counter')

    result = crdt_sim.increment_node(node_id, counter_type)
    return jsonify(result)


@app.route('/api/crdt/decrement', methods=['POST'])
def crdt_decrement():
    """Decrement PN-Counter on a node."""
    data = request.get_json()
    node_id = data.get('node_id', 0)

    result = crdt_sim.decrement_node(node_id)
    return jsonify(result)


@app.route('/api/crdt/merge', methods=['POST'])
def crdt_merge():
    """Merge state from one node to another."""
    data = request.get_json()
    source_id = data.get('source_id', 0)
    target_id = data.get('target_id', 1)
    counter_type = data.get('counter_type', 'g_counter')

    result = crdt_sim.merge_nodes(source_id, target_id, counter_type)
    return jsonify(result)


@app.route('/api/crdt/reset', methods=['POST'])
def crdt_reset():
    """Reset CRDT simulator."""
    global crdt_sim
    crdt_sim = CRDTSimulator(3)
    return jsonify({
        "message": "CRDT reset",
        "state": crdt_sim.get_state()
    })


@app.route('/api/crdt/history', methods=['GET'])
def crdt_history():
    """Get merge history."""
    return jsonify({
        "history": crdt_sim.get_merge_history()
    })


# ===== 2PC API Routes (Lab 3) =====

@app.route('/api/2pc/init', methods=['POST'])
def twopc_init():
    """Initialize 2PC simulator."""
    global twopc_coordinator
    twopc_coordinator = TwoPCCoordinator(3)
    return jsonify({
        "message": "2PC initialized",
        "state": twopc_coordinator.get_state()
    })


@app.route('/api/2pc/state', methods=['GET'])
def twopc_state():
    """Get current 2PC state."""
    return jsonify(twopc_coordinator.get_state())


@app.route('/api/2pc/start', methods=['POST'])
def twopc_start():
    """Start 2PC transaction."""
    return jsonify(twopc_coordinator.start_transaction())


@app.route('/api/2pc/phase1', methods=['POST'])
def twopc_phase1():
    """Execute phase 1 (prepare)."""
    return jsonify(twopc_coordinator.phase1_prepare())


@app.route('/api/2pc/phase2-precommit', methods=['POST'])
def twopc_phase2_precommit():
    """Execute phase 2 (pre-commit) - 3PC mode."""
    return jsonify(twopc_coordinator.phase2_precommit())


@app.route('/api/2pc/phase3-commit', methods=['POST'])
def twopc_phase3_commit():
    """Execute phase 3 (commit) - 3PC mode."""
    return jsonify(twopc_coordinator.phase3_commit())


@app.route('/api/2pc/phase2-commit', methods=['POST'])
def twopc_phase2_commit():
    """Execute phase 2 (commit) - 2PC mode (skip pre-commit)."""
    return jsonify(twopc_coordinator.phase2_commit())


@app.route('/api/2pc/phase2-abort', methods=['POST'])
def twopc_phase2_abort():
    """Execute phase 2 (abort)."""
    return jsonify(twopc_coordinator.phase2_abort())


@app.route('/api/2pc/crash-coordinator', methods=['POST'])
def twopc_crash_coordinator():
    """Simulate coordinator crash."""
    return jsonify(twopc_coordinator.simulate_coordinator_crash())


@app.route('/api/2pc/fail-participant', methods=['POST'])
def twopc_fail_participant():
    """Simulate participant failure."""
    data = request.get_json()
    participant_id = data.get('participant_id', 0)
    return jsonify(twopc_coordinator.fail_participant(participant_id))


@app.route('/api/2pc/reset', methods=['POST'])
def twopc_reset():
    """Reset 2PC simulator."""
    global twopc_coordinator
    twopc_coordinator = TwoPCCoordinator(3)
    return jsonify({
        "message": "2PC reset",
        "state": twopc_coordinator.get_state()
    })


# ===== Saga API Routes (Lab 3) =====

@app.route('/api/saga/init', methods=['POST'])
def saga_init():
    """Initialize Saga simulator."""
    global saga_transaction
    saga_transaction = SagaTransaction(3)
    return jsonify({
        "message": "Saga initialized",
        "state": saga_transaction.get_state()
    })


@app.route('/api/saga/state', methods=['GET'])
def saga_state():
    """Get current Saga state."""
    return jsonify(saga_transaction.get_state())


@app.route('/api/saga/start', methods=['POST'])
def saga_start():
    """Start Saga transaction."""
    return jsonify(saga_transaction.start_saga())


@app.route('/api/saga/execute-all', methods=['POST'])
def saga_execute_all():
    """Execute all services in saga."""
    return jsonify(saga_transaction.execute_all_services())


@app.route('/api/saga/fail-service', methods=['POST'])
def saga_fail_service():
    """Simulate service failure."""
    data = request.get_json()
    service_id = data.get('service_id', 1)
    return jsonify(saga_transaction.fail_service(service_id))


@app.route('/api/saga/reset', methods=['POST'])
def saga_reset():
    """Reset Saga simulator."""
    global saga_transaction
    saga_transaction = SagaTransaction(3)
    return jsonify({
        "message": "Saga reset",
        "state": saga_transaction.get_state()
    })


@app.route('/api/saga/comparison', methods=['GET'])
def saga_comparison():
    """Get 2PC vs Saga comparison."""
    return jsonify(SagaTransaction.compare_with_2pc())


# ===== Quorum API Routes (Lab 4) =====

@app.route('/api/quorum/analyze', methods=['POST'])
def quorum_analyze():
    """Analyze quorum configuration."""
    data = request.get_json()
    n = data.get('n', 5)
    w = data.get('w', 3)
    r = data.get('r', 3)

    # Basic validation
    if w + r > n:
        is_valid = True
        consistency = "Strong (CP)"
    else:
        is_valid = False
        consistency = "Weak (AP)"

    max_write_failures = n - w
    max_read_failures = n - r

    return jsonify({
        "n": n,
        "w": w,
        "r": r,
        "valid": is_valid,
        "consistency": consistency,
        "max_write_failures": max_write_failures,
        "max_read_failures": max_read_failures,
        "overlap": "guaranteed" if is_valid else "not guaranteed"
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
