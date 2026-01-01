// Environment interface for Cloudflare Workers
export interface Env {
  // KV Namespaces
  USERS: KVNamespace;
  REFERRALS: KVNamespace;
  REPORTS: KVNamespace;
  PAYMENTS: KVNamespace;
  CHATS: KVNamespace;
  WAITING: KVNamespace;
  
  // Environment variables
  BOT_TOKEN: string;
  ADMIN_ID: string;
  BOT_USERNAME: string;
  ZARINPAL_MERCHANT_ID: string;
  CALLBACK_URL: string;
}

// User interface
export interface User {
  id: number;
  telegram_id: number;
  name: string;
  gender: string;
  province: string;
  city: string;
  age: number;
  profile_pic: string;
  coins: number;
  referral_code: string;
  registered_at: string;
  banned_until?: string;
}

// Referral interface
export interface Referral {
  id: number;
  inviter_telegram_id: number;
  invited_telegram_id: number;
  referral_code: string;
  created_at: string;
}

// Report interface
export interface Report {
  id: number;
  reporter_id: number;
  reported_id: number;
  reason: string;
  created_at: string;
}

// Payment interface
export interface Payment {
  id: number;
  user_id: number;
  amount: number;
  coins: number;
  authority: string;
  status: string;
  created_at: string;
}

// Chat interface
export interface ActiveChat {
  user1_id: number;
  user2_id: number;
  started_at: string;
}

// Waiting user interface
export interface WaitingUser {
  id: number;
  gender: string;
  target_gender: string;
  timestamp: string;
}

// Telegram Update types
export interface TelegramUpdate {
  update_id: number;
  message?: TelegramMessage;
  callback_query?: TelegramCallbackQuery;
}

export interface TelegramMessage {
  message_id: number;
  from: TelegramUser;
  chat: TelegramChat;
  text?: string;
  photo?: TelegramPhotoSize[];
  date: number;
}

export interface TelegramCallbackQuery {
  id: string;
  from: TelegramUser;
  message?: TelegramMessage;
  data?: string;
}

export interface TelegramUser {
  id: number;
  is_bot: boolean;
  first_name: string;
  last_name?: string;
  username?: string;
}

export interface TelegramChat {
  id: number;
  type: string;
  first_name?: string;
  last_name?: string;
  username?: string;
}

export interface TelegramPhotoSize {
  file_id: string;
  file_unique_id: string;
  width: number;
  height: number;
  file_size?: number;
}

// FSM State
export interface FSMState {
  state: string;
  data: Record<string, any>;
}
