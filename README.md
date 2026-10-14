# Data Engineering Roadmap

Content: `datastructures/`, `interview_prep/`, `pde_certification/`, `notes/`. The site in `website/` (Docusaurus) renders all four as tabs.

```bash
cd website
npm install
npm start      # local dev server
npm run build  # production build
```

Pushing to `main` deploys to GitHub Pages via `.github/workflows/deploy.yml`.
`notes/creds.md` is git-ignored and excluded from the site.
