# Testing & Verification Guide

This guide helps you verify that your Cloudflare Workers bot is working correctly.

## Pre-Deployment Checks

### 1. TypeScript Compilation
```bash
npx tsc --noEmit
```
✅ Should complete with no errors

### 2. Wrangler Configuration
```bash
cat wrangler.toml
```
✅ All KV namespace IDs should be filled in (not "your-xxx-kv-id")

### 3. Secrets Check
```bash
wrangler secret list
```
✅ Should show: BOT_TOKEN, BOT_USERNAME, ADMIN_ID, ZARINPAL_MERCHANT_ID, CALLBACK_URL

## Deployment Verification

### 1. Deploy
```bash
npm run deploy
```
✅ Should show: "Published <your-worker-name> (x.xx sec)"

### 2. Test Worker Endpoint
```bash
curl https://your-worker.workers.dev/
```
✅ Should return: "Telegram Bot Worker is running!"

### 3. Set Webhook
Visit in browser:
```
https://your-worker.workers.dev/setWebhook
```
✅ Should return: `{"ok":true,"result":true,"description":"Webhook was set"}`

## Functional Testing

### Test 1: Bot Registration Flow
1. Open Telegram
2. Search for your bot (@your_bot_username)
3. Send `/start`
4. ✅ Bot should ask for your name
5. Enter a name
6. ✅ Bot should ask for gender with buttons
7. Select gender
8. ✅ Bot should show province selection
9. Select province
10. ✅ Bot should show city selection
11. Select city
12. ✅ Bot should ask for age
13. Enter age (e.g., 25)
14. ✅ Bot should ask for photo
15. Send a photo
16. ✅ Bot should confirm registration and show main menu with "15 سکه"

### Test 2: Profile Display
1. Click "👤 پروفایل" button
2. ✅ Bot should show your profile with photo and details

### Test 3: Referral System
1. Click "🎁 دعوت دوستان" button
2. ✅ Bot should show referral link like: `https://t.me/your_bot?start=ref_123456`
3. Copy the link
4. Open in another Telegram account (or ask a friend)
5. Complete registration through the link
6. ✅ First account should receive notification: "کاربر جدیدی از طریق لینک دعوت شما ثبت‌نام کرد! 💰 10 سکه"
7. Check first account's profile
8. ✅ Coins should have increased by 10

### Test 4: Matching System
1. From first account, click "🔍 اتصال ناشناس"
2. ✅ Bot should ask: "میخوای به کی وصل شی؟"
3. Select gender preference
4. ✅ Bot should show: "در حال جستجوی مخاطب..."
5. From second account, click "🔍 اتصال ناشناس"
6. Select matching gender preference
7. ✅ Both accounts should receive: "مخاطب پیدا شد!"
8. ✅ Chat keyboard should appear with "خروج از چت" button

### Test 5: Chat System
1. Send a message from first account
2. ✅ Second account should receive the message
3. Send a message from second account
4. ✅ First account should receive the message
5. Click "👤 نمایش پروفایل"
6. ✅ Should show partner's profile with photo

### Test 6: End Chat
1. Click "🚪 خروج از چت"
2. ✅ Both users should receive notification: "چت به پایان رسید"
3. ✅ Main menu should return

### Test 7: Report System
1. Start a new chat between two users
2. Click "⚠️ گزارش کاربر"
3. ✅ Should show: "گزارش شما ثبت شد"
4. ✅ Chat should end
5. ✅ Admin account should receive notification about the report

### Test 8: Coins Menu
1. Click "💰 خرید سکه" button
2. ✅ Bot should show coin packages with prices
3. Click on a package (e.g., "50 سکه - 10,000 تومان")
4. ✅ Bot should show Zarinpal payment link (if configured)

### Test 9: Back Button
1. Click "👤 پروفایل"
2. Click "🔙 بازگشت"
3. ✅ Should return to main menu

### Test 10: Coin Deduction
1. Check user's coins (should be 15 initially, or less if already chatted)
2. Start a chat
3. Check coins again
4. ✅ Should have decreased by 2 coins for both users

## Monitoring & Debugging

