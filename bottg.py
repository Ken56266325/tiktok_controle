from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import json
import subprocess
import random
import string
import time
import hmac
import hashlib
from decimal import Decimal
from pathlib import Path
from datetime import datetime, timedelta

TOKEN = "8884084389:AAFJfBOEfThb0ggw33np7UcFnb8zmjHJclo"
YOUR_TELEGRAM_ID = "-1002410017930"
ACCESS_CODE = "562663261106"

authorized_users = set()
last_access_request = {}
user_choices = {}

BINANCE_PAY_ID = "1246661115"
BINANCE_PAY_NAME = "TikSmmKenny"
BINANCE_API_KEY = "e1vyPEcrecEZr7EyV18x9wZLZoLCG3fWhGL3yD3NXUR6hfJ8kicKMX1h5BxijOtS"
BINANCE_SECRET_KEY = "hooDM5WbeZsVlCcO15plRBaNZ05gLlJBuD3SPxEeFn77QxQHbzSze3TDrzgMKtDj"
USED_TX_FILE = Path(__file__).with_name("used_transactions.json")
TAUX_AR_PAR_USD = Decimal("4050")


def ar_to_usdt(amount_ar: int) -> Decimal:
    return (Decimal(amount_ar) / TAUX_AR_PAR_USD).quantize(Decimal("0.01"))


def load_used_txids():
    if not USED_TX_FILE.exists():
        return set()
    try:
        return set(json.loads(USED_TX_FILE.read_text(encoding="utf-8")))
    except Exception:
        return set()


def save_used_txid(txid: str):
    used = load_used_txids()
    used.add(str(txid))
    USED_TX_FILE.write_text(json.dumps(sorted(list(used)), indent=2, ensure_ascii=False), encoding="utf-8")


