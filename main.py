import os, json
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import gspread

# ========== Bagian Google Sheets ==========
def get_gsheet():
    # Ambil kunci JSON dari environment variable
    sa_info = json.loads(os.environ["GCP_SA_KEY"])
    gc = gspread.service_account_from_dict(sa_info)

    # Buka file sheet sesuai nama di environment variable
    sh = gc.open(os.environ.get("SHEET_NAME", "TRANSAKSI BOT"))
    ws = sh.worksheet(os.environ.get("SHEET_WORKSHEET", "Kedai"))
    return ws

def append_tx(user_id, jenis, jumlah, kategori, catatan, metode):
    ws = get_gsheet()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [ts, str(user_id), jenis, str(jumlah), kategori, catatan, metode]
    ws.append_row(row, value_input_option="USER_ENTERED")

# ========== Bagian Telegram Command ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "Halo! Aku bot keuangan.\n"
        "Pakai perintah ini:\n"
        "/income jumlah kategori | catatan | metode\n"
        "/expense jumlah kategori | catatan | metode\n"
        "Contoh:\n"
        "/income 50000 bakmie | porsi pagi | tunai\n"
        "/expense 12000 bahan | mie telur | qris\n"
    )
    await update.message.reply_text(msg)

async def income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ambil pesan setelah /income
    text = update.message.text.split(maxsplit=1)
    if len(text) < 2:
        return await update.message.reply_text("Format salah. Contoh: /income 50000 bakmie | catatan | metode")

    jumlah_dan_lain = text[1].split()
    jumlah = jumlah_dan_lain[0]
    detail = " ".join(jumlah_dan_lain[1:])

    parts = [p.strip() for p in detail.split("|")]
    kategori = parts[0] if len(parts) > 0 else ""
    catatan = parts[1] if len(parts) > 1 else ""
    metode = parts[2] if len(parts) > 2 else ""

    append_tx(update.effective_user.id, "income", jumlah, kategori, catatan, metode)
    await update.message.reply_text(f"Pemasukan {jumlah} dicatat ✅")

async def expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.split(maxsplit=1)
    if len(text) < 2:
        return await update.message.reply_text("Format salah. Contoh: /expense 12000 bahan | catatan | metode")

    jumlah_dan_lain = text[1].split()
    jumlah = jumlah_dan_lain[0]
    detail = " ".join(jumlah_dan_lain[1:])

    parts = [p.strip() for p in detail.split("|")]
    kategori = parts[0] if len(parts) > 0 else ""
    catatan = parts[1] if len(parts) > 1 else ""
    metode = parts[2] if len(parts) > 2 else ""

    append_tx(update.effective_user.id, "expense", jumlah, kategori, catatan, metode)
    await update.message.reply_text(f"Pengeluaran {jumlah} dicatat ✅")

# ========== Jalankan Bot ==========
def main():
    app = ApplicationBuilder().token(os.environ["TG_TOKEN"]).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("income", income))
    app.add_handler(CommandHandler("expense", expense))

    app.run_polling()

if __name__ == "__main__":
    main()
