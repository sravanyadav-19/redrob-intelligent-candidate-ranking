# GitHub Repository Setup — Step by Step
# To be done by Sravan only (one time)

---

## Step 1 — Create the Repository on GitHub

1. Go to: https://github.com/new
2. Fill in:
   - **Repository name:** `redrob-intelligent-candidate-ranking`
   - **Description:** `Multi-signal AI candidate ranking system | Redrob Hackathon Track 1`
   - **Visibility:** ✅ Public (required for submission)
   - **Initialize:** ✅ Add a README (uncheck — we have our own)
3. Click **"Create repository"**

---

## Step 2 — Push This Workspace to GitHub

Run these commands on your local machine:

```bash
# Navigate to the project folder
cd redrob-intelligent-candidate-ranking

# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "feat: initial project structure and team setup"

# Connect to GitHub
git remote add origin https://github.com/sravanyadav-19/redrob-intelligent-candidate-ranking.git

# Push to main
git branch -M main
git push -u origin main
```

---

## Step 3 — Create the `dev` Branch

```bash
# Create dev branch from main
git checkout -b dev
git push -u origin dev
```

---

## Step 4 — Protect the `main` Branch

1. Go to your repo on GitHub
2. Click **Settings** → **Branches**
3. Click **"Add branch protection rule"**
4. Branch name pattern: `main`
5. Check these options:
   - ✅ Require a pull request before merging
   - ✅ Require approvals (set to 1)
   - ✅ Do not allow bypassing the above settings
6. Click **Save changes**

Repeat for `dev` branch — same settings.

---

## Step 5 — Add Collaborators

1. Go to **Settings** → **Collaborators**
2. Click **"Add people"**
3. Add these GitHub usernames one by one:
   - `GorantlaGanesh` → Role: **Write**
   - `rayesh8468` → Role: **Write**
   - `saisahitya-19` → Role: **Write**
4. They will receive an email invite — they must accept it

---

## Step 6 — Create Feature Branches (do this after collaborators accept)

```bash
# Ganesh's branch
git checkout dev
git checkout -b feature/ganesh-embedder
git push -u origin feature/ganesh-embedder

# Rajesh's branch
git checkout dev
git checkout -b feature/rajesh-feature-extractor
git push -u origin feature/rajesh-feature-extractor

# Sahitya's branch
git checkout dev
git checkout -b feature/sahitya-behavioral
git push -u origin feature/sahitya-behavioral

# Your own branch
git checkout dev
git checkout -b feature/sravan-scorer
git push -u origin feature/sravan-scorer

# Go back to dev
git checkout dev
```

---

## Step 7 — Share With Team

Send each member:
1. The repo link: `https://github.com/sravanyadav-19/redrob-intelligent-candidate-ranking`
2. The `CONTRIBUTING.md` file — their complete workflow guide
3. Their specific branch name
4. Tell them: accept the GitHub collaborator invite from their email first

---

## Final Branch Structure After Setup

```
main        ← production, judges see this
└── dev     ← integration, everyone merges here
    ├── feature/sravan-scorer
    ├── feature/ganesh-embedder
    ├── feature/rajesh-feature-extractor
    └── feature/sahitya-behavioral
```

---

## Repo Settings Checklist

- [ ] Repo is Public
- [ ] `main` branch protected (requires PR + 1 approval)
- [ ] `dev` branch protected (requires PR + 1 approval)
- [ ] All 3 collaborators added and accepted
- [ ] All 4 feature branches created
- [ ] `.gitignore` is committed (candidates.jsonl will never be pushed)
- [ ] README is visible on repo homepage