def _binance_signed_get(endpoint: str, params: dict = None):
    import requests as req
    q = dict(params or {})
    q["timestamp"] = int(time.time() * 1000)
    query_string = "&".join(f"{k}={v}" for k, v in q.items())
    signature = hmac.new(BINANCE_SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    q["signature"] = signature
    try:
        r = req.get(
            f"https://api.binance.com{endpoint}",
            params=q,
            headers={"X-MBX-APIKEY": BINANCE_API_KEY},
            timeout=12,
        )
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


def verify_binance_transaction(txid: str, min_usdt: Decimal):
    try:
        start_time = int((time.time() - 90 * 86400) * 1000)
        payload = _binance_signed_get("/sapi/v1/pay/transactions", {"startTime": start_time})
        if payload and payload.get("code") == "000000":
            for tx in payload.get("data", []):
                tx_id = str(tx.get("transactionId", ""))
                note = str(tx.get("note", ""))
                order = str(tx.get("orderId", ""))
                flow = str(tx.get("fundFlow", ""))
                amount = abs(float(tx.get("amount", 0)))
                if flow == "OUT":
                    continue
                if txid in (tx_id, note, order):
                    if Decimal(str(amount)) < min_usdt:
                        return {"valid": False, "error": f"Montant insuffisant: {amount} USDT (minimum {min_usdt})"}
                    return {"valid": True, "amount": amount, "currency": tx.get("currency", "USDT")}
    except Exception:
        pass
    try:
        start_time = int((time.time() - 30 * 86400) * 1000)
        deposits = _binance_signed_get("/sapi/v1/capital/deposit/hisrec", {"startTime": start_time, "status": 1})
        if deposits:
            for dep in deposits:
                if str(dep.get("txId", "")) == txid:
                    amount = float(dep.get("amount", 0))
                    if Decimal(str(amount)) < min_usdt:
                        return {"valid": False, "error": f"Montant insuffisant: {amount} (minimum {min_usdt})"}
                    return {"valid": True, "amount": amount, "currency": dep.get("coin", "USDT")}
    except Exception:
        pass
    return {"valid": False, "error": "Transaction introuvable"}

FILE_ID_VIDEOCOOKIES="BAACAgQAAxkBAAEPkeZoyPXkHQ3rjkDhnLDAcp5dbjqK1gACUx8AAsoOSVJfg1GzMIIVezYE"
FILE_ID_COOKIES="BQACAgQAAxkBAAEPkeBoyPXDGW77tIYaYVvUJ3a8gY8qUQACmBkAAlQfQVJMyYXbTCPb9TYE"
FILE_ID_LASTMAJ ="BAACAgQAAxkBAAEPgOtoxsvAHTKnA1gvUW-4qAtw7uRNcAACdxsAAubjOFKoyUzEO9_m6jYE"
FILE_ID_MAJ2 = "BAACAgQAAxkBAAEEmihoEj7jJic6mGdSfOCOeoyqDfQedAACohgAAmp5kFAtcA3CHvETGDYE"
FILE_ID_32BIT4 = "BQACAgQAAxkBAAEEL4JoDLN12WGPLq9wgKPqXbZHcnKRtgAC2xYAAt-1YFDVMcHK9mWjdTYE"
FILE_ID_32BIT3 = "BQACAgQAAxkBAAEEL4RoDLN5mrRa_zDoTbPvQB5YNSOJCgAC3BYAAt-1YFDSFyimuIw-pzYE"
FILE_ID_32BIT2 = "BQACAgQAAxkBAAEEL5xoDLR3mizzCwcIWfV_2KRGD8qVmQACVBsAAvSuaVDhmfYdqvfXYTYE"
FILE_ID_32BIT0 = "BQACAgQAAxkBAAEEL6JoDLTXvaXmEp07hq6wB1JATsQLTwACVhsAAvSuaVD9quPKXtvd8TYE"
FILE_ID_EMAIL = "BAACAgQAAxkBAAEBfGpn2OxrQ5xCDkYkCZ59VVp94BKtUQACoBoAAiw7wVIQHg070HZLSzYE"
FILE_ID_MAJ = "BAACAgQAAxkBAAEDfh9oBd95rNB5ckfCKLdyAAGLX4PSQMkAAvIYAAILUDFQjA9AqtlIt7w2BA"
FILE_ID_MAJ1 = "BAACAgQAAxkBAAEBVotn1_LKZ66r5I73uqbp-3thqcxr7wACfxcAArnWwVIhX3Pl0CrHRTYE"
FILE_ID_32BITs = "BQACAgQAAxkBAAEC2SNn-mrCfg5KL3zOxOkzw66qQ-i1ZAACKRcAAkk92FO4xIyji3b98zYE"
FILE_ID_64BITs = "BQACAgQAAxkBAAECt-dn-Qz4pn_SnapKpM0NAgjZE5KkLQACRhcAAtz_yFMIS33MnLsZfDYE"
FILE_ID_API = "BAACAgQAAxkBAAITJGeSINsWdi6mJDD75DycW9dVlSckAAKDFQACqP1hU_MOtVwQzxuzNgQ"
FILE_ID_INSTAGRAM = "BAACAgQAAxkBAAIDlGePnx06tbKFfkHoJFrQgFoUj8B5AAKbGwACPGh4UKF9gIAj8VTyNgQ"
FILE_ID_TASK = "BAACAgQAAxkBAAIxCGeZ_RNhvvsfZZyBxRH5JfaBRi1yAAKYFgACYnrQUPTX-tUuQQ50NgQ"
FILE_ID_INSTALLATION_2 = "BAACAgQAAxkBAAIDwGePqcMxmwKPbuTooRoLyT9R6TJ9AAKwGwACPGh4UHPBD6KijC5VNgQ"
FILE_ID_TERMUX = "BQACAgQAAxkBAAIC-2ePjYblWfv6LY3P-HccnmErLgevAAK7HwACX15gU0B87cLoM-h3NgQ"
FILE_ID_32BIT = "BQACAgQAAxkBAAIcOGeTbyMvKf2ZSFGJKRF7ocV3f_IhAAJ0GgACDnuZUBKRYyDeSkZiNgQ"
FILE_ID_64BIT = "BQACAgQAAxkBAAIS-WeSHHj3vGV-BuDKZVXR2Zgni3t_AAIHGQACBGCQUFwtV6c3df2oNgQ"
FILE_ID_CHALLENGE_ERROR = "BAACAgQAAxkBAAIftWeUYiYDhJs6K36VD0faGwVY7q0UAALfGgACDnuZUIrgeMstLeXsNgQ"
FILE_ID_LOGIN_ERROR = "BAACAgQAAxkBAAImsWeW8bA_asxkLQa6xGNEGVaaVu1SAALzFQACJuuxUKU9Uxlyz489NgQ"
FILE_ID_LOGIN_ERROR1 = "BAACAgQAAxkBAAIms2eW8dtkSVcE8-FabAoxRBBqY5MVAAJ3FgACl0axUIJZ7BtgL2jXNgQ"
FILE_ID_TASK1 = "BAACAgQAAxkBAAJP6Geh6lhdxwfKr7B_2vtcMv35cytUAAIWGwAC0WMJUVXY6IOIqr__NgQ"

# ─── UTILITAIRES ───

def load_status():
    with open('status.json', 'r') as f:
        return json.load(f)

def save_status(data):
    with open('status.json', 'w') as f:
        json.dump(data, f, indent=4)
    push_to_github()

def push_to_github():
    try:
        subprocess.run(['git', 'add', 'status.json'], check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Mise à jour de status.json'], check=True, capture_output=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=True, text=True)
        print("\033[1;32m✅ Push GitHub réussi.\033[0m")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\033[1;31m❌ Erreur GitHub : {e}\033[0m")
        return False

def save_status_safe(data):
    with open('status.json', 'w') as f:
        json.dump(data, f, indent=4)
    return push_to_github()

def load_user_data():
    if not os.path.exists('user_data.json'):
        with open('user_data.json', 'w') as f:
            json.dump({}, f)
    with open('user_data.json', 'r') as f:
        return json.load(f)

def save_user_data(data):
    with open('user_data.json', 'w') as f:
        json.dump(data, f, indent=4)

def generate_random_id(base_name: str) -> str:
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return f"{base_name}{random_part}"

def api_hash_exists(api_hash: str) -> bool:
    data = load_status()
    return any(script.get('android_id') == api_hash for script in data['scripts'])

def calculate_actual_remaining_time(script):
    countdown_end = datetime.fromisoformat(script['countdown_start_time'])
    remaining_time = countdown_end - datetime.now()
    if remaining_time.total_seconds() <= 0:
        return 0, 0, 0
    days, seconds = remaining_time.days, remaining_time.seconds
    return days, seconds // 3600, (seconds % 3600) // 60

def calculate_paused_time(script):
    if 'paused_remaining_time' in script:
        total_seconds = script['paused_remaining_time']
        return total_seconds // 86400, (total_seconds % 86400) // 3600, (total_seconds % 3600) // 60
    return 0, 0, 0

def log_payment_details(action, user_telegram, plan, payment_method, transaction_id, unique_id, amount, time_remaining, referred_by=None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sep = "=" * 60
    print(f"\n{sep}\n  🔔 NOUVEAU PAIEMENT/ACTIVATION — {now}\n{sep}")
    print(f"  👤 Nom: {user_telegram.get('full_name','N/A')} | @{user_telegram.get('username','N/A')} | ID: {user_telegram.get('id','N/A')}")
    print(f"  💳 {payment_method} | Trans: {transaction_id} | {amount} AR")
    print(f"  📦 Plan: {plan} | ID: {unique_id} | Temps: {time_remaining}")
    if referred_by:
        print(f"  👥 Référent: {referred_by}")
    print(f"  ✅ {action}\n{sep}\n")

# ─── TICKETS ADMIN ───

async def send_confirmation_ticket(context, activated_id, time_remaining, payment_method, amount, transaction_id, user_telegram, referred_by=None):
    now = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
    full_name = user_telegram.get('full_name', 'N/A')
    username = f"@{user_telegram.get('username')}" if user_telegram.get('username') else "Pas de username"
    msg = (
        f"🎉 *NOUVEAU PAIEMENT CONFIRMÉ*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 *UTILISATEUR TELEGRAM*\n• Nom complet   : `{full_name}`\n• Username      : {username}\n• ID Telegram   : `{user_telegram.get('id','N/A')}`\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n💳 *PAIEMENT*\n• Méthode       : `{payment_method}`\n• ID Transaction: `{transaction_id}`\n• Montant vérifié: `{amount} AR`\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n📦 *ABONNEMENT*\n• ID activé     : `{activated_id}`\n• Temps restant : `{time_remaining}`\n"
    )
    if referred_by:
        msg += f"• ID référent   : `{referred_by}`\n"
    msg += f"\n━━━━━━━━━━━━━━━━━━━━━━\n🕐 *Heure exacte* : `{now}`\n━━━━━━━━━━━━━━━━━━━━━━\n\n✅ Activation réussie via Smmtaskerbot"
    try:
        await context.bot.send_message(chat_id=YOUR_TELEGRAM_ID, text=msg, parse_mode="Markdown")
    except Exception as e:
        print(f"⚠️ Ticket admin non envoyé: {e}")

async def send_affiliation_confirmation_ticket(context, payer_id, activated_id, plan, price, balance_before, balance_after, expiration_date):
    msg = (
        f"🎉 **Ticket de Confirmation Affiliation**\n\n"
        f"🆔 **ID payeur** : `{payer_id}`\n"
        f"🆔 **ID activé** : `{activated_id}`\n"
        f"📜 **Plan activé** : {plan}\n"
        f"💸 **Montant déduit** : `{price} AR`\n"
        f"💰 **Solde avant** : `{balance_before} AR`\n"
        f"💰 **Solde après** : `{balance_after} AR`\n"
        f"📅 **Date d'expiration** : {expiration_date}\n\n"
        "Merci d'utiliser Affiliation Bot !"
    )
    try:
        await context.bot.send_message(chat_id=YOUR_TELEGRAM_ID, text=msg, parse_mode="Markdown")
    except Exception as e:
        print(f"⚠️ Ticket affiliation non envoyé: {e}")

async def send_balance_addition_ticket(context, user_id, balance_before, payment_method, transaction_id, amount_added, balance_after):
    msg = (
        f"💰 **Ticket d'Ajout de Solde - Vérification Admin**\n\n"
        f"🆔 **ID utilisateur** : `{user_id}`\n"
        f"💰 **Solde avant ajout** : `{balance_before} AR`\n"
        f"💳 **Mode de paiement** : {payment_method}\n"
        f"🔢 **ID de transaction** : `{transaction_id}`\n"
        f"💸 **Montant ajouté** : `{amount_added} AR`\n"
        f"💰 **Solde actuel total** : `{balance_after} AR`\n\n"
        "⚠️ Veuillez vérifier cette transaction."
    )
    try:
        await context.bot.send_message(chat_id=YOUR_TELEGRAM_ID, text=msg, parse_mode="Markdown")
    except Exception as e:
        print(f"⚠️ Ticket solde non envoyé: {e}")

# ─── MENUS ───

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in authorized_users:
        await show_main_menu(update)
    else:
        await update.message.reply_text("🔒 Veuillez entrer le code d'accès pour utiliser ce bot :")

async def handle_access_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    if user_id not in authorized_users:
        if text == ACCESS_CODE:
            authorized_users.add(user_id)
            await update.message.reply_text("✅ Accès accordé !")
            await show_main_menu(update)
        else:
            await update.message.reply_text("❌ Code incorrect. Veuillez réessayer :")
    else:
        await handle_choice(update, context)

async def show_main_menu(update: Update):
    keyboard = [
        ["📖 Voir des Tuto", "🔄 Renouveler un abonnement"],
        ["📞 Contacter le service client", "🆔 Obtenir un ID unique"],
        ["📢📣ANNONCE... 📢📣"],
        ["⏸️ Activer/Pause mon ID", "💰 Affiliation"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(
        "👋 Bienvenue sur Smmtaskerbot !\n\nChoisissez une option ci-dessous :",
        reply_markup=reply_markup
    )
    await update.message.reply_text(
        "\n⛔RAHA TOA KA,HANARAKA TUTO/HANAO INSTALLATION DIA TSINDRIO NY:📖 Voir des Tuto ,\n"
        "\n⛔RAHA TOA KOSA KA HANDOHA ABONNEMENT DIA TSINDRIO NY: 🔄 Renouveler un abonnement ,\n"
        "\n⛔RAHA TOA KOSA KA HIRESAKA MIVANTANA @ 'SERVICE CLIENT' DIA TSINDRIO NY:📞 Contacter le service client.\n"
    )

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # ─── RETOUR AU MENU PRINCIPAL (priorité absolue) ───
    if text == "⬅️ Retour au menu principal":
        if user_id in user_choices:
            del user_choices[user_id]
        context.user_data.clear()
        await show_main_menu(update)
        return

    # ─── ANNULER (priorité haute) ───
    if text in ["⬅️ Annuler", "❌ Annuler"]:
        if user_id in user_choices:
            del user_choices[user_id]
        context.user_data.pop('in_affiliation', None)
        await show_main_menu(update)
        return

    # ─── RETOUR (priorité haute) ───
    if text == "⬅️ Retour":
        if context.user_data.get('in_affiliation'):
            await show_affil_renewal_menu(update, user_id, context)
        else:
            await show_payment_options(update)
        return

    # ─── PAIEMENT DIRECT Mvola/AirtelMoney/Binance/Confirmer (priorité haute) ───
    if text == "Binance Pay" and user_id in user_choices and isinstance(user_choices[user_id], dict) and user_choices[user_id].get("plan") and not user_choices[user_id].get("action"):
        await handle_binance_payment(update, context)
        return

    if text == "✅ J'ai payé Binance — Confirmer" and user_id in user_choices:
        context.user_data['waiting_binance_txid'] = True
        await update.message.reply_text(
            "🧾 Envoyez maintenant votre *Transaction ID* Binance :",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([["⬅️ Retour"]], resize_keyboard=True)
        )
        return

    if context.user_data.get('waiting_binance_txid'):
        await process_binance_txid(update, context)
        return

    # ─── ID unique après Binance validé (paiement direct) ───
    if context.user_data.get('waiting_unique_id_after_binance'):
        context.user_data.pop('waiting_unique_id_after_binance', None)
        user_choices[user_id]["user_id"] = text
        await update_subscription(update, context)
        return

    if text == "Mvola" and user_id in user_choices and isinstance(user_choices[user_id], dict) and user_choices[user_id].get("plan") and not user_choices[user_id].get("action") and "amount_missing" not in user_choices[user_id]:
        await handle_payment(update, context, "Mvola")
        return

    if text == "AirtelMoney" and user_id in user_choices and isinstance(user_choices[user_id], dict) and user_choices[user_id].get("plan") and not user_choices[user_id].get("action") and "amount_missing" not in user_choices[user_id]:
        await handle_payment(update, context, "AirtelMoney")
        return

    if text == "Confirmer le paiement" and user_id in user_choices and isinstance(user_choices[user_id], dict) and user_choices[user_id].get("payment_method") and not user_choices[user_id].get("action"):
        await request_transaction_id(update, context, user_choices[user_id]["payment_method"])
        return

    # ─── ID transaction affiliation (priorité haute, avant les elif) ───
    if context.user_data.get('waiting_for_affil_transaction_id'):
        await verify_affil_payment(update, context)
        return

    # ─── OBTENIR UN ID UNIQUE ───
    if text == "🆔 Obtenir un ID unique":
        await update.message.reply_text(
            "👤 Veuillez entrer un SEUL nom Telegram (sans espace) pour obtenir un ID unique :",
            reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True)
        )
        context.user_data['create_id_step'] = 'waiting_telegram_name'

    elif context.user_data.get('create_id_step') == 'waiting_telegram_name':
        telegram_name = text.strip()
        if ' ' in telegram_name:
            await update.message.reply_text("❌ Veuillez entrer un SEUL nom sans espaces. Exemple: 'KennyBot'")
            return
        context.user_data['new_user'] = {'telegram_name': telegram_name}
        context.user_data['create_id_step'] = 'waiting_api_hash'
        await update.message.reply_text(f"🔑 Veuillez maintenant entrer l'API hash pour {telegram_name} :")

    elif context.user_data.get('create_id_step') == 'waiting_api_hash':
        api_hash = text.strip()
        if api_hash_exists(api_hash):
            await update.message.reply_text(
                "❌ Cet API hash existe déjà dans notre système. Veuillez en fournir un autre.",
                reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True)
            )
            context.user_data.pop('create_id_step', None)
            context.user_data.pop('new_user', None)
            return
        context.user_data['new_user']['api_hash'] = api_hash
        context.user_data['create_id_step'] = 'waiting_referrer'
        await update.message.reply_text(
            "👥 Ce compte a-t-il été référé par quelqu'un ?\nSi oui, entrez l'ID du référent.\nSinon, tapez: pas de référent",
            reply_markup=ReplyKeyboardMarkup([["pas de référent"], ["⬅️ Retour au menu principal"]], resize_keyboard=True)
        )

    elif context.user_data.get('create_id_step') == 'waiting_referrer':
        referrer_id = None if text.strip().lower() == 'pas de référent' else text.strip()
        new_user_data = context.user_data.get('new_user', {})
        telegram_name = new_user_data.get('telegram_name')
        api_hash = new_user_data.get('api_hash')

        if not telegram_name or not api_hash:
            await update.message.reply_text("❌ Une erreur s'est produite. Veuillez recommencer.")
            context.user_data.pop('create_id_step', None)
            context.user_data.pop('new_user', None)
            await show_main_menu(update)
            return

        import asyncio
        new_id = generate_random_id(telegram_name)
        data = load_status()
        new_entry = {
            'id': new_id,
            'android_id': api_hash,
            'referred_by': referrer_id,
            'referred_to': [],
            'status': 'active',
            'countdown_start_time': (datetime.now() + timedelta(hours=3)).isoformat(),
            'affiliation_balance': 0,
            'plan': 'Semaine',
            'pause_count': 0,
            'max_pauses': 3
        }
        data['scripts'].append(new_entry)
        if referrer_id:
            for script in data['scripts']:
                if script['id'] == referrer_id:
                    script.setdefault('referred_to', []).append(new_id)
                    break

        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sep = '=' * 55
        print(f"\n{sep}\n  🆔 CRÉATION D'ID — {now_str}\n{sep}")
        print(f"  👤 Nom Telegram  : {telegram_name}")
        print(f"  🆔 ID généré     : {new_id}")
        print(f"  🔑 API Hash      : {api_hash}")
        print(f"  👥 Référent      : {referrer_id if referrer_id else 'Aucun'}")
        print(f"  📤 Push GitHub   : en cours...")

        wait_msg = await update.message.reply_text("⏳ Génération de votre ID en cours.")
        frames = ["⏳ Génération de votre ID en cours.", "⏳ Génération de votre ID en cours..", "⏳ Génération de votre ID en cours...", "🔄 Génération de votre ID en cours..."]
        for frame in frames:
            await asyncio.sleep(0.6)
            try:
                await wait_msg.edit_text(frame)
            except Exception:
                pass

        with open('status.json', 'w') as f:
            json.dump(data, f, indent=4)
        success = push_to_github()
        print(f"  {'✅ Push réussi' if success else '❌ Push échoué'}\n{sep}\n")

        try:
            await wait_msg.delete()
        except Exception:
            pass

        context.user_data.pop('create_id_step', None)
        context.user_data.pop('new_user', None)

        if not success:
            await update.message.reply_text(
                "❌ Une erreur s'est produite lors de la génération de votre ID. Veuillez contacter le service client via : @Kenny5626 ou @taskersupport_bot",
                reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True)
            )
            return

        await update.message.reply_text(
            f"🎉 ID UNIQUE CRÉÉ AVEC SUCCÈS !\n\n"
            f"👤 Nom Telegram: {telegram_name}\n"
            f"🆔 ID généré: `{new_id}`\n"
            f"🔑 API Hash: `{api_hash}`\n"
            f"📊 Plan: 🟢 Basique\n"
            f"🔄 Statut: ✅ Actif\n"
            f"⏳ Heure de bonus: 3h\n"
            f"👥 Référé par: {referrer_id if referrer_id else 'Aucun'}\n\n"
            f"Vous pouvez copier l'ID ci-dessus pour le partager.",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True)
        )

    # ─── AFFILIATION ───
    elif text == "💰 Affiliation":
        context.user_data['in_affiliation'] = True
        await update.message.reply_text(
            "💰 *Menu Affiliation*\n\nChoisissez une option :",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([
                ["👤 Voir mes informations", "🔄 Renouveler un abonnement (affiliation)"],
                ["📞 Contacter le service client affil"],
                ["⬅️ Retour au menu principal"]
            ], resize_keyboard=True)
        )

    elif text == "📞 Contacter le service client affil":
        await update.message.reply_text(
            "📞 Pour contacter le service client, vous pouvez envoyer un message à @Kenny5626 ou @taskersupport_bot.\n\n"
            "⏰ Les horaires de disponibilité sont :\n🕖 Matin : 7h00 à 11h00\n🕑 Après-midi : 14h00 à 19h00\n",
            reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True)
        )

    elif context.user_data.get('waiting_for_affil_id'):
        await register_affil_user(update, context, text)
        context.user_data['waiting_for_affil_id'] = False

    elif text == "👤 Voir mes informations":
        user_data = load_user_data()
        if str(user_id) not in user_data:
            context.user_data['affil_pending_action'] = text
            context.user_data['in_affiliation'] = True
            await update.message.reply_text(
                "⚠️ ATTENTION : Veuillez entrer votre ID unique. Cette action est irréversible. Vérifiez bien votre ID avant de soumettre.",
                reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True)
            )
            context.user_data['waiting_for_affil_id'] = True
        else:
            await show_affil_user_info(update, user_id)

    elif text == "🔄 Renouveler un abonnement (affiliation)":
        user_data = load_user_data()
        if str(user_id) not in user_data:
            context.user_data['affil_pending_action'] = text
            context.user_data['in_affiliation'] = True
            await update.message.reply_text(
                "⚠️ ATTENTION : Veuillez entrer votre ID unique. Cette action est irréversible. Vérifiez bien votre ID avant de soumettre.",
                reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True)
            )
            context.user_data['waiting_for_affil_id'] = True
        else:
            await show_affil_renewal_menu(update, user_id, context)

    elif text in ["📅 Semaine 7j (5 000 AR) affil", "📆 Mois 31j (20 000 AR) affil"] and context.user_data.get('in_affiliation'):
        plan = "Semaine" if "Semaine" in text else "Mois"
        user_choices[user_id] = {"plan": plan}
        await process_affil_subscription(update, user_id, plan, context)

    elif context.user_data.get('waiting_for_another_id'):
        await handle_another_affil_id(update, context, text)
        context.user_data['waiting_for_another_id'] = False

    elif text in ["📱 Mvola", "📱 AirtelMoney"]:
        if user_id in user_choices and "amount_missing" in user_choices.get(user_id, {}):
            await handle_affil_payment(update, context, text.replace("📱 ", ""))
        else:
            await handle_payment(update, context, text.replace("📱 ", ""))

    elif text == "Binance Pay" and user_id in user_choices and "amount_missing" in user_choices.get(user_id, {}):
        await handle_binance_payment(update, context)
        return

    elif text == "🔢 Fournir l'ID de transaction":
        await request_affil_transaction_id(update, context)

    elif text == "✅ Activer mon ID":
        await confirm_affil_payment(update, context)

    elif text == "✅ Activer un autre ID":
        await update.message.reply_text(
            "🔑 Veuillez entrer l'ID unique de la personne à activer :",
            reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True)
        )
        context.user_data['waiting_for_another_id'] = True

    elif text == "✅ Confirmer le paiement":
        if user_id in user_choices and "another_id" in user_choices[user_id]:
            await confirm_another_affil_payment(update, context)
        else:
            await confirm_affil_payment(update, context)

    # ─── PAUSE / REPRISE ───
    elif text == "⏸️ Activer/Pause mon ID":
        context.user_data.pop('in_affiliation', None)
        await update.message.reply_text(
            "🆔 Veuillez entrer votre ID unique :",
            reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True)
        )
        user_choices[user_id] = {"action": "pause_id_request"}

    elif user_id in user_choices and user_choices[user_id].get("action") == "pause_id_request":
        requested_id = text.strip()
        status_data = load_status()
        user_found = next((u for u in status_data["scripts"] if u["id"] == requested_id), None)

        if not user_found:
            await update.message.reply_text(
                "❌ ID introuvable. Veuillez vérifier votre ID.",
                reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True)
            )
            del user_choices[user_id]
            return

        days, hours, minutes = calculate_actual_remaining_time(user_found)
        pause_count = user_found.get('pause_count', 0)
        max_pauses = user_found.get('max_pauses', 3)
        pauses_restantes = max_pauses - pause_count
        is_paused = user_found.get('countdown_paused', False)

        info_message = (
            f"━━━━━━━━━━━━━━━━━━━━━━\n📋 *INFORMATIONS DE VOTRE ID*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🆔 *ID* : `{user_found['id']}`\n"
            f"📱 *Android ID* : `{user_found.get('android_id', 'Non défini')}`\n"
            f"📦 *Plan* : {user_found.get('plan', 'Null')}\n"
            f"✅ *Statut* : {'🟢 Actif' if user_found['status'] == 'active' else '🔴 Inactif'}\n\n"
        )
        if is_paused:
            p_days, p_hours, p_minutes = calculate_paused_time(user_found)
            info_message += f"⏸️ *Compte à rebours* : EN PAUSE\n⏳ *Temps conservé en pause* : {p_days}j {p_hours}h {p_minutes}m\n\n"
        else:
            info_message += f"⏰ *Temps restant* : {days}j {hours}h {minutes}m\n\n"

        barre_pause = "🟥" * pause_count + "🟩" * pauses_restantes
        info_message += (
            f"━━━━━━━━━━━━━━━━━━━━━━\n📊 *GESTION DES PAUSES*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔢 *Pauses utilisées* : {pause_count}/{max_pauses}\n🔋 *Pauses restantes* : {pauses_restantes}/{max_pauses}\n📶 {barre_pause}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n📌 *RÈGLES DE PAUSE*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"• Maximum *{max_pauses} pauses* par renouvellement\n• La mise en pause nécessite au moins *3h restantes*\n"
            f"• Le compteur se remet à 0 à chaque renouvellement\n• Après {max_pauses} pauses : attendre le prochain renouvellement\n\n"
        )
        if pause_count >= max_pauses and not is_paused:
            info_message += f"🚫 *LIMITE ATTEINTE*\nVous avez utilisé toutes vos pauses disponibles.\nRenouvelez votre abonnement pour en bénéficier à nouveau.\n"
        elif pauses_restantes == 1 and not is_paused:
            info_message += f"⚠️ *ATTENTION* : Il ne vous reste plus qu'*1 pause*.\nUtilisez-la avec précaution !\n"
        elif not is_paused:
            info_message += f"✅ Vous avez *{pauses_restantes} pauses* disponibles.\n"

        await update.message.reply_text(info_message, parse_mode="Markdown")

        total_hours = days * 24 + hours
        if is_paused:
            await update.message.reply_text(
                "▶️ Votre compte est actuellement en pause.\nCliquez sur *Reprendre* pour relancer votre abonnement.",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup([["▶️ Reprendre mon ID"], ["⬅️ Retour au menu principal"]], resize_keyboard=True)
            )
        elif total_hours <= 3 or pause_count >= max_pauses:
            reason = (
                f"⛔ *Mise en pause impossible*\n\nIl ne vous reste que *{hours}h {minutes}m*.\nLa pause nécessite au moins *3 heures restantes*.\nVotre abonnement se terminera bientôt."
                if total_hours <= 3 else
                f"🚫 *Limite de pauses atteinte*\n\nVous avez déjà effectué *{max_pauses} pauses*.\nPour éviter les abus, la pause est désactivée jusqu'au\nprochain renouvellement de votre abonnement."
            )
            await update.message.reply_text(reason, parse_mode="Markdown")
            await update.message.reply_text("Retournez au menu principal :", reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True))
        else:
            await update.message.reply_text(
                "⏸️ Vous pouvez mettre votre ID en pause.\nCliquez sur le bouton ci-dessous pour continuer.",
                reply_markup=ReplyKeyboardMarkup([["⏸️ Mettre en pause mon ID"], ["⬅️ Retour au menu principal"]], resize_keyboard=True)
            )
        user_choices[user_id] = {"action": "pause_id_action", "user_id": requested_id}

    elif text == "⏸️ Mettre en pause mon ID":
        if user_id in user_choices and user_choices[user_id].get("action") == "pause_id_action":
            requested_id = user_choices[user_id]["user_id"]
            status_data = load_status()
            for user in status_data["scripts"]:
                if user["id"] == requested_id:
                    remaining_time = datetime.fromisoformat(user['countdown_start_time']) - datetime.now()
                    user['paused_remaining_time'] = int(remaining_time.total_seconds()) if remaining_time.total_seconds() > 0 else 0
                    user['countdown_start_time'] = datetime.now().isoformat()
                    user['countdown_paused'] = True
                    user['pause_count'] = user.get('pause_count', 0) + 1
                    new_pause_count = user['pause_count']
                    max_pauses = user.get('max_pauses', 3)
                    pauses_restantes = max_pauses - new_pause_count
                    save_status(status_data)
                    if new_pause_count == max_pauses:
                        msg = (f"⏸️ *Mise en pause effectuée avec succès !*\n\n🆔 *ID* : `{requested_id}`\n\n"
                               f"━━━━━━━━━━━━━━━━━━━━━━\n⚠️ *ATTENTION — DERNIÈRE PAUSE UTILISÉE*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
                               f"Vous venez d'utiliser votre *{max_pauses}ème et dernière pause* du renouvellement.\n\n"
                               f"🚫 Vous ne pourrez plus effectuer de pause jusqu'au prochain renouvellement.\n\n"
                               f"📊 *Pauses utilisées* : {max_pauses}/{max_pauses}\n🔋 *Pauses restantes* : 0/{max_pauses}\n📶 {'\ud83d\udfe5' * max_pauses}\n")
                    else:
                        barre = "🟥" * new_pause_count + "🟩" * pauses_restantes
                        msg = (f"✅ *Mise en pause effectuée avec succès !*\n\n🆔 *ID* : `{requested_id}`\n\n"
                               f"📊 *Pauses utilisées* : {new_pause_count}/{max_pauses}\n🔋 *Pauses restantes* : {pauses_restantes}/{max_pauses}\n📶 {barre}\n\n"
                               f"💡 Revenez quand vous voulez pour reprendre.\n")
                    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True))
                    break
            del user_choices[user_id]

    elif text == "▶️ Reprendre mon ID":
        if user_id in user_choices and user_choices[user_id].get("action") == "pause_id_action":
            requested_id = user_choices[user_id]["user_id"]
            status_data = load_status()
            for user in status_data["scripts"]:
                if user["id"] == requested_id:
                    if 'paused_remaining_time' in user:
                        user['countdown_start_time'] = (datetime.now() + timedelta(seconds=user['paused_remaining_time'])).isoformat()
                        del user['paused_remaining_time']
                    user['countdown_paused'] = False
                    if user['status'] == 'inactive':
                        user['status'] = 'active'
                    save_status(status_data)
                    await update.message.reply_text(
                        f"▶️ *Votre ID a été repris avec succès !*\n\n🆔 *ID* : `{requested_id}`\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n⏳ *IMPORTANT — À LIRE ATTENTIVEMENT*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"⏱️ Veuillez attendre *5 minutes* avant de lancer la tâche sur Termux.\n\n"
                        f"✅ Ce délai permet au système de se synchroniser correctement avec votre abonnement.\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n❓ *Si ça ne fonctionne toujours pas après 5 min ?*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"🚫 N'envoyez *pas* de message au support avant d'avoir attendu les *5 minutes complètes*.\n\n"
                        f"📞 Support : @Kenny5626 ou @taskersupport\\_bot",
                        parse_mode="Markdown",
                        reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True)
                    )
                    break
            del user_choices[user_id]

    # ─── TUTOS ───
    elif text == "📖 Voir des Tuto":
        await update.message.reply_text(
            "📖 *Tutoriels TikSMM*\n\n"
            "Tous les tutoriels sont disponibles dans notre groupe Telegram :\n\n"
            "👉 https://t.me/+W26JRhUCIH05NGQ0\n\n"
            "📌 Une fois dans le groupe, allez dans la section : *TUTOTIKTOKSMM*",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True)
        )

    elif text == "📢📣ANNONCE... 📢📣":
        await update.message.reply_text(
            "\n😊30 Septembre 2025,Miarahaba anareo tompoko... Eto aho dia mialatsiny indrindra ny t@MAJ teo ny @resaka Connexion...\n",
            reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True, one_time_keyboard=False)
        )

    elif text == "📞 Contacter le service client":
        context.user_data.pop('in_affiliation', None)
        await update.message.reply_text(
            "📞 Pour contacter le service client, vous pouvez envoyer un message à @Kenny5626 ou @taskersupport_bot.\n\n"
            "⏰ Les horaires de disponibilité sont :\n🕖 Matin : 7h00 à 11h00\n🕑 Après-midi : 14h00 à 19h00\n",
            reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True, one_time_keyboard=False)
        )

    # ─── RENOUVELLEMENT ABONNEMENT (paiement direct) ───
    elif text == "🔄 Renouveler un abonnement":
        await update.message.reply_text(
            "💡 Choisissez un plan d'abonnement :\n\n"
            "📅 *Abonnement par semaine* : 5 000 AR / 7 jours (3 pauses max)\n"
            "📆 *Abonnement par mois* : 20 000 AR / 31 jours (15 pauses max)",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([["📅 Semaine 7j (5 000 AR)", "📆 Mois 31j (20 000 AR)"], ["⬅️ Annuler"]], resize_keyboard=True)
        )
        user_choices[user_id] = {"plan": None, "payment_method": None}

    elif text == "📅 Semaine 7j (5 000 AR)":
        user_choices[user_id]["plan"] = "Semaine"
        await show_payment_options(update)

    elif text == "📆 Mois 31j (20 000 AR)":
        user_choices[user_id]["plan"] = "Mois"
        await show_payment_options(update)

    elif user_id in user_choices and isinstance(user_choices[user_id], dict) and "plan" in user_choices[user_id] and "transaction_id" not in user_choices[user_id] and user_choices[user_id].get("plan") and user_choices[user_id].get("payment_method") and not user_choices[user_id].get("action") and "amount_missing" not in user_choices[user_id]:
        user_choices[user_id]["transaction_id"] = text
        tg_user = update.effective_user
        plan = user_choices[user_id].get("plan", "N/A")
        method = user_choices[user_id].get("payment_method", "N/A")
        amount = 5000 if plan == "Semaine" else 20000
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'─'*60}\n  📥 ID TRANSACTION REÇU — {now}\n  👤 {tg_user.full_name} | @{tg_user.username or 'N/A'} | {tg_user.id}\n  💳 {method} | Trans: {text} | {plan} ({amount} AR)\n{'─'*60}\n")
        await request_user_id(update)

    elif user_id in user_choices and isinstance(user_choices[user_id], dict) and "transaction_id" in user_choices[user_id] and "user_id" not in user_choices[user_id] and not user_choices[user_id].get("action") and "amount_missing" not in user_choices[user_id]:
        import asyncio
        user_choices[user_id]["user_id"] = text

        wait_msg = await update.message.reply_text("🔍 Vérification de la transaction en cours.")
        frames = ["🔍 Vérification de la transaction en cours.", "🔍 Vérification de la transaction en cours..", "🔍 Vérification de la transaction en cours...", "🔄 Vérification de la transaction en cours..."]
        for frame in frames:
            await asyncio.sleep(0.6)
            try:
                await wait_msg.edit_text(frame)
            except Exception:
                pass
        try:
            await wait_msg.delete()
        except Exception:
            pass

        is_verified = await verify_payment(update)
        if is_verified:
            await update_subscription(update, context)
        else:
            tg_user = update.effective_user
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n{'─'*60}\n  ❌ PAIEMENT NON VÉRIFIÉ — {now}\n  👤 {tg_user.full_name} | ID: {text}\n{'─'*60}\n")
            await update.message.reply_text(
                "❌ L'activation a échoué. Veuillez vérifier vos informations de paiement.\n\n⬅️ Retournez au menu principal ou contactez le service client.",
                reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True)
            )


