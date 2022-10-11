import logging
import os
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
    CallbackContext,
)
from util import delete_booking, from_iso, get_available_timings, get_bookings, make_booking, next_week, time_to_range, to_iso, weekday

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

def lounge_bookings() -> str:
    bookings = get_bookings()
    if not bookings:
        return ""

    s = "== [Lounge Bookings] ==\n"
    for date in sorted(bookings.keys()):
        s += f"{date[0]:02d}/{date[1]:02d} ({weekday(bookings[date][0][0])})\n"
        day_bookings = sorted(bookings[date])
        for index in range(len(day_bookings)):
            if index >= len(day_bookings):
                break
            hours = 1
            cursor = 1
            time, floor, username = day_bookings[index]
            while(index+cursor < len(day_bookings) and 
                    time.hour + hours >= day_bookings[index+cursor][0].hour):
                if(username == day_bookings[index+cursor][2] and 
                    floor == day_bookings[index+cursor][1] and
                    time.hour + hours == day_bookings[index+cursor][0].hour):
                        hours += 1
                        day_bookings.pop(index+cursor)  
                else:
                    cursor += 1
            s += f"L{floor}: {time_to_range(time, hours)} (@{username})\n"
        s += "\n"
    s = s[:-1]
    s+= "=====================\n"

    return s


