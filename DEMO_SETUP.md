# Westval MVP - Demo Setup Guide

## 🚀 5-Minute Quick Start

This MVP showcases the core features of an enterprise validation management system built in record time using AI.

### Prerequisites
- Docker & Docker Compose installed
- Modern web browser (Chrome, Firefox, Edge)
- 8GB RAM minimum

### Step 1: Clone & Setup

```bash
# Clone repository
git clone https://github.com/vipul-madhani/westval.git
cd westval

# Copy environment file
cp .env.example .env
```

### Step 2: Start Services

```bash
# Start all services with Docker Compose
docker-compose up -d

# Wait for services to start (30 seconds)
sleep 30
```

### Step 3: Initialize Database

```bash
# Initialize database schema
docker-compose exec backend flask init-db

# Load demo data
docker-compose exec backend flask init-demo
```

### Step 4: Access Application

**Frontend:** http://localhost:3000

**Demo Login Credentials:**
- Email: `demo.validator@westval.com`
- Password: `Demo@2025!`

**Additional Users:**
- QA: `demo.qa@westval.com` / `Demo@2025!`
- Approver: `demo.approver@westval.com` / `Demo@2025!`
- Admin: `admin@westval.com` / `Admin@Westval2025!`

---

## 🎯 Demo Walkthrough for Pharma Companies

### 1. Dashboard (Main Screen)
**What to Show:**
- Real-time metrics (5 active projects, 198 tests passed)
- Compliance status indicators
- Project progress bars
- Quick action buttons

**Key Points:**
- "This dashboard provides at-a-glance visibility of all validation activities"
- "Compliance indicators show 21 CFR Part 11, EU Annex 11, and GAMP 5 status"
- "One-click access to all validation functions"

### 2. Workflow & Task Management
**Navigate to:** My Tasks (Bell icon)

**What to Show:**
- Pending approval tasks
- SLA tracking with due dates
- Overdue indicators
- Approve/Reject workflow

**Key Points:**
- "Multi-stage approval workflow with role-based routing"
- "Automatic workload balancing across team members"
- "SLA tracking with escalation for overdue tasks"
- "Every action is audit-trailed with WHO, WHAT, WHEN, WHY"

**Demo Action:**
1. Click on a pending task
2. Add comments
3. Click "Approve" to show workflow progression

### 3. Test Execution with Evidence Capture 🔥
**Navigate to:** Tests → Execute Test

**What to Show:**
- Step-by-step execution interface
- Pass/Fail/N/A selection per step
- Screenshot capture button
- Annotation tools (arrow, circle, rectangle, highlight)
- Real-time evidence timestamping
- Auto-save functionality

**Key Points:**
- "Contemporaneous evidence capture during test execution"
- "Screenshot annotation directly in the platform - no external tools needed"
- "Every piece of evidence is timestamped and linked to the user"
- "Fully 21 CFR Part 11 compliant with electronic signatures"

**Demo Action:**
1. Select test step
2. Click "Capture Evidence"
3. Take screenshot (or use demo screenshot)
4. Draw annotations (arrows, circles)
5. Add notes
6. Save - show timestamp and metadata
7. Mark step as Pass/Fail
8. Submit test execution

### 4. Interactive Traceability Matrix 🔥
**Navigate to:** Traceability Matrix

**What to Show:**
- Graph view with D3.js visualization
- Color-coded nodes (green=passed, red=failed, orange=not tested)
- Drag-and-drop interactive nodes
- Zoom functionality
- Gap analysis
- Coverage metrics (85% coverage)
- Table view toggle

**Key Points:**
- "Real-time traceability from requirements to test cases"
- "Automatic gap detection - highlights untested requirements"
- "Interactive visualization - drag nodes, zoom, explore relationships"
- "One-click drill-down to see requirement details"
- "Export to Excel for regulatory submissions"

**Demo Action:**
1. Show graph view - drag nodes around
2. Point out color coding
3. Highlight untested requirements (orange)
4. Switch to table view
5. Show coverage percentage
6. Click "Export" button

### 5. Reporting & Compliance
**Navigate to:** Reports

**What to Show:**
- Validation Summary Report
- Traceability Matrix Report
- Deviation Report
- Audit Package
- PDF export capability

**Key Points:**
- "Auto-generated reports ready for regulatory submission"
- "Complete audit package with all supporting documentation"
- "Deviation reports automatically track failed tests"
- "Export to PDF, Excel, or JSON"

### 6. Validation Project
**Navigate to:** Validation Projects

**What to Show:**
- ERP System CSV project (demo data)
- Project details, status, timeline
- Associated documents, protocols, test cases
- Risk assessment

---

## 🎨 Key Features Demonstrated

### ✅ Completed in MVP