# ─── AFFILIATION : enregistrement + infos + renouvellement via solde ───

async def register_affil_user(update: Update, context: ContextTypes.DEFAULT_TYPE, unique_id: str):
    user_id = update.effective_user.id
    user_data = load_user_data()
    status_data = load_status()

    if unique_id in [u["id"] for u in status_data["scripts"]]:
        if unique_id in user_data.values():
            await update.message.reply_text("❌ Cet ID est déjà associé à un autre utilisateur. Veuillez entrer votre propre ID.")
        else:
            user_data[str(user_id)] = unique_id
            save_user_data(user_data)
            await update.message.reply_text("✅ Votre ID a été enregistré avec succès !")
            pending = context.user_data.pop('affil_pending_action', None)
            if pending == "👤 Voir mes informations":
                await show_affil_user_info(update, user_id)
            elif pending == "🔄 Renouveler un abonnement (affiliation)":
                await show_affil_renewal_menu(update, user_id, context)
    else:
        await update.message.reply_text("❌ ID introuvable. Veuillez vérifier et réessayer.")

async def show_affil_user_info(update: Update, user_id: int):
    user_data = load_user_data()
    unique_id = user_data.get(str(user_id))
    status_data = load_status()
    user_info = next((u for u in status_data["scripts"] if u["id"] == unique_id), None)

    if user_info:
        affiliate_balance = user_info.get("affiliation_balance", 0)
        countdown_start_time = user_info.get("countdown_start_time")
        if countdown_start_time:
            end_time = datetime.fromisoformat(countdown_start_time)
            remaining_time = end_time - datetime.now()
            days, hours, minutes = remaining_time.days, (remaining_time.seconds // 3600) % 24, (remaining_time.seconds // 60) % 60
            countdown = f"{days} jours, {hours} heures, {minutes} minutes"
        else:
            countdown = "Non défini"
        await update.message.reply_text(
            f"📌 **Informations de votre compte**\n\n"
            f"🆔 **ID** : `{unique_id}`\n"
            f"💰 **Solde d'affiliation** : `{affiliate_balance} AR`\n"
            f"⏳ **Temps restant** : `{countdown}`\n\n"
            "Merci d'utiliser Affiliation Bot !",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True)
        )
    else:
        await update.message.reply_text("❌ ID introuvable.", reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True))

