import { Env, TelegramMessage, TelegramCallbackQuery } from '../types';
import { TelegramBot, removeKeyboard } from '../telegram';
import * as db from '../database';
import * as keyboards from '../keyboards';

// ========================
// Start Handler
// ========================

export async function handleStart(env: Env, bot: TelegramBot, message: TelegramMessage): Promise<void> {
  const userId = message.from.id;
  const user = await db.getUser(env, userId);

  if (user) {
    // User already registered
    await bot.sendMessage(userId, '👋 خوش آمدید!', {
      reply_markup: keyboards.mainKeyboard(),
    });
    return;
  }

  // New user - extract referral code if present
  let refId: number | null = null;
  if (message.text && message.text.includes('ref_')) {
    try {
      const parts = message.text.split('ref_');
      if (parts.length > 1) {
        refId = parseInt(parts[1]);
      }
    } catch (e) {
      // Invalid referral code
    }
  }

  // Store ref_id in FSM if present
  if (refId) {
    await db.setState(env, userId, 'register:name', { ref_id: refId });
  } else {
    await db.setState(env, userId, 'register:name', {});
  }

  await bot.sendMessage(userId, '👤 نام خود را وارد کنید:');
}

// ========================
// Registration Handler
// ========================

export async function handleRegistration(env: Env, bot: TelegramBot, message: TelegramMessage): Promise<void> {
  const userId = message.from.id;
  const state = await db.getState(env, userId);

  if (!state || !state.state.startsWith('register:')) {
    return;
  }

  const currentStep = state.state.split(':')[1];

  switch (currentStep) {
    case 'name':
      await handleNameStep(env, bot, message, state);
      break;
    case 'gender':
      await handleGenderStep(env, bot, message, state);
      break;
    case 'province':
      await handleProvinceStep(env, bot, message, state);
      break;
    case 'city':
      await handleCityStep(env, bot, message, state);
      break;
    case 'age':
      await handleAgeStep(env, bot, message, state);
      break;
    case 'photo':
      await handlePhotoStep(env, bot, message, state);
      break;
  }
}

async function handleNameStep(env: Env, bot: TelegramBot, message: TelegramMessage, state: any): Promise<void> {
  const name = message.text?.trim();
  
  if (!name || name.length < 2) {
    await bot.sendMessage(message.from.id, '❌ نام معتبر وارد کنید.');
    return;
  }

  await db.updateStateData(env, message.from.id, { name });
  await db.setState(env, message.from.id, 'register:gender', state.data);

  await bot.sendMessage(
    message.from.id,
    '🚻 جنسیت خود را انتخاب کنید:',
    { reply_markup: keyboards.genderKeyboard() }
  );
}

async function handleGenderStep(env: Env, bot: TelegramBot, message: TelegramMessage, state: any): Promise<void> {
  if (!message.text || !['پسر', 'دختر'].includes(message.text)) {
    await bot.sendMessage(message.from.id, '❌ فقط از دکمه‌ها استفاده کنید.');
    return;
  }

  await db.updateStateData(env, message.from.id, { gender: message.text });
  await db.setState(env, message.from.id, 'register:province', state.data);

  await bot.sendMessage(
    message.from.id,
    '📍 استان خود را انتخاب کنید:',
    { reply_markup: keyboards.provinceKeyboard() }
  );
}

async function handleProvinceStep(env: Env, bot: TelegramBot, message: TelegramMessage, state: any): Promise<void> {
  const province = message.text;

  if (!province || !keyboards.IRAN_PROVINCES[province]) {
    await bot.sendMessage(
      message.from.id,
      '❌ استان را فقط از کیبورد انتخاب کنید.',
      { reply_markup: keyboards.provinceKeyboard() }
    );
    return;
  }

  await db.updateStateData(env, message.from.id, { province });
  await db.setState(env, message.from.id, 'register:city', state.data);

  await bot.sendMessage(
    message.from.id,
    '🏙️ شهر خود را انتخاب کنید:',
    { reply_markup: keyboards.cityKeyboard(province) }
  );
}