def start(update: Update, context: CallbackContext) -> str:
    """Starts convo"""
    text = ""
    text+= lounge_bookings()
    text+= "\nWhat would you like to do?"
    buttons = [
        [
            InlineKeyboardButton(text="Add Lounge Booking", callback_data="AddLounge"),
            InlineKeyboardButton(text="Delete Lounge Booking", callback_data="DelLounge")
        ],
        [
            InlineKeyboardButton(text="Refresh", callback_data="Refresh"),
            InlineKeyboardButton(text="Cancel", callback_data="Cancel")
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    # If we're starting over we don't need to send a new message
    if update.message:
        update.message.reply_text(
            "Hi, I'm CaptRocBOT!"
        )
        update.message.reply_text(text=text, reply_markup=keyboard)
    else:
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    
    return "StartMenu"

def end(update: Update, context: CallbackContext) -> int:
    """End convo"""
    update.callback_query.answer()
    text = "Bye for now! Use /start to start again."
    update.callback_query.edit_message_text(text=text)

    return ConversationHandler.END

def stop(update: Update, context: CallbackContext) -> int:
    """End Conversation by command."""
    update.message.reply_text("Bye for now! Use /start to start again!")

    return ConversationHandler.END

def lounge_date_menu(update: Update, context: CallbackContext) -> str:
    """Date menu for adding lounge booking"""

    text = "Which day would you like to book?"
    days = next_week()
    f = lambda x : [
        InlineKeyboardButton(
            text=f"{x.day:02d}/{x.month:02d} ({weekday(x)})",
            callback_data=f"DATE_{x.isoformat()}"
        )
    ]
    buttons = [f(day) for day in days]
    buttons.append([
        InlineKeyboardButton(text="Back", callback_data="Back"),
        InlineKeyboardButton(text="Cancel", callback_data="Cancel")
    ])
    keyboard = InlineKeyboardMarkup(buttons)

    # Reset user_data
    context.user_data["DATE"] = None
    context.user_data["FLOOR"] = None
    context.user_data["TIMES"] = set()

    # Respond
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return "LoungeDateMenu"

def lounge_floor_menu(update: Update, context: CallbackContext) -> str:
    """Floor menu for adding lounge booking"""
    if update.callback_query.data.startswith("DATE_"):
        s = update.callback_query.data[5:]
        context.user_data["DATE"] = from_iso(s)
    

    date = context.user_data["DATE"]
    text = (
        f"Date: {date.day}/{date.month}\n"
        f"Select floor"
    )

    buttons = [
        [
            InlineKeyboardButton(text="3", callback_data="FLOOR_3"),
            InlineKeyboardButton(text="4", callback_data="FLOOR_4"),
            InlineKeyboardButton(text="5", callback_data="FLOOR_5")
        ],
        [
            InlineKeyboardButton(text="Back", callback_data="Back"),
            InlineKeyboardButton(text="Cancel", callback_data="Cancel")
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    # Reset user_data
    context.user_data["FLOOR"] = None
    context.user_data["TIMES"] = set()

    # Respond
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return "LoungeFloorMenu"

def lounge_time_menu(update: Update, context: CallbackContext) -> str:
    """Timeslot menu for adding lounge booking"""

    if update.callback_query.data.startswith("FLOOR_"):
        context.user_data["FLOOR"] = int(update.callback_query.data[6:])
    elif update.callback_query.data.startswith("TIME_"):
        context.user_data["TIMES"].add(from_iso(update.callback_query.data[5:]))

    date = context.user_data["DATE"]
    floor = context.user_data["FLOOR"]
    text = (
        f"Date: {date.day}/{date.month}, Floor: {floor}\n"
        f"Select timeslot(s)"
    )
    if context.user_data["TIMES"]:
        text += "\n\nCurrently selected:"
        for time in sorted(context.user_data["TIMES"]):
            text += ''
            text += f"\n{time_to_range(time, 1)}"

    _hours = sorted(list(
        set(get_available_timings(date, floor))
            .difference(context.user_data["TIMES"])
    ))
    f = lambda x : InlineKeyboardButton(text=time_to_range(x, 1), callback_data="TIME_"+to_iso(x))
    buttons = [[f(j) for j in _hours[i:i+2]] for i in range(0, len(_hours), 2)]
    if context.user_data["TIMES"]:
        buttons.append([
            InlineKeyboardButton(text="Back", callback_data="Back"),
            InlineKeyboardButton(text="Confirm", callback_data="Confirm"),
            InlineKeyboardButton(text="Cancel", callback_data="Cancel")
        ])
    else:
        buttons.append([
            InlineKeyboardButton(text="Back", callback_data="Back"),
            InlineKeyboardButton(text="Cancel", callback_data="Cancel")
        ])
    keyboard = InlineKeyboardMarkup(buttons)

    # Respond
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return "LoungeTimeMenu"

def lounge_confirmation(update: Update, context: CallbackContext) -> str:
    """Menu for adding lounge booking"""
    date = context.user_data["DATE"]
    floor = context.user_data["FLOOR"]
    times = sorted(context.user_data["TIMES"])

    from_user = update.callback_query.from_user
    if not make_booking(times, floor, from_user["username"], from_user["id"]):
        text = "Something went wrong while trying to book :/\n"
        text+= "Contact @lord_idiot if this keeps happening."
        buttons = [[InlineKeyboardButton(text="Restart", callback_data="Restart")]]
        keyboard = InlineKeyboardMarkup(buttons)
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, keyboard=keyboard)

    text = (
        f"Booking confirmed with the following details:\n"
        f"Date: {date.day}/{date.month}, Floor: {floor}\n"
        f"Timeslot(s)"
    )
    for time in times:
        text += ''
        text += f"\n* {time_to_range(time, 1)}"

    buttons = [
        [
            InlineKeyboardButton(text="Restart", callback_data="Restart"),
            InlineKeyboardButton(text="Done", callback_data="Done")
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    # Respond
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return "LoungeConfirmation"


def lounge_booking_list_menu(update: Update, context: CallbackContext) -> str:
    """Menu for adding lounge booking"""
    from_user = update.callback_query.from_user
    if update.callback_query.data.startswith("DEL_"):
        floor = int(update.callback_query.data[4:5])
        time = from_iso(update.callback_query.data[5:])
        delete_booking(time, floor, from_user["username"])

    bookings = get_bookings(from_user["username"])
    buttons = []
    for date in sorted(bookings.keys()):
        for booking in sorted(bookings[date]):
            time, floor, username = booking
            button = InlineKeyboardButton(
                text=f"L{floor}: {time.day:02d}/{time.month} ({weekday(time)}) {time_to_range(time, 1)}",
                callback_data=f"DEL_{floor}{to_iso(time)}"
            )
            buttons.append([button])

    text = "Choose a booking to delete.\n"
    text+=f"You have {len(buttons)} booking(s) in the next week."

    buttons.append([
        InlineKeyboardButton(text="Back", callback_data="Back"),
        InlineKeyboardButton(text="Cancel", callback_data="Cancel")
    ])
    keyboard = InlineKeyboardMarkup(buttons)

    # Respond
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return "LoungeBookingListMenu"


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.environ.get("TG_API_KEY"))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states = {
            "StartMenu": [
                CallbackQueryHandler(lounge_date_menu, pattern="^AddLounge$"),
                CallbackQueryHandler(lounge_booking_list_menu, pattern="^DelLounge$"),
                CallbackQueryHandler(start, pattern="^Refresh$"),
                CallbackQueryHandler(end, pattern="^Cancel$"),
            ],
            "LoungeDateMenu": [
                CallbackQueryHandler(start, pattern="^Back$"),
                CallbackQueryHandler(end, pattern="^Cancel$"),
                CallbackQueryHandler(lounge_floor_menu, pattern="^DATE_.*$"),
            ],
            "LoungeFloorMenu": [
                CallbackQueryHandler(lounge_date_menu, pattern="^Back$"),
                CallbackQueryHandler(end, pattern="^Cancel$"),
                CallbackQueryHandler(lounge_time_menu, pattern="^FLOOR_.*$"),
            ],
            "LoungeTimeMenu": [
                CallbackQueryHandler(lounge_floor_menu, pattern="^Back$"),
                CallbackQueryHandler(end, pattern="^Cancel$"),
                CallbackQueryHandler(lounge_confirmation, pattern="^Confirm$"),
                CallbackQueryHandler(lounge_time_menu, pattern="^TIME_.*$"),
            ],
            "LoungeConfirmation": [
                CallbackQueryHandler(start, pattern="^Restart$"),
                CallbackQueryHandler(end, pattern="^Done$"),
            ],
            "LoungeBookingListMenu": [
                CallbackQueryHandler(start, pattern="^Back$"),
                CallbackQueryHandler(end, pattern="^Cancel$"),
                CallbackQueryHandler(lounge_booking_list_menu, pattern="^DEL_.*$"),
            ]
        },
        fallbacks=[CommandHandler("stop", stop), CommandHandler("start", start)]
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == "__main__":
    main()