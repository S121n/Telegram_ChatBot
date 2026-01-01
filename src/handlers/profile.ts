import { Env, TelegramMessage } from '../types';
import { TelegramBot } from '../telegram';
import * as db from '../database';
import * as keyboards from '../keyboards';

// ========================
// Profile Handler
// ========================

export async function handleProfile(env: Env, bot: TelegramBot, message: TelegramMessage): Promise<void> {
  const userId = message.from.id;
  const user = await db.getUser(env, userId);

  if (!user) {
    await bot.sendMessage(userId, '❌ کاربر یافت نشد.');
    return;
  }

  const profileText = `
👤 <b>پروفایل شما</b>

📝 نام: ${user.name}
🚻 جنسیت: ${user.gender}
📍 موقعیت: ${user.city}, ${user.province}
🎂 سن: ${user.age}
💰 سکه: ${user.coins}
  `;

  await bot.sendPhoto(userId, user.profile_pic, {
    caption: profileText,
    parse_mode: 'HTML',
    reply_markup: keyboards.profileKeyboard(),
  });
}

// ========================
// Referral Handler
// ========================

export async function handleReferral(env: Env, bot: TelegramBot, message: TelegramMessage): Promise<void> {
  const userId = message.from.id;
  const user = await db.getUser(env, userId);

  if (!user) {
    await bot.sendMessage(userId, '❌ کاربر یافت نشد.');
    return;
  }

  const botUsername = env.BOT_USERNAME;
  const referralLink = `https://t.me/${botUsername}?start=ref_${userId}`;

  const text = `
🎁 <b>دعوت دوستان</b>

با دعوت دوستان خود، هم شما و هم دوست‌تان سکه رایگان دریافت می‌کنید!

🎁 هر دعوت موفق: <b>10 سکه</b>

🔗 لینک دعوت شما:
<code>${referralLink}</code>

این لینک را برای دوستان خود ارسال کنید!
  `;

  await bot.sendMessage(userId, text, {
    parse_mode: 'HTML',
    reply_markup: keyboards.mainKeyboard(),
  });
}

// ========================
// Back Handler
// ========================

export async function handleBack(env: Env, bot: TelegramBot, message: TelegramMessage): Promise<void> {
  const userId = message.from.id;
  
  await bot.sendMessage(userId, '🔙 بازگشت به منوی اصلی', {
    reply_markup: keyboards.mainKeyboard(),
  });
}
