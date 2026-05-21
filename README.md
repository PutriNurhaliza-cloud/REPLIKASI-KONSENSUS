# 🔗 Raft Simulator - Praktikum Interaktif

**Konsistensi, Replikasi, dan Algoritma Konsensus Terdistribusi**

Simulator interaktif untuk memahami konsep fundamental dalam sistem terdistribusi melalui 4 lab praktikum yang mengeksplorasi Raft consensus algorithm, CRDT, Two-Phase Commit, dan Quorum analysis.

---

## 📚 Tentang Praktikum

**Mata Kuliah:** Infrastruktur Cloud & Sistem Terdistribusi (Semester 4)

**Topik Utama:**
- Consistency Models (Linearizability → Eventual Consistency)
- Replication Strategies (Master-Slave, Multi-Master, Leaderless)
- Conflict Resolution (LWW, CRDT, Version Vectors)
- Consensus Algorithms (Paxos overview, Raft in depth)
- Distributed Transactions (2PC vs Saga Pattern)
- ACID vs BASE trade-offs
- Case Studies (Google Spanner, Amazon Aurora)

---

## 🎯 4 Lab Praktikum

### Lab 1: Raft Leader Election ✓ (Siap)
**URL:** `http://localhost:5000/lab1`

Amati mekanisme leader election dalam Raft dengan menggunakan simulator interaktif.

**Fitur:**
- Visualisasi cluster 5 nodes
- Kill/Resurrect nodes
- Trigger elections
- Append entries
- Real-time state table

**Lab Questions:**
1. Berapa minimum node harus aktif agar election bisa terjadi di cluster 5 node?
2. Apa yang terjadi jika leader crash di tengah Append Entries?
3. Mengapa Raft tidak memilih node dengan log terpendek sebagai leader?

**Jawaban Singkat:**
1. Minimum 3 nodes (majority dari 5)
2. Entry tidak akan di-commit jika tidak mendapat majority ACK
3. Raft memerlukan log yang "up-to-date" (melihat term dan index terbaru)

---

### Lab 2: CRDT G-Counter (Dalam Pengembangan)
**URL:** `http://localhost:5000/lab2`

Pelajari Conflict-free Replicated Data Type dan properti commutativity/idempotency.

**Fitur (akan datang):**
- G-Counter increment simulation
- PN-Counter (increment + decrement)
- Merge demonstration
- Version vector tracking

**Lab Questions:**
1. Mengapa G-Counter tidak bisa di-decrement?
2. Jelaskan commutativity: merge(A,B) = merge(B,A)
3. Sebutkan 2 aplikasi nyata CRDT di production

---

### Lab 3: 2PC vs Saga Pattern (Dalam Pengembangan)
**URL:** `http://localhost:5000/lab3`

Pahami blocking problem pada 2PC dan solusi non-blocking Saga.

**Fitur (akan datang):**
- 2PC phase visualization
- Coordinator crash simulation
- Saga compensation flow
- In-doubt transaction detection

**Lab Questions:**
1. Mengapa 2PC disebut "blocking protocol"?
2. Bagaimana 3PC mengatasi blocking?
3. Saga memiliki "ACD" tapi bukan "I" - apa implikasinya?

---

### Lab 4: Quorum Configuration Analysis ✓ (Siap)
**URL:** `http://localhost:5000/lab4`

Analisis trade-off consistency vs availability dengan berbagai konfigurasi quorum.

**Fitur:**
- Interactive quorum calculator (N, W, R)
- W+R > N validation
- Fault tolerance calculation
- CP vs AP classification

**Lab Questions:**
1. N=5, W=3, R=3: Verifikasi W+R>N, max failures?
2. N=5, W=1, R=5: Kapan berguna?
3. N=5, W=5, R=1: Implikasi untuk availability?

**Contoh Analisis:**

```
Konfigurasi    | W+R>N | Consistency | Use Case
N=5, W=3, R=3  | ✓ YES | Strong (CP) | Banking, Booking
N=5, W=2, R=2  | ✗ NO  | Weak (AP)   | Social Media, Cache
N=3, W=2, R=2  | ✓ YES | Strong      | Cassandra QUORUM
N=5, W=5, R=1  | ✗ NO  | Write-heavy | Availability first
N=5, W=1, R=5  | ✓ YES | Read-heavy  | Analytics, CDN
```

---

## 🚀 Setup & Instalasi

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Modern web browser

