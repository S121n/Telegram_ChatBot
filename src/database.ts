import { Env, User, Referral, Report, Payment, ActiveChat, WaitingUser, FSMState } from './types';

// ========================
// User Operations
// ========================

export async function getUser(env: Env, telegramId: number): Promise<User | null> {
  const user = await env.USERS.get(`user:${telegramId}`, 'json');
  return user as User | null;
}

export async function createUser(env: Env, userData: Omit<User, 'id'>): Promise<User> {
  // Generate unique ID
  const idCounter = await env.USERS.get('counter:users', 'json') as number || 0;
  const newId = idCounter + 1;
  await env.USERS.put('counter:users', JSON.stringify(newId));

  // Generate referral code
  const referralCode = `ref_${userData.telegram_id}`;

  const user: User = {
    ...userData,
    id: newId,
    referral_code: referralCode,
  };

  // Store user by telegram_id (primary key)
  await env.USERS.put(`user:${user.telegram_id}`, JSON.stringify(user));
  
  // Store mapping from referral code to telegram_id
  await env.USERS.put(`refcode:${referralCode}`, String(user.telegram_id));
  
  return user;
}

export async function updateUser(env: Env, telegramId: number, updates: Partial<User>): Promise<void> {
  const user = await getUser(env, telegramId);
  if (!user) return;

  const updatedUser = { ...user, ...updates };
  await env.USERS.put(`user:${telegramId}`, JSON.stringify(updatedUser));
}

export async function addCoins(env: Env, telegramId: number, coins: number): Promise<void> {
  const user = await getUser(env, telegramId);
  if (!user) return;

  user.coins += coins;
  await env.USERS.put(`user:${telegramId}`, JSON.stringify(user));
}

export async function getUserByReferralCode(env: Env, referralCode: string): Promise<User | null> {
  const telegramId = await env.USERS.get(`refcode:${referralCode}`);
  if (!telegramId) return null;
  
  return getUser(env, parseInt(telegramId));
}

// ========================
// Referral Operations
// ========================

export async function createReferral(env: Env, inviterTelegramId: number, invitedTelegramId: number, referralCode: string): Promise<void> {
  const idCounter = await env.REFERRALS.get('counter:referrals', 'json') as number || 0;
  const newId = idCounter + 1;
  await env.REFERRALS.put('counter:referrals', JSON.stringify(newId));

  const referral: Referral = {
    id: newId,
    inviter_telegram_id: inviterTelegramId,
    invited_telegram_id: invitedTelegramId,
    referral_code: referralCode,
    created_at: new Date().toISOString(),
  };

  await env.REFERRALS.put(`referral:${invitedTelegramId}`, JSON.stringify(referral));
}

export async function getReferral(env: Env, invitedTelegramId: number): Promise<Referral | null> {
  const referral = await env.REFERRALS.get(`referral:${invitedTelegramId}`, 'json');
  return referral as Referral | null;
}

// ========================
// Report Operations
// ========================

export async function createReport(env: Env, reporterId: number, reportedId: number, reason: string): Promise<void> {
  const idCounter = await env.REPORTS.get('counter:reports', 'json') as number || 0;
  const newId = idCounter + 1;
  await env.REPORTS.put('counter:reports', JSON.stringify(newId));

  const report: Report = {
    id: newId,
    reporter_id: reporterId,
    reported_id: reportedId,
    reason,
    created_at: new Date().toISOString(),
  };

  // Store with timestamp for potential cleanup
  const key = `report:${reportedId}:${reporterId}:${Date.now()}`;
  await env.REPORTS.put(key, JSON.stringify(report));
}

// ========================
// Payment Operations
// ========================

export async function createPayment(env: Env, userId: number, amount: number, coins: number, authority: string): Promise<void> {
  const idCounter = await env.PAYMENTS.get('counter:payments', 'json') as number || 0;
  const newId = idCounter + 1;
  await env.PAYMENTS.put('counter:payments', JSON.stringify(newId));

  const payment: Payment = {
    id: newId,
    user_id: userId,
    amount,
    coins,
    authority,
    status: 'pending',
    created_at: new Date().toISOString(),
  };

  await env.PAYMENTS.put(`payment:${authority}`, JSON.stringify(payment));
}