async function handleCityStep(env: Env, bot: TelegramBot, message: TelegramMessage, state: any): Promise<void> {
  const city = message.text;
  const province = state.data.province;

  if (!city || !keyboards.IRAN_PROVINCES[province]?.includes(city)) {
    await bot.sendMessage(
      message.from.id,
      '❌ شهر را فقط از کیبورد انتخاب کنید.',
      { reply_markup: keyboards.cityKeyboard(province) }
    );
    return;
  }

  await db.updateStateData(env, message.from.id, { city });
  await db.setState(env, message.from.id, 'register:age', state.data);

  await bot.sendMessage(
    message.from.id,
    '🎂 سن خود را وارد کنید:',
    { reply_markup: removeKeyboard() }
  );
}

async function handleAgeStep(env: Env, bot: TelegramBot, message: TelegramMessage, state: any): Promise<void> {
  const text = message.text?.trim();

  if (!text || !/^\d+$/.test(text)) {
    await bot.sendMessage(message.from.id, '❌ لطفاً سن خود را فقط به صورت عدد وارد کنید.');
    return;
  }

  const age = parseInt(text);

  if (age <= 14) {
    await bot.sendMessage(message.from.id, '❌ سن شما باید بالای ۱۴ سال باشد.');
    return;
  }

  if (age > 100) {
    await bot.sendMessage(message.from.id, '❌ لطفاً سن معتبر وارد کنید.');
    return;
  }

  await db.updateStateData(env, message.from.id, { age });
  await db.setState(env, message.from.id, 'register:photo', state.data);

  await bot.sendMessage(message.from.id, '🖼️ لطفاً یک عکس پروفایل ارسال کنید:');
}

async function handlePhotoStep(env: Env, bot: TelegramBot, message: TelegramMessage, state: any): Promise<void> {
  if (!message.photo || message.photo.length === 0) {
    await bot.sendMessage(message.from.id, '❌ لطفاً فقط عکس ارسال کنید.');
    return;
  }

  const photoId = message.photo[message.photo.length - 1].file_id;
  const data = state.data;

  // Create user
  const user = await db.createUser(env, {
    telegram_id: message.from.id,
    name: data.name,
    gender: data.gender,
    province: data.province,
    city: data.city,
    age: data.age,
    profile_pic: photoId,
    coins: 15, // Initial coins
    referral_code: '', // Will be set in createUser
    registered_at: new Date().toISOString(),
  });

  // Handle referral if present
  const refId = data.ref_id;
  if (refId && refId !== user.telegram_id) {
    const inviter = await db.getUser(env, refId);
    if (inviter) {
      await db.createReferral(env, refId, user.telegram_id, inviter.referral_code);
      // Give coins to inviter
      await db.addCoins(env, refId, 10);
      
      // Notify inviter
      try {
        await bot.sendMessage(
          refId,
          `🎉 کاربر جدیدی از طریق لینک دعوت شما ثبت‌نام کرد!\n\n💰 10 سکه به حساب شما اضافه شد.`
        );
      } catch (e) {
        // Failed to notify inviter
      }
    }
  }

  await db.clearState(env, message.from.id);

  await bot.sendMessage(
    message.from.id,
    '✅ ثبت‌نام شما با موفقیت انجام شد!\n\n🎁 ۱۵ سکه دریافت کردید.',
    { reply_markup: keyboards.mainKeyboard() }
  );
}

// ========================
// Register Button Handler
// ========================

export async function handleRegisterButton(env: Env, bot: TelegramBot, message: TelegramMessage): Promise<void> {
  const userId = message.from.id;
  
  await db.clearState(env, userId);
  await db.setState(env, userId, 'register:name', {});
  
  await bot.sendMessage(userId, '📝 لطفاً نام خود را وارد کنید:', {
    reply_markup: removeKeyboard(),
  });
}
