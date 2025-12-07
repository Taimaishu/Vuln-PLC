# GitHub Setup Instructions

This document explains how to push the Vulnerable PLC project to GitHub.

## Current Status

✅ Git repository initialized
✅ All files staged and committed
✅ Branch set to 'main'
✅ 67 files committed (17,066 lines of code)

## Step 1: Create GitHub Repository

1. Go to https://github.com
2. Click the "+" icon in top right → "New repository"
3. Fill in the details:
   - **Repository name**: `vulnerable-plc` (or your preferred name)
   - **Description**: Comprehensive ICS/SCADA Security Training Lab with 4 PLCs
   - **Visibility**: 
     - ⚠️ **Public** - Anyone can see and clone (recommended for educational projects)
     - **Private** - Only you and collaborators can see
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click "Create repository"

## Step 2: Configure Git Identity (First Time)

Set your git identity so commits are properly attributed:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Then amend the commit to use the correct identity:

```bash
cd /home/taimaishu/vulnerable_plc
git commit --amend --reset-author --no-edit
```

## Step 3: Add Remote and Push

After creating the repository on GitHub, you'll see commands like these:

```bash
cd /home/taimaishu/vulnerable_plc
git remote add origin https://github.com/YOUR_USERNAME/vulnerable-plc.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

### Using SSH (Recommended)

If you have SSH keys set up:

```bash
git remote add origin git@github.com:YOUR_USERNAME/vulnerable-plc.git
git push -u origin main
```

### Authentication

GitHub will prompt for authentication:
- **HTTPS**: Use a Personal Access Token (not password)
  - Create token at: https://github.com/settings/tokens
  - Select scopes: `repo` (full control of private repositories)
- **SSH**: Use your SSH key (no password prompt if key is in ssh-agent)

## Step 4: Verify Upload

After pushing, visit your repository URL:
```
https://github.com/YOUR_USERNAME/vulnerable-plc
```

You should see:
- README.md displayed on the homepage
- 67 files
- Full commit history
- License badge

## Step 5: Add Topics/Tags (Optional)

On your GitHub repository page:
1. Click "About" settings (gear icon)
2. Add topics/tags for discoverability:
   - `ics-security`
   - `scada`
   - `plc`
   - `modbus`
   - `security-training`
   - `penetration-testing`
   - `ctf`
   - `vulnerable-app`
   - `industrial-security`
   - `python`

## Step 6: Add Security Warning

GitHub will automatically add a security warning banner for repositories with "vulnerable" in the name, but you can also add one manually in Settings.

## Future Updates

When you make changes:

```bash
cd /home/taimaishu/vulnerable_plc
git add .
git commit -m "Description of changes"
git push
```

## Recommended Repository Settings

### Branch Protection (Optional)

For collaborative projects:
1. Settings → Branches → Add rule
2. Branch name pattern: `main`
3. Enable:
   - Require pull request reviews
   - Require status checks to pass

### Security

1. Settings → Security & analysis
2. Enable:
   - Dependency graph
   - Dependabot alerts
   - Code scanning (if using GitHub Advanced Security)

### Issues & Discussions

Consider enabling:
- Issues (for bug reports and feature requests)
- Discussions (for community Q&A)
- Wiki (for additional documentation)

## Clone Instructions (For Others)

Once published, others can clone with:

```bash
git clone https://github.com/YOUR_USERNAME/vulnerable-plc.git
cd vulnerable-plc
./install.sh
vuln-plc start
```

## Troubleshooting

### Permission Denied (publickey)

Set up SSH keys:
```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
cat ~/.ssh/id_ed25519.pub
```

Add the public key to GitHub: Settings → SSH and GPG keys → New SSH key

### Authentication Failed (HTTPS)

Create a Personal Access Token:
1. GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: `repo`
4. Use token as password when prompted

### Large Files Warning

If you get warnings about large files:
```bash
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch PATH_TO_LARGE_FILE' \
  --prune-empty --tag-name-filter cat -- --all
```

## Security Considerations

⚠️ **Before pushing to public GitHub:**

1. **Review files** - Ensure no real credentials or secrets
2. **Check .gitignore** - Logs, databases, and PID files excluded
3. **Add disclaimer** - README clearly states educational purpose
4. **License** - MIT license included (educational use)

## Useful Commands

```bash
# Check remote
git remote -v

# View commit log
git log --oneline

# Check status
git status

# View changes
git diff

# Create new branch
git checkout -b feature-name

# List all files in repository
git ls-tree -r main --name-only
```

## Making It Discoverable

1. **Add topics** (as mentioned in Step 5)
2. **Write good README** ✅ Already included
3. **Add screenshots** (optional) - Add PLC dashboard screenshots
4. **Social media** - Share on Twitter, LinkedIn, Reddit (r/netsec, r/cybersecurity)
5. **Blog post** - Write about the project
6. **Awesome lists** - Submit to awesome-security, awesome-pentest lists

## Sample Repository Description

Use this for your repository description:

```
Comprehensive ICS/SCADA security training lab with 4 PLCs, Modbus TCP, 
historian, realistic network traffic, and 200+ pages of documentation. 
For penetration testing practice and security education. ⚠️ Intentionally vulnerable
```

---

**Ready to push!** Follow Steps 1-3 above to publish to GitHub.
