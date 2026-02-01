# ============================================
# 🐍 VIPER ELITE ASSISTANT BOT - VERSIONE ULTRA PRO 2026
# Bot Telegram per gestione clienti Viper Elite Pro
# Creato per: Assistenza e vendita software roulette
# VERSIONE ULTRA PREMIUM CON ASCII ART + CHAT DIRETTA
# ============================================

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import datetime
import json
import os

# =========================================
# CONFIGURAZIONE - MODIFICA QUESTI VALORI
# =========================================

# 1. Inserisci il TOKEN del tuo bot (dal file token_bot.txt)
TOKEN = os.getenv("BOT_TOKEN")

# 2. Inserisci il TUO user ID Telegram (per ricevere notifiche)
# Per trovarlo: avvia il bot e scrivi /getmyid
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# 3. File per salvare i dati clienti
CLIENTI_FILE = "clienti_viper.json"
LOG_FILE = "log_messaggi.txt"
ANALYTICS_FILE = "analytics_viper.json"

# =========================================
# FUNZIONI UTILITÀ
# =========================================

def salva_cliente(user_id, username, first_name, messaggio):
    """Salva info cliente in JSON"""
    try:
        # Carica clienti esistenti
        if os.path.exists(CLIENTI_FILE):
            with open(CLIENTI_FILE, 'r', encoding='utf-8') as f:
                clienti = json.load(f)
        else:
            clienti = {}

        # Aggiungi o aggiorna cliente
        if str(user_id) not in clienti:
            clienti[str(user_id)] = {
                "username": username,
                "first_name": first_name,
                "messaggi": [],
                "primo_contatto": str(datetime.datetime.now())
            }

        # Aggiungi messaggio
        clienti[str(user_id)]["messaggi"].append({
            "data": str(datetime.datetime.now()),
            "messaggio": messaggio
        })

        # Salva file
        with open(CLIENTI_FILE, 'w', encoding='utf-8') as f:
            json.dump(clienti, f, indent=2, ensure_ascii=False)

        return True
    except Exception as e:
        print(f"Errore salvataggio cliente: {e}")
        return False

def log_messaggio(user_id, username, messaggio):
    """Scrive log messaggi in file txt"""
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] User {user_id} (@{username}): {messaggio}\n")
    except:
        pass

# =========================================
# ANALYTICS E TRACKING
# =========================================

def traccia_interazione(user_id, username, first_name, tipo_azione, dettaglio=""):
    """Traccia ogni interazione utente per analytics"""
    try:
        if os.path.exists(ANALYTICS_FILE):
            with open(ANALYTICS_FILE, 'r', encoding='utf-8') as f:
                analytics = json.load(f)
        else:
            analytics = {"utenti": {}, "interazioni": []}

        user_key = str(user_id)
        if user_key not in analytics["utenti"]:
            analytics["utenti"][user_key] = {
                "username": username,
                "first_name": first_name,
                "primo_accesso": str(datetime.datetime.now()),
                "contatore_azioni": {}
            }

        if tipo_azione not in analytics["utenti"][user_key]["contatore_azioni"]:
            analytics["utenti"][user_key]["contatore_azioni"][tipo_azione] = 0

        analytics["utenti"][user_key]["contatore_azioni"][tipo_azione] += 1

        analytics["interazioni"].append({
            "timestamp": str(datetime.datetime.now()),
            "user_id": user_id,
            "username": username,
            "azione": tipo_azione,
            "dettaglio": dettaglio
        })

        with open(ANALYTICS_FILE, 'w', encoding='utf-8') as f:
            json.dump(analytics, f, indent=2, ensure_ascii=False)

        return True
    except Exception as e:
        print(f"Errore tracking: {e}")
        return False