### Instalasi Step-by-Step

```bash
# 1. Clone/download project ke local
cd "d:\KULIAH\Semester 4\Infrastruktur Cloud dan Sistem Terdistribusi\Tugas\Raft Simulator"

# 2. Buat virtual environment (optional tapi recommended)
python -m venv venv

# 3. Aktifkan virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Jalankan Flask development server
python app.py
```

### Browser Access
Buka browser dan navigasi ke: **http://localhost:5000**

---

## 📖 Panduan Penggunaan Lab 1

### Langkah 1: Initialization
```
1. Klik "Initialize Cluster"
2. Sistem akan membuat 5 nodes dengan random leader election
3. Perhatikan mana node yang menjadi LEADER (warna hijau)
4. Lihat TERM di node leader
```

### Langkah 2: Observe Leader Election
```
1. Catat node ID leader
2. Lihat table - leader memiliki state "LEADER"
3. Follower memiliki state "FOLLOWER"
4. Semua node memiliki term yang sama
```

### Langkah 3: Kill Nodes
```
1. Klik pada node di diagram cluster (atau tombol "Kill" di table)
2. Node akan berubah warna menjadi abu-abu (dead)
3. Catat berapa banyak alive nodes di corner kanan atas
4. Coba kill 2 followers - apa yang terjadi?
```

### Langkah 4: Quorum Test
```
1. Kill terus sampai hanya 2 nodes yang hidup (3 mati)
2. Klik "Trigger Election" - apakah ada leader baru?
3. Bandingkan dengan: 5 nodes → majority = 3
   Jika hanya 2 alive, tidak bisa form majority!
```

### Langkah 5: Log Replication
```
1. Reset cluster dengan "Reset" button
2. Setelah ada leader, klik "Append Entry" 3 kali
3. Perhatikan log_length di table
4. Apakah semua nodes memiliki log_length yang sama?
5. Coba kill leader saat append - apakah replika menunggu commit?
```

---

## 🏗️ Project Structure

```
raft-simulator/
├── app.py                          # Flask main app
├── requirements.txt                # Python dependencies
├── test_api.py                     # API test suite
│
├── raft/                           # Raft consensus implementation
│   ├── __init__.py
│   ├── node.py                     # RaftNode class (persistent/volatile state)
│   ├── cluster.py                  # RaftCluster class (5-node simulation)
│   ├── state_machine.py            # (future) State machine implementation
│   └── messages.py                 # (future) RPC message types
│
├── crdt/                           # CRDT implementation
│   ├── __init__.py
│   ├── g_counter.py                # (future) G-Counter (grow-only)
│   ├── pn_counter.py               # (future) PN-Counter (inc+dec)
│   └── version_vector.py           # (future) Version vectors
│
├── transactions/                   # Distributed transaction implementation
│   ├── __init__.py
│   ├── two_phase_commit.py         # (future) 2PC coordinator & participant
│   └── saga.py                     # (future) Saga orchestrator
│
├── quorum/                         # Quorum analysis
│   ├── __init__.py
│   └── analysis.py                 # (future) Detailed analysis functions
│
├── static/                         # Frontend assets
│   ├── css/
│   │   └── style.css               # Global styling
│   └── js/
│       ├── raft-simulator.js       # Lab 1 interactive script
│       ├── crdt-simulator.js       # Lab 2 (future)
│       ├── 2pc-simulator.js        # Lab 3 (future)
│       └── quorum-simulator.js     # Lab 4 (future)
│
├── templates/                      # Jinja2 HTML templates
│   ├── index.html                  # Landing page
│   ├── lab1-raft.html              # Lab 1 UI
│   ├── lab2-crdt.html              # Lab 2 UI
│   ├── lab3-2pc.html               # Lab 3 UI
│   └── lab4-quorum.html            # Lab 4 UI
│
└── README.md                       # This file

```

---

## 🔌 API Endpoints

### Raft Simulation

```
POST   /api/raft/init                Initialize 5-node cluster
GET    /api/raft/state               Get current cluster state
POST   /api/raft/kill-node           Kill specific node (body: {node_id: int})
POST   /api/raft/resurrect-node      Resurrect killed node (body: {node_id: int})
POST   /api/raft/trigger-election    Force election cycle
POST   /api/raft/append-entry        Append entry to leader log
```

### CRDT (Future)

