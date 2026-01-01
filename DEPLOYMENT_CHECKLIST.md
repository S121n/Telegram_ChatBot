# 🚀 Deployment Checklist

Use this checklist to ensure your bot is ready for deployment.

## Pre-Deployment

### ✅ Prerequisites Installed
- [ ] Node.js 18+ installed (`node --version`)
- [ ] npm installed (`npm --version`)
- [ ] Wrangler CLI installed (`npm install -g wrangler`)
- [ ] Git installed (`git --version`)

### ✅ Accounts & Credentials
- [ ] Cloudflare account created (https://dash.cloudflare.com/sign-up)
- [ ] Telegram bot created via @BotFather
- [ ] Bot token obtained from @BotFather
- [ ] Bot username noted (without @)
- [ ] Your Telegram user ID obtained (from @userinfobot)
- [ ] Zarinpal merchant ID (optional, for payments)

### ✅ Initial Setup
```bash
# Clone or navigate to project
cd /path/to/Telegram_ChatBot

# Install dependencies
npm install

# Login to Cloudflare
wrangler login
```
- [ ] Dependencies installed successfully
- [ ] Wrangler logged in successfully

## KV Namespace Creation

### ✅ Create Production Namespaces
```bash
wrangler kv:namespace create "USERS"
wrangler kv:namespace create "REFERRALS"
wrangler kv:namespace create "REPORTS"
wrangler kv:namespace create "PAYMENTS"
wrangler kv:namespace create "CHATS"
wrangler kv:namespace create "WAITING"
```
- [ ] All 6 production namespaces created
- [ ] IDs noted for each namespace

### ✅ Create Preview Namespaces
```bash
wrangler kv:namespace create "USERS" --preview
wrangler kv:namespace create "REFERRALS" --preview
wrangler kv:namespace create "REPORTS" --preview
wrangler kv:namespace create "PAYMENTS" --preview
wrangler kv:namespace create "CHATS" --preview
wrangler kv:namespace create "WAITING" --preview
```
- [ ] All 6 preview namespaces created
- [ ] Preview IDs noted for each namespace

## Configuration

### ✅ Update wrangler.toml
Open `wrangler.toml` and replace ALL placeholder IDs:

```toml
# Example - replace with YOUR actual IDs
[[kv_namespaces]]
binding = "USERS"
id = "abc123..."              # ← Replace this
preview_id = "def456..."      # ← And this
```

- [ ] USERS namespace IDs updated (both id and preview_id)
- [ ] REFERRALS namespace IDs updated
- [ ] REPORTS namespace IDs updated
- [ ] PAYMENTS namespace IDs updated
- [ ] CHATS namespace IDs updated
- [ ] WAITING namespace IDs updated
- [ ] **VERIFIED**: No "your-xxx-kv-id" placeholders remain

### ✅ Set Environment Secrets
```bash
wrangler secret put BOT_TOKEN
# Enter your bot token when prompted

wrangler secret put BOT_USERNAME
# Enter your bot username (without @)

wrangler secret put ADMIN_ID
# Enter your Telegram user ID

wrangler secret put ZARINPAL_MERCHANT_ID
# Enter your Zarinpal merchant ID (or "test" for now)

wrangler secret put CALLBACK_URL
# Enter temporary URL: https://example.com
# (will update after deployment)
```

- [ ] BOT_TOKEN set
- [ ] BOT_USERNAME set
- [ ] ADMIN_ID set
- [ ] ZARINPAL_MERCHANT_ID set
- [ ] CALLBACK_URL set (temporary)

### ✅ Verify Secrets
```bash
wrangler secret list
```
- [ ] All 5 secrets listed
- [ ] No actual values shown (security check)

## Deployment

### ✅ TypeScript Compilation Check
```bash
npx tsc --noEmit
```
- [ ] Compilation successful (no errors)

### ✅ Deploy to Cloudflare
```bash
npm run deploy
```
- [ ] Deployment successful
- [ ] Worker URL noted (e.g., `https://telegram-chatbot.yourname.workers.dev`)

### ✅ Update Callback URL
```bash
wrangler secret put CALLBACK_URL
# Enter your actual worker URL
```
- [ ] CALLBACK_URL updated with real worker URL

## Post-Deployment Verification

### ✅ Test Worker Endpoint
```bash
curl https://your-worker-url.workers.dev/
```
Expected: "Telegram Bot Worker is running!"
- [ ] Worker responds correctly

### ✅ Set Telegram Webhook
Visit in browser: `https://your-worker-url.workers.dev/setWebhook`

Expected: `{"ok":true,"result":true,"description":"Webhook was set"}`
- [ ] Webhook set successfully

### ✅ Test Bot on Telegram
1. Open Telegram
2. Search for your bot (@your_bot_username)
3. Send `/start`

Expected behavior:
- [ ] Bot responds immediately
- [ ] Asks for your name
- [ ] Registration flow begins

### ✅ Complete Registration Test
- [ ] Enter name → Gender selection appears
- [ ] Select gender → Province selection appears
- [ ] Select province → City selection appears
- [ ] Select city → Age prompt appears
- [ ] Enter age → Photo prompt appears
- [ ] Send photo → Registration confirms with "15 سکه"
- [ ] Main menu appears with all buttons

### ✅ Feature Verification
- [ ] "👤 پروفایل" shows profile with photo
- [ ] "🎁 دعوت دوستان" shows referral link
- [ ] "🔍 اتصال ناشناس" starts matching flow
- [ ] "💰 خرید سکه" shows coin packages
- [ ] "🔙 بازگشت" returns to main menu

## Monitoring

### ✅ Live Logs
```bash
npm run tail
```
- [ ] Logs show incoming webhook calls
- [ ] No errors visible in logs

### ✅ Cloudflare Dashboard
Visit: https://dash.cloudflare.com/

- [ ] Worker visible in dashboard
- [ ] Requests showing in analytics
- [ ] No errors in dashboard

## Multi-User Testing

### ✅ Test with Second User
1. Create/use second Telegram account
2. Register second user
3. Test matching:
   - [ ] User 1 clicks "اتصال ناشناس"
   - [ ] User 1 selects target gender
   - [ ] User 2 clicks "اتصال ناشناس"
   - [ ] User 2 selects matching gender
   - [ ] Both receive "مخاطب پیدا شد!"
   
4. Test chat:
   - [ ] Messages forward correctly
   - [ ] Photos send correctly
   - [ ] "نمایش پروفایل" works
   - [ ] "خروج از چت" ends chat for both
   
5. Test coins:
   - [ ] Both users lose 2 coins after match
   - [ ] Coin count visible in profile

### ✅ Test Referral System
- [ ] User 1 shares referral link
- [ ] User 3 registers via link
- [ ] User 1 receives notification
- [ ] User 1 gains 10 coins

## Production Readiness

### ✅ Security
- [ ] No secrets in code
- [ ] No sensitive data in logs
- [ ] HTTPS enabled (automatic)
- [ ] Environment variables encrypted

### ✅ Performance
- [ ] Response time <100ms
- [ ] No timeout errors
- [ ] Multiple users can register simultaneously

### ✅ Documentation
- [ ] README.md reviewed
- [ ] QUICKSTART.md available
- [ ] TESTING.md available for team
- [ ] MIGRATION.md available for reference

## Final Checks

### ✅ Cost Monitoring
Check Cloudflare dashboard:
- [ ] Within free tier limits
- [ ] No unexpected charges
- [ ] Usage patterns normal

### ✅ Backup & Recovery
- [ ] Code pushed to Git repository
- [ ] Environment variables documented
- [ ] KV namespace IDs backed up
- [ ] Deployment process documented

## Launch! 🚀

### ✅ Go Live
- [ ] All tests pass
- [ ] No errors in logs
- [ ] Performance acceptable
- [ ] Documentation complete
- [ ] Team briefed (if applicable)

### ✅ Post-Launch Monitoring (First 24h)
- [ ] Check logs regularly: `npm run tail`
- [ ] Monitor Cloudflare dashboard
- [ ] Test bot functionality periodically
- [ ] Respond to any user reports

## Troubleshooting Reference

If issues occur, refer to:
- **Setup issues**: QUICKSTART.md
- **Testing issues**: TESTING.md
- **Feature issues**: README.md
- **Migration questions**: MIGRATION.md

### Common Issues Quick Fix

**Bot doesn't respond:**
```bash
curl https://your-worker-url.workers.dev/setWebhook
npm run tail
```

**KV errors:**
```bash
wrangler kv:namespace list
# Verify all 6 namespaces exist
```

**Deployment errors:**
```bash
wrangler secret list
# Verify all 5 secrets are set
cat wrangler.toml
# Check for placeholder IDs
```

## Success! 🎉

If all items are checked, your bot is:
- ✅ Fully deployed
- ✅ Production-ready
- ✅ Monitored
- ✅ Documented
- ✅ Tested

**Congratulations! Your serverless Telegram bot is live!**

---

*Estimated time to complete: 10-15 minutes*
*Cost: $0/month (within free tier)*
