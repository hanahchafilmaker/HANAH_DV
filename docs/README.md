
# 📚 논문 각주 자동 교정기 (Paper Footnote Correction Tool)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-blue?logo=python">
  <img src="https://img.shields.io/badge/Tkinter-GUI-green">
  <img src="https://img.shields.io/badge/Thread-Safe-ff6b6b">
  <img src="https://img.shields.io/badge/Architecture-Queue%20Dispatcher-orange">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen">
</p>

---

## 🧠 Overview

논문 각주 자동 교정기는 논문 내 각주를 분석하고 참고문헌과 자동 매칭하여
교정 작업을 지원하는 데스크톱 GUI 도구입니다.

Tkinter 기반이지만, 안정성을 위해 멀티스레드 + Queue Dispatcher 구조로 설계되었습니다.

---

## ✨ Key Features

### 📌 Footnote Intelligence

 자동 각주 추출
 구조화된 footnote parsing
 reference candidate ranking

### 📚 Reference Matching Engine

 Top-K 후보 생성
 DOI / ISBN 기반 매칭
 similarity scoring system

### 🧩 Interactive UI

 후보 선택 GUI
 실시간 결과 반영
 편집 가능한 reference panel

### 🛡 Stability First Design

 Thread-safe architecture
 Crash-resistant UI lifecycle
 Safe widget registry system

---

## 🧱 Architecture

<p align="center">

```text
Worker Threads
      ↓
   Queue (Event Bus)
      ↓
Main Thread Dispatcher
      ↓
UI Registry (Tkinter Widgets)
```

</p>

---

## 🏗 System Design

### 🔹 1. Data Layer (Pure Data Only)

```python
fn = {
    "fn_id": "FN_001",
    "fn_text": "..."
}
```

✔ NO widget allowed
✔ NO UI logic allowed

---

### 🔹 2. Event Layer (Thread-safe Queue)

```python
ui_queue.put(("update_candidate", fn_id, data))
```

✔ Worker threads only communicate via queue

---

### 🔹 3. UI Layer (Registry Pattern)

```python
ui_registry[fn_id] = {
    "frame": frame,
    "label": label
}
```

✔ Only main thread accesses UI widgets

---

### 🔹 4. Dispatcher (Single UI Entry Point)

✔ All UI updates go through main thread dispatcher
✔ Prevents race condition & invalid Tk calls

---

## 🚨 Stability Guarantees

### ❌ Prevented Issues

 `invalid command name` (Tkinter destroy crash)
 thread UI access violations
 uninitialized widget reference
 partial UI state corruption
 race condition during window close

---

### ✅ Safety Rules

 🧵 Worker thread → NEVER touch Tkinter
 📬 Communication → ONLY queue
 🧠 UI updates → ONLY dispatcher
 🧩 Widgets → ONLY UI registry
 📦 Data → fn is PURE DATA ONLY

---

## 🧪 How to Run

```bash
pip install -r requirements.txt
python main_gui.py
```

or

```bash
run_thesis.bat
```

---

## 📁 Project Structure

```text
논문_교정기/
│
├── main_gui.py              # GUI controller (dispatcher)
├── footnote_manager.py      # footnote parsing & matching engine
├── engine.py                # scoring & matching logic
├── footnote_editor.py      # UI editor module
│
├── tests/                  # unit tests
├── sample/                 # sample documents
├── dist/                   # build output
└── requirements.txt
```

---

## 🧠 Design Philosophy

> “UI is single-thread owned. Everything else communicates through messages.”

This project strictly separates:

 Data (fn)
 Logic (engine)
 UI (registry)
 Communication (queue)

---

## 🔥 Why This Architecture Matters

Tkinter is not thread-safe.

So this system guarantees:

✔ No direct cross-thread UI access
✔ No widget leakage into data layer
✔ No partial UI creation state
✔ No crash during window shutdown

---

## 🚀 Future Improvements

 UI Factory Pattern full refactor
 async pipeline for matching engine
 batch document processing mode
 performance caching layer
 candidate scoring ML upgrade

---

## 🧾 License


---

## 💬 Summary

> A robust, thread-safe academic footnote correction system built on Tkinter with a queue-driven UI architecture.

---
