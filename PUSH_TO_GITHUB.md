# Push to GitHub

Your project is committed locally. To push to GitHub:

## 1. Create a new repository on GitHub

- Go to https://github.com/new
- Repository name: **ProjectAria** (or any name you like)
- Choose **Private** or **Public**
- Do **not** add a README, .gitignore, or license (we already have them)
- Click **Create repository**

## 2. Add remote and push

Run these in your project folder (replace `YOUR_USERNAME` with your GitHub username):

```bash
cd /Users/adityavarma/ProjectAria
git remote add origin https://github.com/YOUR_USERNAME/ProjectAria.git
git push -u origin main
```

If you use SSH:

```bash
git remote add origin git@github.com:YOUR_USERNAME/ProjectAria.git
git push -u origin main
```

If the repo already exists and you only need to push:

```bash
git push -u origin main
```

Done. You can delete this file after pushing if you like.
