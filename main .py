import logging
from telegram import Update, constants
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)

class SmartFatawaBot:
    def init(self, telegram_token, ai_api_key):
        self.telegram_token = telegram_token
        
        genai.configure(api_key=ai_api_key)
        
        system_instructions = (
            "أنت باحث إسلامي سني موثوق. مهمتك الإجابة على أسئلة المستخدمين بأسلوب مهذب وميسر. "
            "اعتمد في إجاباتك حصرياً على فتاوى كبار العلماء (ابن باز، ابن عثيمين، الفوزان، اللجنة الدائمة، وموقع إسلام ويب). "
            "إذا كان السؤال واضحاً، أعطِ الخلاصة مع ذكر الدليل إن وجد. "
            "إذا كان السؤال في مسائل طبية أو مالية معقدة أو لم تكن متأكداً من الإجابة الشرعية بنسبة 100%، قل بوضوح: "
            "'عذراً، هذه المسألة تحتاج إلى تفصيل أو سؤال عالم فقيه مباشرة، ولا يسعني الإجابة عليها'."
        )
        self.model = genai.GenerativeModel(
            'gemini-1.5-flash',
            system_instruction=system_instructions
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            f"مرحباً بك {update.effective_user.first_name}.\n\n"
            "أنا الآن مساعدك الشرعي الذكي 🧠.\n"
            "اسألني أي سؤال، وسأقوم بتحليله وتلخيص الإجابة لك من أقوال كبار العلماء الموثوقين."
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_question = update.message.text
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.TYPING)
        status_msg = await update.message.reply_text("🤔 جاري تحليل سؤالك وصياغة الإجابة...")

        try:
            response = self.model.generate_content(user_question)
            answer = response.text
            
            await status_msg.edit_text(answer, parse_mode=constants.ParseMode.MARKDOWN)

        except Exception as e:
            logger.error(f"AI Error: {e}")
            await status_msg.edit_text("عذراً، حدث ضغط على النظام ولن أتمكن من الإجابة الآن. يرجى المحاولة بعد قليل.")

    def run(self):
        app = Application.builder().token(self.telegram_token).build()
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
        
        print("البوت الذكي يعمل الآن... اضغط Ctrl+C للإيقاف")
        app.run_polling(drop_pending_updates=True)

if name == 'main':
    MY_TELEGRAM_TOKEN = '8789097580:AAEPqPbidABnmzQdn0DYNGSGduq53Y9dofw' 
    MY_GEMINI_API_KEY = 'AIzaSyDDueFk_67n0U6Zxzo3VEuCPXHFMgGQ7yk'
    
    bot = SmartFatawaBot(MY_TELEGRAM_TOKEN, MY_GEMINI_API_KEY)
    bot.run()