async def show_affil_renewal_menu(update: Update, user_id: int, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💡 Choisissez un plan d'abonnement :\n\n"
        "📅 *Abonnement par semaine* : 5 000 AR / 7 jours (3 pauses max)\n"
        "📆 *Abonnement par mois* : 20 000 AR / 31 jours (15 pauses max)",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([
            ["📅 Semaine 7j (5 000 AR) affil", "📆 Mois 31j (20 000 AR) affil"],
            ["⬅️ Retour au menu principal"]
        ], resize_keyboard=True)
    )

async def process_affil_subscription(update: Update, user_id: int, plan: str, context: ContextTypes.DEFAULT_TYPE):
    user_data = load_user_data()
    unique_id = user_data.get(str(user_id))
    status_data = load_status()
    user_info = next((u for u in status_data["scripts"] if u["id"] == unique_id), None)

    if user_info:
        price = 5000 if plan == "Semaine" else 20000
        balance = user_info.get("affiliation_balance", 0)
        if balance >= price:
            user_choices[user_id] = {"plan": plan, "price": price, "user_id": unique_id}
            await update.message.reply_text(
                f"🆔 **ID** : `{unique_id}`\n💰 **Solde actuel** : `{balance} AR`\n📜 **Plan sélectionné** : {plan}\n"
                f"💸 **Montant à déduire** : `{price} AR`\n💰 **Solde après activation** : `{balance - price} AR`\n\nChoisissez une option ci-dessous :",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup([["✅ Activer mon ID", "✅ Activer un autre ID"], ["❌ Annuler"]], resize_keyboard=True)
            )
        else:
            amount_missing = price - balance
            user_choices[user_id] = {"plan": plan, "price": price, "amount_missing": amount_missing, "user_id": unique_id}
            await update.message.reply_text(
                f"❌ Solde insuffisant !\n🆔 **ID** : `{unique_id}`\n📜 **Plan sélectionné** : {plan}\n"
                f"💸 **Montant total** : `{price} AR`\n💰 **Solde actuel** : `{balance} AR`\n💵 **Montant manquant** : `{amount_missing} AR`\n\n"
                "💳 Choisissez une méthode de paiement pour compléter le montant manquant :",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup([["📱 Mvola", "📱 AirtelMoney"], ["Binance Pay"], ["⬅️ Retour au menu principal"]], resize_keyboard=True)
            )
    else:
        await update.message.reply_text("❌ ID introuvable.", reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True))

