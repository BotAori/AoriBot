import telebot
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode
import io
from telebot import types

# Token bot yang didapatkan dari BotFather
BOT_TOKEN = '7828467446:AAHQNCv2I3OWC5qLwPdvw190W3s59iCsQPI'
bot = telebot.TeleBot(BOT_TOKEN)

# Fungsi untuk membuat QR code dari teks
def create_qr(message, text):
    qr_img = qrcode.make(text)
    img_byte_arr = io.BytesIO()
    qr_img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # Membuat tombol berbagi QR code
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Bagikan ke...", switch_inline_query=text)
    markup.add(button)

    bot.send_photo(message.chat.id, img_byte_arr, reply_to_message_id=message.message_id, reply_markup=markup)

# Fungsi untuk memindai dan membaca QR code dari gambar
def scan_qr(message, image):
    decoded = decode(image)
    if decoded:
        result = decoded[0].data.decode('utf-8')

        # Membuat tombol untuk membuka tautan jika hasil scan berupa URL
        markup = types.InlineKeyboardMarkup()
        if result.startswith('http://') or result.startswith('https://'):
            button = types.InlineKeyboardButton("Buka Tautan", url=result)
            markup.add(button)
        
        bot.reply_to(message, f'Hasil scan: {result}', reply_to_message_id=message.message_id, reply_markup=markup)
    else:
        bot.reply_to(message, "Tidak ada kode QR yang ditemukan di gambar ini.", reply_to_message_id=message.message_id)

# Fungsi untuk menangani jika pengguna mengirim gambar biasa (bukan QR code)
def handle_non_qr_image(message):
    bot.reply_to(message, "Gambar ini bukan kode QR. Kirimi saya teks atau gambar QR code untuk diproses.")

# Handler untuk perintah /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Kirimi saya teks atau gambar.")

# Handler untuk mendeteksi jika pengguna mengirim teks
@bot.message_handler(content_types=['text'])
def handle_text(message):
    text = message.text
    create_qr(message, text)

# Handler untuk mendeteksi jika pengguna mengirim gambar (untuk memindai QR)
@bot.message_handler(content_types=['photo'])
def handle_image(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    img = Image.open(io.BytesIO(downloaded_file))
    
    # Coba memindai gambar, jika tidak ada QR, berikan pesan bahwa gambar tidak mengandung QR code
    decoded = decode(img)
    if decoded:
        scan_qr(message, img)
    else:
        handle_non_qr_image(message)

# Memulai polling untuk bot
bot.polling()