def genera_report_analytics():
    """Genera report statistiche per admin"""
    try:
        if not os.path.exists(ANALYTICS_FILE):
            return "📊 Nessun dato analytics disponibile."

        with open(ANALYTICS_FILE, 'r', encoding='utf-8') as f:
            analytics = json.load(f)

        totale_utenti = len(analytics["utenti"])
        oggi = datetime.datetime.now().date()
        inizio_settimana = oggi - datetime.timedelta(days=oggi.weekday())

        nuovi_oggi = 0
        nuovi_settimana = 0

        for user_data in analytics["utenti"].values():
            data_accesso = datetime.datetime.fromisoformat(user_data["primo_accesso"]).date()
            if data_accesso == oggi:
                nuovi_oggi += 1
            if data_accesso >= inizio_settimana:
                nuovi_settimana += 1

        conteggio_azioni = {}
        for interazione in analytics["interazioni"]:
            azione = interazione["azione"]
            if azione not in conteggio_azioni:
                conteggio_azioni[azione] = 0
            conteggio_azioni[azione] += 1

        top_azioni = sorted(conteggio_azioni.items(), key=lambda x: x[1], reverse=True)[:10]

        clicks_acquista = conteggio_azioni.get("click_acquista", 0)
        clicks_prezzi = conteggio_azioni.get("click_prezzi", 0)
        totale_click = sum(conteggio_azioni.values())
        conversione = (clicks_acquista / totale_click * 100) if totale_click > 0 else 0

        report_lines = [
            "╔═══════════════════════════════╗",
            "║ 📊 VIPER BOT ANALYTICS 📊 ║",
            "╚═══════════════════════════════╝",
            "",
            "👥 **UTENTI:**",
            f"• Totali: {totale_utenti}",
            f"• Nuovi Oggi: +{nuovi_oggi}",
            f"• Nuovi Settimana: +{nuovi_settimana}",
            "",
            "🔥 **TOP 10 SEZIONI:**"
        ]

        emoji_map = {
            "start": "🚀",
            "click_prezzi": "💰",
            "click_video": "🎥",
            "click_funzionalita": "⚡",
            "click_acquista": "💎",
            "click_assistenza": "📞",
            "click_faq": "❓",
            "messaggio": "💬"
        }

        for i, (azione, count) in enumerate(top_azioni, 1):
            emoji = emoji_map.get(azione, "•")
            nome = azione.replace("click_", "").replace("_", " ").title()
            report_lines.append(f"{i}. {emoji} {nome}: {count} clicks")

        report_lines.extend([
            "",
            "📈 **CONVERSIONE:**",
            f"• Click su Prezzi: {clicks_prezzi}",
            f"• Click su Acquista: {clicks_acquista}",
            f"• Tasso Conversione: {conversione:.1f}%",
            "",
            f"📊 **TOTALE INTERAZIONI:** {len(analytics['interazioni'])}",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"Aggiornato: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
        ])

        return "\n".join(report_lines)
    except Exception as e:
        return f"❌ Errore generazione report: {e}"

# =========================================
# MENU E TASTIERE
# =========================================

def get_main_menu():
    """Restituisce la tastiera del menu principale"""
    keyboard = [
        [InlineKeyboardButton("💰 Prezzi e Abbonamenti", callback_data="prezzi")],
        [InlineKeyboardButton("🎥 Video Demo", callback_data="video")],
        [InlineKeyboardButton("⚡ Funzionalità Software", callback_data="funzionalita")],
        [InlineKeyboardButton("💎 Acquista Ora", callback_data="acquista")],
        [InlineKeyboardButton("📞 Assistenza", callback_data="assistenza")],
        [InlineKeyboardButton("❓ FAQ", callback_data="faq")]
    ]
    return InlineKeyboardMarkup(keyboard)

# =========================================
# HANDLERS COMANDI
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Messaggio di benvenuto"""
    user = update.effective_user
    traccia_interazione(user.id, user.username, user.first_name, "start", "Comando /start")

    welcome = f"""
