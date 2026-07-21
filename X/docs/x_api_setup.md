# X API Setup

Last checked: 2026-07-04

## Current State

You have created a client app and received the Consumer Key and Consumer Secret.
These are app credentials. They are not enough by themselves to publish posts or
read private account-context data as your X account.

For a single-account local operations assistant, use OAuth 1.0a first:

- Consumer Key / API Key;
- Consumer Secret / API Key Secret;
- Access Token;
- Access Token Secret.

OAuth 2.0 can be added later if this becomes a multi-user app.

## Safety Rules

- Never paste keys into chat.
- Never screenshot keys.
- Never commit `.env`.
- Store real keys only in local `.env` or a password manager.
- If a key leaks, rotate it in the X Developer Console.
- Keep app permissions minimal.
- Start with read/write posting only; do not enable DM access unless the product needs it.

## Developer Console Steps

1. Open the app in X Developer Console.
2. Set app permissions to `Read and Write`.
3. Save changes.
4. Go to `Keys and tokens`.
5. If you changed permissions after generating tokens, regenerate the Access Token and Secret.
6. Copy `.env.example` to `.env`.
7. Fill these values in `.env`:

```env
X_API_KEY=...
X_API_KEY_SECRET=...
X_ACCESS_TOKEN=...
X_ACCESS_TOKEN_SECRET=...
```

Optional values:

```env
X_BEARER_TOKEN=...
X_CLIENT_ID=...
X_CLIENT_SECRET=...
X_CALLBACK_URL=http://127.0.0.1:8765/callback
```

## Local Validation

Run:

```powershell
python scripts/check_x_env.py
```

This only validates that required variables exist locally. It does not call X
and does not publish anything.

Run the read-only API probe after adding credits:

```powershell
python scripts/check_x_api_readonly.py
```

This checks public read access and your authorized account identity. It does not
publish anything.

## Publishing Test

Use dry-run first:

```powershell
python scripts/post_x.py --text "Your post text"
```

Actually publishing requires an explicit confirmation flag:

```powershell
python scripts/post_x.py --text "Your post text" --confirm
```

Do not use `--confirm` for generated text until a human has reviewed the exact
post body.

## Automation Boundary

The initial integration should support:

- importing your own posts and metrics;
- drafting posts;
- queueing reviewed posts;
- publishing only after explicit confirmation;
- logging every external action.

Do not implement:

- automated likes;
- bulk follow/unfollow;
- unsolicited DMs;
- keyword-search auto-replies to strangers;
- X website scripting;
- rate-limit bypass;
- coordinated engagement.
