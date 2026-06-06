# Contributing Guide — Team Workflow

## Branch Strategy

We use a simple **feature branch → pull request → main** workflow.
Nobody pushes directly to `main`. Ever.

```
main
├── dev                        ← integration branch (merge here first)
│   ├── feature/ganesh-embedder
│   ├── feature/rajesh-feature-extractor
│   └── feature/sahitya-behavioral
```

---

## Branch Naming Rules

| Who | Branch Name |
|-----|-------------|
| Sravan | `feature/sravan-scorer` |
| Ganesh | `feature/ganesh-embedder` |
| Rajesh | `feature/rajesh-feature-extractor` |
| Sahitya | `feature/sahitya-behavioral` |

Use exactly these names. No spaces. No capitals.

---

## Daily Git Workflow (Step by Step)

### First time setup (do this once)

```bash
# Clone the repo
git clone https://github.com/sravanyadav-19/redrob-intelligent-candidate-ranking.git
cd redrob-intelligent-candidate-ranking

# Set your identity
git config user.name "Your Name"
git config user.email "your@email.com"

# Create and switch to your branch
git checkout -b feature/your-branch-name

# Push your branch to GitHub
git push -u origin feature/your-branch-name
```

---

### Every day — Start of work

```bash
# Always start by syncing with latest dev
git checkout dev
git pull origin dev

# Switch back to your branch
git checkout feature/your-branch-name

# Merge latest dev into your branch
git merge dev
```

---

### Every day — End of work (save your progress)

```bash
# See what you changed
git status

# Stage all your changes
git add .

# Commit with a clear message
git commit -m "feat: describe what you did today"

# Push to GitHub
git push origin feature/your-branch-name
```

---

### When your task is complete — Open a Pull Request

1. Go to: `https://github.com/sravanyadav-19/redrob-intelligent-candidate-ranking`
2. Click **"Compare & pull request"** on your branch
3. Set:
   - **Base branch:** `dev` (NOT main)
   - **Title:** `[Ganesh] Embedder module complete` (use your name)
   - **Description:** What you built, what the output file is, any known issues
4. Assign **Sravan** as reviewer
5. Click **"Create pull request"**
6. Wait for Sravan to review and merge — do NOT merge yourself

---

## Commit Message Format

Use this format for every commit:

```
type: short description of what you did
```

| Type | When to use |
|------|-------------|
| `feat:` | Added new code / feature |
| `fix:` | Fixed a bug |
| `docs:` | Updated README or comments |
| `test:` | Added or fixed tests |
| `refactor:` | Cleaned up code, no new features |
| `data:` | Changes to data processing scripts |

**Examples:**
```
feat: add cosine similarity computation for all candidates
fix: handle null summary field in parser
docs: update README with run instructions
refactor: clean up feature extractor logic
```

---

## Rules

1. **Never push to `main` directly** — always go through a PR
2. **Never commit `candidates.jsonl`** — it is gitignored, keep it local
3. **Never commit model weights or `.pkl` files** — too large
4. **Always pull before you start working** — avoids conflicts
5. **One task per branch** — don't mix your work with someone else's

---

## What To Do If You Get a Conflict

```bash
# When merge conflict happens
git status          # see which files have conflicts

# Open the conflicted file — look for:
# <<<<<<< HEAD
# your code
# =======
# their code
# >>>>>>> dev

# Keep the correct version, delete the markers
# Then:
git add .
git commit -m "fix: resolve merge conflict in filename.py"
git push origin feature/your-branch-name
```

If you're confused — **message Sravan before doing anything else.**

---

## File Ownership (who touches what)

| File | Owner | Others |
|------|-------|--------|
| `src/pipeline.py` | Sravan | Do not touch |
| `src/scorer.py` | Sravan | Do not touch |
| `src/embedder.py` | Ganesh | Only Ganesh edits |
| `src/parser.py` | Ganesh | Only Ganesh edits |
| `src/feature_extractor.py` | Rajesh | Only Rajesh edits |
| `src/behavioral_signals.py` | Sahitya | Only Sahitya edits |
| `src/reasoning.py` | Sahitya | Only Sahitya edits |
| `README.md` | Sravan | Others can suggest via PR |
| `requirements.txt` | Sravan | Message Sravan if you need a new package |

---

## Quick Reference Card

```bash
# Clone (once)
git clone https://github.com/sravanyadav-19/redrob-intelligent-candidate-ranking.git

# Daily start
git checkout dev && git pull origin dev
git checkout feature/your-branch && git merge dev

# Save work
git add . && git commit -m "feat: what I did" && git push origin feature/your-branch

# Check status anytime
git status
git log --oneline -5
```