╔═══════════════════════════════╗
║                               ║
║     🐍 VIPER ELITE PRO 🐍     ║
║                               ║
║   ╔═══════════════════════╗   ║
║   ║     🎰 ROULETTE 🎰    ║   ║
║   ║                       ║   ║
║   ║  🔴 32 15 ⚫ 19 🔴   ║   ║
║   ║  ⚫ 4  21 🔴 2  ⚫   ║   ║
║   ║  🔴 25 17 ⚫ 34 🔴   ║   ║
║   ║  ⚫ 6  27 🔴 13 ⚫   ║   ║
║   ║                       ║   ║
║   ╚═══════════════════════╝   ║
║                               ║
║   🤖 AI PREDICTION SYSTEM     ║
║                               ║
╚═══════════════════════════════╝

👋 **Ciao {user.first_name}!**

Benvenuto nel sistema di assistenza del **software di predizione roulette più avanzato del 2026**.

╔═══════════════════════════════╗
║   🔥 CARATTERISTICHE VIPER:   ║
╠═══════════════════════════════╣
║  🤖 5 Algoritmi AI paralleli  ║
║  🎯 Sistema ENSEMBLE Multi    ║
║  ⚡ Predizioni tempo reale    ║
║  💰 7 Sistemi Montante        ║
║  📊 Win Rate 65-75%           ║
║  🎯 AutoClick Puntate         ║
║  📈 Grafici sganciabili       ║
╚═══════════════════════════════╝

👇 **Usa i bottoni qui sotto** 👇
"""

    await update.message.reply_text(
        welcome,
        reply_markup=get_main_menu()
    )

async def getmyid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /getmyid - Mostra l'ID dell'utente"""
    user_id = update.effective_user.id
    await update.message.reply_text(f"🆔 Il tuo Telegram ID è: `{user_id}`")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stats - Mostra analytics (solo admin)"""
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Comando riservato all'amministratore.")
        return

    report = genera_report_analytics()
    await update.message.reply_text(report)

# =========================================
# COMANDO /reply PER RISPONDERE AI CLIENTI
# =========================================

async def reply_to_client(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando per rispondere ai clienti - solo admin"""
    user_id = update.effective_user.id

    # Solo l'admin può usare questo comando
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Comando riservato all'amministratore.")
        return

    # Verifica formato comando
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ **Formato errato!**\n\n"
            "Usa: /reply [user_id] [messaggio]\n\n"
            "Esempio:\n"
            "/reply 1937247536 Ciao, come posso aiutarti?"
        )
        return

    try:
        # Estrai user_id e messaggio
        target_user_id = int(context.args[0])
        reply_message = " ".join(context.args[1:])

        # Invia messaggio al cliente
        await context.bot.send_message(
            chat_id=target_user_id,
            text=f"""
╔═══════════════════════════════╗
║   💬 RISPOSTA DAL SUPPORTO 💬 ║
╚═══════════════════════════════╝

{reply_message}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 Rispondi pure qui per continuare!
"""
        )

        # Conferma all'admin
        await update.message.reply_text(
            f"✅ **Messaggio inviato con successo!**\n\n"
            f"👤 Destinatario: User ID {target_user_id}\n"
            f"💬 Tuo messaggio: {reply_message}"
        )

    except ValueError:
        await update.message.reply_text("❌ **User ID non valido!** Deve essere un numero.")
    except Exception as e:
        await update.message.reply_text(f"❌ **Errore invio messaggio:** {e}")