async def handle_affil_payment(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str):
    user_id = update.effective_user.id
    amount_missing = user_choices[user_id]["amount_missing"]
    context.user_data['affil_payment_method'] = method
    text_info = (
        f"📱 **{method}**\n\nNuméro : {'0388605629' if method == 'Mvola' else '0336728640'}\n"
        f"Nom du destinataire : Mampifaly Felicien Kenny Nestin\nMontant : {amount_missing} AR\n\n"
        "📌 Après avoir effectué le paiement, cliquez sur **🔢 Fournir l'ID de transaction** ou **⬅️ Retour**."
    )
    await update.message.reply_text(text_info, reply_markup=ReplyKeyboardMarkup([["🔢 Fournir l'ID de transaction", "⬅️ Retour"]], resize_keyboard=True))

async def request_affil_transaction_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔢 Entrez l'ID de transaction (Trans ID / Ref ID / Reference No) :\n\n⛔ Entrez UNIQUEMENT l'ID, rien d'autre.",
        reply_markup=ReplyKeyboardMarkup([["⬅️ Retour"]], resize_keyboard=True)
    )
    context.user_data['waiting_for_affil_transaction_id'] = True

async def verify_affil_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import asyncio
    user_id = update.effective_user.id
    transaction_id = update.message.text
    payment_method = context.user_data.get('affil_payment_method')
    amount_missing = user_choices[user_id]["amount_missing"]
    context.user_data.pop('waiting_for_affil_transaction_id', None)

    wait_msg = await update.message.reply_text("🔍 Vérification de la transaction en cours.")
    frames = ["🔍 Vérification de la transaction en cours.", "🔍 Vérification de la transaction en cours..", "🔍 Vérification de la transaction en cours...", "🔄 Vérification de la transaction en cours..."]
    import asyncio
    for frame in frames:
        await asyncio.sleep(0.6)
        try:
            await wait_msg.edit_text(frame)
        except Exception:
            pass
    try:
        await wait_msg.delete()
    except Exception:
        pass

    if await verify_transaction(transaction_id, payment_method, amount_missing):
        await update.message.reply_text("✅ Paiement vérifié avec succès !")
        await update_affiliation_balance(update, context, amount_missing, payment_method, transaction_id)
    else:
        await update.message.reply_text("❌ Transaction non trouvée ou montant incorrect. Veuillez réessayer ou contacter le service client.")
        await show_main_menu(update)

