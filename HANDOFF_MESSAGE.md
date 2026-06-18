# Welcome to the Spire 3.0.0 Bug Burndown Dashboard!

You've been handed off ownership of this dashboard. **Don't worry** - it's designed to be low-maintenance and Claude is here to help you every step of the way.

---

## 🎯 What You Just Inherited

An **automated bug tracking dashboard** that updates itself 3 times a day and deploys to GitHub Pages. It tracks Spire 3.0.0 release bugs with visual projections showing whether the team is on track to hit zero bugs by Code Freeze.

**Live Dashboard**: https://DaniloFortis.github.io/spire-burndown-3-0/

**How much work is this?**
- **Daily**: Nothing! It's fully automated.
- **Weekly**: ~5 minutes to verify it's working correctly.
- **Monthly**: ~15 minutes to review trends and data quality.

---

## 🤖 Your New Best Friend: Claude

You're reading this in Claude Code, which means **Claude already has full context** about this entire project. Claude has read all the documentation, understands how everything works, and can help you with anything.

### Start Here - Ask Claude:

Open this project in Claude Code and try these commands:

**First time setup:**
> "Help me set up this burndown dashboard"

**Understand what you're looking at:**
> "Explain this dashboard to me"
> "What do the three projection lines mean?"
> "Show me the current metrics"

**Check if it's working:**
> "Are the automated updates running?"
> "Verify the dashboard is up to date"

**When something breaks:**
> "The dashboard isn't updating, help me debug"
> "GitHub Actions failed, what should I do?"

**Make changes:**
> "How do I update the milestone dates?"
> "Change the automation to run 4 times daily instead of 3"

Claude will walk you through everything step-by-step.

---

## 📚 Essential Documentation

Claude has already read all of these, but you should too:

1. **CLAUDE.md** ⭐ **START HERE** ⭐
   - Complete project overview
   - What every file does
   - Common Claude commands
   - How everything works

2. **SETUP.md** - Initial setup walkthrough
   - Prerequisites
   - Step-by-step installation
   - Verification checklist

3. **MAINTENANCE.md** - Daily operations
   - What runs automatically (everything!)
   - Weekly tasks
   - Monthly tasks
   - How to manually update if needed

4. **TROUBLESHOOTING.md** - When things break
   - Common issues and fixes
   - Error reference table
   - "Ask Claude first" for everything

5. **HANDOFF_CHECKLIST.md** - Onboarding guide
   - Setup checklist
   - First week learning plan
   - Success criteria

---

## 🚀 Your First 30 Minutes

### Step 1: Clone and Setup (10 min)

```bash
git clone https://github.com/DaniloFortis/spire-burndown-3-0.git
cd spire-burndown-3-0
pip install -r requirements.txt
```

**Or just ask Claude:**
> "Set up this dashboard for me"

### Step 2: View the Dashboard (5 min)

1. **Online**: https://DaniloFortis.github.io/spire-burndown-3-0/
2. **Locally**: 
   ```bash
   python generate_burndown_projection_chart.py
   # Open spire_3_0_projection_dashboard.html
   ```

**Or ask Claude:**
> "Show me the dashboard"

### Step 3: Verify Automation (5 min)

Check that automatic updates are running:
- Visit: https://github.com/DaniloFortis/spire-burndown-3-0/actions
- Look for ✅ green checkmarks (recent runs)

**Or ask Claude:**
> "Check if automation is working"

### Step 4: Ask Questions (10 min)

Now that you've seen it, ask Claude:
> "What are the most important things I need to know?"
> "What breaks most often?"
> "What should I monitor weekly?"

---

## ✅ How to Know You're Doing It Right

**After your first week, you should be able to:**
1. View the live dashboard and understand what the 3 lines mean
2. Check if automated updates are running (GitHub Actions tab)
3. Manually regenerate the dashboard if needed
4. Ask Claude for help when something's unclear

**That's it!** You don't need to understand Python, GitHub Actions, or Plotly. Claude knows all that.

---

## 🆘 When You Need Help

**First, ask Claude** (seriously, Claude is faster than Googling):
> "I'm stuck on [X], help me"
> "This error appeared: [paste error]"
> "Walk me through [task]"

**If Claude can't solve it:**
1. Check `TROUBLESHOOTING.md` - covers 90% of issues
2. Check GitHub Actions logs for errors
3. Contact the previous owner (if available)

**Emergency fallback** (if dashboard is broken and you can't fix it):
```bash
# Disable automation (stop it from breaking repeatedly)
# Go to: Settings → Actions → General → "Disable Actions"

# Update manually once while you debug
python update_today_burndown.py
```

---

## 💡 Pro Tips

1. **The dashboard updates itself** - You almost never need to run scripts manually
2. **Weekend plateaus are normal** - Lines stay flat Sat/Sun (no work expected)
3. **Bugs marked "WON'T FIX" don't count** - They're excluded from active counts
4. **GitHub Pages takes 1-2 min to deploy** - Be patient after pushing
5. **Claude has full project context** - Seriously, just ask Claude anything

---

## 🎯 Your Mission

**Keep the dashboard running** so the team can track bug progress toward Code Freeze.

- If it's working (updates 3x daily, shows current data) → You're doing great!
- If it breaks → Ask Claude to help you fix it
- If you want to change something → Ask Claude how to do it

**Remember**: This dashboard was designed to be low-maintenance. You shouldn't be spending hours on this. If you are, ask Claude: "This is taking too long, help me simplify it."

---

## 📞 Quick Reference

| What You Need | Where to Look |
|---------------|---------------|
| How does this work? | Ask Claude: "Explain the dashboard" |
| First time setup | SETUP.md or ask Claude |
| Is automation working? | https://github.com/DaniloFortis/spire-burndown-3-0/actions |
| Live dashboard | https://DaniloFortis.github.io/spire-burndown-3-0/ |
| Common issues | TROUBLESHOOTING.md |
| Full project overview | CLAUDE.md |

---

## 🎉 You've Got This!

This dashboard is designed to be **hands-off and resilient**. It updates itself, deploys automatically, and has comprehensive documentation.

**Your job**: Check in weekly, make sure it's working, and ask Claude if anything seems weird.

**Claude's job**: Help you understand it, debug issues, and make changes.

**The dashboard's job**: Track bugs and project when they'll hit zero.

---

**Ready to get started?**

Ask Claude:
> "I'm the new owner of this dashboard. Walk me through what I need to know."

Claude will take it from there. Welcome aboard! 🚀
