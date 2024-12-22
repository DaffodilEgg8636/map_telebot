import telebot
from config import TOKEN, DATABASE
from logic import DB_Map

bot = telebot.TeleBot(TOKEN)
manager = DB_Map(DATABASE)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, "Доступные команды:\n"
                                      "/show_city <название города> - показать город на карте\n"
                                      "/remember_city <название города> - сохранить город\n"
                                      "/show_my_cities - показать сохраненные города.")

@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    city_name = ' '.join(message.text.split()[1:])
    coordinates = manager.get_coordinates(city_name)

    if coordinates:
        path = f"{city_name.replace(' ', '_')}.png"
        manager.create_graph(path, [(city_name, *coordinates)])
        with open(path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    else:
        bot.send_message(message.chat.id, "Город не найден. Убедитесь, что название указано правильно.")

@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    city_name = ' '.join(message.text.split()[1:])
    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f"Город {city_name} успешно сохранен!")
    else:
        bot.send_message(message.chat.id, "Такого города я не знаю. Убедитесь, что название указано правильно.")

@bot.message_handler(commands=['show_my_cities'])
def handle_show_my_cities(message):
    user_id = message.chat.id
    cities = manager.select_cities(user_id)

    if cities:
        path = f"user_{user_id}_cities.png"
        manager.create_graph(path, cities)
        with open(path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    else:
        bot.send_message(message.chat.id, "У вас еще нет сохраненных городов.")

if __name__ == "__main__":
    manager.create_user_table()
    bot.polling()