async def verify_transaction(transaction_id: str, payment_method: str, amount_required: int) -> bool:
    file_path = "/data/data/com.termux/files/home/sms_filtered.txt"
    used_file_path = "/data/data/com.termux/files/home/used_transactions1.txt"
    if os.path.exists(used_file_path):
        with open(used_file_path, 'r') as f:
            if any(transaction_id in line for line in f.readlines()):
                return False
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if payment_method == "AirtelMoney" and f"Trans ID: {transaction_id}" in line:
                try:
                    if int(line.split("Montant:")[1].split(" Ar")[0].strip()) >= amount_required:
                        remove_transaction_from_file(file_path, transaction_id, used_file_path)
                        return True
                except ValueError:
                    continue
            elif payment_method == "Mvola" and f"Ref ID: {transaction_id}" in line:
                try:
                    if int(line.split("Montant:")[1].split(" Ar")[0].strip()) >= amount_required:
                        remove_transaction_from_file(file_path, transaction_id, used_file_path)
                        return True
                except ValueError:
                    continue
    return False

async def update_affiliation_balance(update: Update, context: ContextTypes.DEFAULT_TYPE, amount_missing: int, payment_method: str, transaction_id: str):
    user_id = update.effective_user.id
    unique_id = user_choices[user_id]["user_id"]
    status_data = load_status()
    for user in status_data["scripts"]:
        if user["id"] == unique_id:
            balance_before = user.get("affiliation_balance", 0)
            user["affiliation_balance"] += amount_missing
            balance_after = user["affiliation_balance"]
            save_status(status_data)
            await send_balance_addition_ticket(context, unique_id, balance_before, payment_method, transaction_id, amount_missing, balance_after)
            await update.message.reply_text(f"✅ {amount_missing} AR ont été ajoutés à votre solde d'affiliation.")
            await process_affil_subscription(update, user_id, user_choices[user_id]["plan"], context)
            break