### Live Logs
```bash
npm run tail
```
Watch for:
- ✅ Incoming webhook calls
- ✅ User actions
- ❌ Errors or exceptions

### Check KV Data

#### View User
```bash
wrangler kv:key get "user:YOUR_TELEGRAM_ID" --namespace-id=YOUR_USERS_KV_ID
```

#### List Users
```bash
wrangler kv:key list --namespace-id=YOUR_USERS_KV_ID --prefix="user:"
```

#### Check Chat Status
```bash
wrangler kv:key get "chat:YOUR_TELEGRAM_ID" --namespace-id=YOUR_CHATS_KV_ID
```

#### View Waiting Queue
```bash
wrangler kv:key list --namespace-id=YOUR_WAITING_KV_ID --prefix="waiting:"
```

## Common Issues & Solutions

### Issue: Bot doesn't respond
**Solution**:
```bash
# Check webhook status
curl https://your-worker.workers.dev/setWebhook

# Check logs
npm run tail
```

### Issue: "Worker threw exception"
**Solution**:
- Check all KV namespace IDs in wrangler.toml
- Verify all secrets are set: `wrangler secret list`
- Check logs for specific error

### Issue: User data not persisting
**Solution**:
```bash
# Verify KV namespace is correct
wrangler kv:namespace list

# Check if data is being written
wrangler kv:key list --namespace-id=YOUR_USERS_KV_ID
```

### Issue: Matching not working
**Solution**:
```bash
# Check waiting queue
wrangler kv:key list --namespace-id=YOUR_WAITING_KV_ID

# Verify gender matching logic in logs
npm run tail
```

### Issue: Payments not working
**Solution**:
- Verify ZARINPAL_MERCHANT_ID is correct
- Check CALLBACK_URL matches your worker URL
- Verify webhook endpoint is accessible

## Performance Testing

### Test Response Time
```bash
time curl -X POST https://your-worker.workers.dev/webhook \
  -H "Content-Type: application/json" \
  -d '{"update_id":1,"message":{"message_id":1,"from":{"id":12345},"chat":{"id":12345},"text":"/start"}}'
```
✅ Should complete in <100ms

### Test Concurrent Users
Use a load testing tool or multiple Telegram accounts to test:
- ✅ Multiple registrations simultaneously
- ✅ Multiple chats active at once
- ✅ Matching queue handling

## Security Checks

### 1. Secrets Protection
```bash
# These should NOT show actual values
cat wrangler.toml | grep -i token
```
✅ Should only show placeholder comments

### 2. Environment Variables
```bash
wrangler secret list
```
✅ Should show secret names, not values

### 3. Webhook Security
```bash
# Only your webhook URL should work
curl -X POST https://your-worker.workers.dev/webhook
```
✅ Should be protected/handled properly

## Success Criteria

Your bot is fully operational when:
- ✅ All registration steps work
- ✅ Profile displays correctly
- ✅ Referral system works and gives coins
- ✅ Matching connects two users
- ✅ Chat messages are forwarded correctly
- ✅ Coins are deducted on chat start
- ✅ End chat works for both users
- ✅ Report system notifies admin
- ✅ All KV operations succeed
- ✅ No errors in logs (npm run tail)

## Continuous Monitoring

Set up regular checks:
1. Test bot weekly
2. Monitor KV storage usage in Cloudflare dashboard
3. Check for any errors in Cloudflare Workers dashboard
4. Verify webhook is still set: visit `/setWebhook` monthly

## Need Help?

If tests fail:
1. Check logs: `npm run tail`
2. Review error messages
3. Verify KV namespaces are created
4. Confirm all secrets are set
5. Check Cloudflare Workers dashboard for errors

## Automated Testing (Optional)

For CI/CD, you can create a test script:

```bash
#!/bin/bash
echo "Testing worker endpoint..."
curl -s https://your-worker.workers.dev/ | grep -q "running"
if [ $? -eq 0 ]; then
  echo "✅ Worker is responding"
else
  echo "❌ Worker is not responding"
  exit 1
fi
```

Save as `test.sh`, make executable: `chmod +x test.sh`, run: `./test.sh`
