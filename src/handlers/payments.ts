import { Env, TelegramMessage, TelegramCallbackQuery } from '../types';
import { TelegramBot } from '../telegram';
import * as db from '../database';
import * as keyboards from '../keyboards';

// ========================
// Coins Menu Handler
// ========================

export async function handleCoinsMenu(env: Env, bot: TelegramBot, message: TelegramMessage): Promise<void> {
  const userId = message.from.id;
  const user = await db.getUser(env, userId);

  if (!user) {
    await bot.sendMessage(userId, '❌ کاربر یافت نشد.');
    return;
  }

  const text = `
💰 <b>خرید سکه</b>

موجودی فعلی: <b>${user.coins} سکه</b>

با خرید سکه می‌توانید:
• با کاربران جدید چت کنید (هر چت 2 سکه)
• از امکانات ویژه استفاده کنید

یکی از بسته‌های زیر را انتخاب کنید:
  `;

  await bot.sendMessage(userId, text, {
    parse_mode: 'HTML',
    reply_markup: keyboards.coinsKeyboard(),
  });
}

// ========================
// Buy Coins Callback Handler
// ========================

export async function handleBuyCoins(env: Env, bot: TelegramBot, query: TelegramCallbackQuery): Promise<void> {
  const userId = query.from.id;
  const data = query.data;

  if (!data) return;

  const packages: Record<string, { coins: number; amount: number }> = {
    buy_50: { coins: 50, amount: 10000 },
    buy_100: { coins: 100, amount: 18000 },
    buy_200: { coins: 200, amount: 35000 },
    buy_500: { coins: 500, amount: 80000 },
  };

  const pkg = packages[data];

  if (!pkg) {
    await bot.answerCallbackQuery(query.id, 'بسته نامعتبر');
    return;
  }

  // Create payment
  const authority = generateAuthority();
  await db.createPayment(env, userId, pkg.amount, pkg.coins, authority);

  // Create Zarinpal payment
  const paymentUrl = await createZarinpalPayment(env, pkg.amount, authority);

  if (!paymentUrl) {
    await bot.answerCallbackQuery(query.id, 'خطا در ایجاد پرداخت', true);
    return;
  }

  await bot.answerCallbackQuery(query.id);
  
  await bot.sendMessage(
    userId,
    `💳 برای خرید ${pkg.coins} سکه به مبلغ ${pkg.amount.toLocaleString()} تومان، روی لینک زیر کلیک کنید:\n\n${paymentUrl}`,
    { reply_markup: keyboards.mainKeyboard() }
  );
}

// ========================
// Payment Verification Handler
// ========================

export async function handlePaymentCallback(env: Env, authority: string, status: string): Promise<Response> {
  if (status !== 'OK') {
    return new Response('پرداخت ناموفق بود', {
      status: 200,
      headers: { 'Content-Type': 'text/html; charset=utf-8' },
    });
  }

  const payment = await db.getPayment(env, authority);

  if (!payment) {
    return new Response('پرداخت قبلاً بررسی شده', {
      status: 200,
      headers: { 'Content-Type': 'text/html; charset=utf-8' },
    });
  }

  if (payment.status !== 'pending') {
    return new Response('پرداخت قبلاً بررسی شده', {
      status: 200,
      headers: { 'Content-Type': 'text/html; charset=utf-8' },
    });
  }

  // Verify payment with Zarinpal
  const verified = await verifyZarinpalPayment(env, authority, payment.amount);

  if (!verified) {
    await db.updatePaymentStatus(env, authority, 'failed');
    return new Response('پرداخت تایید نشد', {
      status: 200,
      headers: { 'Content-Type': 'text/html; charset=utf-8' },
    });
  }

  // Payment successful
  await db.updatePaymentStatus(env, authority, 'success');
  await db.addCoins(env, payment.user_id, payment.coins);

  // Notify user
  const bot = new TelegramBot(env.BOT_TOKEN);
  try {
    await bot.sendMessage(
      payment.user_id,
      `✅ پرداخت شما با موفقیت انجام شد!\n\n💰 ${payment.coins} سکه به حساب شما اضافه شد.`
    );
  } catch (e) {
    console.error('Failed to notify user:', e);
  }

  return new Response('پرداخت با موفقیت انجام شد!', {
    status: 200,
    headers: { 'Content-Type': 'text/html; charset=utf-8' },
  });
}

// ========================
// Helper Functions
// ========================

function generateAuthority(): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let result = '';
  for (let i = 0; i < 36; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

async function createZarinpalPayment(env: Env, amount: number, authority: string): Promise<string | null> {
  const data = {
    merchant_id: env.ZARINPAL_MERCHANT_ID,
    amount: amount,
    description: 'خرید سکه ربات تلگرام',
    callback_url: `${env.CALLBACK_URL}/payment/callback`,
    metadata: {
      authority: authority,
    },
  };

  try {
    const response = await fetch('https://api.zarinpal.com/pg/v4/payment/request.json', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    const result = await response.json();

    if (result?.data?.code === 100) {
      const authorityFromZP = result.data.authority;
      return `https://www.zarinpal.com/pg/StartPay/${authorityFromZP}`;
    }
  } catch (e) {
    console.error('Zarinpal payment creation failed:', e);
  }

  return null;
}

async function verifyZarinpalPayment(env: Env, authority: string, amount: number): Promise<boolean> {
  const data = {
    merchant_id: env.ZARINPAL_MERCHANT_ID,
    authority: authority,
    amount: amount,
  };

  try {
    const response = await fetch('https://api.zarinpal.com/pg/v4/payment/verify.json', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    const result = await response.json();

    if (result?.data?.code === 100 || result?.data?.code === 101) {
      return true;
    }
  } catch (e) {
    console.error('Zarinpal payment verification failed:', e);
  }

  return false;
}
