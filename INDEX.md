# 📑 INDEX - SEMUA DOKUMENTASI LAB

## 📚 Struktur Dokumentasi

```
Raft Simulator/
├── README.md                    # Overview project & setup
├── SOLUSI_SEMUA_LAB.md         # ⭐ SOLUSI LENGKAP (2,880 baris)
├── PANDUAN_CEPAT.md            # ⭐ RINGKASAN SINGKAT
├── app.py                       # Flask backend
│
├── raft/
│   ├── node.py                 # Raft node implementation
│   └── cluster.py              # 5-node cluster
│
├── crdt/
│   ├── g_counter.py            # G-Counter (grow-only)
│   ├── pn_counter.py           # PN-Counter (inc+dec)
│   ├── version_vector.py       # Causal ordering
│   └── simulator.py            # CRDT simulation
│
├── transactions/
│   ├── two_phase_commit.py     # 2PC coordinator & participants
│   └── saga.py                 # Saga orchestrator
│
└── templates/
    ├── lab1-raft.html          # Interactive Raft simulator
    ├── lab2-crdt.html          # Interactive CRDT simulator
    ├── lab3-2pc.html           # 2PC vs Saga comparison
    └── lab4-quorum.html        # Quorum calculator
```

---

## 🎯 Navigasi Cepat

### Untuk Belajar Konsep
1. Baca: `PANDUAN_CEPAT.md` (5 min read)
2. Practice: Buka simulator di browser
3. Deep dive: `SOLUSI_SEMUA_LAB.md` (detailed explanation)

### Untuk Persiapan Ujian
1. Review: `PANDUAN_CEPAT.md` - poin kunci
2. Study: `SOLUSI_SEMUA_LAB.md` - setiap pertanyaan + jawaban
3. Test: Jalankan simulator, eksperimen dengan skenario

### Untuk Referensi Cepat
- **Lab 1**: Majority voting, quorum, election safety
- **Lab 2**: Commutativity, CRDT properties, PN-Counter
- **Lab 3**: 2PC blocking, 3PC recovery, Saga compensation
- **Lab 4**: Quorum math, W+R>N, consistency levels

---

## 📋 Isi File SOLUSI_SEMUA_LAB.md

### Lab 1: Raft Leader Election (600+ baris)
```
├─ Q1: Minimum nodes for election
│  └─ Konsep quorum, skenario test, tabel fault tolerance
├─ Q2: Leader crash saat append entries
│  └─ Entry lifecycle, majority ACK requirement, testing steps
└─ Q3: Up-to-date log check
   └─ Candidate election safety, scenarios, proof
```

### Lab 2: CRDT G-Counter (800+ baris)
```
├─ Q1: G-Counter vs PN-Counter
│  └─ Structure, why grow-only, PN-Counter mechanism
├─ Q2: Commutativity importance
│  └─ Definition, scenarios, network implications
└─ Q3: Real-world applications
   └─ Apple Notes, VS Code, AWS examples
```

### Lab 3: 2PC vs Saga (950+ baris)
```
├─ Q1: Blocking problem & in-doubt state
│  └─ 2PC phases, blocking timeline, participant state machine
├─ Q2: 3PC solution
│  └─ Pre-commit phase, recovery rules, limitations
└─ Q3: Saga lacks Isolation
   └─ ACID analysis, isolation levels, mitigation strategies
```

### Lab 4: Quorum Analysis (530+ baris)
```
├─ Q1: N=5, W=3, R=3 (Strong Consistency)
│  └─ Verification, failure analysis, use cases
├─ Q2: N=5, W=1, R=5 (Write-Fast)
│  └─ Durability focus, disaster recovery, performance
└─ Q3: N=5, W=5, R=1 (Read-Fast)
   └─ Availability implications, problems, mitigation
```

---

## 🌐 Akses Simulator (Live)

### URLs
```
http://localhost:5000/lab1       ← Raft interactive simulator
http://localhost:5000/lab2       ← CRDT with merge visualization
http://localhost:5000/lab3       ← 2PC vs Saga pattern
http://localhost:5000/lab4       ← Quorum calculator
```

### Status
- ✅ Lab 1 (Raft): Complete & Tested
- ✅ Lab 2 (CRDT): Complete & Tested
- ✅ Lab 3 (2PC/Saga): Complete & Tested
- ✅ Lab 4 (Quorum): Complete & Tested

---

## 📚 Buku Referensi Rekomendasi

### Untuk Raft
- "Raft Consensus Algorithm" - https://raft.github.io/
- "In Search of an Understandable Consensus Algorithm"

### Untuk CRDT
- "CRDT: Conflict-free Replicated Data Types" - https://crdt.tech/
- "A Conflict-Free Replicated JSON Datatype"

### Untuk Distributed Systems
- "Designing Data-Intensive Applications" - Martin Kleppmann
- "Google Spanner: Becoming a SQL System"
- "Amazon Aurora: Design Considerations"

---

## 💡 Tips Belajar

### Strategi 1: Konsep → Simulator → Kode
1. Pahami teori (baca PANDUAN_CEPAT)
2. Eksperimen di simulator
3. Baca kode implementasi (app.py, raft/, crdt/, transactions/)
4. Buat skenario sendiri

### Strategi 2: Problem-Based Learning
1. Baca pertanyaan di SOLUSI_SEMUA_LAB
2. Coba jawab sendiri
3. Bandingkan dengan solusi
4. Test di simulator

### Strategi 3: Skenario-Based
1. Pilih skenario (e.g., "Network partition dengan 3-2 split")
2. Prediksi apa yang terjadi
3. Test di simulator
4. Analisis hasil

---

## 🎓 Checklist Persiapan Ujian

### Konsep Raft
- [ ] Pahami majority voting (quorum)
- [ ] Tahu 3 states: follower, candidate, leader
- [ ] Mengerti term + term comparison
- [ ] Log replication mechanism
- [ ] Leader election safety
- [ ] Leader completeness guarantee

### Konsep CRDT
- [ ] G-Counter adalah grow-only
- [ ] PN-Counter = P - N
- [ ] Commutativity vs Associativity
- [ ] Version vector untuk causal ordering
- [ ] Merge adalah idempotent
- [ ] Real-world examples (Notes, Figma, etc)

### Konsep 2PC
- [ ] 2 phases: Prepare + Commit
- [ ] Participant states: INITIAL → PREPARED → COMMITTED
- [ ] In-doubt state masalah
- [ ] Blocking problem explanation
- [ ] 3PC add Pre-Commit phase
- [ ] Saga sebagai alternatif

### Konsep Quorum
- [ ] W+R > N = strong consistency
- [ ] Max write failures = N-W
- [ ] Max read failures = N-R
- [ ] Consistency classification
- [ ] Trade-offs: availability vs consistency
- [ ] Practical configurations

---

## 📞 Support

### Jika ada error di simulator:
```bash
# Terminal
pkill -f "python app.py"
python app.py
# Refresh browser
```

### Jika ada pertanyaan:
- Review SOLUSI_SEMUA_LAB.md terlebih dulu
- Check browser console (F12) untuk JavaScript errors
- Verify Flask server running: `curl http://localhost:5000/`

---

**Status: ✅ SEMUA LAB SIAP UNTUK UJIAN**

Last updated: 2026-05-18
Files: 3 (README + 2 solution guides + 4 lab implementations)
Total lines: 2,880+ (SOLUSI_SEMUA_LAB) + 150+ (PANDUAN_CEPAT)
