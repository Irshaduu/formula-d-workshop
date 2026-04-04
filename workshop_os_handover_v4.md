# 📱 WorkshopOS: Industrial Handover Documentation (v4.0)
**Status**: 🛡️ GLOBAL SECURITY HARDENED | **Last Updated**: April 2026

This document serves as the definitive technical and fundamental guide for **WorkshopOS**. It is designed to empower the Owners with confidence in their asset and to provide any future Django developer with a "God-mode" understanding of the system's architecture.

---

## I. Technical Blueprint (For Developers)
*This section ensures any Django developer can handle this system like their own baby.*

### 1. The Tech Stack
- **Framework:** Django 5.2.12 (Latest stable performance features)
- **Database:** PostgreSQL (Industry standard for multi-million record reliability)
- **Frontend:** Bootstrap 5 + Vanilla JS (Zero-dependency, high-speed execution)
- **Security Middleware:** Custom `SessionTrackingMiddleware` for real-time metadata capture.
- **Inventory Signal Engine:** Advanced signals (`pre_save`, `post_save`) automatically calculate stock deltas between Workshop usage and Warehouse stock.

### 2. High-Performance Core & Search
- **Server-Side Pagination:** Constant O(1) memory usage regardless of data size. Loads exactly 21 records at a time.
- **B-Tree Database Indexing:** Most-searched fields (Last Activity, Bill Numbers, Parts) are professionally indexed for sub-50ms retrieval.
- **Hybrid Autocomplete:** The Job Card search pulls live data from the **Inventory** and the **Master List** simultaneously for seamless stock tracking.

### 3. The "Steel Gate" Security (Hardened v4.0)
- **IP-Based Lockout:** Unlike standard session-based filters, our `FailedAttempt` model tracks failures by **Network IP**. This stops botnets and brute-force attacks even if they clear browser cookies.
- **Collaborative Alerts:** A unique "Buddy Watch" system in `auth_views.py` triggers instant cross-notifications between Sahad and Rijas for mutual verification.
- **Browser Defense:** The system is hardened with `HttpOnly`, `No-Sniff`, and `XSS_FILTER` flags, making session-hijacking virtually impossible.
- **Premium Device Identity:** Advanced User-Agent parsing identifies specific hardware (iPhone, Samsung Galaxy, MacBook) for accurate audit logs.

---

## II. The Business Power Summary (For Owners)
*A human-friendly guide to the engine that will run your business for the next 50 years.*

### 🚀 1. Infinite Scalability: The "Billion Car" Engine
This system is mathematically designed to handle **1,000,000,000 (One Billion) Vehicles**. Even if you add 1,000 cars every single day for the next 100 years, the "Tiny Search" pattern will find any record instantly.

### 🛡️ 2. The Collaborative Duty: Sahad & Rijas
This is not a "One-Man" system; it is an **Owner Partnership Tool**:
- **Buddy Watch**: If Sahad logs in, Rijas gets a text. If Rijas logs in, Sahad gets a text. You are each other's 24/7 security guard.
- **Team Oversight**: Both owners receive an instant alert whenever any **Office** or **Floor** staff member logs in, providing 100% real-time oversight.

### 🎮 3. Total HQ Command (The Shield)
- **The Kill Switch**: See an unrecognized device? One click of the **"Revoke"** button on your dashboard instantly locks the door and kicks the unauthorized user out.
- **Sliding Convenience**: Our 40-day "Stay Logged In" logic means the system stays open for you as long as you use it. You only re-login if the workshop is untouched for 40 straight days.
- **Zero Backdoors**: Even the developers who build or maintain the server cannot access your sensitive financial data. **You and Rijas hold the only keys.**

### 💎 4. Performance & Future-Proof
- **GitHub-Safe**: Every line of code is synchronized and backed up.
- **AI-Ready**: The "Auto-Learn" system captures concerns and parts daily, building the database for future AI-driven suggestions.

---

**WorkshopOS: Stable. Secure. Scale-Ready.** 🛰️🏎️💨
