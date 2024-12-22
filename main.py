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
                                      "/show_city <название города> <цвет маркера> - показать город на карте\n"
                                      "/remember_city <название города> - сохранить город\n"
                                      "/show_my_cities <цвет маркера> - показать сохраненные города\n"
                                      "/set_features <ocean/land> - установить заливку континентов или океанов.")

@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    args = message.text.split()[1:]  # Exclude the command itself
    if len(args) < 1:
        bot.send_message(message.chat.id, "Введите название города.")
        return

    # Assume last argument is color only if len(args) > 1 and it looks like a color
    possible_color = args[-1].lower()
    valid_colors = {'red', 'blue', 'green', 'yellow', 'black', 'white'}  # Add more valid colors as needed
    if len(args) > 1 and possible_color in valid_colors:
        city_name = ' '.join(args[:-1])  # Everything except the last word
        color = possible_color
    else:
        city_name = ' '.join(args)  # Entire message after the command is the city name
        color = 'red'  # Default color

    coordinates = manager.get_coordinates(city_name)
    if coordinates:
        path = f"{city_name.replace(' ', '_')}.png"
        manager.create_graph(path, [(city_name, *coordinates)], color=color)
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
    args = message.text.split()
    user_id = message.chat.id
    color = args[1] if len(args) > 1 else 'blue'
    cities = manager.select_cities(user_id)

    if cities:
        path = f"user_{user_id}_cities.png"
        manager.create_graph(path, cities, color)
        with open(path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    else:
        bot.send_message(message.chat.id, "У вас еще нет сохраненных городов.")

@bot.message_handler(commands=['set_features'])
def handle_set_features(message):
    feature = ' '.join(message.text.split()[1:]).lower()
    if feature in ['ocean', 'land']:
        manager.set_fill(feature)
        bot.send_message(message.chat.id, f"Заливка для {feature} установлена!")
    else:
        bot.send_message(message.chat.id, "Неверная опция. Используйте 'ocean' или 'land'.")

if __name__ == "__main__":
    manager.create_user_table()
    bot.polling()