async def confirm_affil_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import asyncio
    user_id = update.effective_user.id
    unique_id = user_choices[user_id]["user_id"]
    plan = user_choices[user_id]["plan"]
    price = user_choices[user_id]["price"]

    wait_msg = await update.message.reply_text("⚙️ Activation de l'abonnement en cours.")
    frames = ["⚙️ Activation de l'abonnement en cours.", "⚙️ Activation de l'abonnement en cours..", "⚙️ Activation de l'abonnement en cours...", "🔄 Activation de l'abonnement en cours..."]
    for frame in frames:
        await asyncio.sleep(0.6)
        try:
            await wait_msg.edit_text(frame)
        except Exception:
            pass
    try:
        await wait_msg.delete()
    except Exception:
        pass

    status_data = load_status()

    for user in status_data["scripts"]:
        if user["id"] == unique_id:
            balance = user.get("affiliation_balance", 0)
            if balance >= price:
                remaining_balance = balance - price
                current_time = datetime.now()
                existing_str = user.get("countdown_start_time", "")
                days_to_add = 7 if plan == "Semaine" else 31
                max_pauses = 3 if plan == "Semaine" else 15
                try:
                    existing = datetime.fromisoformat(existing_str.replace('Z', '+00:00')).replace(tzinfo=None) if existing_str else None
                    if existing and existing > current_time:
                        new_time = existing + timedelta(days=days_to_add)
                        delta = new_time - current_time
                        time_display = f"{delta.days} jours et {delta.seconds // 3600}h"
                    else:
                        new_time = current_time + timedelta(days=days_to_add)
                        time_display = f"{days_to_add} jours"
                except:
                    new_time = current_time + timedelta(days=days_to_add)
                    time_display = f"{days_to_add} jours"
                user['pause_count'] = 0
                user['max_pauses'] = max_pauses
                user["countdown_start_time"] = new_time.isoformat()
                user["affiliation_balance"] = remaining_balance
                user["plan"] = plan
                user["status"] = "active"
                referred_by = user.get("referred_by")
                if referred_by:
                    for ref_user in status_data["scripts"]:
                        if ref_user["id"] == referred_by:
                            ref_user["affiliation_balance"] = ref_user.get("affiliation_balance", 0) + 500
                            break
                save_status(status_data)
                expiration_date = new_time.strftime("%d/%m/%Y %H:%M")
                await update.message.reply_text(
                    f"🎉 **Activation réussie !**\n\n🆔 **ID** : `{unique_id}`\n📜 **Plan activé** : {plan}\n"
                    f"📅 **Date d'expiration** : {expiration_date}\n💰 **Solde restant** : `{remaining_balance} AR`\n"
                    f"⏳ **Temps total** : {time_display}\n✅ **Statut** : ACTIF\n\nMerci d'utiliser Affiliation Bot !",
                    parse_mode="Markdown",
                    reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True)
                )
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sep = '=' * 55
                print(f"\n{sep}\n  🎉 ACTIVATION AFFILIATION — {now_str}\n{sep}")
                print(f"  🆔 ID activé     : {unique_id}")
                print(f"  📦 Plan          : {plan}")
                print(f"  💸 Prix          : {price} AR")
                print(f"  💰 Solde avant   : {balance} AR")
                print(f"  💰 Solde après   : {remaining_balance} AR")
                print(f"  📅 Expiration    : {expiration_date}")
                print(f"  ⏳ Temps total   : {time_display}\n{sep}\n")
                await send_affiliation_confirmation_ticket(context, unique_id, unique_id, plan, price, balance, remaining_balance, expiration_date)
            else:
                await update.message.reply_text("❌ Solde insuffisant pour confirmer l'activation.")
            break

async def handle_another_affil_id(update: Update, context: ContextTypes.DEFAULT_TYPE, another_id: str):
    user_id = update.effective_user.id
    status_data = load_status()
    user_info = next((u for u in status_data["scripts"] if u["id"] == another_id), None)
    if user_info:
        plan = user_choices[user_id]["plan"]
        price = user_choices[user_id]["price"]
        user_choices[user_id]["another_id"] = another_id
        await update.message.reply_text(
            f"🆔 **ID à activer** : `{another_id}`\n📜 **Plan sélectionné** : {plan}\n💸 **Montant à déduire** : `{price} AR`\n\n✅ Confirmez le paiement pour activer l'abonnement.",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([["✅ Confirmer le paiement"], ["❌ Annuler"]], resize_keyboard=True)
        )
    else:
        await update.message.reply_text("❌ ID introuvable.", reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True))

async def confirm_another_affil_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import asyncio
    user_id = update.effective_user.id
    unique_id = user_choices[user_id]["another_id"]
    payer_id = user_choices[user_id]["user_id"]
    plan = user_choices[user_id]["plan"]
    price = user_choices[user_id]["price"]

    wait_msg = await update.message.reply_text("⚙️ Activation de l'abonnement en cours.")
    frames = ["⚙️ Activation de l'abonnement en cours.", "⚙️ Activation de l'abonnement en cours..", "⚙️ Activation de l'abonnement en cours...", "🔄 Activation de l'abonnement en cours..."]
    for frame in frames:
        await asyncio.sleep(0.6)
        try:
            await wait_msg.edit_text(frame)
        except Exception:
            pass
    try:
        await wait_msg.delete()
    except Exception:
        pass

    status_data = load_status()

    for user in status_data["scripts"]:
        if user["id"] == unique_id:
            payer_info = next((u for u in status_data["scripts"] if u["id"] == payer_id), None)
            if payer_info and payer_info.get("affiliation_balance", 0) >= price:
                remaining_balance = payer_info["affiliation_balance"] - price
                current_time = datetime.now()
                existing_str = user.get("countdown_start_time", "")
                days_to_add = 7 if plan == "Semaine" else 31
                max_pauses = 3 if plan == "Semaine" else 15
                try:
                    existing = datetime.fromisoformat(existing_str.replace('Z', '+00:00')).replace(tzinfo=None) if existing_str else None
                    if existing and existing > current_time:
                        new_time = existing + timedelta(days=days_to_add)
                        delta = new_time - current_time
                        time_display = f"{delta.days} jours et {delta.seconds // 3600}h"
                    else:
                        new_time = current_time + timedelta(days=days_to_add)
                        time_display = f"{days_to_add} jours"
                except:
                    new_time = current_time + timedelta(days=days_to_add)
                    time_display = f"{days_to_add} jours"
                user['pause_count'] = 0
                user['max_pauses'] = max_pauses
                user["countdown_start_time"] = new_time.isoformat()
                user["plan"] = plan
                user["status"] = "active"
                payer_info["affiliation_balance"] = remaining_balance
                referred_by = user.get("referred_by")
                if referred_by:
                    for ref_user in status_data["scripts"]:
                        if ref_user["id"] == referred_by:
                            ref_user["affiliation_balance"] = ref_user.get("affiliation_balance", 0) + 500
                            break
                save_status(status_data)
                expiration_date = new_time.strftime("%d/%m/%Y %H:%M")
                await update.message.reply_text(
                    f"🎉 **Activation réussie !**\n\n🆔 **ID activé** : `{unique_id}`\n📜 **Plan activé** : {plan}\n"
                    f"📅 **Date d'expiration** : {expiration_date}\n💰 **Solde restant** : `{remaining_balance} AR`\n"
                    f"⏳ **Temps total** : {time_display}\n✅ **Statut** : ACTIF\n\nMerci d'utiliser Affiliation Bot !",
                    parse_mode="Markdown",
                    reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True)
                )
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sep = '=' * 55
                print(f"\n{sep}\n  🎉 ACTIVATION AFFILIATION (AUTRE ID) — {now_str}\n{sep}")
                print(f"  🆔 ID payeur     : {payer_id}")
                print(f"  🆔 ID activé     : {unique_id}")
                print(f"  📦 Plan          : {plan}")
                print(f"  💸 Prix          : {price} AR")
                print(f"  💰 Solde avant   : {payer_info['affiliation_balance'] + price} AR")
                print(f"  💰 Solde après   : {remaining_balance} AR")
                print(f"  📅 Expiration    : {expiration_date}")
                print(f"  ⏳ Temps total   : {time_display}\n{sep}\n")
                await send_affiliation_confirmation_ticket(context, payer_id, unique_id, plan, price, payer_info["affiliation_balance"] + price, remaining_balance, expiration_date)
            else:
                await update.message.reply_text("❌ Solde insuffisant pour confirmer l'activation.")
            break

# ─── PAIEMENT DIRECT (renouvellement sans solde affiliation) ───

async def show_payment_options(update: Update):
    await update.message.reply_text(
        "💳 Choisissez une méthode de paiement :",
        reply_markup=ReplyKeyboardMarkup([["Mvola", "AirtelMoney"], ["Binance Pay"], ["⬅️ Annuler"]], resize_keyboard=True)
    )


