# TEMPORARY — TradeThesis single-bot patch for Codespaces

This directory is temporary. It was added so you can run the bot installer from the online VS Code workspace without downloading a separate ZIP. After you have applied or rejected the patch and told ChatGPT, the temporary directory will be removed from `my-new-branch` in a cleanup commit.

## Before you run it

- This patch is for the **actual bot working copy**, not the `prototypeweb` Django repository and not the reference snapshot.
- Stop the running bot before patching.
- Make sure the actual bot working copy has a clean Git worktree. The installer refuses to overwrite uncommitted work.
- Do not start a second polling process for the same Telegram bot token.
- It does not commit, push, or deploy your bot.

## From Codespaces

First pull the temporary helper into your current website workspace (only if your worktree is clean):

```bash
cd /workspaces/prototypeweb
git status --short --branch
git pull --ff-only origin my-new-branch
```

Then apply it to the **actual bot Git working copy** (replace the path with the directory containing its `main.py` and `.git`):

```bash
bash /workspaces/prototypeweb/tools/temporary-telegram-single-bot/apply.sh /path/to/actual-bot-working-copy
```

The installer checks that the patch fits before applying it, backs up `main.py` in a sibling directory, runs syntax validation and six offline tests, and tries to reverse only this patch if validation fails. It uses `PYTHONDONTWRITEBYTECODE=1` during tests to avoid `__pycache__` noise.

The patch adds a handler for only `/start verify_<token>` to the existing bot. Regular `/start` keeps the current manager experience. It also adds `tradethesis_verification_bridge.py` and a six-test suite.

## Runtime settings

In the existing bot process's local `.env.txt`, configure the Academy staging URL and the same `PROVISION_SHARED_SECRET` used by Django. Never commit or paste the secret. The bot token must match Django Admin → Bot Configuration. Do not create a second verification bot.

```dotenv
TRADETHESIS_TELEGRAM_WEBHOOK_URL=https://tradethesis-academy-staging.onrender.com/bot/telegram/webhook/
PROVISION_SHARED_SECRET=<same private value as Academy staging>
```

## After execution

Inspect the bot working-copy diff and installer output. Do not deploy the website until the bot patch has been validated. The Django-side fix is already committed on `my-new-branch`; do not apply the Django patch again.

When you are done, say **"remove the temporary Telegram helper"** and I will delete this directory from the branch. No deployment is part of this temporary helper.
