# Sevasetu: Smart Resource Allocation & Volunteer Coordination

**AI-powered platform that transforms scattered community data into actionable insights, intelligently matching volunteers with tasks and optimizing resource allocation for measurable social impact.**

---

## 🎯 Problem Statement

### The Challenge
Local social groups and NGOs collect critical information about community needs through paper surveys and field reports. However:

- **Data is scattered** across different places—impossible to see the biggest problems clearly
- **Volunteers exist but are not matched** to where they're actually needed  
- **Resources are allocated inefficiently**—no data-driven allocation strategy
- **Impact is unmeasured**—no clear feedback loop to improve future decisions
- **Trust is low**—no transparency in how donations and resources are used

**Result:** Massive inefficiency in social impact despite good intentions.

---

## 💡 Our Solution: Sevasetu

An **AI-powered operating system** that converts unstructured real-world chaos into structured, actionable workflows.

```
Problem (Unstructured Data)
    ↓
Verification (AI + Validation)
    ↓
Task Creation (Structured Workflow)
    ↓
Smart Matching (Volunteers ↔ Tasks)
    ↓
Resource Allocation (Intelligence-Driven)
    ↓
Execution + Proof (Tracked & Transparent)
    ↓
Impact Measurement (Real-Time Analytics)
```

---

## 🏗️ System Architecture: 5 Interconnected Layers

### **1. User Layer** 👥
- **Communities** report problems with location & details
- **Volunteers** discover and execute tasks near them
- **NGO Members** manage operations & resources
- **NGOs** control resources and verify solutions

### **2. Problem Intelligence Layer** 🧠
- Problems submitted with **proof** (images, documents)
- **AI categorizes** issues by type, urgency, location
- **Duplicate detection** prevents redundant work
- **NGO verification** adds credibility

### **3. Execution Layer** 📋
- Problems → Tasks (automated conversion)
- Tasks → Volunteers (smart matching via AI)
- Real-time progress tracking
- Proof upload on completion

### **4. Resource Layer** 📦
- **Central inventory** of NGO resources
- **Task requirements** defined explicitly
- **Smart allocation** algorithm matches needs ↔ supply
- **Usage tracking** in real-time

### **5. Financial Layer** 💰
- Transparent donation tracking
- Ledger-based fund management
- Expenses linked to specific tasks
- Trust + accountability

---

## 🤖 AI Integration (The Differentiator)

### Problem Intelligence
- **Categorization**: Auto-tags problems (health, infrastructure, education, etc.) using Gemini
- **Urgency Detection**: Prioritizes critical issues using NLP
- **Duplicate Finding**: Prevents redundant task creation

### Matching Engine
- **Volunteer-Task Matching**: Considers skills, location, availability
- **Resource-Task Matching**: Allocates inventory intelligently
- **Geo-Location Proximity**: Haversine distance algorithm (15km radius matching)
- **Real-Time Optimization**: Adjusts assignments as new data arrives

### Analytics & Monitoring
- **Impact Measurement**: Tracks completion rates, volunteer satisfaction
- **Bottleneck Detection**: Flags delayed tasks, underutilized resources
- **Performance Insights**: Dashboards for NGO decision-makers

### Continuous Learning
- Learns from task completion patterns
- Improves volunteer-task matching over time
- Optimizes resource allocation based on outcomes

---

## ✨ Key Features

| Feature | Impact |
|---------|--------|
| **Multi-Role Dashboard** | Communities, Volunteers, NGO staff, Admins—all have tailored views |
| **Geo-Location Matching** | Volunteers see tasks within 15km radius (location-aware matching) |
| **AI Problem Categorization** | Auto-detects problem types; instant prioritization |
| **Resource Inventory** | Central management; prevents over-allocation & waste |
| **Task Assignment Automation** | Auto-matches tasks to volunteers based on skills + location |
| **Proof of Work** | Photo/document upload on task completion (transparency) |
| **Real-Time Notifications** | Push alerts for assignments, task updates, donations |
| **Financial Transparency** | Ledger-based tracking; link donations to actual impact |
| **Volunteer Skills Survey** | Captures skills; improves future matching accuracy |

---

## 🛠️ Technical Stack

### Frontend
- **React + TypeScript** (Vite)
- **Tailwind CSS** for responsive UI
- **Axios** for API calls
- **Real-time notifications** system

### Backend
- **FastAPI** (Python) — modern, fast API framework
- **PostgreSQL** (Neon) — serverless relational database
- **SQLAlchemy** — ORM for clean queries
- **JWT Authentication** — secure role-based access
- **Gemini AI API** — LLM integration for problem categorization

### AI/ML
- **Gemini** — lightweight, fast problem categorization & NLP
- **Custom Matching Algorithm** — volunteer-task-resource optimization
- **Haversine Distance** — geo-location proximity matching (15km radius)

### Current Deployment
- **Frontend**: Vercel (serverless, auto-scaling)
- **Backend**: Render (managed container, auto-deploy from GitHub)
- **Database**: Neon PostgreSQL (serverless, auto-backup)

---

## 📊 How It Works (User Flow)

### **For Communities**
1. Report a problem (with location, details, proof image)
2. AI categorizes + prioritizes automatically
3. Watch as volunteers respond in real-time
4. Provide feedback on solution quality

### **For Volunteers**
1. Sign up → add skills + location
2. Browse tasks within 15km radius (location-aware discovery)
3. Accept a task → get assigned
4. Execute → upload proof → mark complete
5. Earn recognition + build portfolio

