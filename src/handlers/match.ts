import { Env, TelegramMessage } from '../types';
import { TelegramBot } from '../telegram';
import * as db from '../database';
import * as keyboards from '../keyboards';

// ========================
// Start Match Handler
// ========================

export async function handleStartMatch(env: Env, bot: TelegramBot, message: TelegramMessage): Promise<void> {
  const userId = message.from.id;

  // Check if user is already in chat
  if (await db.isInChat(env, userId)) {
    await bot.sendMessage(
      userId,
      '❌ شما در حال حاضر در چت هستید.',
      { reply_markup: keyboards.chatKeyboard() }
    );
    return;
  }

  // Show gender selection
  await bot.sendMessage(
    userId,
    '👫 میخوای به کی وصل شی ؟',
    { reply_markup: keyboards.genderKeyboard() }
  );

  // Set state to wait for gender selection
  await db.setState(env, userId, 'matching:select_gender', {});
}

// ========================
// Select Target Gender Handler
// ========================

export async function handleSelectGender(env: Env, bot: TelegramBot, message: TelegramMessage): Promise<void> {
  const targetGender = message.text;
  const userId = message.from.id;

  if (!targetGender || !['پسر', 'دختر'].includes(targetGender)) {
    return;
  }

  const user = await db.getUser(env, userId);

  if (!user) {
    await bot.sendMessage(
      userId,
      '❌ کاربر یافت نشد. لطفاً ابتدا ثبت‌نام کنید.',
      { reply_markup: keyboards.mainKeyboard() }
    );
    return;
  }

  // Check coin balance
  if (user.coins < 2) {
    await bot.sendMessage(
      userId,
      '❌ سکه کافی ندارید.\n\n💰 برای هر چت 2 سکه نیاز است.\nاز منوی اصلی می‌توانید سکه خریداری کنید.',
      { reply_markup: keyboards.mainKeyboard() }
    );
    return;
  }

  // Try to find a match
  const match = await db.findMatch(env, userId, user.gender, targetGender);

  if (match) {
    // Deduct coins from both users
    await db.addCoins(env, userId, -2);
    await db.addCoins(env, match.id, -2);

    // Start chat
    await db.startChat(env, userId, match.id);

    // Clear any waiting state
    await db.clearState(env, userId);
    await db.clearState(env, match.id);

    // Notify both users
    await bot.sendMessage(
      userId,
      '✅ مخاطب پیدا شد!\n\n💬 می‌توانید شروع به چت کنید.',
      { reply_markup: keyboards.chatKeyboard() }
    );

    try {
      await bot.sendMessage(
        match.id,
        '✅ مخاطب پیدا شد!\n\n💬 می‌توانید شروع به چت کنید.',
        { reply_markup: keyboards.chatKeyboard() }
      );
    } catch (e) {
      console.error('Failed to notify partner:', e);
    }
  } else {
    // Add to waiting list
    await db.addToWaiting(env, userId, user.gender, targetGender);
    await db.clearState(env, userId);
    
    await bot.sendMessage(
      userId,
      '⏳ در حال جستجوی مخاطب...\n\nلطفاً صبر کنید تا مخاطبی پیدا شود.',
      { reply_markup: keyboards.mainKeyboard() }
    );
  }
}
