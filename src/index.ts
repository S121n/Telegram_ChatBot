import { Env, TelegramUpdate } from './types';
import { TelegramBot } from './telegram';
import * as db from './database';
import * as registerHandlers from './handlers/register';
import * as profileHandlers from './handlers/profile';
import * as matchHandlers from './handlers/match';
import * as chatHandlers from './handlers/chat';
import * as paymentHandlers from './handlers/payments';

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // Handle webhook setup
    if (url.pathname === '/setWebhook' && request.method === 'GET') {
      const bot = new TelegramBot(env.BOT_TOKEN);
      const webhookUrl = `${url.origin}/webhook`;
      const result = await bot.setWebhook(webhookUrl);
      return new Response(JSON.stringify(result), {
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Handle payment callback
    if (url.pathname === '/payment/callback' && request.method === 'GET') {
      const authority = url.searchParams.get('Authority') || '';
      const status = url.searchParams.get('Status') || '';
      return await paymentHandlers.handlePaymentCallback(env, authority, status);
    }

    // Handle Telegram webhook
    if (url.pathname === '/webhook' && request.method === 'POST') {
      try {
        const update: TelegramUpdate = await request.json();
        await handleUpdate(env, update);
        return new Response('OK', { status: 200 });
      } catch (e) {
        console.error('Error handling update:', e);
        // Return generic error without exposing internal details
        return new Response('Internal Server Error', { status: 500 });
      }
    }

    // Default response
    return new Response('Telegram Bot Worker is running!', { status: 200 });
  },
};

async function handleUpdate(env: Env, update: TelegramUpdate): Promise<void> {
  const bot = new TelegramBot(env.BOT_TOKEN);

  // Handle callback queries (inline buttons)
  if (update.callback_query) {
    await handleCallbackQuery(env, bot, update.callback_query);
    return;
  }

  // Handle messages
  if (update.message) {
    await handleMessage(env, bot, update.message);
  }
}

async function handleCallbackQuery(env: Env, bot: TelegramBot, query: any): Promise<void> {
  const data = query.data;

  if (data?.startsWith('buy_')) {
    await paymentHandlers.handleBuyCoins(env, bot, query);
  }
}

async function handleMessage(env: Env, bot: TelegramBot, message: any): Promise<void> {
  const userId = message.from.id;
  const text = message.text;

  // Check if user is banned
  const user = await db.getUser(env, userId);
  if (user?.banned_until) {
    const bannedUntil = new Date(user.banned_until);
    if (bannedUntil > new Date()) {
      await bot.sendMessage(
        userId,
        `⛔ حساب شما تا ${bannedUntil.toLocaleDateString('fa-IR')} مسدود شده است.`
      );
      return;
    }
  }

  // Get current state
  const state = await db.getState(env, userId);

  // Handle registration flow
  if (state?.state.startsWith('register:')) {
    await registerHandlers.handleRegistration(env, bot, message);
    return;
  }

  // Handle matching flow
  if (state?.state === 'matching:select_gender') {
    await matchHandlers.handleSelectGender(env, bot, message);
    return;
  }

  // Check if user is registered (except for /start and registration button)
  if (!user && text !== '/start' && text !== 'ثبت نام') {
    await bot.sendMessage(
      userId,
      '👋 خوش آمدید\nبرای استفاده از ربات ابتدا باید ثبت‌نام کنید.',
      {
        reply_markup: {
          keyboard: [[{ text: 'ثبت نام' }]],
          resize_keyboard: true,
        },
      }
    );
    return;
  }

  // Handle commands and buttons
  if (text === '/start') {
    await registerHandlers.handleStart(env, bot, message);
  } else if (text === 'ثبت نام') {
    await registerHandlers.handleRegisterButton(env, bot, message);
  } else if (text === '👤 پروفایل') {
    await profileHandlers.handleProfile(env, bot, message);
  } else if (text === '🎁 دعوت دوستان') {
    await profileHandlers.handleReferral(env, bot, message);
  } else if (text === '🔙 بازگشت') {
    await profileHandlers.handleBack(env, bot, message);
  } else if (text === '🔍 اتصال ناشناس') {
    await matchHandlers.handleStartMatch(env, bot, message);
  } else if (text === '🚪 خروج از چت') {
    await chatHandlers.handleEndChat(env, bot, message);
  } else if (text === '👤 نمایش پروفایل') {
    await chatHandlers.handleShowPartnerProfile(env, bot, message);
  } else if (text === '⚠️ گزارش کاربر') {
    await chatHandlers.handleReport(env, bot, message);
  } else if (text === '💰 خرید سکه') {
    await paymentHandlers.handleCoinsMenu(env, bot, message);
  } else {
    // Check if user is in chat - forward message
    const partnerId = await db.getPartner(env, userId);
    if (partnerId) {
      await chatHandlers.handleChatMessage(env, bot, message);
    }
  }
}