async def handle_binance_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    plan = user_choices[user_id]["plan"]
    amount_ar = user_choices[user_id].get("amount_missing") or (5000 if plan == "Semaine" else 20000)
    min_usdt = ar_to_usdt(amount_ar)
    user_choices[user_id]["payment_method"] = "Binance Pay"
    user_choices[user_id]["binance_min_usdt"] = str(min_usdt)
    await update.message.reply_text(
        f"💱 *Paiement via Binance Pay*\n\n"
        f"📅 Plan : *{plan}*\n"
        f"💰 Montant AR : *{amount_ar} AR*\n"
        f"💵 Montant USDT à envoyer : *{min_usdt} USDT*\n"
        f"_(Taux : 1 USD = 4 050 AR)_\n\n"
        f"💸 Envoyez via *Binance Pay* vers :\n"
        f"• 🆔 *ID Binance Pay :* `{BINANCE_PAY_ID}`\n"
        f"• 👤 *Nom receveur :* `{BINANCE_PAY_NAME}`\n\n"
        f"✅ Vérifiez bien le nom avant d'envoyer !\n\n"
        f"Une fois payé, cliquez sur *✅ J'ai payé Binance — Confirmer*",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [["✅ J'ai payé Binance — Confirmer"], ["❌ Annuler"], ["⬅️ Retour"]],
            resize_keyboard=True
        )
    )


async def process_binance_txid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import asyncio
    user_id = update.effective_user.id
    txid = update.message.text.strip()
    context.user_data.pop('waiting_binance_txid', None)

    used = load_used_txids()
    if txid in used:
        await update.message.reply_text(
            f"❌ *Transaction déjà utilisée.*\n\n🔗 TXID : `{txid}`\nContactez le support : @Kenny5626",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True)
        )
        return

    wait_msg = await update.message.reply_text("🔍 Vérification Binance en cours.")
    frames = ["🔍 Vérification Binance en cours.", "🔍 Vérification Binance en cours..", "🔍 Vérification Binance en cours...", "🔄 Vérification Binance en cours..."]
    for frame in frames:
        await asyncio.sleep(0.7)
        try:
            await wait_msg.edit_text(frame)
        except Exception:
            pass
    try:
        await wait_msg.delete()
    except Exception:
        pass

    min_usdt = Decimal(user_choices[user_id].get("binance_min_usdt", "1.00"))
    check = verify_binance_transaction(txid, min_usdt)

    if not check.get("valid"):
        await update.message.reply_text(
            f"❌ *Transaction invalide*\n\n🔗 TXID : `{txid}`\n📝 Raison : {check.get('error', 'Inconnue')}\n\nRéessayez ou contactez : @Kenny5626",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True)
        )
        return

    save_used_txid(txid)

    # Vérifier si c'est affiliation (amount_missing) ou paiement direct
    if "amount_missing" in user_choices[user_id]:
        amount_missing = user_choices[user_id]["amount_missing"]
        await update_affiliation_balance(update, context, amount_missing, "Binance Pay", txid)
    else:
        user_choices[user_id]["transaction_id"] = txid
        context.user_data['waiting_unique_id_after_binance'] = True
        await update.message.reply_text(
            "🔑 Veuillez entrer votre ID unique pour activer l'abonnement :",
            reply_markup=ReplyKeyboardMarkup([["⬅️ Retour"]], resize_keyboard=True)
        )

async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str):
    user_id = update.effective_user.id
    user_choices[user_id]["payment_method"] = method
    plan = user_choices[user_id]["plan"]
    amount = 5000 if plan == "Semaine" else 20000
    num = "0388605629" if method == "Mvola" else "0336728640"
    await update.message.reply_text(
        f"📱 **{method}**\n\nNuméro : {num}\nNom du destinataire : Mampifaly Felicien Kenny Nestin\nMontant : {amount} AR\n\n"
        "📌 Après avoir effectué le paiement, cliquez sur **Confirmer le paiement** ou **Annuler**.",
        reply_markup=ReplyKeyboardMarkup([["Confirmer le paiement", "⬅️ Annuler"]], resize_keyboard=True)
    )

async def request_transaction_id(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str):
    await update.message.reply_text(
        f"🔢 Entrez l'ID de transaction {method} (Trans ID / Ref ID / Reference No) :\n\n⛔ Entrez UNIQUEMENT l'ID, rien d'autre.",
        reply_markup=ReplyKeyboardMarkup([["⬅️ Retour"]], resize_keyboard=True)
    )

async def request_user_id(update: Update):
    await update.message.reply_text(
        "🔑 Veuillez entrer votre ID unique pour activer l'abonnement :",
        reply_markup=ReplyKeyboardMarkup([["⬅️ Retour"]], resize_keyboard=True)
    )

async def verify_payment(update: Update):
    user_id = update.effective_user.id
    transaction_id = user_choices[user_id].get("transaction_id")
    payment_method = user_choices[user_id].get("payment_method")
    plan = user_choices[user_id].get("plan")
    amount_required = 5000 if plan == "Semaine" else 20000
    return await verify_transaction(transaction_id, payment_method, amount_required)

def remove_transaction_from_file(file_path, transaction_id, used_file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    with open(file_path, 'w') as f:
        for line in lines:
            if transaction_id not in line:
                f.write(line)
    with open(used_file_path, 'a') as f:
        f.write(f"{transaction_id}\n")

async def update_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import asyncio
    user_id = update.effective_user.id
    tg_user = update.effective_user
    unique_id = user_choices[user_id]["user_id"]
    plan = user_choices[user_id]["plan"]
    payment_method = user_choices[user_id]["payment_method"]
    transaction_id = user_choices[user_id]["transaction_id"]
    amount = 5000 if plan == "Semaine" else 20000
    user_telegram_info = {"id": tg_user.id, "full_name": tg_user.full_name, "username": tg_user.username or "N/A"}

    wait_msg = await update.message.reply_text("⚙️ Activation de l'abonnement en cours.")
    frames = ["⚙️ Activation de l'abonnement en cours.", "⚙️ Activation de l'abonnement en cours..", "⚙️ Activation de l'abonnement en cours...", "🔄 Activation de l'abonnement en cours..."]
    for frame in frames:
        await asyncio.sleep(0.6)
        try:
            await wait_msg.edit_text(frame)
        except Exception:
            pass
    try:
        await wait_msg.delete()
    except Exception:
        pass

    status_data = load_status()
    user_found = False
    referred_by = None

    for user in status_data["scripts"]:
        if user["id"] == unique_id:
            user_found = True
            current_time = datetime.now()
            existing_str = user.get("countdown_start_time", "")
            days_to_add = 7 if plan == "Semaine" else 31
            max_pauses = 3 if plan == "Semaine" else 15
            try:
                existing = datetime.fromisoformat(existing_str.replace('Z', '+00:00')).replace(tzinfo=None) if existing_str else None
                if existing and existing > current_time:
                    new_time = existing + timedelta(days=days_to_add)
                    delta = new_time - current_time
                    time_display = f"{delta.days} jours et {delta.seconds // 3600}h"
                else:
                    new_time = current_time + timedelta(days=days_to_add)
                    time_display = f"{days_to_add} jours"
            except:
                new_time = current_time + timedelta(days=days_to_add)
                time_display = f"{days_to_add} jours"
            user['pause_count'] = 0
            user['max_pauses'] = max_pauses
            user["countdown_start_time"] = new_time.isoformat()
            user["plan"] = plan
            user["status"] = "active"
            referred_by = user.get("referred_by")
            if referred_by:
                for ref_user in status_data["scripts"]:
                    if ref_user["id"] == referred_by:
                        ref_user["affiliation_balance"] = ref_user.get("affiliation_balance", 0) + 500
                        break
            save_status(status_data)
            log_payment_details("ABONNEMENT ACTIVÉ ✅", user_telegram_info, plan, payment_method, transaction_id, unique_id, amount, time_display, referred_by)
            await send_confirmation_ticket(context, unique_id, time_display, payment_method, amount, transaction_id, user_telegram_info, referred_by)
            await update.message.reply_text(
                f"✅ Votre ID `{unique_id}` a été activé avec succès !\n\n📦 Plan : {plan}\n⏳ Temps total : {time_display}\n✅ Statut : ACTIF\n\nMerci pour votre abonnement ! 🙏",
                reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True)
            )
            break

    if not user_found:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'─'*60}\n  ⚠️  ID UNIQUE INTROUVABLE — {now}\n  👤 {tg_user.full_name} | ID saisi: {unique_id}\n{'─'*60}\n")
        await update.message.reply_text(
            "❌ ID utilisateur introuvable. Veuillez vérifier votre ID unique ou contacter le service client.",
            reply_markup=ReplyKeyboardMarkup([["⬅️ Retour au menu principal"]], resize_keyboard=True)
        )

# ─── MAIN ───

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_access_code))
    print("🤖 Bot démarré...")
    app.run_polling()

if __name__ == "__main__":
    main()