export async function getPayment(env: Env, authority: string): Promise<Payment | null> {
  const payment = await env.PAYMENTS.get(`payment:${authority}`, 'json');
  return payment as Payment | null;
}

export async function updatePaymentStatus(env: Env, authority: string, status: string): Promise<void> {
  const payment = await getPayment(env, authority);
  if (!payment) return;

  payment.status = status;
  await env.PAYMENTS.put(`payment:${authority}`, JSON.stringify(payment));
}

// ========================
// Chat Operations
// ========================

export async function isInChat(env: Env, userId: number): Promise<boolean> {
  const chat = await env.CHATS.get(`chat:${userId}`);
  return chat !== null;
}

export async function startChat(env: Env, user1Id: number, user2Id: number): Promise<void> {
  const chat: ActiveChat = {
    user1_id: user1Id,
    user2_id: user2Id,
    started_at: new Date().toISOString(),
  };

  await env.CHATS.put(`chat:${user1Id}`, String(user2Id));
  await env.CHATS.put(`chat:${user2Id}`, String(user1Id));
}

export async function getPartner(env: Env, userId: number): Promise<number | null> {
  const partnerId = await env.CHATS.get(`chat:${userId}`);
  return partnerId ? parseInt(partnerId) : null;
}

export async function endChat(env: Env, userId: number): Promise<number | null> {
  const partnerId = await getPartner(env, userId);
  
  if (partnerId) {
    await env.CHATS.delete(`chat:${userId}`);
    await env.CHATS.delete(`chat:${partnerId}`);
  }
  
  return partnerId;
}

// ========================
// Waiting Queue Operations
// ========================

export async function addToWaiting(env: Env, userId: number, gender: string, targetGender: string): Promise<void> {
  const waitingUser: WaitingUser = {
    id: userId,
    gender,
    target_gender: targetGender,
    timestamp: new Date().toISOString(),
  };

  // Store by user's own gender so others can find them
  // Key pattern: waiting:{user's_gender}:{userId}
  const key = `waiting:${gender}:${userId}`;
  await env.WAITING.put(key, JSON.stringify(waitingUser), {
    expirationTtl: 3600, // Expire after 1 hour
  });
}

export async function findMatch(env: Env, userId: number, gender: string, targetGender: string): Promise<WaitingUser | null> {
  // Search for users of the target gender who want someone of our gender
  // Key pattern: waiting:{gender}:{userId}
  // We want users in waiting:{targetGender}:* who have target_gender === gender
  const list = await env.WAITING.list({ prefix: `waiting:${targetGender}:` });
  
  for (const key of list.keys) {
    const waitingUserData = await env.WAITING.get(key.name, 'json') as WaitingUser;
    
    if (!waitingUserData) continue;
    
    // Check if waiting user wants someone of our gender (creating mutual match)
    if (waitingUserData.target_gender === gender && waitingUserData.id !== userId) {
      // Remove from waiting list
      await env.WAITING.delete(key.name);
      return waitingUserData;
    }
  }
  
  return null;
}

export async function removeFromWaiting(env: Env, userId: number): Promise<void> {
  // List all waiting entries and find the one for this user
  const list = await env.WAITING.list();
  
  for (const key of list.keys) {
    if (key.name.endsWith(`:${userId}`)) {
      await env.WAITING.delete(key.name);
      break;
    }
  }
}

// ========================
// FSM State Operations
// ========================

export async function getState(env: Env, userId: number): Promise<FSMState | null> {
  const state = await env.USERS.get(`state:${userId}`, 'json');
  return state as FSMState | null;
}

export async function setState(env: Env, userId: number, state: string, data: Record<string, any> = {}): Promise<void> {
  const fsmState: FSMState = { state, data };
  await env.USERS.put(`state:${userId}`, JSON.stringify(fsmState), {
    expirationTtl: 3600, // Expire after 1 hour
  });
}

export async function updateStateData(env: Env, userId: number, updates: Record<string, any>): Promise<void> {
  const currentState = await getState(env, userId);
  if (!currentState) return;

  currentState.data = { ...currentState.data, ...updates };
  await env.USERS.put(`state:${userId}`, JSON.stringify(currentState), {
    expirationTtl: 3600,
  });
}

export async function clearState(env: Env, userId: number): Promise<void> {
  await env.USERS.delete(`state:${userId}`);
}