# =========================================
# HANDLER BOTTONI (CALLBACK)
# =========================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce i click sui bottoni"""
    query = update.callback_query
    await query.answer()

    # ANALYTICS: Traccia click bottone
    traccia_interazione(query.from_user.id, query.from_user.username, query.from_user.first_name, f"click_{query.data}", f"Click su {query.data}")

    # Menu principale
    if query.data == "menu":
        text = """
╔═══════════════════════════════╗
║                               ║
║     🐍 VIPER ELITE PRO 🐍     ║
║       MENU PRINCIPALE         ║
║                               ║
╚═══════════════════════════════╝

Seleziona cosa vuoi sapere! 👇
"""
        await query.edit_message_text(text, reply_markup=get_main_menu())

    # PREZZI
    elif query.data == "prezzi":
        text = """
╔═══════════════════════════════╗
║     💰 PREZZI E PIANI 💰     ║
╚═══════════════════════════════╝

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃     ⭐ PIANO MENSILE ⭐      ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                              ┃
┃       💎 €119.99/mese        ┃
┃                              ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  ✅ Tutte le funzionalità    ┃
┃  ✅ 5 Algoritmi AI           ┃
┃  ✅ Sistema ENSEMBLE         ┃
┃  ✅ AutoStart dal 5° numero  ┃
┃  ✅ AutoClick Puntate        ┃
┃  ✅ Grafici sganciabili      ┃
┃  ✅ 7 Sistemi Montante       ┃
┃  ✅ Supporto prioritario     ┃
┃  ✅ Rinnovo automatico       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃   🔥 PIANO TRIMESTRALE 🔥    ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                              ┃
┃    💎 €279.99 (3 mesi)       ┃
┃   Risparmi €80 vs mensile!   ┃
┃                              ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  ✅ TUTTO del piano mensile  ┃
┃  ✅ Supporto VIP             ┃
┃  ✅ Priorità assistenza      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃   💎 PIANO SEMESTRALE 💎     ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                              ┃
┃    💎 €449.99 (6 mesi)       ┃
┃  Risparmi €270 vs mensile!   ┃
┃                              ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  ✅ TUTTO del piano mensile  ┃
┃  ✅ Supporto VIP PREMIUM     ┃
┃  ✅ Consulenza strategie     ┃
┃  ✅ Community VIP esclusiva  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃    🏆 PIANO LIFETIME 🏆      ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                              ┃
┃     💎 €1399.99 UNICO        ┃
┃   (Paghi 1 volta, tuo        ┃
┃       per sempre!)           ┃
┃                              ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  ✅ TUTTO dei piani sopra    ┃
┃  ✅ NESSUN rinnovo MAI       ┃
┃  ✅ Aggiornamenti GRATUITI   ┃
┃      a vita                  ┃
┃  ✅ Supporto VIP PLATINUM    ┃
┃  ✅ Community esclusiva      ┃
┃  ✅ Nuove funzioni incluse   ┃
┃  ✅ Consulenze 1-to-1        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

╔═══════════════════════════════╗
║   🎁 BONUS IN TUTTI I PIANI:  ║
╠═══════════════════════════════╣
║  📄 PDF Strategie Avanzate    ║
║  🎥 Video Tutorial Completo   ║
║  📊 Guida Gestione Bankroll   ║
║  💬 Supporto Telegram 24/7    ║
╚═══════════════════════════════╝

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃    💳 METODI DI PAGAMENTO:   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

📱 **PAYPAL:**
Email: mn307316@gmail.com
Importo: Scegli il tuo piano
Causale: VIPER PRO + username

🏦 **BONIFICO BANCARIO:**
Intestatario: Gianluca Nicoletti
IBAN: IT62M0357601601010006611048
Importo: Scegli il tuo piano
Causale: VIPER PRO + username

╔═══════════════════════════════╗
║     🔥 GARANZIA 7 GIORNI     ║
║   SODDISFATTI O RIMBORSATI   ║
╚═══════════════════════════════╝

⚠️ **DOPO IL PAGAMENTO:**
📸 Invia screenshot a @System99_Official
⚡ Ricevi il software in 1 ora!
"""
        keyboard = [
            [InlineKeyboardButton("💎 Acquista Ora", callback_data="acquista")],
            [InlineKeyboardButton("🔙 Torna al Menu", callback_data="menu")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # VIDEO DEMO
    elif query.data == "video":
        text = """
╔═══════════════════════════════╗
║        🎥 VIDEO DEMO 🎥       ║
╚═══════════════════════════════╝

Guarda il software in azione! 🔥

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃     📹 VIDEO DISPONIBILI:    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

1️⃣ **Demo Completa Software**
   ⏱️ 15 minuti
   📊 Tutte le funzionalità live

2️⃣ **Sessione Live Roulette**
   ⏱️ 30 minuti
   💰 Predizioni vincenti reali

3️⃣ **Tutorial Installazione**
   ⏱️ 10 minuti
   🔧 Setup completo passo-passo

4️⃣ **Strategie Avanzate**
   ⏱️ 20 minuti
   🎯 Come usare i 7 Montante

╔═══════════════════════════════╗
║    📺 GUARDA SU YOUTUBE:     ║
║   🔗 "VIPER ELITE PRO 2026"  ║
╚═══════════════════════════════╝

💬 Per link diretti clicca "Assistenza"!
"""
        keyboard = [
            [InlineKeyboardButton("📞 Ricevi Link Video", callback_data="assistenza")],
            [InlineKeyboardButton("🔙 Torna al Menu", callback_data="menu")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # FUNZIONALITÀ
    elif query.data == "funzionalita":
        text = """
╔═══════════════════════════════╗
║    ⚡ FUNZIONALITÀ 2026 ⚡    ║
╚═══════════════════════════════╝

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🤖 5 ALGORITMI AI PARALLELI ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🎯 Pattern Recognition AI
   └─ Riconosce schemi ricorrenti

📊 Probabilistic Engine
   └─ Calcoli probabilistici avanzati

🌡️ Sector Analyzer
   └─ Analisi settori caldi/freddi

🔮 Sequence Predictor
   └─ Previsione sequenze

🔥 Hot Numbers Tracker
   └─ Tracking numeri frequenti

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃      🎯 SISTEMA ENSEMBLE:    ┃
┃  Gli AI votano insieme la    ┃
┃    predizione migliore!      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃   🔥 FUNZIONI KILLER 2026:   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🎯 **AUTOCLICK PUNTATE MAGICO**
Il cursore si muove DA SOLO e
punta automaticamente i numeri
predetti sul tappeto roulette!
Velocità fulmine ⚡
Precisione laser 🎯

📈 **GRAFICI WIN/LOSS VOLANTI**
Grafico bankroll SGANCIABILE!
Lo trascini dove vuoi sullo
schermo mentre giochi. Sempre
visibile, sempre aggiornato! 💎

⚡ **AUTOSTART PREDIZIONI ISTANTANEE**
DIMENTICA I 25 NUMERI!
Dal 5° numero inserito il VIPER
già PREVEDE IL FUTURO della ruota!
Predizioni DEVASTANTI immediate!
Aggancio alla ruota FULMINEO! 🔥
Non aspetti più - DOMINI SUBITO!

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃    💰 7 SISTEMI MONTANTE:    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

1️⃣ Martingala Classica
2️⃣ Reverse Martingala
3️⃣ D'Alembert Progressivo
4️⃣ Fibonacci Avanzato
5️⃣ Labouchère Modificato
6️⃣ Paroli System
7️⃣ Custom Strategy (tua!)

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃   📊 STATISTICHE AVANZATE:   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

✅ Win Rate tempo reale
✅ Profitto/Perdita sessione
✅ Numeri caldi ultimi 100 spin
✅ Analisi settori ruota
✅ Grafici trend vincite
✅ Report sessione PDF

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🎮 INTERFACCIA PROFESSIONAL ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

✅ Dashboard moderna
✅ Input rapido numeri
✅ Predizioni immediate
✅ Puntate automatiche
✅ Gestione bankroll auto
✅ Modalità "Stealth" casino

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃      🔐 SICUREZZA 100%:      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

✅ Licenza VIP personale
✅ Nessuna connessione online
✅ Dati salvati in locale
✅ Privacy garantita

💎 Clicca "Acquista" per dominare!
"""
        keyboard = [
            [InlineKeyboardButton("💎 Acquista Ora", callback_data="acquista")],
            [InlineKeyboardButton("🔙 Torna al Menu", callback_data="menu")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # ACQUISTA
    elif query.data == "acquista":
        text = """
╔═══════════════════════════════╗
║     💎 ACQUISTA ADESSO! 💎    ║
╚═══════════════════════════════╝

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃     PIANI DISPONIBILI:       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

⭐ **MENSILE:** €119.99/mese
🔥 **TRIMESTRALE:** €279.99 (3 mesi)
💎 **SEMESTRALE:** €449.99 (6 mesi)
🏆 **LIFETIME:** €1399.99 (1 VOLTA!)

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃     COSA RICEVI SUBITO:      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

✅ Software viper_elite_pro.py
✅ Licenza VIP attivata
✅ AutoClick Puntate Magico 🎯
✅ Grafici Win/Loss sganciabili 📈
✅ AutoStart dal 5° numero ⚡
✅ 5 Algoritmi AI + ENSEMBLE 🤖
✅ 7 Sistemi Montante 💰
✅ Guida installazione PDF
✅ Video tutorial completi
✅ Supporto 24/7
✅ Community VIP Telegram
✅ Aggiornamenti futuri gratis

╔═══════════════════════════════╗
║       💳 COME PAGARE:        ║
╚═══════════════════════════════╝

📱 **PAYPAL:**
┌─────────────────────────────┐
│ 1. Invia a:                 │
│    mn307316@gmail.com       │
│                             │
│ 2. Importo:                 │
│    Scegli il tuo piano:     │
│    • Mensile: €119.99       │
│    • Trimestrale: €279.99   │
│    • Semestrale: €449.99    │
│    • Lifetime: €1399.99     │
│                             │
│ 3. Causale:                 │
│    VIPER PRO + username     │
│                             │
│ 4. Tipo:                    │
│    "Amici e Parenti"        │
│    (no commissioni)         │
└─────────────────────────────┘

🏦 **BONIFICO BANCARIO:**
┌─────────────────────────────┐
│ Intestatario:               │
│ Gianluca Nicoletti          │
│                             │
│ IBAN:                       │
│ IT62M0357601601010006611048 │
│                             │
│ Importo:                    │
│ Scegli il tuo piano:        │
│ • Mensile: €119.99          │
│ • Trimestrale: €279.99      │
│ • Semestrale: €449.99       │
│ • Lifetime: €1399.99        │
│                             │
│ Causale:                    │
│ VIPER PRO + username        │
└─────────────────────────────┘

╔═══════════════════════════════╗
║   ⚠️ DOPO IL PAGAMENTO:     ║
╠═══════════════════════════════╣
║   📸 Invia screenshot        ║
║   conferma pagamento         ║
║   a @System99_Official       ║
║                              ║
║   ⚡ Ricevi software in 1 ora! ║
╚═══════════════════════════════╝

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃      🔥 GARANZIA 7 GIORNI    ┃
┃   SODDISFATTI O RIMBORSATI   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

**Clicca qui sotto per confermare!** 👇
"""
        keyboard = [
            [InlineKeyboardButton("💎 HO PAGATO - INVIA CONFERMA", url="https://t.me/System99_Official")],
            [InlineKeyboardButton("💬 Domande sul pagamento?", callback_data="assistenza")],
            [InlineKeyboardButton("🔙 Torna al Menu", callback_data="menu")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # ASSISTENZA
    elif query.data == "assistenza":
        text = """
╔═══════════════════════════════╗
║     📞 ASSISTENZA 24/7 📞    ║
╚═══════════════════════════════╝

Hai bisogno di aiuto? 💪
Siamo qui per te!

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃      CONTATTI DIRETTI:       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

👤 **Telegram Proprietario:**
@System99_Official
https://t.me/System99_Official

📧 **Email Supporto:**
mn307316@gmail.com
(risposta entro 24h)

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  SUPPORTO DISPONIBILE PER:   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

✅ Domande pre-acquisto
✅ Assistenza pagamento
✅ Problemi tecnici
✅ Richieste personalizzazioni
✅ Consulenza strategie
✅ Qualsiasi altra domanda

╔═══════════════════════════════╗
║      💬 COMMUNITY VIP:       ║
║  Dopo acquisto ricevi accesso ║
║   al gruppo esclusivo clienti! ║
╚═══════════════════════════════╝

⏰ **Orari supporto:**
Lun-Dom: 9:00 - 23:00 (CET)
Risposta media: 1-2 ore

**Scrivi qui o clicca bottone sotto!** 👇
"""
        keyboard = [
            [InlineKeyboardButton("💬 CONTATTA PROPRIETARIO", url="https://t.me/System99_Official")],
            [InlineKeyboardButton("🔙 Torna al Menu", callback_data="menu")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # FAQ
    elif query.data == "faq":
        text = """
╔═══════════════════════════════╗
║     ❓ FAQ - DOMANDE ❓      ║
╚═══════════════════════════════╝

**Q: Il software funziona davvero?**
A: VIPER usa 5 AI che analizzano
pattern e probabilità. Non è magia,
ma matematica avanzata! Aumenta
significativamente le tue vincite!

**Q: Cos'è l'AutoStart dal 5° numero?**
A: Non serve più inserire 25 numeri!
Dal 5° numero inserito VIPER già
predice e si aggancia alla ruota
con predizioni devastanti!

**Q: Come funziona l'AutoClick?**
A: Il cursore si muove DA SOLO e
clicca automaticamente i numeri
predetti sul tappeto! Fulmineo!

**Q: Serve connessione internet?**
A: NO! Funziona 100% offline dopo
installazione. Privacy totale.

**Q: Su quali dispositivi?**
A: Windows, Mac, Linux. Serve solo
Python (ti diamo guida completa).

**Q: Posso usarlo nei casino online?**
A: SÌ! Funziona con qualsiasi roulette
(fisica o online). Inserisci numeri
e ricevi predizioni immediate.

**Q: Quanto posso vincere?**
A: Dipende da bankroll e disciplina.
Clienti riportano win rate 65-75%
con gestione corretta!

**Q: C'è garanzia?**
A: SÌ! 7 giorni soddisfatti o
rimborsati, nessuna domanda.

**Q: Ricevo aggiornamenti?**
A: SÌ! Tutti gli aggiornamenti futuri
sono GRATUITI (specie con Lifetime).

**Q: È legale?**
A: SÌ! È software di analisi
statistica, completamente legale.

**Q: Serve esperienza programmazione?**
A: NO! Interfaccia user-friendly,
basta seguire la guida.

**Q: Supporto in italiano?**
A: SÌ! Supporto completo italiano 24/7.

Altre domande? Clicca "Assistenza"! 💬
"""
        keyboard = [
            [InlineKeyboardButton("📞 Altre Domande?", callback_data="assistenza")],
            [InlineKeyboardButton("💎 Acquista Ora", callback_data="acquista")],
            [InlineKeyboardButton("🔙 Torna al Menu", callback_data="menu")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# =========================================
# HANDLER MESSAGGI CON FORWARD DIRETTO
# =========================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce i messaggi degli utenti - CON FORWARD DIRETTO ALL'ADMIN"""
    user = update.effective_user
    message_text = update.message.text

    # ANALYTICS: Traccia messaggio
    traccia_interazione(user.id, user.username, user.first_name, "messaggio", message_text[:50])

    # Salva messaggio cliente
    salva_cliente(user.id, user.username, user.first_name, message_text)
    log_messaggio(user.id, user.username, message_text)

    # 🔥 FORWARD DIRETTO ALL'ADMIN!
    if ADMIN_ID != 0:
        try:
            # INOLTRA il messaggio originale del cliente
            await context.bot.forward_message(
                chat_id=ADMIN_ID,
                from_chat_id=update.message.chat_id,
                message_id=update.message.message_id
            )

            # Invia notifica con info cliente e istruzioni risposta
            info_cliente = f"""
╔═══════════════════════════════╗
║  🔔 NUOVO CLIENTE! RISPONDI!  ║
╚═══════════════════════════════╝

👤 **User:** {user.first_name}
    @{user.username if user.username else 'nessun username'}
🆔 **ID:** {user.id}
📅 **Data:** {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⬆️ **MESSAGGIO DEL CLIENTE QUI SOPRA** ⬆️

💬 **PER RISPONDERE:**
Usa il comando:
/reply {user.id} tuo messaggio qui

📝 **Esempio:**
/reply {user.id} Ciao! Come posso aiutarti?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**TOTALE INTERAZIONI:** {len(analytics['interazioni']) if os.path.exists(ANALYTICS_FILE) else 0}
"""

            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=info_cliente
            )

        except Exception as e:
            print(f"Errore forward messaggio: {e}")

    # Risposta automatica al cliente
    risposta = f"""
╔═══════════════════════════════╗
║   ✅ MESSAGGIO RICEVUTO! ✅   ║
╚═══════════════════════════════╝

Ciao **{user.first_name}**! 👋

Un operatore ti risponderà
entro 1 ora. ⏰

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃   Nel frattempo puoi:        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

• Vedere i **Prezzi**
• Guardare i **Video Demo**
• Leggere le **FAQ**

👇 Usa i bottoni per info immediate!
"""

    await update.message.reply_text(
        risposta,
        reply_markup=get_main_menu()
    )

# =========================================
# MAIN - AVVIO BOT
# =========================================

def main():
    """Funzione principale - avvia il bot"""
    print("=" * 70)
    print("🐍 VIPER ELITE ASSISTANT BOT - VERSIONE ULTRA PREMIUM 2026")
    print("=" * 70)

    # Controlla configurazione
    if ADMIN_ID == 0:
        print("⚠️  ATTENZIONE: ADMIN_ID non configurato!")
        print("   Per ricevere notifiche, avvia il bot e scrivi /getmyid")
        print("   Poi modifica ADMIN_ID nel codice.")
        print()

    # Crea applicazione
    application = Application.builder().token(TOKEN).build()

    # Registra handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("getmyid", getmyid))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("reply", reply_to_client))  # NUOVO!
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Stampa info bot
    print("✅ Bot configurato con ASCII ART ULTRA PREMIUM!")
    print("✅ SISTEMA CHAT DIRETTA ATTIVATO!")
    print(f"📱 Username: @ViperEliteAssistant_bot")
    print(f"🔗 Link: https://t.me/ViperEliteAssistant_bot")
    print(f"📊 File clienti: {CLIENTI_FILE}")
    print(f"📄 File log: {LOG_FILE}")
    print()
    print("💰 NUOVI PREZZI 2026:")
    print(f"   Mensile: €119.99")
    print(f"   Trimestrale: €279.99")
    print(f"   Semestrale: €449.99")
    print(f"   Lifetime: €1399.99")
    print()
    print("💰 DATI PAGAMENTO:")
    print(f"   PayPal: mn307316@gmail.com")
    print(f"   Bonifico: Gianluca Nicoletti")
    print(f"   IBAN: IT62M0357601601010006611048")
    print()
    print("🔥 NUOVE FEATURES:")
    print("   🎯 AutoClick Puntate Magico")
    print("   📈 Grafici Win/Loss Sganciabili")
    print("   ⚡ AutoStart dal 5° Numero")
    print()
    print("💬 SISTEMA CHAT DIRETTA:")
    print("   📨 Messaggi clienti inoltrati a te")
    print("   ✍️  Rispondi con: /reply [user_id] [messaggio]")
    print()
    print("🎨 VERSIONE: ULTRA PREMIUM ASCII ART + CHAT DIRETTA")
    print("📊 Comando ANALYTICS: /stats (solo admin)")
    print("🚀 Bot ONLINE! Premi CTRL+C per fermare.")
    print("=" * 70)

    # Avvia bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