1. **Workflow Engine**
   - Multi-stage approvals (Draft → Review → QA → Approve)
   - Role-based task routing
   - Workload balancing
   - SLA tracking
   - Escalation rules

2. **Screenshot Capture & Annotation** ⭐
   - Browser-based screenshot tool
   - Annotation tools: arrows, circles, rectangles, highlights
   - Notes and metadata
   - Timestamped evidence

3. **Test Execution** ⭐
   - Step-by-step execution UI
   - Pass/Fail/N/A per step
   - Evidence attachment per step
   - Auto-save
   - Real-time status updates

4. **Interactive Traceability Matrix** ⭐
   - D3.js force-directed graph
   - Color-coded status
   - Gap analysis
   - Coverage metrics
   - Table/Graph toggle
   - Export functionality

5. **Reporting**
   - Validation summary
   - Traceability reports
   - Deviation tracking
   - Audit packages
   - PDF/Excel export

6. **Compliance**
   - 21 CFR Part 11 architecture
   - Audit trail logging
   - Electronic signatures ready
   - Role-based access control

---

## 💡 Talking Points for Pharma Demos

### Opening Statement
"What you're seeing is a modern validation management platform built specifically for pharmaceutical and life sciences companies. Unlike legacy tools, this combines the best features of ValGenesis, Kneat, and HP ALM with modern AI capabilities."

### During Demo
- **Speed**: "This was built in 5 days using AI-assisted development - showing how modern technology can accelerate delivery"
- **Cost**: "Traditional validation tools cost $100K-$500K per year. This is a fraction of that cost"
- **Compliance**: "Built from the ground up with 21 CFR Part 11 and EU Annex 11 compliance"
- **Modern UX**: "Clean, intuitive interface - no training required unlike legacy tools"

### Handling Questions

**Q: "How does this compare to ValGenesis?"**
A: "We've implemented the core validation lifecycle features - workflow approvals, test execution with evidence capture, and traceability. What makes us different is modern technology, AI integration, and significantly lower cost."

**Q: "Is it 21 CFR Part 11 compliant?"**
A: "Yes. We have audit trails, electronic signatures, access controls, and data integrity built in. Every action is logged with WHO, WHAT, WHEN, WHY."

**Q: "Can it integrate with our existing systems?"**
A: "Yes. We have REST APIs and can integrate with Jira, Azure DevOps, LIMS, ERP systems. The architecture is designed for integration."

**Q: "What about mobile access?"**
A: "The web interface is mobile-responsive. Native mobile apps are in our roadmap for offline test execution."

**Q: "How long to implement?"**
A: "Typical implementation is 4-8 weeks including data migration, user training, and validation of the system itself."

---

## 📊 Demo Data Included

### Project: ERP System CSV - SAP Implementation
- **Status**: In Progress (85% complete)
- **Type**: Computer System Validation
- **Timeline**: 30 days in, 60 days remaining

### Requirements: 7 total
- REQ-001: User Authentication (Critical) ✅ Verified
- REQ-002: Data Export (High) ✅ Verified  
- REQ-003: Password Reset (Medium) ⚠️ Not Tested
- REQ-004: User Profile (Low) ✅ Verified
- REQ-005: Admin Dashboard (Critical) ❌ Failed
- REQ-006: Audit Trail (Critical) ✅ Verified
- REQ-007: Electronic Signatures (Critical) ✅ Verified

### Test Cases: 6 total
- 5 Passed
- 1 Failed (TC-004: Admin Dashboard Load)
- Shows realistic scenario with deviation

### Users
- John Smith (Validator)
- Sarah Johnson (QA Manager)
- Michael Davis (Head of Quality)

---

## 🔧 Troubleshooting

### Services won't start
```bash
# Check Docker status
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs frontend

# Restart services
docker-compose restart
```

### Database errors
```bash
# Reset database
docker-compose down -v
docker-compose up -d
docker-compose exec backend flask init-db
docker-compose exec backend flask init-demo
```

### Frontend not loading
```bash
# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

---

## 🎯 Next Steps After Demo

1. **Pilot Project** (4 weeks)
   - Select one validation project
   - Migrate existing data
   - Train 5-10 users
   - Run parallel with existing system

2. **Full Implementation** (8-12 weeks)
   - Complete data migration
   - Train all users
   - Validate the validation system (IQ/OQ/PQ)
   - Go live

3. **Customization** (Ongoing)
   - Custom workflows
   - Integration with your systems
   - Custom reports
   - Branding

---

## 📞 Support

For demo support or questions:
- GitHub Issues: https://github.com/vipul-madhani/westval/issues
- Documentation: See README.md and FEATURES.md

---

**Remember**: This MVP demonstrates core functionality. Full enterprise features (mobile apps, advanced integrations, offline mode) are in the roadmap and can be prioritized based on your needs.