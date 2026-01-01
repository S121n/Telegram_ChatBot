# Telegram Anonymous Chat Bot - Cloudflare Workers

This is a Telegram bot for anonymous chat matching, running on Cloudflare Workers with KV storage. Users can register, match with others based on gender preferences, chat anonymously, and purchase coins for additional chats.

## Features

- 🔐 User registration with profile details (name, gender, location, age, photo)
- 👥 Anonymous chat matching based on gender preferences
- 💬 Real-time message forwarding between matched users
- 💰 Coin-based system for chat access
- 🎁 Referral system with rewards
- 💳 Zarinpal payment integration
- ⚠️ User reporting system
- 🚫 Ban management

## Architecture

- **Platform**: Cloudflare Workers (serverless)
- **Database**: Cloudflare KV (key-value storage)
- **Language**: TypeScript
- **Bot Framework**: Direct Telegram Bot API
- **Payment Gateway**: Zarinpal

## Prerequisites

1. Node.js 18+ installed
2. Cloudflare account
3. Wrangler CLI installed: `npm install -g wrangler`
4. Telegram Bot Token (from [@BotFather](https://t.me/botfather))
5. Zarinpal Merchant ID (for payments)

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
cd /path/to/Telegram_ChatBot
npm install
```

### 2. Login to Cloudflare

```bash
wrangler login
```

### 3. Create KV Namespaces

Run these commands to create all required KV namespaces:

```bash
# Production namespaces
wrangler kv:namespace create "USERS"
wrangler kv:namespace create "REFERRALS"
wrangler kv:namespace create "REPORTS"
wrangler kv:namespace create "PAYMENTS"
wrangler kv:namespace create "CHATS"
wrangler kv:namespace create "WAITING"

# Preview namespaces (for development)
wrangler kv:namespace create "USERS" --preview
wrangler kv:namespace create "REFERRALS" --preview
wrangler kv:namespace create "REPORTS" --preview
wrangler kv:namespace create "PAYMENTS" --preview
wrangler kv:namespace create "CHATS" --preview
wrangler kv:namespace create "WAITING" --preview
```

Each command will output an ID. Update the `wrangler.toml` file with these IDs.

### 4. Update wrangler.toml

Edit `wrangler.toml` and replace the KV namespace IDs with your actual IDs from step 3:

```toml
[[kv_namespaces]]
binding = "USERS"
id = "your-actual-users-kv-id"
preview_id = "your-actual-users-kv-preview-id"

# ... repeat for all namespaces
```

### 5. Set Environment Variables

Set your secrets using Wrangler:

```bash
# Telegram Bot Token (get from @BotFather)
wrangler secret put BOT_TOKEN

# Bot Username (without @)
wrangler secret put BOT_USERNAME

# Admin Telegram ID
wrangler secret put ADMIN_ID

# Zarinpal Merchant ID
wrangler secret put ZARINPAL_MERCHANT_ID

# Callback URL (your worker URL)
wrangler secret put CALLBACK_URL
```

When prompted, enter the actual values.

### 6. Deploy to Cloudflare Workers

```bash
npm run deploy
```

This will deploy your worker and give you a URL like: `https://telegram-chatbot.your-subdomain.workers.dev`

### 7. Set Telegram Webhook

After deployment, visit this URL to set up the webhook:

```
https://telegram-chatbot.your-subdomain.workers.dev/setWebhook
```

You should see a success message from Telegram.

### 8. Update Callback URL

Update the `CALLBACK_URL` secret with your actual worker URL:

```bash
wrangler secret put CALLBACK_URL
# Enter: https://telegram-chatbot.your-subdomain.workers.dev
```

## Project Structure

```
src/
├── index.ts              # Main entry point, webhook handler
├── types.ts              # TypeScript interfaces
├── telegram.ts           # Telegram Bot API client
├── database.ts           # KV storage operations
├── keyboards.ts          # Keyboard layouts and constants
└── handlers/
    ├── register.ts       # User registration flow
    ├── profile.ts        # Profile and referral handlers
    ├── match.ts          # Matching system
    ├── chat.ts           # Chat functionality
    └── payments.ts       # Payment and coins system
```

## KV Storage Structure

### USERS namespace
- `user:{telegram_id}` → User object
- `refcode:{referral_code}` → telegram_id
- `state:{telegram_id}` → FSM state
- `counter:users` → User ID counter

### CHATS namespace
- `chat:{user_id}` → partner_id

### WAITING namespace
- `waiting:{target_gender}:{user_id}` → WaitingUser object

### REFERRALS namespace
- `referral:{invited_telegram_id}` → Referral object
- `counter:referrals` → Referral ID counter

### PAYMENTS namespace
- `payment:{authority}` → Payment object
- `counter:payments` → Payment ID counter

### REPORTS namespace
- `report:{reported_id}:{reporter_id}:{timestamp}` → Report object
- `counter:reports` → Report ID counter

## Development

Run locally with:

```bash
npm run dev
```

This starts a local development server. You'll need to use a tool like ngrok to expose it to Telegram for testing:

```bash
ngrok http 8787
# Then visit https://your-ngrok-url.ngrok.io/setWebhook
```

## Monitoring

View logs in real-time:

```bash
npm run tail
```

## Cost Estimate

Cloudflare Workers offers a generous free tier:
- **Workers**: 100,000 requests/day free
- **KV Storage**: 100,000 reads/day, 1,000 writes/day free
- **KV Storage**: First 1 GB stored free

For a small to medium bot, this should be completely free!

## Security Notes

1. Never commit secrets to Git
2. Keep your `BOT_TOKEN` secure
3. Use Cloudflare's Web Application Firewall (WAF) if needed
4. Regularly review reported users
5. Monitor for abuse patterns

## Troubleshooting

### Bot doesn't respond
1. Check webhook is set: Visit `/setWebhook` endpoint
2. Check logs: `wrangler tail`
3. Verify environment variables are set

### KV errors
1. Ensure all KV namespaces are created
2. Verify IDs in `wrangler.toml` match your actual KV namespace IDs
3. Check KV quotas in Cloudflare dashboard

### Payment issues
1. Verify Zarinpal merchant ID is correct
2. Check callback URL is set correctly
3. Ensure your worker URL is accessible

## Support

For issues related to:
- **Cloudflare Workers**: [Cloudflare Docs](https://developers.cloudflare.com/workers/)
- **Telegram Bot API**: [Telegram Bot API Docs](https://core.telegram.org/bots/api)
- **Zarinpal**: [Zarinpal Docs](https://docs.zarinpal.com/)

## License

MIT
