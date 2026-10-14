# Apply the approved ChartLab change set

This ZIP contains exactly five new files for `ZaphodBeeblebrox12/prototypeweb`, branch `my-new-branch`. It does not contain a `.git` directory and does not modify your repository by itself.

## 1. Extract
Extract this ZIP into the root of your local repository clone. Merge the included `prototypes/` and `docs/` folders with existing folders if prompted; do not replace unrelated files.

## 2. Review
From the repository root, run:

```bash
git status --short
git diff --no-index /dev/null prototypes/chartlab/mark-the-zone/README.md
```

The five paths expected to be new are:
- `prototypes/chartlab/mark-the-zone/index.html`
- `prototypes/chartlab/mark-the-zone/README.md`
- `docs/chartlab/ANSWER-KEYS.md`
- `docs/chartlab/answer-keys.json`
- `docs/chartlab/README.md`

Open `prototypes/chartlab/mark-the-zone/index.html` in a browser to review the standalone prototype.

## 3. Commit only these five files
Make sure your current branch is `my-new-branch`, then run:

```bash
git switch my-new-branch
git add prototypes/chartlab/mark-the-zone/index.html prototypes/chartlab/mark-the-zone/README.md docs/chartlab/ANSWER-KEYS.md docs/chartlab/answer-keys.json docs/chartlab/README.md
git diff --cached --stat
git diff --cached --name-status
```

Confirm the staged list contains exactly those five new files. Then commit and push:

```bash
git commit -m "Add standalone ChartLab support and resistance lab"
git push origin my-new-branch
```

No course-room integration, dashboard changes, authentication, payment changes, or screenshots are included.
