#!/bin/bash
# Run this script from inside the cybersecurity-portfolio folder
# to initialise git and push to GitHub.
#
# Usage:
#   chmod +x init_repo.sh
#   ./init_repo.sh YOUR_GITHUB_USERNAME

set -e

USERNAME=${1:-"YOUR_USERNAME"}
REPO_NAME="cybersecurity-portfolio"

echo "[*] Initialising git repository..."
git init
git add .
git commit -m "feat: initial cybersecurity portfolio — 3 projects

Project 1: RSA & Diffie-Hellman cryptography from scratch (number theory)
Project 2: Network anomaly detection with ML (NSL-KDD dataset)
Project 3: Automated DevSecOps pipeline (GitHub Actions + Trivy + Bandit + Gitleaks)"

echo ""
echo "[*] Next steps:"
echo "  1. Create a NEW repo on GitHub called '${REPO_NAME}' (no README, no .gitignore)"
echo "  2. Then run:"
echo ""
echo "     git remote add origin https://github.com/${USERNAME}/${REPO_NAME}.git"
echo "     git branch -M main"
echo "     git push -u origin main"
echo ""
echo "[*] After pushing, go to the Actions tab on GitHub to watch the security pipeline run!"