```
POST   /api/crdt/init                Initialize CRDT simulators
POST   /api/crdt/increment           Increment counter
POST   /api/crdt/sync                Merge states
GET    /api/crdt/state               Get counter states
```

### 2PC (Future)

```
POST   /api/2pc/init                 Initialize transaction
POST   /api/2pc/step                 Advance phase
POST   /api/2pc/simulate-abort       Simulate abort
POST   /api/2pc/simulate-failure     Simulate coordinator crash
GET    /api/2pc/state                Get transaction state
```

### Quorum Analysis

```
POST   /api/quorum/analyze           Analyze W, R, N config
```

---

## 📊 Contoh Skenario Lab 1

### Skenario 1: Basic Election
```
1. Init cluster → Node 2 jadi leader (Term 1)
2. Trigger election → Node 4 menang (Term 2)
3. Trigger lagi → Node 1 menang (Term 3)
→ Kesimpulan: Term selalu naik, berbeda leader tiap kali
```

### Skenario 2: Quorum Loss
```
1. Init cluster → 5 nodes, leader = Node 0
2. Kill Node 1, 2, 3 → 2 nodes alive (tidak majority)
3. Trigger election → Tidak ada leader dipilih!
→ Kesimpulan: Minimum majority (3/5) diperlukan
```

### Skenario 3: Log Replication
```
1. Init cluster → leader = Node 3
2. Append Entry 3x → leader log = [entry1, entry2, entry3]
3. Check followers → semua followers juga punya 3 entries
→ Kesimpulan: Replication otomatis ke semua followers
```

### Skenario 4: Leader Crash During Replication
```
1. Init cluster → leader = Node 2
2. Kill Node 1 (non-leader)
3. Append Entry → leader replikasi ke 3 followers
4. Kill leader (Node 2) → hanya 2 nodes alive
5. Trigger election → tidak ada leader (quorum lost)
→ Kesimpulan: Replication lag tolerance terbatas
```

---

## 🧪 Testing

### Run API Tests
```bash
python test_api.py
```

Menjalankan comprehensive API test suite covering:
- Initialization
- State queries
- Node kill/resurrect
- Election triggering
- Entry appending
- Quorum analysis

### Expected Output
```
============================================================
TESTING RAFT SIMULATOR API
============================================================

[Test 1] POST /api/raft/init
Status: 200
Leader: Node 0
Alive nodes: 5/5
...
============================================================
ALL TESTS COMPLETED SUCCESSFULLY
============================================================
```

---

## 📝 Technical Notes

### Raft Implementation Details

**NodeState Machine:**
```
FOLLOWER --[election timeout]--> CANDIDATE --[majority vote]--> LEADER
   ^                                 |                              |
   |<----------[higher term]---------|                              |
   |<------------------------[append entries from leader]----------+
```

**Persistent State** (pada disk/storage):
- `current_term`: Latest term server has seen
- `voted_for`: Candidate ID yang menerima vote di current term
- `log[]`: Array entries, masing-masing dengan term & command

**Volatile State** (setiap server):
- `commit_index`: Index of highest log entry known to be committed
- `last_applied`: Index of highest log entry applied to state machine

**Volatile State** (leader saja):
- `next_index[]`: Untuk setiap server, index of next log entry to send
- `match_index[]`: Untuk setiap server, index of highest log entry known to be replicated

### Election Logic
```python
1. Follower timeout (150-300ms) → becomes Candidate
2. Candidate increments term, votes untuk diri sendiri
3. Requests votes dari semua nodes
4. Node grant vote jika:
   - Candidate term >= node current term
   - Candidate log is at least as up-to-date
5. Jika candidate dapat mayoritas votes → LEADER
6. Jika receive append_entries dari leader → FOLLOWER
7. Jika receive higher term → FOLLOWER
```

### Quorum Majority
```
5 nodes → majority = 3
3 nodes → majority = 2
7 nodes → majority = 4
```

---

## 📚 Learning Resources

### Concepts yang Dijelajahi

1. **Consensus (Raft):**
   - Leader election dengan term-based voting
   - Log replication dengan majority ACK
   - Safety guarantees (election safety, log matching, leader completeness)

2. **Consistency Models:**
   - Linearizability (strongest)
   - Sequential, Causal
   - Read-your-writes
   - Eventual (weakest, high availability)

3. **Replication Strategies:**
   - Master-Slave: Simple, single point of failure untuk writes
   - Multi-Master: Geo-distributed, tapi conflict resolution kompleks
   - Leaderless: Dynamo-style quorum read/write

