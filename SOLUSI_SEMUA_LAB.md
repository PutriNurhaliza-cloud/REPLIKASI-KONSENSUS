# Panduan Penyelesaian Semua Lab: Raft Simulator
**Infrastruktur Cloud & Sistem Terdistribusi - Semester 4**

---

## 📋 DAFTAR ISI
1. [Lab 1: Raft Leader Election](#lab-1-raft-leader-election)
2. [Lab 2: CRDT G-Counter](#lab-2-crdt-g-counter)
3. [Lab 3: 2PC vs Saga Pattern](#lab-3-2pc-vs-saga-pattern)
4. [Lab 4: Quorum Configuration Analysis](#lab-4-quorum-configuration-analysis)

---

# LAB 1: RAFT LEADER ELECTION

**URL:** `http://localhost:5000/lab1`

## Pertanyaan 1: Minimum Node untuk Election di Cluster 5 Node

### ❓ Pertanyaan
Berapa minimum node harus aktif agar election bisa terjadi di cluster 5 node?

### 📝 Jawaban
**Minimum 3 nodes dari 5 nodes (3/5 = 60%)**

### 📖 Penjelasan Lengkap

#### Konsep Quorum Majority
Dalam Raft consensus, untuk memilih leader diperlukan **majority** vote:
```
Majority = (Total Nodes / 2) + 1
Untuk 5 nodes: Majority = (5/2) + 1 = 2.5 + 1 = 3.5 → dibulatkan UP = 3 nodes
```

#### Mengapa Harus Majority?
- **Mencegah Split Brain:** Jika hanya 2 nodes yang hidup, tidak boleh ada 2 leader terpisah
- **Konsistensi:** Hanya 1 partition dengan majority yang bisa progress
- **Fault Tolerance:** Bisa toleransi sampai N-M = 5-3 = 2 nodes down

#### Skenario Pengujian di Lab 1

**Langkah 1: Initialize Cluster**
```
1. Buka http://localhost:5000/lab1
2. Klik tombol "Initialize Cluster"
3. Lihat 5 nodes dengan 1 leader (warna hijau), 4 followers (warna biru)
4. Catat Leader ID dan Term
```

**Langkah 2: Kill 2 Nodes (masih punya majority)**
```
1. Klik pada node ID untuk "kill" → node berubah warna abu-abu
2. Kill node 1 dan node 2
3. Status: 3 nodes hidup (leader + 2 followers)
4. Hasil: Cluster masih bisa berjalan normal
```

**Langkah 3: Kill 1 Node Lagi (hilang majority)**
```
1. Kill 1 node lagi → hanya 2 nodes yang hidup
2. Klik tombol "Trigger Election"
3. Hasil: TIDAK ADA LEADER BARU yang terpilih
4. System FROZEN - menunggu minimal 1 node lagi hidup
```

**Langkah 4: Resurrect Node (kembali punya majority)**
```
1. Klik tombol "Resurrect" pada node yang mati
2. Cluster kembali punya 3 nodes yang hidup
3. Klik "Trigger Election" → leader baru terpilih
```

#### Tabel Fault Tolerance

| Total Nodes | Majority | Max Down | Contoh Skenario |
|-------------|----------|----------|-----------------|
| 3          | 2        | 1        | Online: 2 nodes → Election OK |
| 5          | 3        | 2        | Online: 3 nodes → Election OK |
| 7          | 4        | 3        | Online: 4 nodes → Election OK |
| 1          | 1        | 0        | Solo node = leader (partition) |

#### Kesimpulan
```
✓ 3 nodes → Majority tercapai → Leader bisa dipilih
✗ 2 nodes → Minority → No election possible
✓ Raft lebih konservative daripada simple majority voting
```

---

## Pertanyaan 2: Apa Terjadi jika Leader Crash saat Append Entries?

### ❓ Pertanyaan
Apa yang terjadi jika leader crash di tengah Append Entries?

### 📝 Jawaban
**Entry tidak akan di-commit jika tidak mendapat majority ACK. Followers tetap menyimpan entry tapi belum apply.**

### 📖 Penjelasan Lengkap

#### State Machine Entry Lifecycle

```
┌─────────────────────────────────────────────────────┐
│ CLIENT REQUEST (Write operation)                     │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────┐
    │ LEADER receives entry      │
    │ - Add to leader log        │
    │ - Send to all followers    │
    └────────────┬───────────────┘
                 │
       ┌─────────┴─────────┬──────────────┐
       │                   │              │
       ▼                   ▼              ▼
    Follower1         Follower2      Follower3
    Append OK         Append OK      [CRASH]
       │                 │
       └─────────────────┼──────────────────┐
                         │                  │
                    ┌────▼──────────┐       │
                    │ Majority ACK  │       │ Still waiting
                    │ (2/3 respond)  │       │ for response
                    └────┬──────────┘       │
                         │                  │
        ┌────────────────▼──────────────────┴────────┐
        │ Entry COMMITTED                            │
        │ - Safe to serve to clients                 │
        │ - Can be applied to state machine          │
        │ - Follower3 akan catch-up saat recovery    │
        └────────────────────────────────────────────┘
```

#### Skenario Pengujian

**Setup:**
```
1. Initialize cluster → 5 nodes, leader = Node 3
2. Lihat state: Node 3 adalah leader
```

**Langkah 1: Normal Append (semua hidup)**
```
1. Klik "Append Entry" 3 kali
2. Perhatikan di table:
   - Leader: log_length = 3
   - Followers: log_length = 3
3. Semua nodes punya log yang sama → Entries COMMITTED
```

**Langkah 2: Kill follower, append entry**
```
1. Kill Node 1 (non-leader)
2. Klik "Append Entry"
3. Leader masih bisa append karena punya majority (2 dari 4 yang hidup)
4. Followers lain: log_length += 1
5. Node 1 (mati): log_length tetap lama
```

**Langkah 3: Kill leader saat append (crash mid-way)**
```
1. Kill Node 3 (leader) segera setelah klik "Append Entry"
2. Yang terjadi:
   - Entry belum disebar ke semua followers
   - Entry di leader log tapi belum majority ACK
   - Follower yang terima entry menyimpannya
   - Leader baru terpilih
3. Entry yang belum di-commit akan:
   - Di-DISCARD oleh follower jika tidak diperlukan
   - Tidak akan diaplikasi ke state machine
   - Hilang selamanya (data loss jika tidak replicated)
```

#### Kondisi Entry COMMITTED

Entry baru bisa di-commit jika:
```python
if (ACK_count >= MAJORITY) and (Entry in leader log):
    commit_index = entry_index
    # Sekarang aman untuk serve ke client
    # Aman untuk apply ke state machine
```

#### Apa yang Aman vs Tidak Aman

| Status | Aman? | Alasan |
|--------|-------|--------|
| Entry di leader log saja | ❌ NO | Bisa hilang jika leader crash |
| Entry di leader + 1 follower | ❌ NO | Kurang dari majority |
| Entry di leader + 2 followers (3/5) | ✅ YES | Majority tercapai |
| Entry sudah committed | ✅ YES | Guaranteed tidak hilang |

#### Kesimpulan
```
✓ Leader crash SEBELUM majority ACK → Entry LOST
✓ Leader crash SESUDAH majority ACK → Entry SAFE (akan di-replicate)
✓ Majority requirement menjamin durability
```

---

## Pertanyaan 3: Mengapa Raft Tidak Pilih Node dengan Log Terpendek sebagai Leader?

### ❓ Pertanyaan
Mengapa Raft tidak memilih node dengan log terpendek sebagai leader?

### 📝 Jawaban
**Karena node dengan log terpendek mungkin tidak punya entries yang sudah di-commit. Raft memerlukan log yang "up-to-date" (melihat term dan index terbaru) untuk menjamin safety.**

### 📖 Penjelasan Lengkap

#### Candidate Election Safety Check

Ketika node menjadi candidate dan request vote, setiap node checker:

```python
def grant_vote(candidate):
    # Voter memeriksa: apakah candidate's log lebih up-to-date?
    
    if candidate.last_term < self.last_term:
        return False  # Candidate log KETINGGALAN
    
    if candidate.last_term == self.last_term:
        if candidate.last_index < self.last_index:
            return False  # Candidate log lebih PENDEK
    
    # Jika sampai sini, candidate log UP-TO-DATE
    return True
```

#### Definisi "Up-to-date"

Log A lebih up-to-date dari log B jika:
```
1. A.last_term > B.last_term, ATAU
2. A.last_term == B.last_term DAN A.last_index > B.last_index
```

#### Contoh Skenario

**Setup: 5 nodes dengan berbagai log states**

```
Node 0: log = [e1, e2, e3, e4, e5] ← LONGEST
        term = 5
        last_index = 5

Node 1: log = [e1, e2, e3, e4]
        term = 5
        last_index = 4

Node 2: log = [e1, e2, e3]       ← SHORTEST
        term = 5
        last_index = 3

Node 3: log = [e1, e2, e3, e4, e5]
        term = 4                 ← STALE TERM
        last_index = 5

Node 4: log = [e1, e2, e3, e4, e5]
        term = 5
        last_index = 5
```

**Skenario: Siapa yang bisa jadi leader?**

```
Candidate Scenarios:
────────────────────────────────────────────────────────

Scenario A: Node 2 (SHORTEST log) menjadi candidate
   ┌─────────────────────────────────────────┐
   │ Node 2 request vote dengan:             │
   │ - last_term = 5                         │
   │ - last_index = 3 (PENDEK)               │
   └─────────────────────────────────────────┘
   
   Node 0 menerima request:
   - Node 0 punya: last_index = 5
   - Node 2 punya: last_index = 3
   - REJECT ❌ (Node 2 log lebih pendek)
   
   Node 1 menerima request:
   - Node 1 punya: last_index = 4
   - Node 2 punya: last_index = 3
   - REJECT ❌ (Node 2 log lebih pendek)
   
   Result: Node 2 TIDAK BISA JADI LEADER
           (Votes tidak sampai majority)

────────────────────────────────────────────────────────

Scenario B: Node 0 (LONGEST log) menjadi candidate
   ┌─────────────────────────────────────────┐
   │ Node 0 request vote dengan:             │
   │ - last_term = 5                         │
   │ - last_index = 5 (PANJANG)              │
   └─────────────────────────────────────────┘
   
   Node 1 menerima request:
   - Node 1 punya: last_index = 4
   - Node 0 punya: last_index = 5 ✓
   - GRANT ✅
   
   Node 2 menerima request:
   - Node 2 punya: last_index = 3
   - Node 0 punya: last_index = 5 ✓
   - GRANT ✅
   
   Result: Node 0 BISA JADI LEADER ✅
           (Votes mencapai majority)

────────────────────────────────────────────────────────

Scenario C: Node 3 (STALE term) menjadi candidate
   ┌─────────────────────────────────────────┐
   │ Node 3 request vote dengan:             │
   │ - last_term = 4 (OUTDATED)              │
   │ - last_index = 5                        │
   └─────────────────────────────────────────┘
   
   Node 0 menerima request:
   - Node 0 punya: last_term = 5
   - Node 3 punya: last_term = 4 ✗
   - REJECT ❌ (Node 3 term lebih lama)
   
   Result: Node 3 TIDAK BISA JADI LEADER ❌
           (last_term lebih rendah = outdated)
```

#### Mengapa Ini Penting?

**Safety Guarantee (Leader Completeness):**
```
"Jika entry sudah di-commit di term sebelumnya,
entry tersebut HARUS ada di log leader baru di term saat ini"

Proof:
- Entry di-commit = ada di majority nodes
- Node baru yang jadi leader = minimal punya log dari majority
- Oleh karena itu, entry tersebut PASTI ada di leader baru
```

#### Skenario Pengujian di Lab 1

**Langkah 1: Perhatikan log state saat initialize**
```
1. Buka Lab 1, klik "Initialize Cluster"
2. Lihat table: kolom "log_length" untuk setiap node
3. Seharusnya semua node punya log_length yang sama (semua 0 atau sama)
```

**Langkah 2: Append entry, trigger election**
```
1. Klik "Append Entry" 2 kali
2. Lihat log_length: leader = 2, followers = 2 (replicated)
3. Klik "Trigger Election"
4. Perhatikan mana node yang jadi leader baru
5. Leader baru HARUS punya log_length >= followers lain
```

**Langkah 3: Simulate stale leader**
```
1. Append entry 3 kali
2. Kill 1 follower (akan ketinggalan entry berikutnya)
3. Append entry 2 kali lagi
4. Resurrect follower yang mati tadi
5. Perhatikan: Follower akan catch-up dengan leader
6. Entry yang hilang akan di-replicate kembali
```

#### Kesimpulan

```
WHY Raft tidak pilih shortest log:
════════════════════════════════════════════════════════

✓ Committed entries HARUS preserve di leader baru
✓ Voter isi up-to-date check menjamin invariant ini
✓ Node dengan log terpendek = kemungkinan besar missing committed entries
✓ Hanya node dengan log up-to-date bisa jadi leader

Analogi:
- Log panjang = "saya sudah lihat term terbaru"
- Log pendek = "saya ketinggalan berita, tidak eligible"
```

---

# LAB 2: CRDT G-COUNTER

**URL:** `http://localhost:5000/lab2`

## Pertanyaan 1: Mengapa G-Counter Tidak Bisa Di-decrement?

### ❓ Pertanyaan
Mengapa G-Counter tidak bisa di-decrement? Bagaimana PN-Counter mengatasinya?

### 📝 Jawaban
**G-Counter grow-only karena setiap node maintain counter sendiri dan hanya bisa increment. Untuk decrement, gunakan PN-Counter yang terdiri dari 2 G-Counters (positive & negative).**

### 📖 Penjelasan Lengkap

#### Struktur G-Counter

```
G-Counter = [c_node0, c_node1, c_node2, ...]

Contoh: 3 nodes
Initial:  [0, 0, 0]

Node 0 increment:
Result:   [1, 0, 0]

Node 1 increment 2x:
Result:   [1, 2, 0]

Value = sum([1, 2, 0]) = 3
```

#### Mengapa Tidak Bisa Decrement?

**Alasan Fundamental:**
```
1. Setiap node hanya track COUNTER SENDIRI
2. Tidak boleh negative (tidak masuk akal physically)
3. Hanya bisa increment (grow)

Jika dicoba decrement:
[2, 1, 0] -1 → [2, 0, 0]?
                atau [1, 1, 0]?
                
AMBIGUOUS! Tidak tahu node mana yang decrement
Juga melanggar CRDT property: harus commutative
```

#### Masalah Decrement pada CRDT

**Skenario Masalah:**

```
Node A state: [2, 0]  → value = 2
Node B state: [0, 3]  → value = 3

Merge:      [max(2,0), max(0,3)] = [2, 3] → value = 5

Kalau ada decrement:
Node A: [2, 0] - 1 = ???
Node B: [0, 3] - 1 = ???

Opsi 1 - Decrement dari own counter:
  Node A: [1, 0]
  Node B: [0, 2]
  Merge: [1, 2] = 3
  
Opsi 2 - Decrement dari sum:
  Node A: [1, 0]  (kurangin 1 dari Node A)
  Node B: [0, 3]  (Node B belum decrement)
  Merge: [1, 3] = 4
  
BERBEDA! Hasil merge tidak konsisten
      → Violation of merge property!
```

#### Solusi: PN-Counter (Positive-Negative Counter)

**Ide:** Pakai 2 G-Counter terpisah
```
PN-Counter = (G-Counter positive, G-Counter negative)
Value = positive.sum() - negative.sum()

Positive P = [p0, p1, p2]
Negative N = [n0, n1, n2]
Value = sum(P) - sum(N)
```

**Contoh Operasi:**

```
Initial PN-Counter:
  P = [0, 0, 0] → sum = 0
  N = [0, 0, 0] → sum = 0
  Value = 0 - 0 = 0

Operation 1: Node 0 increment
  P = [1, 0, 0] → sum = 1
  N = [0, 0, 0] → sum = 0
  Value = 1 - 0 = 1 ✓

Operation 2: Node 1 increment 2x
  P = [1, 2, 0] → sum = 3
  N = [0, 0, 0] → sum = 0
  Value = 3 - 0 = 3 ✓

Operation 3: Node 2 DECREMENT 2x
  P = [1, 2, 0] → sum = 3
  N = [0, 0, 2] → sum = 2  (increment negative counter)
  Value = 3 - 2 = 1 ✓

Merge dengan Node A:
  Node A: P_a=[2,0,0], N_a=[0,0,0]
  Node B: P_b=[1,2,0], N_b=[0,0,2]
  
  Merge P: [max(2,1), max(0,2), max(0,0)] = [2, 2, 0] → sum = 4
  Merge N: [max(0,0), max(0,0), max(0,2)] = [0, 0, 2] → sum = 2
  Value = 4 - 2 = 2 ✓ (CONSISTENT!)
```

#### Langkah-langkah di Lab 2

**Tab 1: G-Counter (Grow-Only)**
```
1. Buka http://localhost:5000/lab2
2. Klik tab "G-Counter" (default)
3. Lihat 3 nodes: A, B, C dengan state counter sendiri
```

**Langkah 1: Increment dan lihat state**
```
1. Klik "+1 Node A" → State menjadi [1, 0, 0]
2. Klik "+1 Node B" 2x → State menjadi [1, 2, 0]
3. Klik "+1 Node C" → State menjadi [1, 2, 1]
4. Perhatikan: Hanya bisa increment, tidak ada tombol minus
```

**Langkah 2: Merge dan lihat commutativity**
```
1. Sebelum merge, catat state:
   Node A: [1, 2, 1]
   Node B: [1, 2, 1]
   Node C: [1, 2, 1]
   Value semua = 4

2. Klik "Merge A→B":
   Hasilnya: max([1,2,1], [1,2,1]) = [1, 2, 1] (tidak berubah karena sudah sama)

3. Lakukan increment lagi:
   Node A: +1 → [2, 2, 1] = 5
   Node B: +1 → [1, 3, 1] = 5
   
4. Klik "Merge A→B":
   Result: [max(2,1), max(2,3), max(1,1)] = [2, 3, 1] = 6

5. Klik "Merge B→A" (reverse):
   Result: [max(2,1), max(3,2), max(1,1)] = [2, 3, 1] = 6
   
   SAMA! Ini adalah commutativity
```

**Tab 2: PN-Counter (dengan Decrement)**
```
1. Klik tab "PN-Counter"
2. Sekarang ada tombol "+1" DAN "-1" untuk setiap node
3. Lihat state: 2 array (positive & negative)
```

**Langkah 3: PN-Counter dengan decrement**
```
1. Klik "+1 Node A" 3x:
   Positive = [3, 0, 0]
   Negative = [0, 0, 0]
   Value = 3 - 0 = 3

2. Klik "-1 Node B" 2x:
   Positive = [3, 0, 0]
   Negative = [0, 2, 0]
   Value = 3 - 2 = 1

3. Klik "+1 Node C":
   Positive = [3, 0, 1]
   Negative = [0, 2, 0]
   Value = 4 - 2 = 2

4. Klik "Merge A→B":
   Merge positive:  [max(3,3), max(0,0), max(0,1)] = [3, 0, 1]
   Merge negative:  [max(0,0), max(0,2), max(0,0)] = [0, 2, 0]
   Value = 4 - 2 = 2 ✓
```

#### Perbandingan G-Counter vs PN-Counter

| Aspek | G-Counter | PN-Counter |
|-------|-----------|-----------|
| Operasi | Increment saja | Increment + Decrement |
| Struktur | 1 array | 2 array (P & N) |
| Space | O(n) | O(2n) |
| Commutativity | Ya | Ya |
| Use Case | Hit counter, likes | Bank balance, temp control |

#### Kesimpulan

```
WHY G-Counter tidak bisa decrement:
═══════════════════════════════════════════════════════

✓ Setiap node maintain counter sendiri
✓ Decrement tidak commutative pada single counter
✓ Merge menjadi ambiguous

SOLUSI PN-Counter:
✓ Pisah menjadi positive dan negative counters
✓ Setiap operasi di counter sendiri (grow-only)
✓ Merge tetap commutative
✓ Value = positive - negative

ANALOGI: G-Counter = odometer (hanya bisa naik)
        PN-Counter = bank account (bisa naik dan turun)
```

---

## Pertanyaan 2: Jelaskan Commutativity - Mengapa Penting?

### ❓ Pertanyaan
Jelaskan commutativity: merge(A,B) = merge(B,A). Mengapa penting untuk distributed systems?

### 📝 Jawaban
**Commutativity berarti urutan merge tidak penting - hasil akhir sama. Ini penting karena di distributed systems, network tidak menjamin urutan message.**

### 📖 Penjelasan Lengkap

#### Definisi Commutativity pada CRDT

```
Operasi ⊕ (merge) adalah commutative jika:
  a ⊕ b = b ⊕ a

Untuk CRDT:
  merge(state_A, state_B) = merge(state_B, state_A)
```

#### Skenario: Mengapa Urutan Bisa Berbeda

**Setup 3 nodes yang tidak saling berhubungan:**

```
Node A state: [1, 0, 0] (increment locally)
Node B state: [0, 1, 0] (increment locally)
Node C state: [0, 0, 0] (belum dapat update)

Network topology:
    A ←→ B
    ↓   ↓
    └─→ C

Kemungkinan 1: A update dulu, B menyusul
    C terima dari A:  [1, 0, 0]
    C terima dari B:  [0, 1, 0]
    Merge(A, B):      [1, 1, 0] = 2

Kemungkinan 2: B update dulu, A menyusul
    C terima dari B:  [0, 1, 0]
    C terima dari A:  [1, 0, 0]
    Merge(B, A):      [1, 1, 0] = 2

SAMA! Urutan tidak penting.
```

#### Contoh: Sistem TIDAK Commutative (Masalah)

**Operasi LWW (Last-Write-Wins) - NOT Commutative:**

```
Initial state: value = 10

Update 1: "SET value=20" at t=100ms
Update 2: "SET value=30" at t=200ms

Skenario A: Apply Update 1, then Update 2
    value = 20 (setelah Update 1)
    value = 30 (setelah Update 2)
    Final: 30 ✓

Skenario B: Apply Update 2, then Update 1 (network delay)
    value = 30 (setelah Update 2)
    value = 20 (setelah Update 1, timestamp lebih lama)
    Final: 20 ✗

BERBEDA! LWW tidak commutative
→ Diperlukan global clock untuk consistency
```

#### Mengapa Commutativity Penting di Distributed Systems

**Problem 1: Network Latency Tidak Predictable**

```
Scenario: Bank transfer $100 dari A ke B

Coordinator A: append [transfer: A→B, +100]
Coordinator B: append [transfer: A→B, +100]

Jika network delay berbeda:
  Replica 1: dapat A update dulu, B update kedua → +200
  Replica 2: dapat B update dulu, A update kedua → +200
  Replica 3: hanya dapat 1 update → +100

ISSUE: Berbeda state di replicas! 
       Tapi jika commutative, eventually consistent.
```

**Problem 2: Partition Tolerance (Network Split)**

```
Network split ke 2 partitions:

Partition 1 (A, B):
  - A increment: [1, 0]
  - B increment: [1, 1] (A replicate ke B)
  - B state: [1, 1]

Partition 2 (C):
  - C increment: [0, 0, 1]
  - C state: [0, 0, 1]

Network heal, C join lagi:
  Merge([1, 1, 0], [0, 0, 1]):
    = [max(1,0), max(1,0), max(0,1)]
    = [1, 1, 1]
    
  vs Merge reverse order:
    = [max(0,1), max(0,1), max(1,0)]
    = [1, 1, 1]
    
  SAMA! Partition order tidak penting.
```

**Problem 3: Concurrent Writes**

```
Concurrent operations (happened at same time):
  Operation 1: A++
  Operation 2: B++

Possible execution order:
  Path 1: [A++, then B++]
  Path 2: [B++, then A++]
  Path 3: [A++ || B++ (parallel)]
  
Jika commutative:
  All paths → [1, 1] (SAME RESULT)
  
Jika tidak:
  Paths bisa menghasilkan berbeda
  → Race condition, data corruption
```

#### Langkah-langkah Test Commutativity di Lab 2

**Skenario 1: Test merge commutativity (A,B) = (B,A)**

```
Setup:
1. Buka Lab 2, pastikan tab G-Counter
2. Klik "Initialize" (jika belum)
```

**Langkah 1: Create different states**
```
1. Klik "+1 Node A" 3x → A=[3, 0, 0]
2. Klik "+1 Node B" 2x → B=[0, 2, 0]
3. Klik "+1 Node C" 1x → C=[0, 0, 1]

State sebelum merge:
  A: [3, 0, 0] = 3
  B: [0, 2, 0] = 2
  C: [0, 0, 1] = 1
```

**Langkah 2: Merge A→B, record result**
```
1. Catat state awal:
   A: [3, 0, 0]
   B: [0, 2, 0]
   
2. Klik "Merge A→B":
   Expected B: [max(3,0), max(0,2), max(0,0)] = [3, 2, 0] = 5
   
3. Catat hasil: B=[3, 2, 0]
```

**Langkah 3: Reset dan merge B→A (reverse order)**
```
1. Klik "Reset"
2. Buat state yang sama:
   - Klik "+1 Node A" 3x → A=[3, 0, 0]
   - Klik "+1 Node B" 2x → B=[0, 2, 0]
   - Klik "+1 Node C" 1x → C=[0, 0, 1]
   
3. Klik "Merge B→A":
   Expected A: [max(0,3), max(2,0), max(0,0)] = [3, 2, 0] = 5
   
4. Bandingkan hasil: SAMA dengan A→B ✓
```

**Skenario 2: Associativity - (A ⊕ B) ⊕ C = A ⊕ (B ⊕ C)**

```
Setup:
  A = [1, 0, 0]
  B = [0, 1, 0]
  C = [0, 0, 1]

Path 1: Merge A,B first then C
  Step 1: Merge(A, B) = [1, 1, 0]
  Step 2: Merge([1,1,0], C) = [1, 1, 1]
  Result: [1, 1, 1] = 3

Path 2: Merge B,C first then A
  Step 1: Merge(B, C) = [0, 1, 1]
  Step 2: Merge(A, [0,1,1]) = [1, 1, 1]
  Result: [1, 1, 1] = 3

SAMA! Associativity holds.
```

#### Sifat-sifat CRDT (Merge Properties)

| Sifat | Formula | Contoh |
|-------|---------|--------|
| Commutativity | a⊕b = b⊕a | [1,0]⊕[0,1] = [0,1]⊕[1,0] = [1,1] |
| Associativity | (a⊕b)⊕c = a⊕(b⊕c) | Merge order tidak penting |
| Idempotency | a⊕a = a | [1,0]⊕[1,0] = [1,0] |

#### Analogi Dunia Nyata

```
Commutativity di real world:

Contoh 1: Memasak (ORDER matters, NOT commutative)
  ❌ Fry then add water ≠ Add water then fry
  → Fire + water = disaster
  
Contoh 2: Menggabung playlist musik (ORDER doesn't matter, IS commutative)
  ✓ [Playlist A merge Playlist B] = [Playlist B merge Playlist A]
  ✓ Same songs, possibly different order, but same set
  
Contoh 3: Voting/polling (COMMUTATIVE)
  ✓ Vote counted in any order = same total
  
Contoh 4: Banking (MUST BE COMMUTATIVE)
  ✓ Withdraw then deposit = deposit then withdraw (amount wise)
```

#### Kesimpulan

```
WHY Commutativity penting:
════════════════════════════════════════════════════════

✓ Network latency tidak predictable
✓ Network bisa reorder messages
✓ Partitions bisa terjadi
✓ Concurrent writes bisa happen

TANPA Commutativity:
  → Berbeda state di replicas
  → Inconsistency
  → Data corruption

DENGAN Commutativity:
  → Same result regardless of order
  → Eventual consistency guaranteed
  → Safe for distributed systems
```

---

## Pertanyaan 3: Sebutkan 2 Aplikasi CRDT di Production

### ❓ Pertanyaan
Sebutkan 2 aplikasi nyata CRDT di production.

### 📝 Jawaban
**1. Apple Notes (untuk sync across devices)**
**2. VS Code Collaborative Editing (untuk real-time co-editing)**

### 📖 Penjelasan Lengkap

#### Aplikasi 1: Apple Notes

**Requirement:**
```
- User punya iPhone, iPad, Mac
- Edit note di iPhone
- Open same note di Mac → otomatis ter-update
- Offline edits → sync when online
- Tidak boleh ada "conflict", harus merge automatik
```

**Mengapa CRDT diperlukan:**

```
Scenario: Edit yang concurrent

Mac user: Edit "Buy milk" → "Buy milk & eggs"
iPhone user: Edit "Buy milk" → "Buy milk at Whole Foods"

Tanpa CRDT (LWW - Last-Write-Wins):
  Result: Hanya 1 change terlihat (yang terakhir)
  Data loss! iPhone edit hilang atau vice versa

Dengan CRDT (Apple menggunakan CRDT variant):
  Merge kedua edits:
  "Buy milk & eggs at Whole Foods"
  
  Atau jika conflict:
  Show both: "Buy milk & eggs" | "Buy milk at Whole Foods"
  User pilih atau merge manually
```

**Implementasi:**
```
- Apple Documents use CRDT for Text
- iCloud sync = CRDT merge di backend
- Each device punya replica
- Changes merge otomatis
```

**Keuntungan:**
```
✓ No server required for merge
✓ Offline-first (edit tanpa internet)
✓ No conflicts (atau visible conflicts)
✓ Fast sync (merge local, kirim delta)
```

#### Aplikasi 2: VS Code Live Share (Collaborative Editing)

**Requirement:**
```
- Multiple developers edit same file
- Real-time updates (< 100ms latency)
- No locks/pessimistic locking
- Handle concurrent edits at same position
- Maintain code correctness (no garbage)
```

**Mengapa CRDT diperlukan:**

```
Scenario: Concurrent insertion at same position

Developer A at 10:00:00.100 inserts "foo" at line 5, char 10
Developer B at 10:00:00.101 inserts "bar" at line 5, char 10

Tanpa CRDT:
  A's view:   "foo bar"     (A insert dulu)
  B's view:   "bar foo"     (B insert dulu)
  
  Conflict! Merge hasil berbeda

Dengan CRDT (VS Code menggunakan Operational Transformation variant):
  Both use unique site ID:
  A: [5, 10, "foo", siteID_A]
  B: [5, 10, "bar", siteID_B]
  
  Final: "foo bar" atau "bar foo" tapi CONSISTENT everywhere
  (tergantung siteID ordering, tapi deterministic)
```

**Implementasi:**
```
- VS Code Live Share server relay edits
- Setiap edit = operation dengan unique ID
- CRDT algorithm (OP-based atau state-based)
- All clients apply operations in same order
- Converge ke same state
```

**Keuntungan:**
```
✓ Blazingly fast (tidak perlu tunggu server confirm)
✓ Offline support (queue operations, sync later)
✓ No conflicts (CRDT handles it)
✓ Complex merges ok (nested edits, formatting, etc)
```

#### Aplikasi 3 (Bonus): Figma (Collaborative Design)

```
Why Figma is perfect for CRDT:

Scenario: Designer A & B move shape at same time
  A: moves shape from (100,100) to (200,200)
  B: moves shape from (100,100) to (300,200)
  
  Tanpa CRDT:
    Conflict! Shape cannot be di 2 tempat
    
  Dengan CRDT (Figma architecture):
    Each shape position = CRDT value
    Final position determined by merge
    Maybe (250, 200) = average, atau last-write-wins
    
Result: Both see consistent state, no "undo/redo loops"
```

#### Aplikasi 4 (Bonus): Apache Cassandra (Distributed Database)

```
Why Cassandra uses CRDT-like structures:

Multi-DC setup:
  DataCenter 1: Update user profile
  DataCenter 2: Update same user profile (no sync yet)
  
Cassandra approach:
  - Uses "last-write-wins" with timestamp
  - Or "conflict-free replicated type" for certain data types
  - Merge updates dari both DCs automatically
  
Example:
  DC1: Set user age = 25
  DC2: Set user age = 26 (3 seconds later)
  
  Merge: age = 26 (LWW = last write wins)
```

#### Perbandingan Approaches

| Aplikasi | CRDT Type | Conflict Resolution |
|----------|-----------|---------------------|
| Apple Notes | Text CRDT | Auto-merge + manual |
| VS Code | OP-Transform | Deterministic order |
| Figma | Composite CRDT | Last-write-wins + merge |
| Cassandra | Vector clocks + LWW | Last-write-wins |

#### Tantangan Implementasi CRDT

```
1. Space amplification
   - Need to track per-node state
   - vs centralized: only need current state
   
2. Complexity
   - Algorithm bisa jadi complex
   - Need careful implementation
   
3. Garbage collection
   - Tombstones accumulate
   - Need periodic cleanup
   
4. Performance
   - Each merge = compute overhead
   - But offline-first benefit bisa justify
```

#### Kesimpulan

```
Real-world CRDT applications:
════════════════════════════════════════════════════════

✓ Apple Notes
  → Seamless sync across devices
  → Offline edits merge automatically
  
✓ VS Code Live Share
  → Real-time co-editing
  → No locks, high throughput
  
✓ Figma (Design collaboration)
  → Multiple users edit same canvas
  → No file locking
  
✓ Cassandra (Database)
  → Multi-DC consistency
  → Automatic conflict resolution

These are production systems dengan millions of users,
proving CRDT viability for real-world distributed apps.
```

---

# LAB 3: 2PC VS SAGA PATTERN

**URL:** `http://localhost:5000/lab3`

## Pertanyaan 1: Mengapa 2PC "Blocking Protocol"? Apa "In-doubt"?

### ❓ Pertanyaan
Mengapa 2PC disebut "blocking protocol"? Apa yang dimaksud "in-doubt transaction"?

### 📝 Jawaban
**2PC "blocking" karena participant menunggu coordinator mengirim commit/abort. Jika coordinator crash, participants terkunci ("in-doubt") sampai coordinator recovery.**

### 📖 Penjelasan Lengkap

#### Phases of 2PC

```
Phase 1: PREPARE (Vote)
├─ Coordinator: "Can you commit?"
├─ Participants: Check lokally, lock resources
└─ Return: YES atau NO

Phase 2: COMMIT (Write)
├─ Coordinator: "Please commit!" atau "Abort!"
├─ Participants: Write to disk, unlock
└─ Return: ACK

CRITICAL WINDOW:
├─ After Phase 1: Resources LOCKED
├─ Before Phase 2: NO DECISION YET
└─ If crash here: IN_DOUBT = BLOCKED
```

#### Apa itu "Blocking"?

```
Timeline dari perspective participant:

T1: Receive prepare request
    └─ Start transaction
    └─ Lock resources
    └─ Vote YES (dapat commit)

T2: WAITING for coordinator commit/abort
    ├─ Resources still LOCKED
    ├─ Other transactions BLOCKED
    ├─ Cannot read/write those resources
    └─ CAN ONLY WAIT

T3a: Receive commit → PROCEED
     └─ Write to disk, unlock
     
T3b: Receive abort → ROLLBACK
     └─ Discard changes, unlock
     
T3c: NO MESSAGE (coordinator crash)
     └─ STUCK! BLOCKED indefinitely
     └─ Resources locked, can't do anything
     └─ Called "IN_DOUBT" state
```

#### Contoh Skenario Blocking

**Banking Transfer: $100 dari Account A ke Account B**

```
Initial:
  Account A: $1000
  Account B: $500

Transactions:
  T1: A → B, $100

Timeline:

T=0s: Coordinator asks participants to prepare
      
T=1s: Participant A checks: Can deduct $100?
      YES (punya $1000 > $100)
      - LOCK Account A (prevent other transactions)
      - Vote YES, put in redo log
      
T=2s: Participant B checks: Can add $100?
      YES
      - LOCK Account B
      - Vote YES, put in redo log

T=3s: Both voted YES
      Coordinator decides: COMMIT
      - Send "commit" to all participants
      
T=4s: Participant A receives commit
      - Update: A = $900
      - Write to disk
      - UNLOCK Account A
      
T=5s: Participant B receives commit
      - Update: B = $600
      - Write to disk
      - UNLOCK Account B

SUCCESS! Transaction complete.

═════════════════════════════════════════════════════════

But what if:

T=0s-2s: Same as before (both locked, voted YES)

T=3s: Coordinator CRASH before sending commit
      
T=3.5s: Participant A still waiting
        - Account A locked
        - Other transactions try to access A: BLOCKED
        - "What should I do? Commit or Abort?"
        - Can't decide, must wait for coordinator
        
T=4s: Participant B same situation
      - Account B locked
      - BLOCKED
      
T=5s-1000s: Waiting...
            Coordinator still down...
            Resources still locked...
            This is BLOCKING + IN_DOUBT problem!
```

#### In-Doubt Transaction State

```
In-doubt = Participant voted YES but didn't receive final decision

Characteristics:
├─ Resources are LOCKED (held by participant)
├─ Transaction state: PREPARED but not COMMITTED/ABORTED
├─ Participant CANNOT:
│   ├─ Commit (don't know if others voted YES)
│   ├─ Abort (don't know coordinator's decision)
│   └─ Unlock resources (might violate atomicity)
├─ Can ONLY: WAIT for coordinator decision
└─ Problem: If coordinator down → WAIT FOREVER
```

**State diagram:**

```
PARTICIPANT STATE MACHINE:

        ┌──────────────┐
        │   INITIAL    │
        └──────┬───────┘
               │
        Prepare Request
               │
               ▼
        ┌──────────────┐
        │  PREPARING   │
        │ (Check local)│
        └──────┬───────┘
               │
        ┌──────┴──────────┐
        │                 │
        ▼                 ▼
    YES vote          NO vote
        │                 │
        ▼                 ▼
    ┌──────────────┐  ┌──────────────┐
    │  PREPARED    │  │   ABORTED    │
    │ (LOCKED!)    │  │ (Rolled back)│
    └──────┬───────┘  └──────────────┘
           │
    Waiting for decision...
           │
    ┌──────┴──────────┐
    │                 │
    ▼                 ▼
Commit        Abort
msg           msg
    │                 │
    ▼                 ▼
┌──────────────┐  ┌──────────────┐
│  COMMITTED   │  │   ABORTED    │
│ (UNLOCK!)    │  │ (UNLOCK!)    │
└──────────────┘  └──────────────┘

PROBLEM: If stuck at PREPARED state
         └─ Resources locked indefinitely
```

#### Langkah-langkah Test di Lab 3

**Bagian 1: Normal 2PC (No Failure)**

```
1. Buka http://localhost:5000/lab3
2. Pilih tab "2PC Protocol"
3. Klik "Initialize 2PC" → 3 participants
```

**Langkah 1: Normal flow**
```
1. Klik "Start Transaction"
   → Log shows: "Started 2PC protocol"
   → Phase: "PREPARE"
   
2. Klik "Phase 1: Prepare"
   → All 3 participants vote YES
   → State: PREPARED
   → Status: "All participants voted YES"
   
3. Perhatikan participant state:
   └─ All showing "PREPARED" (LOCKED at this point)
   
4. Klik "Phase 2: Commit"
   → All participants move to COMMITTED
   → Resources UNLOCKED
   → Transaction complete
```

**Bagian 2: In-Doubt Scenario (Coordinator Crash)**

```
1. Klik "Initialize 2PC" → reset
2. Klik "Start Transaction"
3. Klik "Phase 1: Prepare"
   → All participants PREPARED and LOCKED
   → Ready for commit
```

**Langkah 2: Simulate crash**
```
1. Klik "💥 Crash Coordinator"
   → Log shows: "CRASH: Coordinator crashed during phase 2!"
   
2. Perhatikan participant states:
   └─ All showing "IN_DOUBT"
   └─ They're locked, waiting for coordinator
   
3. Lihat status message:
   └─ "IN_DOUBT (3 participants waiting for coordinator)"
   
4. Log shows the problem:
   ├─ "Participants have voted YES and are holding locks"
   ├─ "They cannot commit or abort without coordinator"
   ├─ "This is called 'IN_DOUBT' transaction state"
   └─ "Must wait for coordinator recovery"
```

**Langkah 3: Coordinator recovery (manual intervention)**
```
Note: Lab tidak auto-recovery, tapi real system akan:
1. Coordinator restart
2. Read redo log: "3 participants voted YES"
3. Send "commit" to all
4. Participants unlock
5. IN_DOUBT resolved

This recovery dapat take menit sampai jam!
(Depending on coordinator restart time)
```

#### Impact on System

**Consequences of Blocking:**

```
1. RESOURCE LOCKING
   - Database rows locked
   - Other queries blocked
   - Cascading delays
   
2. LATENCY
   - Slow transactions block others
   - Aggravates the problem
   - Timeout more likely
   
3. THROUGHPUT
   - Fewer transactions can proceed
   - System becomes bottleneck
   - Coordinator crash = total halt

4. SCALABILITY
   - Not good for microservices (many participants)
   - Each participant = more chances to fail
   - More locks = more contention
```

**Why it's called "SPOF" (Single Point Of Failure):**

```
2PC topology:

          COORDINATOR
               ▲
            ┌──┼──┐
            │  │  │
            ▼  ▼  ▼
          P1  P2  P3
          
If COORDINATOR fails:
  └─ All participants stuck
  └─ Cannot proceed
  └─ System halted
  
= Single Point Of Failure
```

#### Kesimpulan

```
WHY 2PC is BLOCKING:
════════════════════════════════════════════════════════

✓ Participants lock resources after Phase 1 vote
✓ Must wait for Phase 2 decision
✓ If coordinator crashes → IN_DOUBT state
✓ Participants cannot commit nor abort
✓ Resources held indefinitely

IN_DOUBT = Participant status
├─ After Phase 1: Voted YES
├─ Before Phase 2: Waiting for decision
├─ Problem: Coordinator may be dead
├─ Result: STUCK with locked resources
└─ Impact: Cascading system failures

This is WHY 2PC unsuitable for:
  ✗ Long-running transactions
  ✗ Microservices (many participants)
  ✗ Unreliable networks
  ✗ High availability requirements

Good for:
  ✓ Short transactions (< 100ms)
  ✓ Reliable infrastructure
  ✓ Banking (ACID critical)
  ✓ Few participants
```

---

#### Lab 3: 3PC Mode Testing (Safer Alternative)

**🎯 3PC Mode vs 2PC Mode:**

Lab 3 sekarang menyediakan 2 mode protokol:
- **2PC Mode** (2 Phases): PREPARE → COMMIT (blocking, faster)
- **3PC Mode** (3 Phases): PREPARE → PRE-COMMIT → COMMIT (non-blocking, safer)

**Langkah-langkah Test 3PC Mode:**

**Part 1: Normal 3PC (Successful commit)**

```
1. Klik "Initialize 2PC" → setup 3 participants
2. Klik "Start Transaction"
3. Klik "Phase 1: Prepare"
   → All participants show "PREPARED" state
   → Resources LOCKED
```

**Phase 2: PRE-COMMIT (NEW)**
```
4. Klik "Phase 2: Pre-Commit (3PC)"  ← BARU!
   → Participants move to "PRE_COMMITTED" state
   → Status: "PRE-COMMIT PHASE: 3 pre-committed"
   → Resources STILL LOCKED
   → This is the KEY difference from 2PC!
   
5. Di log, akan melihat:
   ├─ "Phase 2 (3PC): 3 participants pre-committed"
   └─ "3PC Mode: All participants ready to commit..."
```

**Phase 3: COMMIT**
```
6. Klik "Phase 3: Commit (3PC)"  ← NEW PHASE!
   → Participants move to "COMMITTED" state
   → All participants successfully committed
   → Resources UNLOCKED
   
7. Transaction complete successfully!
```

**Part 2: 3PC with Coordinator Crash (Recovery)**

```
1. Klik "Initialize 2PC" → reset
2. Klik "Start Transaction"
3. Klik "Phase 1: Prepare"
   → All participants PREPARED (locked)
```

**Simulate crash at Phase 2:**
```
4. Klik "Phase 2: Pre-Commit (3PC)"
   → Participants PRE_COMMITTED
   
5. SEGERA klik "💥 Crash Coordinator"
   → Coordinator crashes during Phase 2
   
6. Log akan menunjukkan:
   ├─ "ERROR: Coordinator crashed during phase 2!"
   ├─ "Participants in PRE_COMMITTED state can safely commit"
   ├─ "They will auto-commit after timeout (3PC recovery rule)"
   └─ "Participants: Auto-committed after timeout"
   
7. Lihat state participant:
   └─ Mereka AUTOMATICALLY COMMITTED tanpa coordinator!
   └─ Ini adalah keuntungan 3PC vs 2PC
```

**Key Difference Visualization:**

```
2PC Mode:
├─ Phase 1: PREPARE
└─ Phase 2: COMMIT (if crash here → IN_DOUBT forever!)
   
3PC Mode:
├─ Phase 1: PREPARE
├─ Phase 2: PRE-COMMIT  ← Safety buffer
└─ Phase 3: COMMIT (if crash here → participants auto-commit)

Why Phase 2 (PRE-COMMIT) helps:
├─ All participants acknowledge they can commit
├─ Coordinator crash doesn't leave them hanging
├─ They can make unilateral decision after timeout
└─ No more blocking indefinitely!
```

**Part 3: Compare 2PC vs 3PC Side-by-Side**

```
2PC Mode Testing:
1. Klik "Initialize 2PC"
2. Klik "Start Transaction"
3. Klik "Phase 1: Prepare" → PREPARED
4. Immediately klik "💥 Crash Coordinator"
5. Result: All participants IN_DOUBT (BLOCKED!)

vs

3PC Mode Testing:
1. Klik "Initialize 2PC"
2. Klik "Start Transaction"
3. Klik "Phase 1: Prepare" → PREPARED
4. Klik "Phase 2: Pre-Commit (3PC)" → PRE_COMMITTED
5. Immediately klik "💥 Crash Coordinator"
6. Result: All participants AUTO-COMMIT (NO BLOCKING!)

CONCLUSION: 3PC Mode melindungi dari blocking problem!
```

---

## Pertanyaan 2: Bagaimana 3PC Mengatasi Blocking Problem?

### ❓ Pertanyaan
Bagaimana 3PC (Three-Phase Commit) mencoba mengatasi blocking problem?

### 📝 Jawaban
**3PC menambah Phase di antara Prepare dan Commit: Phase "Pre-Commit". Jika coordinator crash di Phase 2, participants bisa membuat keputusan sendiri.**

### 📖 Penjelasan Lengkap

#### 2PC vs 3PC Comparison

```
2PC (2 Phases):
└─ Phase 1: PREPARE (vote)
└─ Phase 2: COMMIT/ABORT (decide)
   Problem: Crash between P1→P2 = IN_DOUBT


3PC (3 Phases):
├─ Phase 1: PREPARE (vote) - "Can you commit?"
├─ Phase 2: PRE-COMMIT - "Wait, coordinator will send final decision"
└─ Phase 3: COMMIT/ABORT - "Do it!"
   Solution: Coordinator crash di P2 bisa resolve
```

#### 3PC Timeline & Recovery

```
Normal 3PC Flow:

T1: Phase 1 - PREPARE
    ├─ Coord: "Can you commit?"
    ├─ Participants: Vote YES/NO
    └─ Lock resources

T2: Phase 2 - PRE-COMMIT  ← BARU!
    ├─ Coord: "Prepare to commit (but not yet!)"
    ├─ Participants: Acknowledge, ready
    └─ Resources still locked
    
T3: Phase 3 - COMMIT
    ├─ Coord: "Commit!" (or abort)
    ├─ Participants: Execute, unlock
    └─ Done

═══════════════════════════════════════════════════════

3PC with Recovery - Phase 2 Crash:

T1-T2: Same as normal
       Participants in PRE-COMMIT state

T2.5: Coordinator CRASH

T3+: Timeout occurs
     Participants: "Coordinator tidak balas 30 detik"
     Decision: We can safely COMMIT
               (Because all voted YES in Phase 1)
               
Reasoning:
├─ If ALL participants reached PRE-COMMIT state
├─ = ALL voted YES in Phase 1
├─ = ALL are ready to commit
├─ = Safe to commit even without coordinator
└─ Worst case: Need recover coordinator log to verify
```

#### State Machine 3PC

```
COORDINATOR STATE:

        ┌─────────────┐
        │   INITIAL   │
        └──────┬──────┘
               │
        All participants
        send VOTE YES?
               │
               ▼
        ┌──────────────┐
        │PHASE1_DONE   │
        │(can abort OK)│
        └──────┬───────┘
               │
        Send PRE-COMMIT?
               │
               ▼
        ┌──────────────┐
        │PHASE2_DONE   │  ← Can safely commit
        │(PRE-COMMIT   │    (all participants aware)
        │ acknowledged)│
        └──────┬───────┘
               │
        Send COMMIT?
               │
               ▼
        ┌──────────────┐
        │   COMMITTED  │
        └──────────────┘


PARTICIPANT STATE:

During PHASE 2 (PRE-COMMIT):
├─ If no coordinator response → Timeout
├─ Participant checks:
│   "Did I vote YES in Phase 1?" → YES
│   "Did I acknowledge PRE-COMMIT?" → YES
│   "Are all other participants up?" → Check via gossip/heartbeat
│   If all YES → Safe to COMMIT unilaterally
└─ Commit and move on
```

#### 3PC Recovery Rules

```
Recovery Rule 1: Phase 1 timeout
├─ Participants: Abort (not everyone voted YES yet)
└─ Resource: Unlock, no damage

Recovery Rule 2: Phase 2 timeout  ← KEY DIFFERENCE
├─ Participants: All voted YES (Phase 1 passed)
├─ Coordinator crashed before COMMIT message
├─ Participants can safely COMMIT
├─ Can use quorum voting if needed
└─ No blocking!

Recovery Rule 3: Phase 3 timeout
├─ Commit already decided in Phase 2
├─ Just complete the operation
└─ Idempotent operation required
```

#### Contoh Skenario 3PC

**Banking Transfer Example:**

```
Account A: $1000
Account B: $500
Transfer: $100 A→B

PHASE 1: PREPARE
├─ Coord: "Can you do it?"
├─ A: Check $100 available → YES, lock
├─ B: Check empty → YES, lock
└─ State: Both PREPARED

PHASE 2: PRE-COMMIT  ← NEW PHASE
├─ Coord: "Waiting for final decision"
├─ A: Acknowledge, wait
├─ B: Acknowledge, wait
├─ A state: PRE-COMMIT (still locked)
├─ B state: PRE-COMMIT (still locked)
└─ COORDINATOR CRASHES HERE!

PHASE 3: COMMIT (NOT SENT)
├─ A times out after 30s
├─ A decides: "I voted YES, I'm in PRE-COMMIT"
│           "Other participants also in PRE-COMMIT"
│           "Safe to commit"
├─ A commits: $1000 - $100 = $900
├─ A unlocks
│
├─ B times out after 30s
├─ B decides: "I voted YES, I'm in PRE-COMMIT"
│           "Safe to commit"
├─ B commits: $500 + $100 = $600
├─ B unlocks
│
└─ RESULT: Transaction complete WITHOUT coordinator!
           A=$900, B=$600 ✓
```

#### 3PC Limitations

```
3PC bukan "magic bullet", masih punya masalah:

1. Network Partition = Still problematic
   ├─ Partition 1: Coordinator + some participants
   ├─ Partition 2: Other participants
   ├─ Both partitions think they should commit
   ├─ Result: Inconsistency (worse than 2PC!)
   └─ Need more complex rules (Paxos/Raft)

2. Still requires synchronous commit
   ├─ All participants must respond
   ├─ One slow participant = blocks all
   ├─ Doesn't solve latency problem
   └─ Just makes it 3 round-trips instead of 2

3. Complex to implement
   ├─ Recovery protocol intricate
   ├─ Need careful logging
   ├─ Hard to debug
   └─ Rarely implemented correctly

4. Message overhead
   ├─ 3 phases = more network round-trips
   ├─ More bandwidth
   ├─ Worse latency than 2PC (sometimes)
```

#### Why 3PC Rarely Used in Practice

```
1. Paxos/Raft simpler & more proven
   └─ Better than 3PC for consensus
   
2. Saga pattern more practical
   └─ Asynchronous, loosely coupled
   
3. Eventually consistent databases
   └─ Multi-master replication
   
4. Microservices prefer event sourcing
   └─ Compensation-based approach

3PC = theoretical contribution to distributed systems
    but not practical for production systems
```

#### Kesimpulan

```
HOW 3PC attempts to solve blocking:
════════════════════════════════════════════════════════

✓ Adds Phase 2: PRE-COMMIT (intermediate state)
✓ Participants aware of decision before commit
✓ If coordinator crashes in Phase 2:
  └─ Participants know all voted YES
  └─ Can commit autonomously
  └─ No blocking!

HOWEVER:
✗ Network partition still problematic
✗ Complex to implement correctly
✗ Message overhead (3 phases)
✗ Rarely used in practice

MODERN ALTERNATIVES:
✓ Paxos/Raft - consensus for leader election
✓ Saga - compensating transactions
✓ Event sourcing - eventual consistency
✓ CRDT - conflict-free merge

Takeaway: 3PC is academic solution
         Real systems use Saga or gossip protocols
```

---

## Pertanyaan 3: Saga ACD tapi bukan "I" - Apa Implikasinya?

### ❓ Pertanyaan
Saga memiliki "ACD" tapi bukan "I" (Isolation). Apa artinya dan bagaimana mitigasinya?

### 📝 Jawaban
**Saga memiliki:**
- **A (Atomicity)** - All-or-nothing via compensation
- **C (Consistency)** - Eventual consistency
- **D (Durability)** - Log stored
**TAPI TIDAK I (Isolation)** - Intermediate states visible. Mitigasi: Saga orchestrator atau compensation logic.**

### 📖 Penjelasan Lengkap

#### ACID Properties

```
ACID = Atomicity, Consistency, Isolation, Durability

2PC: ✓ A ✓ C ✓ I ✓ D  (Full ACID)
Saga: ✓ A ✓ C ✗ I ✓ D  (BASE - Basically Available, Soft state, Eventual consistency)
```

#### What is Isolation?

```
Isolation (I) dalam ACID:

Definition: Each transaction isolated from others
            - One transaction's intermediate state
            - NOT visible to other transactions

Example with Isolation (2PC):

T1: Transfer $100 A→B
T2: Check balance A

Timeline with ISOLATION:
├─ T1 starts: A=$1000
├─ T1 takes $100: A=$900 (HIDDEN from T2!)
├─ T2 reads A: Still see $1000 (isolated)
├─ T1 commits: A=$900
├─ T2 reads A: Now see $900 (after T1 commit)
└─ Result: T2 never see "in-between" state
```

#### Why Saga Lost Isolation

```
Saga = Each service commits independently

T1: Saga "Transfer $100 A→B"
├─ Step 1: Service A: A -= 100  ← IMMEDIATE commit
│         Now A = $900
├─ Step 2: Service B: B += 100  ← IMMEDIATE commit
│         Now B = $600

T2: Check balance A (happens between Step 1 and 2)
└─ Sees A = $900

PROBLEM:
├─ T1 tidak selesai (masih Step 2)
├─ Tapi T2 sudah lihat partial state
├─ Jika T1 gagal di Step 2 → Compensate (undo Step 1)
├─ Tapi T2 sudah pake data A=$900 yang akan di-undo!
└─ Inconsistency bisa terjadi

= LACK OF ISOLATION
```

#### Skenario: Lost Isolation Problem

**E-commerce Order Saga:**

```
Scenario: Place order $100, need:
1. Reserve inventory
2. Process payment
3. Ship order

Saga Flow:

Time 1.0s: Order starts
           Item count = 100

Time 1.1s: Service 1 - Reserve inventory
           Item reserved for this order
           → Item count = 99 ✓
           → COMMIT immediately
           
           [Another user checks inventory NOW]
           → See 99 items available
           → User thinks only 1 item left
           → User order too

Time 1.2s: Service 2 - Process payment
           Credit card charged
           → COMMIT immediately

Time 1.3s: Service 3 - Ship order
           Tries to create shipment
           → ERROR: Payment failed!
           → Shipping service timeout
           → Saga ABORTS

Time 1.4s: Compensation for Step 1
           Un-reserve inventory
           → Item count back to 100

RESULT:
├─ Item count = 100 (inventory restored)
├─ Credit card charged (payment NOT reversed!)
├─ But other user also ordered (saw 99)
├─ Now inventory overbooked
└─ Lost Isolation + inconsistency!
```

#### Isolation Levels in Databases

```
From strongest to weakest isolation:

1. SERIALIZABLE ← 2PC can guarantee this
   - Transactions appear to run sequentially
   - No dirty read, no phantom read
   - Highest consistency
   - Lowest concurrency

2. REPEATABLE READ
   - Same transaction sees same data
   - But new rows can appear (phantom)

3. READ COMMITTED
   - Only see committed data
   - Dirty reads prevented
   - Lost updates possible

4. READ UNCOMMITTED ← Saga basically here
   - Can see uncommitted data
   - Dirty reads allowed
   - No isolation

SAGA typically at READ UNCOMMITTED level
= Other transactions see partial saga state!
```

#### Mitigasi Lack of Isolation - Strategi 1: Saga Orchestrator

```
Orchestrator mengontrol state visibility:

Service A                 Service B
(Debit $100)             (Credit $100)

Time 1.0s: Start debit
          A: EXECUTING
          B: WAITING (not started yet)
          
Time 1.1s: Debit OK
          A: COMMITTED ✓
          B: WAITING (still waiting for signal)
          
Time 1.2s: Can T2 read?
          Orchestrator: NO!
          Reason: Saga not complete (B still waiting)
          Result: T2 blocked or get "Saga in progress" error
          
Time 1.3s: B OK
          A: COMMITTED ✓
          B: COMMITTED ✓
          Saga complete
          
Time 1.4s: Can T2 read?
          Orchestrator: YES!
          Result: T2 see consistent state
```

**Implementation:**

```python
class SagaOrchestrator:
    def execute_saga(saga_id):
        # Mark saga as "IN_PROGRESS"
        saga_state[saga_id] = "IN_PROGRESS"
        
        try:
            # Execute all steps
            result1 = service_a.debit(saga_id, 100)
            result2 = service_b.credit(saga_id, 100)
            
            # Mark complete
            saga_state[saga_id] = "COMPLETED"
            return "SUCCESS"
        except:
            # Compensate
            service_a.credit_back(saga_id, 100)
            saga_state[saga_id] = "COMPENSATED"
            return "FAILED"

# Other transactions see saga state:
def read_account(account_id):
    active_sagas = find_active_sagas(account_id)
    if active_sagas:
        # Option 1: Block read
        return ERROR("Saga in progress")
        
        # Option 2: Return locked message
        return {value: old_value, status: "LOCKED"}
        
        # Option 3: Wait for saga
        wait_for_sagas(active_sagas)
        return current_value
```

#### Mitigasi Strategi 2: Idempotent Operations

```
Idempotency = Operation can run multiple times, same result

Problem scenario:
├─ Service receives "charge $100"
├─ Process it
├─ Network timeout (response lost)
├─ Orchestrator retry
├─ Service receives again → Charge $200!

Solution: Idempotent operation with dedup ID

def charge_payment(dedup_id, amount):
    # Check if already processed
    if record = find_by_dedup_id(dedup_id):
        return record.result  # Return same result
    
    # Process
    result = credit_card.charge(amount)
    
    # Store with dedup_id
    store_result(dedup_id, result)
    
    return result

Multiple calls with same dedup_id:
├─ Call 1: Process, return result_1
├─ Call 2: Find in DB, return result_1 (same!)
├─ Call 3: Find in DB, return result_1 (same!)
└─ Result: Always $100 charged (idempotent)
```

#### Mitigasi Strategi 3: Semantic Locking

```
Instead of database locks, use business logic locks:

Table: order_status
┌────────┬──────────────┐
│ order_id│ status       │
├────────┼──────────────┤
│ ORD-001│ PENDING      │
│ ORD-002│ RESERVED     │  ← Semantic lock!
│ ORD-003│ SHIPPED      │
└────────┴──────────────┘

When saga executes:
├─ Status = "RESERVED" (semantic lock)
├─ Other transactions check status
├─ See "RESERVED" = Order being processed
├─ Don't interfere
└─ Isolation via application logic, not DB

Benefits:
├─ Works across services (no global DB lock)
├─ Explicit, visible locks
├─ Can timeout and compensate
```

#### Mitigasi Strategi 4: Read Your Own Write

```
Principle: A transaction only reads data it writes

Saga T1 writes: account_balance = $900

T2 tries to read account_balance:
├─ From Service A cache: $1000 (stale)
├─ Check: Is T1 the writer? YES
├─ Use T1's value: $900 (consistent with T1)
└─ Result: Read your own write

Implementation:
class TransactionContext:
    def __init__(saga_id):
        self.saga_id = saga_id
        self.writes = {}  # Track writes
    
    def write(entity_id, value):
        self.writes[entity_id] = value
    
    def read(entity_id):
        # Check own writes first
        if entity_id in self.writes:
            return self.writes[entity_id]
        # Otherwise read from DB
        return database.read(entity_id)
```

#### Comparison: 2PC vs Saga Isolation

| Scenario | 2PC Isolation | Saga Isolation |
|----------|---------------|----------------|
| **Dirty Read** | ❌ Prevented | ⚠️ Possible |
| **Lost Update** | ❌ Prevented | ⚠️ Possible |
| **Phantom Read** | ❌ Prevented | ⚠️ Possible |
| **Consistency** | ✓ Strong | ⚠️ Eventual |
| **Blocking** | ⚠️ Possible | ❌ None |
| **Availability** | ⚠️ Lower | ✓ Higher |

#### Real-World Example: AWS

```
Amazon uses Saga for multi-step operations:

Example: Purchase with multiple services
├─ Service 1: Inventory check & reserve
├─ Service 2: Payment processing
├─ Service 3: Logistics & shipping
├─ Service 4: Notification

Isolation level: READ_COMMITTED (not SERIALIZABLE)
├─ Other services can see partial state
├─ "Order RESERVED" but not yet paid
├─ User sees "Order processing..."
└─ Acceptable in e-commerce

NOT using 2PC because:
├─ Would block entire system on failures
├─ Logistics service might be slow/unreliable
├─ Payment timeout affects inventory lock
└─ Better to use Saga + compensations
```

#### Trade-offs: Isolation vs Availability

```
Strong Isolation (2PC):
  ├─ Pros: ✓ Consistent
  │       ✓ Predictable
  │       ✓ ACID
  ├─ Cons: ✗ Blocking
  │        ✗ Low availability
  │        ✗ SPOF (coordinator)
  └─ Use: Banking (< 1000 TPS)

Weak Isolation (Saga):
  ├─ Pros: ✓ High availability
  │       ✓ High throughput (100K TPS)
  │       ✓ Distributed
  ├─ Cons: ✗ Eventual consistency
  │        ✗ Complex compensations
  │        ✗ Hard to reason about
  └─ Use: E-commerce, social media (millions TPS)
```

#### Kesimpulan

```
SAGA LACKS ISOLATION (I):
════════════════════════════════════════════════════════

✓ Has: Atomicity (via compensation)
✓ Has: Consistency (eventual)
✓ Has: Durability (log based)
✗ NO: Isolation (intermediate states visible)

IMPLICATIONS of lost Isolation:
├─ Dirty reads possible (see partial saga state)
├─ Lost updates possible (concurrent modifications)
├─ Phantom reads possible (new rows appear)
└─ Eventual consistency (not strong consistency)

HOW TO MITIGATE:
✓ Saga orchestrator (explicit state tracking)
✓ Idempotent operations (handle retries)
✓ Semantic locking (business logic locks)
✓ Read-your-own-writes (transaction context)
✓ Compensating transactions (rollback logic)

BOTTOM LINE:
├─ Use 2PC: If ACID critical (banking)
├─ Use Saga: If availability critical (e-commerce)
└─ Trade-off: Consistency vs Availability (CAP theorem)
```

---

# LAB 4: QUORUM CONFIGURATION ANALYSIS

**URL:** `http://localhost:5000/lab4`

## Pertanyaan 1: N=5, W=3, R=3 - Verifikasi W+R>N, Max Failures?

### ❓ Pertanyaan
N=5, W=3, R=3: Verifikasi W+R>N, max failures?

### 📝 Jawaban
**W+R = 3+3 = 6 > N = 5 ✓ (Valid)**
**Max write failures = 5-3 = 2**
**Max read failures = 5-3 = 2**
**Consistency = Strong (CP - Consistent & Partition tolerant)**

### 📖 Penjelasan Lengkap

#### Quorum Concept

```
N = Total replicas
W = Write quorum (how many must acknowledge)
R = Read quorum (how many must return same value)

Requirement: W + R > N

Reasoning:
├─ Write set = W replicas
├─ Read set = R replicas
├─ If W + R > N, there MUST be overlap
└─ Overlapping replica = guarantee read sees latest write
```

#### N=5, W=3, R=3 Analysis

**Step 1: Verify W+R > N**

```
W + R = 3 + 3 = 6
N = 5

6 > 5? YES ✓

This means:
├─ Write goes to 3 replicas (W=3)
├─ Read checks 3 replicas (R=3)
├─ Must have ≥ (3 + 3 - 5) = 1 replica in common
└─ Guaranteed read sees write!
```

**Step 2: Max Failure Analysis**

```
Max Write Failures:
├─ Need W=3 to acknowledge
├─ Total N=5
├─ Can tolerate: 5 - 3 = 2 failures
├─ Meaning: If 3 or more replicas alive → write succeeds
├─ If only 2 alive → write fails!

Max Read Failures:
├─ Need R=3 to return
├─ Total N=5
├─ Can tolerate: 5 - 3 = 2 failures
├─ Meaning: If 3 or more replicas alive → read succeeds
└─ If only 2 alive → read fails!

Conclusion:
├─ Both read and write tolerate max 2 failures
└─ Requires minimum 3 replicas to function
```

**Step 3: Consistency Guarantee**

```
Consistency check:
├─ W=3, R=3, N=5 → 3+3 > 5 ✓ STRONG CONSISTENCY
├─ Why? Because read MUST overlap with write
├─ Example:

Write operation:
├─ Write to replicas: [A, B, C]
├─ W=3 requirement satisfied
├─ Value stored in A, B, C

Read operation:
├─ Read from replicas: [D, E, ?]
├─ Only 2 replicas? Need third
├─ Read from C (from write set)
├─ [D, E, C] - at least one has latest value!
└─ Guaranteed to see latest write

Result: STRONG CONSISTENCY (CP)
```

**Step 4: Failure Tolerance Table**

| Scenario | Alive | Dead | Write OK? | Read OK? | System |
|----------|-------|------|-----------|----------|--------|
| Normal | 5 | 0 | ✓ | ✓ | Running |
| 1 down | 4 | 1 | ✓ | ✓ | Running |
| 2 down | 3 | 2 | ✓ | ✓ | Running |
| 3 down | 2 | 3 | ✗ | ✗ | Down |

#### Step-by-Step Lab 4 Test

**Setup:**
```
1. Buka http://localhost:5000/lab4
2. Klik tab "Quorum Calculator" (atau similar)
3. Enter values: N=5, W=3, R=3
```

**Langkah 1: Input dan verification**
```
1. Input:
   - N = 5
   - W = 3
   - R = 3

2. System calculates:
   - W + R = 6
   - 6 > 5? YES
   - Status: ✓ VALID QUORUM
```

**Langkah 2: Read max failure calculation**
```
1. Max Write Failures = N - W = 5 - 3 = 2
   └─ Interpretation: Can lose 2 replicas, write still succeeds
   
2. Max Read Failures = N - R = 5 - 3 = 2
   └─ Interpretation: Can lose 2 replicas, read still succeeds
```

**Langkah 3: Consistency classification**
```
Since W + R > N:
  └─ Classification: STRONG CONSISTENCY
  └─ Type: CP (Consistent & Partition Tolerant)
  └─ Tradeoff: Sacrifices Availability (A)
  
Explanation:
  ├─ Read MUST wait for W=3 replicas
  ├─ If only 2 replicas up, read blocks
  ├─ But guaranteed to see latest write
  └─ Strong consistency > High availability (here)
```

**Langkah 4: Visualization - Draw quorum sets**

```
Write operation:
W=3 → Pick any 3 replicas to write

Possibility 1:      Possibility 2:
   [A, B, C]          [B, C, D]
        ↓                  ↓
    write OK           write OK

Read operation:
R=3 → Pick any 3 replicas to read

Possibility 1:      Possibility 2:
   [A, D, E]          [A, B, C]
        ↓                  ↓
    read OK            read OK

Check overlap:
├─ Write to [A, B, C]
├─ Read from [D, E, ?]
├─ Missing C (from write set)
├─ Would need to read from C
└─ No choice, must include overlap
```

#### Comparison with Other Quorum Configs

```
Configuration | W | R | N | Valid? | Consistency | Use Case
──────────────┼───┼───┼───┼────────┼─────────────┼──────────────────
              3   3   5   ✓ YES    Strong CP    Banking (this case)
              2   2   3   ✓ YES    Strong CP    Cassandra QUORUM
              5   1   5   ✗ NO     Weak AP      Read-heavy analytics
              1   5   5   ✓ YES    Strong CP    Write-heavy cache
              3   3   3   ✓ YES    Strong CP    3-node cluster
```

#### Kesimpulan Pertanyaan 1

```
N=5, W=3, R=3 ANALYSIS:
════════════════════════════════════════════════════════

✓ W + R > N:
  └─ 3 + 3 = 6 > 5 ✓ VALID

✓ Max Failures:
  ├─ Write failures: 2 (can lose 2 replicas)
  ├─ Read failures: 2 (can lose 2 replicas)
  └─ Min alive needed: 3 replicas

✓ Consistency:
  ├─ Type: STRONG (CP)
  ├─ Guarantee: Read sees latest write
  ├─ Tradeoff: Lower availability (blocks if < 3 alive)
  └─ Use: Banking, critical systems

Use this for:
  ✓ Strong consistency requirement
  ✓ Can tolerate unavailability
  ✓ Few replicas (3-5 nodes)
```

---

## Pertanyaan 2: N=5, W=1, R=5 - Kapan Berguna?

### ❓ Pertanyaan
N=5, W=1, R=5: Kapan berguna?

### 📝 Jawaban
**N=5, W=1, R=5 berguna untuk READ-HEAVY workloads. Write fast (1 replica), read dari semua (5 replicas) untuk durability.**

### 📖 Penjelasan Lengkap

#### Analysis N=5, W=1, R=5

**Verification:**

```
W + R = 1 + 5 = 6
N = 5

6 > 5? YES ✓ (Still valid!)

This is extreme:
├─ W=1: Write to minimal replicas (FAST)
├─ R=5: Read from all replicas (SLOW)
├─ Tradeoff: Fast writes, slow reads
```

**Failure Analysis:**

```
Max Write Failures: 5 - 1 = 4
├─ Even if 4 replicas down, write OK!
├─ Write to remaining 1 replica → SUCCEEDS
├─ Amazing availability for writes

Max Read Failures: 5 - 5 = 0
├─ Need ALL 5 replicas to respond
├─ If even 1 replica down → read FAILS
├─ Very low read availability!
```

**Consistency:**

```
Even though W + R > N, consistency still depends on write pattern:

Scenario: Write to 1 replica, read from 5
├─ Most replicas don't have latest value
├─ When read from 5 replicas:
│   ├─ 1 replica has new value
│   ├─ 4 replicas have old value
│   └─ Majority wins (4 old > 1 new)
│       → Read returns OLD VALUE!
│       
└─ Result: Read may not see latest write!
   (Despite W+R > N guarantee)

Why? Because:
├─ We need to READ FROM MAJORITY (at least W replicas)
├─ R=5 means ALL replicas
├─ Majority vote on value
├─ 4 old > 1 new → old wins
└─ Breaks consistency
```

**Real behavior:**

```
Write: value_new
├─ Write to 1 replica (e.g., A)
├─ Replica A: value_new
├─ Replicas B,C,D,E: value_old

Read: Must check all 5
├─ A: value_new (1 vote)
├─ B: value_old (1 vote)
├─ C: value_old (1 vote)
├─ D: value_old (1 vote)
├─ E: value_old (1 vote)
├─ Majority: value_old (4 votes > 1)
└─ Return value_old (STALE!)

= NOT CONSISTENT!
```

#### When N=5, W=1, R=5 is Useful

**Use Case 1: Disaster Recovery / Archival**

```
Scenario: Store important backup data

Requirements:
├─ Write frequently (new backups)
├─ Rarely read (only on disaster)
├─ Must be durable (available in all locations)

Configuration N=5, W=1, R=5:
├─ Write backup quickly to 1 site (W=1)
├─ Replicate to all 5 sites eventually (R=5)
├─ Read from all 5 sites on recovery
├─ If any 4 sites down, can still write
└─ Data safe (replicated to all 5)

Example:
├─ Write to S3 bucket (1)
├─ S3 replicates to 4 other regions (eventually)
├─ On disaster: read from all regions to verify
└─ Ensure most complete version found
```

**Use Case 2: Audit Logs (Write-Optimized)**

```
Scenario: Log immutable audit trails

Requirements:
├─ Write many logs/second
├─ Rarely read (compliance review)
├─ Must preserve all (legal requirement)

Configuration N=5, W=1, R=5:
├─ Write log to 1 node fast (W=1)
├─ Asynchronously replicate to 4 others
├─ Read from all 5 on audit (R=5)
├─ High write throughput
└─ Durable (survive any 4 failures)

Performance:
├─ Write latency: 1 node = fast
├─ Read latency: all 5 nodes = slow (but rare)
├─ Throughput: 10,000+ writes/sec
```

**Use Case 3: CDN with Local Cache**

```
Scenario: Content delivery network

Configuration N=5, W=1, R=5:
├─ W=1: Write to origin node (fast upload)
├─ Content pushes to 4 edge caches asynchronously
├─ R=5: Full verification (read from all edges)

Example:
├─ User uploads video to origin (1 node)
├─ Origin writes log: "Video available"
├─ Video replicates to edges: USA, EU, ASIA, etc
├─ Customer can start watching from nearest edge
├─ On read: verify all edges have copy
```

**Use Case 4: Time-Series Database (Metrics)**

```
Scenario: Store high-frequency metrics

Requirements:
├─ Billions of writes/second (metrics)
├─ Occasional reads (analytics, dashboards)

Configuration N=5, W=1, R=5:
├─ Write metric to 1 replica (fast)
├─ Metrics replicate in background
├─ Read from all 5 on query (comprehensive)
├─ Even if 4 replicas behind, still write

Example InfluxDB:
├─ Telegraf sends metrics → InfluxDB write path (W=1)
├─ InfluxDB replicates across cluster
├─ Grafana query on all replicas (R=5)
```

#### Consistency vs Availability Trade-off

```
N=5, W=1, R=5 Summary:

Consistency: EVENTUAL (not strong!)
├─ Read may return stale data
├─ Need application-level resolution
├─ Add version vectors or timestamps
└─ Check which value is newest

Availability: EXCELLENT for writes
├─ Tolerate 4 failures → write OK
├─ Only need 1 replica alive
├─ Perfect for disaster scenarios

Availability: POOR for reads
├─ Need all 5 replicas → read fails if any down
├─ Not good for read-heavy access
└─ Only read when absolutely need all data

Tradeoff:
├─ Sacrifice strong consistency
├─ Gain write availability
├─ Accept read latency & potential inconsistency
└─ Good for durability (all replicas have it)
```

#### When NOT to Use N=5, W=1, R=5

```
✗ Real-time systems
  ├─ Need consistent views
  └─ Stock trading, banking (use W+R > N properly)

✗ High-frequency read workloads
  ├─ R=5 = very slow
  ├─ Need all 5 replicas respond
  └─ Any latency = bottleneck

✗ Concurrent writes
  ├─ May read stale data
  ├─ Apply conflicting updates
  └─ Chaos ensues

✓ Write-once (immutable) data
  ├─ No concurrent writes
  ├─ Perfect for logs, backups
  └─ OK to read stale version
```

#### Kesimpulan Pertanyaan 2

```
N=5, W=1, R=5 USE CASES:
════════════════════════════════════════════════════════

✓ When berguna:
  ├─ High write throughput needed
  ├─ Disaster recovery / durability critical
  ├─ Audit logs (write-once)
  ├─ Backups / archives
  ├─ Can tolerate inconsistency
  └─ Reads rare or can handle stale data

✓ Benefits:
  ├─ Write availability: extremely high
  ├─ Write latency: extremely low
  ├─ Durability: guaranteed (all 5 replicas)
  ├─ Failure tolerance: 4 replicas can be down
  └─ Throughput: very high

✗ Drawbacks:
  ├─ Read latency: very high (need all 5)
  ├─ Read availability: low (all 5 must be up)
  ├─ Consistency: eventual (may read stale)
  ├─ Not suitable for online transactions
  └─ Complex application logic needed

Real examples:
  ✓ Apache Cassandra: Write-heavy cluster
  ✓ DynamoDB: Backup replication
  ✓ CloudFlare: CDN edge replication
```

---

## Pertanyaan 3: N=5, W=5, R=1 - Implikasi Availability?

### ❓ Pertanyaan
N=5, W=5, R=1: Implikasi untuk availability?

### 📝 Jawaban
**N=5, W=5, R=1 adalah OPPOSITE dari sebelumnya: Write-Heavy blocking, Read-Heavy fast. Availability SANGAT RENDAH karena perlu semua 5 replicas hidup untuk write.**

### 📖 Penjelasan Lengkap

#### Analysis N=5, W=5, R=1

**Verification:**

```
W + R = 5 + 1 = 6
N = 5

6 > 5? YES ✓ (Valid!)

This is extreme opposite:
├─ W=5: Write to ALL replicas (SLOW, risky)
├─ R=1: Read from 1 replica (FAST)
├─ Tradeoff: Slow writes, fast reads
```

**Failure Analysis:**

```
Max Write Failures: 5 - 5 = 0
├─ Need ALL 5 replicas alive
├─ If even 1 replica down → write FAILS
├─ Zero failure tolerance for writes!
├─ SINGLE POINT OF FAILURE!

Max Read Failures: 5 - 1 = 4
├─ Only need 1 replica to respond
├─ Can tolerate 4 failures
├─ If 4 replicas down, read still OK
├─ Amazing availability for reads
```

**Availability Impact:**

```
Failure scenario:

Normal state (all 5 up):
├─ Writes: ✓ OK (all 5 acknowledge)
├─ Reads: ✓ OK (ask any 1)
└─ System: Fully operational

1 Replica goes down (4 left):
├─ Writes: ✗ FAIL (need all 5, only have 4)
├─ Reads: ✓ OK (need 1, have 4)
├─ Users: Cannot write, but can read
└─ Impact: Severe (no data changes possible)

Example: Outage at 1 datacenter
├─ N=5 replicas across 5 datacenters
├─ Datacenters: [US-East, US-West, EU, ASIA, ???]
├─ If 1 datacenter fails → CANNOT WRITE
├─ But can still read from others
└─ System stuck in read-only mode!
```

#### Availability Probability

```
Assume each replica has 99.9% uptime (3-9s downtime/month)

Availability of single replica: 99.9% = 0.999
Availability of all 5 (need for write):
  = 0.999^5
  = 0.995 (about 99.5% uptime)
  = 3.6 hours downtime/month!

vs Read (need 1 of 5):
  = 1 - (0.001)^5
  = 1 - 10^-15
  ≈ 99.9999999999999% uptime
  = < 1 second downtime/month!

HUGE DIFFERENCE in availability!
```

#### When N=5, W=5, R=1 is Useful

**Use Case 1: Critical System with Read Cache**

```
Scenario: Banking with hot cache

Requirements:
├─ Writes: MUST succeed (strong consistency)
├─ Reads: MUST be fast (from cache)
├─ Replicas: For consistency, not read scale

Configuration N=5, W=5, R=1:
├─ Every write replicated to all 5
├─ Reads from local cache (R=1)
├─ All replicas have latest data
├─ Bank teller reads from cache instantly

Workflow:
├─ Customer deposits $100 → Must go to all 5 replicas
├─ System waits for all 5 ACK (slow but safe)
├─ Customer requests balance → Read from cache (fast)
└─ Cash consistent (always up-to-date)
```

**Use Case 2: Distributed Lock Coordination**

```
Scenario: Distributed consensus (like Raft/Paxos)

Requirements:
├─ Writes: Only leader writes (must reach all)
├─ Reads: From any replica
├─ Consistency: Strong (all see same log)

Configuration N=5, W=5, R=1:
├─ Write new log entry: reach all 5 followers
├─ Confirms all seen entry before committing
├─ Read from cache: any replica
└─ Guaranteed consistency

Example: Etcd (Kubernetes config store)
├─ Writes to Etcd: reach quorum (at least 3 of 5)
├─ Reads from Etcd: any replica
├─ Actually uses W=quorum (not all 5)
├─ But concept similar: strong write consistency
```

**Use Case 3: Shared State in Cluster**

```
Scenario: Cluster-wide shared state management

Requirements:
├─ Configuration must be exactly same everywhere
├─ Updates rare (not read-heavy)
├─ Reads cheap (use cache)

Configuration N=5, W=5, R=1:
├─ Change cluster configuration
├─ Broadcast to all 5 nodes
├─ All must ACK before proceeding
├─ Then read from any node with cache

Example: Kubernetes control plane
├─ Write: Apply to all etcd replicas
├─ Read: From any node (cached)
├─ Ensures cluster state consistent
```

#### Performance Characteristics

```
N=5, W=5, R=1:

Write Performance:
├─ Latency: max(5 replicas) = very slow
├─ Typical: 100-500ms (cross-datacenter)
├─ Must wait for slowest replica
├─ Bottleneck: network latency
├─ Throughput: very low (waits for all)

Read Performance:
├─ Latency: 1 replica = very fast
├─ Typical: 1-10ms (cache hit)
├─ Immediately return
├─ No waiting for others
├─ Throughput: very high

Example timing:
├─ US: 10ms latency
├─ EU: 100ms latency
├─ ASIA: 150ms latency
├─ Write must wait for ASIA: 150ms+
├─ Read can use nearest: 10ms
└─ Write is 15x slower!
```

#### Comparison: All Three Configurations

| Config | W | R | N | Write Avail | Read Avail | Use Case |
|--------|---|---|---|------------|-----------|----------|
| **Strong CP** | 3 | 3 | 5 | ✓ Moderate | ✓ Moderate | Banking |
| **Write Fast** | 1 | 5 | 5 | ✓✓ Excellent | ✗ Poor | Backups |
| **Read Fast** | 5 | 1 | 5 | ✗ Poor | ✓✓ Excellent | Cache layer |

#### Problems with N=5, W=5, R=1

**Problem 1: Cascading Failure**

```
Scenario: 1 replica slow (not down, just lagging)

Timeline:
├─ T=0ms: Send write to all 5
├─ T=10ms: Replica 1,2,3,4 ACK
├─ T=1000ms: Replica 5 (WAN link) still processing
├─ T=1050ms: Replica 5 finally ACK
├─ Write returns after 1050ms

Impact:
├─ Users waiting 1+ second for write
├─ All subsequent reads delayed
├─ System feels unresponsive
├─ May timeout (user cancels)
└─ Cascading failure
```

**Problem 2: Network Partition**

```
Scenario: 1 partition has 4 nodes, 1 partition has 1 node

Partition A (4 nodes):
├─ Can write? NO (need all 5, only have 4)
├─ Can read? YES
└─ Stuck in read-only mode

Partition B (1 node):
├─ Can write? NO (need all 5, only have 1)
├─ Can read? YES
└─ Stuck in read-only mode

Result: Entire system unavailable for writes!
```

#### Mitigation Strategies

**Strategy 1: Use Quorum Instead**

```
Instead of N=5, W=5, R=1
Use: N=5, W=3, R=3

Benefits:
├─ Write only need 3 (not all 5)
├─ Can tolerate 2 failures
├─ Much higher availability
├─ Trade-off: Slightly longer read (check 3 replicas)
```

**Strategy 2: Read Your Own Write**

```
After write completes, read from:
├─ Replica that ACK the write
├─ Not from random replica
├─ Ensure read sees own write

Implementation:
├─ Track which replica has latest write
├─ Client read from that replica
├─ Even if other replicas behind
```

**Strategy 3: Leader-Based**

```
Use one leader (write) + followers (read):
├─ Write to leader + 2 followers (W=3)
├─ Read from any follower (R=1)
├─ Better availability than W=5, R=1
├─ Leader acts as buffer/cache
```

#### Kesimpulan Pertanyaan 3

```
N=5, W=5, R=1 IMPLICATIONS:
════════════════════════════════════════════════════════

✗ SEVERE AVAILABILITY PROBLEMS:

✗ Write Availability:
  ├─ Requires ALL 5 replicas alive
  ├─ Zero failure tolerance
  ├─ 99.5% uptime (not 99.9%+)
  ├─ 1 replica down = writes fail
  ├─ SPOF for write path

✗ Write Latency:
  ├─ Must wait for slowest replica
  ├─ Cross-datacenter = very slow
  ├─ Tail latency problem
  └─ Cascading failures possible

✓ Read Performance:
  ├─ Fast (only check 1 replica)
  ├─ High throughput
  ├─ Low latency

Use only when:
  ✓ Writes very rare
  ✓ Reads very frequent
  ✓ Failure tolerance unimportant
  ✓ Can afford downtime for writes

BETTER ALTERNATIVE:
  ✓ Use N=5, W=3, R=3 (balanced)
  ✓ Or N=5, W=1, R=5 (disaster recovery)
  ✓ Or leader + followers (practical)
```

---

## 🎯 RINGKASAN SEMUA LAB

### Lab 1: Raft Leader Election ✅
- **Q1:** Min 3 nodes (majority dari 5)
- **Q2:** Entry hilang jika crash sebelum majority ACK
- **Q3:** Log up-to-date check menjamin leader completeness

### Lab 2: CRDT G-Counter ✅
- **Q1:** G-Counter grow-only, PN-Counter untuk decrement
- **Q2:** Commutativity → merge order tidak penting
- **Q3:** Real examples: Apple Notes, VS Code Live Share

### Lab 3: 2PC vs Saga ✅
- **Q1:** 2PC blocking karena in-doubt state
- **Q2:** 3PC tambah Phase 2 untuk recovery
- **Q3:** Saga lacks Isolation (I), mitigasi dengan orchestrator

### Lab 4: Quorum Analysis ✅
- **Q1:** W=3, R=3, N=5 → Strong consistency (CP)
- **Q2:** W=1, R=5 → Write-fast (untuk backups)
- **Q3:** W=5, R=1 → Read-fast tapi write-unavailable

---

**Setiap jawaban dilengkapi contoh praktik dan implementasi di simulator! 🚀**
