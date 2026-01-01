import { Env, TelegramMessage } from '../types';
import { TelegramBot } from '../telegram';
import * as db from '../database';
import * as keyboards from '../keyboards';

// ========================
// Chat Message Handler
// ========================

export async function handleChatMessage(env: Env, bot: TelegramBot, message: TelegramMessage): Promise<void> {
  const userId = message.from.id;
  const partnerId = await db.getPartner(env, userId);

  if (!partnerId) {
    return; // Not in chat
  }

  // Forward message to partner
  try {
    if (message.text) {
      await bot.sendMessage(partnerId, message.text);
    } else if (message.photo) {
      const photoId = message.photo[message.photo.length - 1].file_id;
      await bot.sendPhoto(partnerId, photoId, {
        caption: message.text || '',
      });
    }
  } catch (e) {
    console.error('Failed to forward message to partner:', e);
    await bot.sendMessage(
      userId,
      '❌ خطا در ارسال پیام. مخاطب ممکن است ربات را بلاک کرده باشد.'
    );
  }
}

// ========================
// End Chat Handler
// ========================

export async function handleEndChat(env: Env, bot: TelegramBot, message: TelegramMessage): Promise<void> {
  const userId = message.from.id;
  const partnerId = await db.endChat(env, userId);

  if (!partnerId) {
    await bot.sendMessage(
      userId,
      '❌ شما در چت نیستید.',
      { reply_markup: keyboards.mainKeyboard() }
    );
    return;
  }

  // Notify both users
  await bot.sendMessage(
    userId,
    '👋 چت به پایان رسید.\n\nبرای یافتن مخاطب جدید از منوی اصلی استفاده کنید.',
    { reply_markup: keyboards.mainKeyboard() }
  );

  try {
    await bot.sendMessage(
      partnerId,
      '👋 مخاطب چت را ترک کرد.\n\nبرای یافتن مخاطب جدید از منوی اصلی استفاده کنید.',
      { reply_markup: keyboards.mainKeyboard() }
    );
  } catch (e) {
    console.error('Failed to notify partner:', e);
  }
}

// ========================
// Show Profile Handler
// ========================

export async function handleShowPartnerProfile(env: Env, bot: TelegramBot, message: TelegramMessage): Promise<void> {
  const userId = message.from.id;
  const partnerId = await db.getPartner(env, userId);

  if (!partnerId) {
    await bot.sendMessage(
      userId,
      '❌ شما در چت نیستید.',
      { reply_markup: keyboards.mainKeyboard() }
    );
    return;
  }

  const partner = await db.getUser(env, partnerId);

  if (!partner) {
    await bot.sendMessage(userId, '❌ خطا در دریافت اطلاعات مخاطب.');
    return;
  }

  const profileText = `
👤 <b>پروفایل مخاطب</b>

📝 نام: ${partner.name}
🚻 جنسیت: ${partner.gender}
📍 موقعیت: ${partner.city}, ${partner.province}
🎂 سن: ${partner.age}
  `;

  await bot.sendPhoto(userId, partner.profile_pic, {
    caption: profileText,
    parse_mode: 'HTML',
    reply_markup: keyboards.chatKeyboard(),
  });
}

// ========================
// Report Handler
// ========================

export async function handleReport(env: Env, bot: TelegramBot, message: TelegramMessage): Promise<void> {
  const userId = message.from.id;
  const partnerId = await db.getPartner(env, userId);

  if (!partnerId) {
    await bot.sendMessage(
      userId,
      '❌ شما در چت نیستید.',
      { reply_markup: keyboards.mainKeyboard() }
    );
    return;
  }

  // Create report
  await db.createReport(env, userId, partnerId, 'User reported during chat');

  // End chat
  await db.endChat(env, userId);

  await bot.sendMessage(
    userId,
    '✅ گزارش شما ثبت شد. متشکریم.\n\nچت به پایان رسید.',
    { reply_markup: keyboards.mainKeyboard() }
  );

  // Notify admin
  try {
    const reporter = await db.getUser(env, userId);
    const reported = await db.getUser(env, partnerId);
    
    await bot.sendMessage(
      parseInt(env.ADMIN_ID),
      `⚠️ گزارش جدید\n\nگزارش‌دهنده: ${reporter?.name} (${userId})\nگزارش‌شده: ${reported?.name} (${partnerId})`
    );
  } catch (e) {
    console.error('Failed to notify admin:', e);
  }
}
