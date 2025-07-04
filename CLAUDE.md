# AI Agent Project - Claude Collaboration Guide

**Version:** 1.0 (Pragmatic MVP Edition)  
**Priority:** Keep it simple, ship it fast

---

## 🎯 Core Principles

1. **Build Something People Want** - Not what engineers admire
2. **Ship Weekly** - Progress over perfection
3. **One Agent First** - Master single use case before expanding
4. **User Feedback Loop** - Talk to users, not to architecture diagrams

---

## 📋 Development Workflow

### Step 1: Define User Story
```
As a [user type]
I want to [action]
So that [value]
```

### Step 2: Minimal Implementation
- Simplest code that works
- No premature optimization
- Focus on core value delivery

### Step 3: Deploy & Measure
- Deploy to real users immediately
- Measure actual usage
- Collect qualitative feedback

### Step 4: Iterate Based on Data
- Fix only what users complain about
- Add only what users request
- Optimize only proven bottlenecks

---

## 🛠 Tech Guidelines

### Code Style
- Prefer clarity over cleverness
- Use established patterns
- Write tests for critical paths only
- Document the "why", not the "what"

### Architecture
- Start monolithic, split when needed
- Use boring technology
- Minimize dependencies
- Choose libraries with good documentation

### AI Integration
- Start with one AI provider
- Implement fallback for failures
- Track token usage from day 1
- Cache responses aggressively

---

## 📝 Project Structure

```
aiagent/
├── src/
│   ├── api/          # API endpoints
│   ├── agent/        # AI agent logic
│   ├── services/     # Business logic
│   └── utils/        # Shared utilities
├── tests/            # Test files
├── docs/             # Documentation
└── scripts/          # Automation scripts
```

---

## ⚡ Quick Commands

```bash
# Development
npm run dev          # Start development server
npm run test         # Run tests
npm run build        # Build for production

# Deployment
npm run deploy       # Deploy to production
npm run rollback     # Rollback last deployment
```

---

## 🚨 Anti-Patterns to Avoid

Based on lessons learned:

❌ **DON'T**
- Over-engineer the architecture
- Build features nobody asked for
- Optimize before measuring
- Create complex abstractions
- Delay shipping for "perfection"

✅ **DO**
- Ship the simplest version first
- Talk to users constantly
- Measure everything
- Iterate based on feedback
- Keep the codebase simple

---

## 🎯 Success Criteria

Every feature must answer YES to:
1. Does a real user need this?
2. Can we ship it this week?
3. Can we measure its impact?
4. Is it the simplest solution?

---

## 📊 Metrics to Track

From Day 1:
- User sign-ups
- Feature usage (events)
- AI token costs
- User retention (daily/weekly)
- Time to first value
- Error rates
- User feedback sentiment

---

## 🔄 Iteration Cycle

**Monday**: Plan based on last week's data  
**Tuesday-Thursday**: Build and test  
**Friday**: Ship to production  
**Weekend**: Monitor and collect feedback  
**Repeat**: Every single week

---

Remember: **Perfect is the enemy of shipped**

Every line of code should be in service of delivering value to users, not impressing other developers.