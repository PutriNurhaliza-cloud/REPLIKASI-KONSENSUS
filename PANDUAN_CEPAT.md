# 📚 PANDUAN CEPAT - SOLUSI LAB 1-4

## 🎯 Ringkasan Singkat

### Lab 1: Raft Leader Election ✅

**Q1: Minimum node untuk election di 5 nodes?**
- ✅ **Jawaban: 3 nodes (majority)**
- Alasan: Majority = (5/2)+1 = 3
- Formula: Dapat toleransi N-M = 5-3 = 2 kegagalan

**Q2: Apa terjadi jika leader crash saat Append Entries?**
- ✅ **Jawaban: Entry hilang jika tidak majority ACK**
- Entry di leader tapi belum di-replicate ke majority → tidak di-commit
- Followers yang terima entry tetap simpan, tapi belum apply ke state machine

**Q3: Mengapa Raft tidak pilih node dengan log terpendek?**
- ✅ **Jawaban: Karena harus menjamin log completeness**
- Up-to-date check: vote hanya ke node dengan log terbaru (term & index)
- Mencegah committed entries hilang

---

### Lab 2: CRDT G-Counter ✅

**Q1: Mengapa G-Counter tidak bisa decrement? PN-Counter caranya?**
- ✅ **G-Counter**: Grow-only karena setiap node maintain counter sendiri
- ✅ **PN-Counter**: Gunakan 2 G-Counter (positive & negative)
  - Value = sum(positive) - sum(negative)
  - Solusi: Decrement → increment negative counter

**Q2: Jelaskan commutativity merge(A,B) = merge(B,A). Mengapa penting?**
- ✅ **Definisi**: Urutan merge tidak penting, hasil sama
- ✅ **Penting karena**: Network tidak menjamin urutan message
- Network delay, latency, partition → commutativity guarantee consistency

**Q3: 2 aplikasi CRDT di production?**
- ✅ **Apple Notes**: Sync across devices, offline edits merge otomatis
- ✅ **VS Code Live Share**: Real-time co-editing, no locks, fast

---

### Lab 3: 2PC vs Saga Pattern ✅

**Q1: Mengapa 2PC "blocking protocol"? Apa "in-doubt"?**
- ✅ **Blocking**: Participant tunggu coordinator commit/abort (resources locked)
- ✅ **In-doubt**: Participant voted YES tapi tidak terima final decision
- ❌ Jika coordinator crash → participant terkunci indefinite

**Q2: Bagaimana 3PC atasi blocking problem?**
- ✅ **3PC = 3 Phases**: Prepare → Pre-Commit → Commit
- Phase 2 PRE-COMMIT memberi sinyal ke participants bahwa siap commit
- Jika timeout di Phase 2, participants bisa commit sendiri (safe decision)

**Q3: Saga punya "ACD" tapi bukan "I" - implikasi?**
- ✅ **Punya**: Atomicity (via compensation), Consistency (eventual), Durability
- ❌ **Tidak punya**: Isolation - intermediate states visible
- ✅ **Mitigasi**: Saga orchestrator, idempotent operations, semantic locking

---

### Lab 4: Quorum Configuration Analysis ✅

**Q1: N=5, W=3, R=3 - Verifikasi W+R>N, max failures?**
```
✅ Verification: 3+3 = 6 > 5 ✓ VALID
✅ Max write failures: 5-3 = 2
✅ Max read failures: 5-3 = 2
✅ Consistency: STRONG (CP)
✅ Use case: Banking (ACID critical)
```

**Q2: N=5, W=1, R=5 - Kapan berguna?**
```
✅ Berguna untuk: WRITE-HEAVY workloads
✅ Write fast: 1 replica saja (W=1)
✅ Read comprehensive: semua replicas (R=5)
✅ Use cases: Backups, audit logs, disaster recovery
⚠️ Consistency: Eventual (may read stale data)
```

**Q3: N=5, W=5, R=1 - Implikasi availability?**
```
❌ Write availability: SANGAT RENDAH
  - Perlu semua 5 replicas hidup
  - 1 replica down = write FAILS
  - Uptime: 99.5% (not 99.9%)
  
✅ Read availability: SANGAT TINGGI
  - Hanya perlu 1 replicas
  - 4 replicas bisa down, read OK
  - Uptime: 99.99999%+
  
⚠️ Use case: Read cache layer dengan rare writes
❌ Tidak cocok untuk production write-heavy
```

---

## 📖 Aksess Lengkap

File solusi lengkap tersedia di:
```
SOLUSI_SEMUA_LAB.md (2,880 baris)
```

Berisi:
- ✅ Jawaban detail untuk setiap pertanyaan
- ✅ Penjelasan mendalam dengan diagram
- ✅ Langkah-langkah test di simulator
- ✅ Contoh skenario real-world
- ✅ Kesimpulan untuk setiap topik

---

## 🎓 Untuk Ujian - Poin Kunci

### Raft (Lab 1)
- [ ] Majority = (N/2)+1
- [ ] Quorum prevents split-brain
- [ ] Up-to-date check untuk log completeness
- [ ] Entry di-commit hanya setelah majority ACK

### CRDT (Lab 2)
- [ ] Commutativity adalah kunci distributed systems
- [ ] G-Counter = grow-only
- [ ] PN-Counter = 2 G-Counter (P - N)
- [ ] Version vector untuk track causal ordering

### 2PC vs Saga (Lab 3)
- [ ] 2PC = blocking (resources locked)
- [ ] In-doubt = waiting untuk coordinator
- [ ] 3PC = add Phase untuk recovery
- [ ] Saga = eventual consistency + compensation

### Quorum (Lab 4)
- [ ] W+R > N = strong consistency (CP)
- [ ] W+R ≤ N = eventual consistency (AP)
- [ ] Max write failures = N - W
- [ ] Max read failures = N - R

---

## 🚀 Akses Simulator

```
Lab 1 (Raft):      http://localhost:5000/lab1
Lab 2 (CRDT):      http://localhost:5000/lab2
Lab 3 (2PC/Saga):  http://localhost:5000/lab3
Lab 4 (Quorum):    http://localhost:5000/lab4
```

Semua sedang running di port 5000 ✅

---

**Created: 2026-05-18**
**Status: READY FOR EXAM**