### **For NGOs**
1. Verify incoming problems
2. Create tasks from verified problems
3. Manage volunteer assignments intelligently
4. Allocate resources using smart algorithm
5. Track donations → link to real impact
6. View analytics dashboards

---

## 🚀 Why This Solution Wins

### **1. End-to-End System** 
Not just reporting, not just volunteers—**full pipeline from problem to solution**.

### **2. Intelligence-Driven** 
AI doesn't just categorize; it **actively matches** people ↔ tasks ↔ resources.

### **3. Data-Driven Decisions** 
Every action generates data; analytics improve future decisions.

### **4. Real-World Applicability** 
Built for **Indian NGOs** facing real infrastructure, health, education challenges.

### **5. Transparency** 
Financial ledger + task tracking = trust in organizations.

### **6. Scalability** 
Serverless architecture scales with demand; costs stay low.

---

## 🎯 Alignment With Hackathon Evaluation

### ✅ **Technical Merit (40%)**
- Robust FastAPI backend with proper error handling
- SQLAlchemy ORM + PostgreSQL for data integrity
- Real-time matching algorithm (haversine distance, skill-based)
- JWT authentication + role-based access control
- Gemini AI integration for intelligent categorization
- Clean, modular code structure with async support

### ✅ **User Experience (10%)**
- Intuitive multi-role dashboards (volunteer, NGO, admin)
- Real-time notifications (push alerts)
- Geo-location aware task discovery (15km radius)
- Seamless onboarding (registration → profile → task discovery)

### ✅ **Alignment With Cause (25%)**
- **Directly solves** problem statement: scattered data → actionable insights
- Volunteer coordination at scale with smart matching
- Measurable impact (task completion, resource usage, donations)
- Trust-building through transparency

### ✅ **Innovation & Creativity (25%)**
- AI-powered problem categorization (not manual)
- Intelligent matching algorithm (considers multiple factors)
- Resource allocation layer (most solutions ignore this!)
- Financial transparency (novel for this space)

---

## 🏃 How to Run Locally

### **Backend Setup**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
# Server runs on http://127.0.0.1:8000
```

### **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
# App runs on http://localhost:5173
```

### **Environment Variables**
Backend needs: `backend/.env` file with
```
NEON_DB=<your_postgres_url>
JWT_SECRET=<secret_key>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
YOUR_API_KEY=
AUTO_ASSIGN_INTERVAL_SECONDS=30
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=<your_email>
MAIL_PASSWORD=<your_app_password>
FRONTEND_ORIGINS=https://sevasetu.vercel.app
```

Frontend needs: `frontend/.env.local` with
```
VITE_API_BASE_URL=https://your-backend-url/api/v1
```

---

## 🌐 Live Deployment

- **Frontend**: https://sevasetu-ycap.vercel.app
- **Backend API**: https://sevasetu-ycap.onrender.com
- **API Documentation**: https://sevasetu-ycap.onrender.com/docs

---

## 📈 Future Roadmap

### **Phase 2: Enterprise Scaling & GCP Migration**

#### Migration to Google Cloud Platform
- [ ] **Cloud Run** (from Render) — containerized FastAPI backend with auto-scaling
- [ ] **Cloud SQL** — managed PostgreSQL with automated backups
- [ ] **Cloud Storage** — document/proof storage with CDN
- [ ] **Firestore** — real-time notification queue
- [ ] **Pub/Sub** — async task processing
- [ ] **Cloud AI/ML** — Vision API for proof validation, NLP for problem categorization
- [ ] **BigQuery** — data warehouse for impact analytics
- [ ] **Data Studio** — executive dashboards

**Why GCP?**
- Seamless AI/ML integration (Vertex AI, Vision API)
- Auto-scaling based on demand
- Reduced operational overhead
- Better compliance for Indian data (India region availability)

#### Additional Integrations
- [ ] SMS/WhatsApp integration (Twilio) for low-connectivity areas
- [ ] Offline-first mobile app (PWA)
- [ ] Advanced analytics dashboards

### **Phase 3: Intelligence Enhancement**
- [ ] Multi-language NLP (Hindi, Tamil, Kannada support)
- [ ] Computer vision for proof validation (auto-verify images)
- [ ] Predictive resource forecasting (ML model)
- [ ] Volunteer burnout detection + automated reassignment
- [ ] Demand forecasting for resource pre-positioning

### **Phase 4: Ecosystem & Mobile**
- [ ] Native Mobile app (iOS + Android)
- [ ] Blockchain ledger (immutable donation records)
- [ ] Third-party NGO API (marketplace)
- [ ] SMS-based task assignment (feature phone support)

---

## 📦 Submission Details

- **Problem Statement**: Smart Resource Allocation & Data-Driven Volunteer Coordination
- **Prototype Link**: https://sevasetu-daza.vercel.app (live MVP)
- **GitHub Repository**: https://github.com/Ayush-Gupta100/SevaSetu
- **Technical Stack**: React + TypeScript, FastAPI, PostgreSQL, Gemini AI
- **AI Integration**: Problem categorization, intelligent matching, resource optimization

---

## 👥 Team

**Google Solution Challenge 2026 India Submission**

Built with ❤️ by a passionate team dedicated to creating real social impact.


## 📞 Support

For questions or feedback:
- **GitHub**: https://github.com/Ayush-Gupta100/SevaSetu
- **Hackathon**: Google Solution Challenge 2026 India

---

**One-Liner**: An AI-powered platform that transforms scattered community data into actionable insights, intelligently matching volunteers with tasks and optimizing resource allocation for measurable social impact.
