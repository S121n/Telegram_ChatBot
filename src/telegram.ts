import { Env } from './types';

// Telegram Bot API client
export class TelegramBot {
  private token: string;
  private apiUrl: string;

  constructor(token: string) {
    this.token = token;
    this.apiUrl = `https://api.telegram.org/bot${token}`;
  }

  async sendMessage(
    chatId: number,
    text: string,
    options: {
      reply_markup?: any;
      parse_mode?: string;
    } = {}
  ): Promise<any> {
    const response = await fetch(`${this.apiUrl}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text,
        parse_mode: options.parse_mode || 'HTML',
        reply_markup: options.reply_markup,
      }),
    });

    return response.json();
  }

  async sendPhoto(
    chatId: number,
    photo: string,
    options: {
      caption?: string;
      reply_markup?: any;
      parse_mode?: string;
    } = {}
  ): Promise<any> {
    const response = await fetch(`${this.apiUrl}/sendPhoto`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        photo,
        caption: options.caption,
        parse_mode: options.parse_mode || 'HTML',
        reply_markup: options.reply_markup,
      }),
    });

    return response.json();
  }

  async answerCallbackQuery(
    callbackQueryId: string,
    text?: string,
    showAlert: boolean = false
  ): Promise<any> {
    const response = await fetch(`${this.apiUrl}/answerCallbackQuery`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        callback_query_id: callbackQueryId,
        text,
        show_alert: showAlert,
      }),
    });

    return response.json();
  }

  async setWebhook(url: string): Promise<any> {
    const response = await fetch(`${this.apiUrl}/setWebhook`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url,
        drop_pending_updates: true,
      }),
    });

    return response.json();
  }

  async deleteWebhook(): Promise<any> {
    const response = await fetch(`${this.apiUrl}/deleteWebhook`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        drop_pending_updates: true,
      }),
    });

    return response.json();
  }
}

// Helper function to create keyboard markup
export function createKeyboard(buttons: string[][], resize = true, oneTime = false) {
  return {
    keyboard: buttons.map(row => row.map(text => ({ text }))),
    resize_keyboard: resize,
    one_time_keyboard: oneTime,
  };
}

// Helper function to create inline keyboard
export function createInlineKeyboard(buttons: { text: string; callback_data: string }[][]) {
  return {
    inline_keyboard: buttons,
  };
}

// Helper function to remove keyboard
export function removeKeyboard() {
  return {
    remove_keyboard: true,
  };
}
