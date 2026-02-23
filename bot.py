import logging
import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from dotenv import load_dotenv
import os

BOT_TOKEN = os.getenv( "8439932038:AAGHVntB9u4PGhGywdaViffzml0KlXWXmA4")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Стани розмови
SETTINGS, DAILY_REPORT, GOALS = range(3)

class StrategicCoachBot:
    def __init__(self):
        self.user_data = {}  # {user_id: {"goals_1y": "", "goals_3m": "", ...}}
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        keyboard = [
            [InlineKeyboardButton("⚙️ Налаштувати цілі", callback_data="setup_goals")],
            [InlineKeyboardButton("📊 Сьогоднішній звіт", callback_data="daily_report")],
            [InlineKeyboardButton("📈 Мій план", callback_data="show_plan")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = (
            "🤖 **Стратегічний AI-Наставник**\n\n"
            "Я аналізую твою поведінку, цілі та дії.\n"
            "Формую чіткий план для довгострокового успіху.\n\n"
            "Спочатку налаштуй цілі ➡️"
        )
        
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)
        
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                "вік": 25, "цілі_1рік": "", "цілі_3місяці": "", 
                "години": 4, "перешкоди": "", "історія": [], "сьогодні": ""
            }
        return SETTINGS
    
    async def setup_goals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "⚙️ **Налаштування цілей**\n\n"
            "1. Твій вік:\n"
            "2. Цілі на 1 рік:\n"
            "3. Цілі на 3 місяці:\n"
            "4. Годин на день:\n"
            "5. Основні перешкоди:\n\n"
            "_Напиши все одним повідомленням або по черзі._"
        )
        return SETTINGS
    
    async def handle_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        text = update.message.text
        
        # Парсинг налаштувань (проста логіка)
        lines = text.split('\n')
        if len(lines) >= 5:
            self.user_data[user_id].update({
                "вік": int(re.findall(r'\d+', lines[0])[0]),
                "цілі_1рік": lines[1].strip(),
                "цілі_3місяці": lines[2].strip(),
                "години": int(re.findall(r'\d+', lines[3])[0]),
                "перешкоди": lines[4].strip()
            })
        
        keyboard = [[InlineKeyboardButton("✅ Готово", callback_data="goals_done")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "✅ **Цілі збережено!**\n\n"
            f"Вік: {self.user_data[user_id]['вік']}\n"
            f"1 рік: {self.user_data[user_id]['цілі_1рік'][:50]}...\n"
            f"3 місяці: {self.user_data[user_id]['цілі_3місяці'][:50]}...\n"
            f"Години: {self.user_data[user_id]['години']}\n"
            f"Перешкоди: {self.user_data[user_id]['перешкоди'][:50]}...",
            parse_mode="Markdown", reply_markup=reply_markup
        )
        return DAILY_REPORT
    
    async def daily_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "📊 **Сьогоднішній звіт**\n\n"
            "Що ти зробив сьогодні?\n"
            "• Час на основну ціль\n"
            "• Прогрес по 3-місячних задачах\n"
            "• Перешкоди дня\n\n"
            "_Приклад: '2 год кодинг, пробіжка 5км, відволікся на соцмережі'._"
        )
        return DAILY_REPORT
    
    async def handle_daily_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        self.user_data[user_id]["сьогодні"] = update.message.text
        self.user_data[user_id]["історія"].append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "report": update.message.text
        })
        
        # Генерація стратегічного плану
        plan = self.generate_strategic_plan(user_id)
        
        keyboard = [
            [InlineKeyboardButton("📈 Новий план", callback_data="new_plan")],
            [InlineKeyboardButton("📊 Історія", callback_data="history")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(plan, parse_mode="Markdown", reply_markup=reply_markup)
        return ConversationHandler.END
    
    def generate_strategic_plan(self, user_id):
        data = self.user_data[user_id]
        
        # Аналіз
        analysis = self.analyze_situation(data)
        problem = self.identify_main_problem(data)
        positives = self.find_positives(data)
        tomorrow_plan = self.create_tomorrow_plan(data)
        key_action = self.strategic_action(data)
        reflection_question = self.reflection_question(data)
        
        return (
            f"**🔍 Стратегічний аналіз**\n\n"
            f"{analysis}\n\n"
            f"**🚨 Головна системна проблема:**\n{problem}\n\n"
            f"**✅ Зроблено правильно:**\n{positives}\n\n"
            f"**📅 ПЛАН НА ЗАВТРА**\n\n"
            f"{tomorrow_plan}\n\n"
            f"**🎯 КЛЮЧОВА ДІЯ (найважливіша):**\n{key_action}\n\n"
            f"**❓ ПИТАННЯ ДЛЯ РЕФЛЕКСІЇ:**\n{reflection_question}"
        )
    
    def analyze_situation(self, data):
        # Логіка аналізу (спрощена)
        if "соцмереж" in data["сьогодні"].lower() or "відволікся" in data["сьогодні"].lower():
            return "Траєкторія відхиляється через неконтрольовані відволікання. Дисципліна на рівні 40%."
        return "Стабільний прогрес, але бракує фокусу на пріоритетах."
    
    def identify_main_problem(self, data):
        if "час" in data["перешкоди"].lower():
            return "Недостатній контроль часу — основний блокатор прогресу."
        return "Відсутність чіткої послідовності в діях."
    
    def find_positives(self, data):
        if any(word in data["сьогодні"].lower() for word in ["код", "біг", "читання"]):
            return "Фізична активність та робочий час — сильні сторони."
        return "Базова дисципліна присутня."
    
    def create_tomorrow_plan(self, data):
        hours = data["години"]
        return (
            f"**06:00-07:00** Фізична активність (30 хв біг + розтяжка)\n"
            f"**07:00-08:00** Сніданок + планування дня\n"
            f"**08:00-11:00** ГЛИБОКА РОБОТА ({hours} год на головну ціль)\n"
            f"**11:00-11:15** Перерва\n"
            f"**11:15-12:30** Навчання/доп. задачі\n"
            f"**12:30-13:30** Обід + прогулянка\n"
            f"**13:30-16:00** Робота/проєкти\n"
            f"**20:00-21:00** Рефлексія + план на завтра\n"
            f"**22:00** Сон"
        )
    
    def strategic_action(self, data):
        return "Заблокуй соцмережі на 4 год робочого часу (Freedom/StayFocusd)."
    
    def reflection_question(self, data):
        return "Яка одна звичка блокує 80% мого прогресу?"
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == "setup_goals":
            return await self.setup_goals(update, context)
        elif query.data == "daily_report":
            return await self.daily_report(update, context)
        elif query.data == "new_plan":
            user_id = query.from_user.id
            plan = self.generate_strategic_plan(user_id)
            await query.edit_message_text(plan, parse_mode="Markdown")
        elif query.data == "history":
            user_id = query.from_user.id
            history = "\n".join([f"{h['date']}: {h['report'][:50]}..." for h in self.user_data[user_id]["історія"][-5:]])
            await query.edit_message_text(f"📜 **Історія (останні 5 днів):**\n\n{history}", parse_mode="Markdown")
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("❌ Скасовано. /start для початку.")
        return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    bot = StrategicCoachBot()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", bot.start)],
        states={
            SETTINGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_settings)],
            DAILY_REPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_daily_report)],
        },
        fallbacks=[CommandHandler("cancel", bot.cancel)],
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(bot.button_handler))
    
    print("🤖 Стратегічний наставник запущено!")
    app.run_polling()

if __name__ == "__main__":
    main()