4. **Conflict Resolution:**
   - LWW (Last-Write-Wins): Sederhana tapi data loss silent
   - CRDT: Mathematically guaranteed merge
   - Version Vectors: Detect concurrent conflicts

5. **Distributed Transactions:**
   - 2PC: ACID penuh tapi blocking
   - Saga: Non-blocking tapi eventual consistency

6. **Trade-offs:**
   - CP vs AP classification
   - Consistency vs Availability vs Partition tolerance
   - Write vs Read latency

---

## 🐛 Troubleshooting

### Flask tidak start
```bash
# Port 5000 sudah terpakai?
python -m flask run --port 8000

# Atau buka port baru di app.py:
if __name__ == '__main__':
    app.run(debug=True, port=8000)
```

### No module named 'flask'
```bash
# Install lagi dependencies
pip install -r requirements.txt
```

### Browser shows "Cannot GET /lab1"
```bash
1. Ensure Flask server is running
2. Check URL: http://localhost:5000/lab1 (not /lab1/)
3. Check browser console for JavaScript errors
```

### Cluster state not updating
```bash
1. Klik "Initialize Cluster" dulu
2. Check browser console (F12) for CORS or fetch errors
3. Ensure backend server running (terminal shows Flask debug output)
```

---

## 🎓 Exam Preparation

### Important Concepts untuk Ujian

1. **Raft Leadership Election**
   - Minimum quorum untuk elect leader
   - Role of term in detecting stale leaders
   - Why log up-to-date check is necessary

2. **Log Replication**
   - When entry is considered committed
   - Majority ACK requirement
   - What happens when leader crashes

3. **CRDT Properties**
   - Commutativity: merge(A,B) = merge(B,A)
   - Idempotency: merge(A,A) = A
   - Associativity: merge(A, merge(B,C)) = merge(merge(A,B), C)

4. **Consistency Tradeoffs**
   - Strong consistency: Linearizability, Sequential
   - Eventual consistency: HIGH availability
   - Middle ground: Causal, Read-your-writes

5. **2PC vs Saga**
   - 2PC: Blocking, ACID, SPOF coordinator
   - Saga: Non-blocking, Eventual consistency, Compensating transactions

6. **Quorum Math**
   - W + R > N → strong read guaranteed (CP)
   - W + R ≤ N → weak read (AP)
   - Fault tolerance = N - W (write), N - R (read)

---

## 📝 Assignment Checklist

- [ ] Selesaikan Lab 1 dan jawab 3 pertanyaan
- [ ] Selesaikan Lab 4 dan jawab 7 pertanyaan
- [ ] Dokumentasikan 3 skenario Lab 1
- [ ] Analisis 4 konfigurasi quorum di Lab 4
- [ ] Submit laporan praktikum dengan screenshots
- [ ] Prepare untuk quiz/ujian dengan resources di section 🎓

---

## 📞 Support

Jika ada pertanyaan atau issues:
1. Check browser console (F12) untuk JavaScript errors
2. Check terminal Flask server untuk backend errors
3. Ensure Python version >= 3.8
4. Ensure all dependencies installed: `pip install -r requirements.txt`

---

## 🔄 Future Enhancements

- [ ] Lab 2 CRDT: Full G-Counter & PN-Counter implementation
- [ ] Lab 3 2PC: Interactive coordinator & participant flow
- [ ] Lab 3 Saga: Orchestration-based saga visualization
- [ ] Enhanced visualizations dengan SVG/Canvas
- [ ] Network simulation dengan packet loss/delay
- [ ] Persistence: Save/load cluster state
- [ ] Export to JSON: Simulasi results untuk dokumentasi

---

## 📖 References

1. Raft Consensus Algorithm: https://raft.github.io/
2. CRDT Papers: https://crdt.tech/
3. Designing Data-Intensive Applications (Martin Kleppmann)
4. Google Spanner: Becoming a SQL System
5. Amazon Aurora: Design Considerations for High Throughput Cloud-Native Relational Databases

---

## 📜 License

Educational Purpose - Materi Kuliah ITS

**Created:** 2024
**Status:** Active Development
**Version:** 1.0.0

---

**Happy Learning! 🚀**

Simulasi interaktif ini dirancang untuk memperdalam pemahaman tentang consensus algorithms, replikasi data, dan distributed systems. Setiap lab memberikan hands-on experience yang tidak bisa didapat dari teori saja.

