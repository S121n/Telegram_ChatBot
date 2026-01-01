# Quick Start Guide - Cloudflare Workers Deployment

This guide will help you deploy your Telegram bot to Cloudflare Workers in minutes.

## Prerequisites Checklist

- [ ] Node.js 18+ installed
- [ ] Cloudflare account (free tier works!)
- [ ] Telegram Bot Token from @BotFather
- [ ] Zarinpal Merchant ID (optional, for payments)

## Step-by-Step Deployment

### 1. Install Dependencies

```bash
npm install
npm install -g wrangler
```

### 2. Login to Cloudflare

```bash
wrangler login
```

This will open a browser window. Login and authorize Wrangler.

### 3. Create KV Namespaces (Copy-Paste Friendly)

Run all these commands:

```bash
wrangler kv:namespace create "USERS"
wrangler kv:namespace create "USERS" --preview
wrangler kv:namespace create "REFERRALS"
wrangler kv:namespace create "REFERRALS" --preview
wrangler kv:namespace create "REPORTS"
wrangler kv:namespace create "REPORTS" --preview
wrangler kv:namespace create "PAYMENTS"
wrangler kv:namespace create "PAYMENTS" --preview
wrangler kv:namespace create "CHATS"
wrangler kv:namespace create "CHATS" --preview
wrangler kv:namespace create "WAITING"
wrangler kv:namespace create "WAITING" --preview
```

Each command outputs an ID like:
```
✨ Success! Created KV namespace USERS
Add the following to your wrangler.toml:
{ binding = "USERS", id = "abcd1234..." }
```

**IMPORTANT**: Copy all these IDs and update `wrangler.toml`

### 4. Update wrangler.toml

Open `wrangler.toml` and replace the placeholder IDs with your actual IDs:

```toml
[[kv_namespaces]]
binding = "USERS"
id = "paste-your-users-id-here"
preview_id = "paste-your-users-preview-id-here"
```

Repeat for all 6 namespaces (USERS, REFERRALS, REPORTS, PAYMENTS, CHATS, WAITING).

**⚠️ CRITICAL**: Make sure you replace ALL placeholder IDs (like "your-users-kv-id") with actual IDs. Deploying with placeholder IDs will cause the bot to fail!

### 5. Set Secrets

```bash
# Bot token from @BotFather
wrangler secret put BOT_TOKEN

# Your bot's username (without @)
wrangler secret put BOT_USERNAME

# Your Telegram user ID (you can get it from @userinfobot)
wrangler secret put ADMIN_ID

# Zarinpal merchant ID (or leave blank for now)
wrangler secret put ZARINPAL_MERCHANT_ID

# Worker URL - deploy first, then update this
wrangler secret put CALLBACK_URL
```

For the CALLBACK_URL, just enter a placeholder like `https://example.com` for now. We'll update it after deployment.

### 6. Deploy

```bash
npm run deploy
```

You'll get a URL like: `https://telegram-chatbot.your-subdomain.workers.dev`

### 7. Update Callback URL

Now update the callback URL with your actual worker URL:

```bash
wrangler secret put CALLBACK_URL
# Enter: https://telegram-chatbot.your-subdomain.workers.dev
```

### 8. Set Telegram Webhook

Visit this URL in your browser:

```
https://telegram-chatbot.your-subdomain.workers.dev/setWebhook
```

You should see: `{"ok":true,"result":true,"description":"Webhook was set"}`

### 9. Test Your Bot!

Open Telegram and search for your bot. Send `/start` and follow the registration process!

## Verification

✅ Bot responds to /start
✅ Registration flow works
✅ Main menu appears after registration
✅ Can see profile
✅ Referral link generates

## Common Issues

### Bot doesn't respond
- Check webhook: Visit `/setWebhook` again
- Check logs: `wrangler tail`
- Verify BOT_TOKEN is correct

### "Error 1101: Worker threw exception"
- Check all KV namespace IDs are correct in wrangler.toml
- Verify all 6 namespaces are created (production + preview)

### KV namespace errors
- Make sure you created both regular and preview namespaces (12 total)
- Double-check IDs in wrangler.toml match exactly

## Next Steps

- Test all features (registration, matching, chat)
- Configure Zarinpal for payments (optional)
- Customize Persian text in handlers
- Add your own features!

## Monitoring

Watch live logs:
```bash
wrangler tail
```

## Cost

With Cloudflare's free tier:
- ✅ 100,000 requests/day FREE
- ✅ 100,000 KV reads/day FREE
- ✅ 1,000 KV writes/day FREE
- ✅ 1 GB KV storage FREE

Perfect for personal projects and small-medium bots!

## Need Help?

- Check the main README.md for detailed documentation
- Review Cloudflare Workers docs: https://developers.cloudflare.com/workers/
- Telegram Bot API: https://core.telegram.org/bots/api
