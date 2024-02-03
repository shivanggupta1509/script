# -*- coding: utf-8 -*-
import asyncio
import random
import re
from telethon.sync import TelegramClient, events

api_id = '24674411'
api_hash = 'bdada0468935f9a011a5c18977a5ae5f'
phone_number = '+919987460270'
file_path = 'data.txt'
group_usernames = ['onyxchecker_bot']
approved_messages = {}
client = TelegramClient('session_name', api_id, api_hash)
cmd_file = 'cmds.txt'

# Flags to control sending
send_cards_flag = True

def read_commands():
        with open(cmd_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                cmd_val = lines[0].split('=')[1].strip()
        return cmd_val

# Function to update the command in the text file
async def update_cmd(cmd_val):
    data = f"cmd = {cmd_val}"
    with open(cmd_file, 'w') as file:
        file.write(data)

# ... (other functions and event handlers)

@client.on(events.NewMessage(pattern=r'/cmd'))
async def handle_cmd_update(event):
    try:
        message = event.message.text
        parts = message.split()
        if len(parts) == 2 and parts[0] == '/cmd':
            new_cmd = parts[1]
            await update_cmd(new_cmd)
            await event.respond('Command updated successfully!')
        else:
            await event.respond('Invalid command format. Use "/cmd {new_command}"')
    except ValueError:
        await event.respond('Invalid command format. Use "/cmd {new_command}"')


# Function to read data from the text file
def read_data():
    with open(file_path, 'r') as file:
        data = file.readlines()
        # Extracting BIN, expiry month, and expiry year from the file
        bin_val = data[0].split('=')[1].strip()
        exp_m_val = data[1].split('=')[1].strip()
        exp_y_val = data[2].split('=')[1].strip()
    return bin_val, exp_m_val, exp_y_val

# Function to update data in the text file
async def update_data(bin_val, exp_m_val, exp_y_val):
    data = f"bin = {bin_val}\nexpm = {exp_m_val}\nexpy = {exp_y_val}"
    with open(file_path, 'w') as file:
        file.write(data)
async def update_cmd(cmd_val):
    data = f"cmd = {cmd_val}"
    with open(cmd_file, 'w') as file:
        file.write(data)
# Function to generate a card with provided BIN, expiry month, and expiry year, and random CVV
# Adjust the gen_card function to accept cmd as an argument:
def gen_card(cmd, bin_val, exp_m_val, exp_y_val):
    cvv = str(random.randint(0, 999)).zfill(3)
    card_number = bin_val
    for _ in range(15 - len(bin_val)):
        digit = random.randint(0, 9)
        card_number += str(digit)
    digits = [int(x) for x in card_number]
    for i in range(0, 16, 2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    total = sum(digits)
    check_digit = (10 - (total % 10)) % 10
    card_number += str(check_digit)

    return f".{cmd} {card_number}|{exp_m_val}|{exp_y_val}|{cvv}"

async def send_message(client, group_username, card_info):
    await client.send_message(group_username, card_info)

async def send_cards():
    global send_cards_flag
    while True:
        if send_cards_flag:
            bin_val, exp_m_val, exp_y_val = read_data()
            cmd = read_commands()  # Retrieve the cmd value
            card_info = gen_card(cmd, bin_val, exp_m_val, exp_y_val)  # Pass cmd to gen_card
            for group_username in group_usernames:
                await send_message(client, group_username, card_info)
        await asyncio.sleep(37)
@client.on(events.NewMessage(pattern=r'/u'))
async def handle_update(event):
    try:
        message = event.message.text
        if '|' in message:
            pattern = re.compile(r'/u (\d{16})\|(\d{2})\|(\d{4})')
            match = pattern.match(message)
            if match:
                cc_number, exp_m_val, exp_y_val = match.groups()
                bin_val = cc_number[:12]  # Extract first 12 digits as BIN
                await update_data(bin_val, exp_m_val, exp_y_val)
                await event.respond('Data updated successfully!')

            else:
                await event.respond('Invalid command format. Use "/u {cc}|{expm}|{expy}|{cvv}"')
        else:
            parts = message.split()
            if len(parts) >= 4 and parts[0] == '/u':
                bin_val, exp_m_val, exp_y_val = parts[1], parts[2], parts[3]
                cvv_val = ""  # Assuming CVV is not provided in the old format
                await update_data(bin_val, exp_m_val, exp_y_val)
                await event.respond('Data updated successfully!')
            else:
                await event.respond('Invalid command format. Use "/u {cc}|{expm}|{expy}|{cvv}"')
    except ValueError:
        await event.respond('Invalid command format. Use "/u {cc}|{expm}|{expy}|{cvv}"')


@client.on(events.NewMessage(pattern=r'/start(\s+\d+)?'))
async def handle_start(event):
    global send_cards_flag

    # Extract the argument after /start (if any)
    argument = event.pattern_match.group(1)

    # If no argument is provided, or if it's just /start without a number
    if argument is None:
        send_cards_flag = True  # Continue sending CC details indefinitely

    else:
        # Extract the number from the argument
        try:
            repeat_count = int(argument.strip())
            # Set send_cards_flag to True for the specified number of times
            for _ in range(repeat_count):
                bin_val, exp_m_val, exp_y_val = read_data()
                card_info = gen_card(bin_val, exp_m_val, exp_y_val)
                for group_username in group_usernames:
                    await send_message(client, group_username, card_info)
                await asyncio.sleep(45)
            send_cards_flag = False  # Stop sending after the specified count
        except ValueError:
            await event.respond('Invalid argument format. Use "/start" or "/start <number>"')

    await event.respond('Sending cc!')


@client.on(events.NewMessage(pattern=r'/stop'))
async def handle_stop(event):
    global send_cards_flag
    send_cards_flag = False
    await event.respond('Stopped!')

# New function to handle .a {email} command
@client.on(events.NewMessage(pattern=r'\.a (.+)'))
async def handle_email_command(event):
    email = event.pattern_match.group(1)
    # Create a message with the email in italic format using Markdown
    formatted_email = f"**𝙊𝙣𝙡𝙮𝙁𝙖𝙣𝙨 100$\n\n𝙀𝙢𝙖𝙞𝙡 - `{email}`\n𝙋𝙖𝙨𝙨 - `Ariz123`\n\n𝙍𝙪𝙡𝙚𝙨-\n\n1)𝙐𝙨𝙚 𝙉𝙚𝙬 𝙔𝙤𝙧𝙠 𝙄𝙋 𝙊𝙣𝙡𝙮.\n2)𝙑𝙋𝙉 𝙏𝙤 𝙐𝙨𝙚 - 𝙒𝙞𝙣𝙙𝙨𝙘𝙧𝙞𝙗𝙚\n3)90$+ 𝙨𝙥𝙚𝙣𝙩 𝙩𝙝𝙚𝙣 𝙬𝙖𝙧𝙧𝙖𝙣𝙩𝙮 𝙚𝙣𝙙𝙨\n4)𝘿𝙤𝙣'𝙩 𝙨𝙪𝙗𝙨𝙘𝙧𝙞𝙗𝙚 𝙛𝙧𝙚𝙚 𝙢𝙤𝙙𝙚𝙡𝙨 𝙛𝙞𝙧𝙨𝙩.\n5)𝙄𝙛 𝙖𝙣𝙮 𝙧𝙪𝙡𝙚 𝙗𝙧𝙤𝙠𝙚𝙣 𝙩𝙝𝙚𝙣 𝙬𝙖𝙧𝙧𝙖𝙣𝙩𝙮 𝙬𝙤𝙣'𝙩 𝙗𝙚 𝙖𝙥𝙥𝙡𝙞𝙚𝙙.\n\n𝙏𝙝𝙖𝙣𝙠𝙨 𝙛𝙤𝙧 𝙗𝙪𝙮𝙞𝙣𝙜 𝙛𝙧𝙤𝙢 @arizalsells1\n\n𝙋𝙡𝙚𝙖𝙨𝙚 𝙜𝙞𝙫𝙚 𝙫𝙤𝙪𝙘𝙝 **"
    # Edit the message to include the formatted email
    await event.edit(formatted_email)

@client.on(events.NewMessage(pattern=r'\.5 (.+)'))
async def handle_email_command(event):
    email = event.pattern_match.group(1)
    # Create a message with the email in italic format using Markdown
    formatted_email = f"**𝙊𝙣𝙡𝙮𝙁𝙖𝙣𝙨 50$\n\n𝙀𝙢𝙖𝙞𝙡 - `{email}`\n𝙋𝙖𝙨𝙨 - `Ariz123`\n\n𝙍𝙪𝙡𝙚𝙨-\n\n1)𝙐𝙨𝙚 𝙉𝙚𝙬 𝙔𝙤𝙧𝙠 𝙄𝙋 𝙊𝙣𝙡𝙮.\n2)𝙑𝙋𝙉 𝙏𝙤 𝙐𝙨𝙚 - 𝙒𝙞𝙣𝙙𝙨𝙘𝙧𝙞𝙗𝙚\n3)50$ 𝙨𝙥𝙚𝙣𝙩 𝙩𝙝𝙚𝙣 𝙬𝙖𝙧𝙧𝙖𝙣𝙩𝙮 𝙚𝙣𝙙𝙨\n4)𝘿𝙤𝙣'𝙩 𝙨𝙪𝙗𝙨𝙘𝙧𝙞𝙗𝙚 𝙛𝙧𝙚𝙚 𝙢𝙤𝙙𝙚𝙡𝙨 𝙛𝙞𝙧𝙨𝙩.\n5)𝙄𝙛 𝙖𝙣𝙮 𝙧𝙪𝙡𝙚 𝙗𝙧𝙤𝙠𝙚𝙣 𝙩𝙝𝙚𝙣 𝙬𝙖𝙧𝙧𝙖𝙣𝙩𝙮 𝙬𝙤𝙣'𝙩 𝙗𝙚 𝙖𝙥𝙥𝙡𝙞𝙚𝙙.\n\n𝙏𝙝𝙖𝙣𝙠𝙨 𝙛𝙤𝙧 𝙗𝙪𝙮𝙞𝙣𝙜 𝙛𝙧𝙤𝙢 @arizalsells1\n\n𝙋𝙡𝙚𝙖𝙨𝙚 𝙜𝙞𝙫𝙚 𝙫𝙤𝙪𝙘𝙝 **"
    # Edit the message to include the formatted email
    await event.edit(formatted_email)

@client.on(events.NewMessage(pattern=r'\.s (.+)'))
async def handle_email_command(event):
    email = event.pattern_match.group(1)
    # Create a message with the email in italic format using Markdown
    formatted_email = f"**𝙊𝙣𝙡𝙮𝙁𝙖𝙣𝙨 𝘼𝙪𝙩𝙤𝙧𝙚𝙘𝙝𝙖𝙧𝙜𝙚\n\n𝙀𝙢𝙖𝙞𝙡 - `{email}`\n𝙋𝙖𝙨𝙨 - `Ariz123`\n\n𝙍𝙪𝙡𝙚𝙨-\n\n1)𝙐𝙨𝙚 𝙉𝙚𝙬 𝙔𝙤𝙧𝙠 𝙄𝙋 𝙊𝙣𝙡𝙮.\n2)𝙑𝙋𝙉 𝙏𝙤 𝙐𝙨𝙚 - 𝙒𝙞𝙣𝙣𝙙𝙨𝙘𝙧𝙞𝙗𝙚\n3)𝙄𝙛 𝙩𝙝𝙚 𝙖𝙘𝙘𝙤𝙪𝙣𝙩 𝙧𝙚𝙡𝙤𝙖𝙙𝙨 𝙩𝙬𝙞𝙘𝙚 𝙩𝙝𝙚𝙣 200$ 𝙨𝙥𝙚𝙣𝙙 𝙬𝙖𝙧𝙧𝙖𝙣𝙩𝙮 𝙞𝙛 𝙞𝙩 𝙧𝙚𝙡𝙤𝙖𝙙𝙨 𝙤𝙣𝙘𝙚 𝙤𝙧 𝙣𝙤𝙩 𝙚𝙫𝙚𝙣 𝙤𝙣𝙘𝙚 𝙩𝙝𝙚𝙣 𝙄 𝙬𝙞𝙡𝙡 𝙜𝙞𝙫𝙚 𝙩𝙤𝙩𝙖𝙡 𝙖𝙘𝙘𝙤𝙪𝙣𝙩 𝙬𝙤𝙧𝙩𝙝 𝙖𝙩𝙡𝙚𝙖𝙨𝙩 250$(𝙞𝙣𝙘𝙡𝙪𝙙𝙞𝙣𝙜 𝙩𝙝𝙚 100 𝙤𝙧 150)\n4)𝘿𝙤𝙣'𝙩 𝙨𝙪𝙗𝙨𝙘𝙧𝙞𝙗𝙚 𝙛𝙧𝙚𝙚 𝙢𝙤𝙙𝙚𝙡𝙨 𝙛𝙞𝙧𝙨𝙩.\n5)𝙄𝙛 𝙖𝙣𝙮 𝙧𝙪𝙡𝙚 𝙗𝙧𝙤𝙠𝙚𝙣 𝙩𝙝𝙚𝙣 𝙬𝙖𝙧𝙧𝙖𝙣𝙩𝙮 𝙬𝙤𝙣'𝙩 𝙗𝙚 𝙖𝙥𝙥𝙡𝙞𝙚𝙙.\n\n𝙏𝙝𝙖𝙣𝙠𝙨 𝙛𝙤𝙧 𝙗𝙪𝙮𝙞𝙣𝙜 𝙛𝙧𝙤𝙢 @arizalsells1\n\n𝙋𝙡𝙚𝙖𝙨𝙚 𝙜𝙞𝙫𝙚 𝙫𝙤𝙪𝙘𝙝 **"
    # Edit the message to include the formatted email
    await event.edit(formatted_email)


@client.on(events.NewMessage(pattern=r'\.upi'))
async def handle_upi_command(event):
    # Edit the message to display "hello"
    await event.edit("**UPI IDs \n1st- `shivanggupta.1509@oksbi`\n2nd- `shivanggupta.1509-1@oksbi`\nBanking Name - Shivang Gupta**")


@client.on(events.NewMessage(pattern=r'\.crypto'))
async def handle_upi_command(event):
    # Edit the message to display "hello"
    await event.edit("**Crypto Adresses -\n\n\nLTC-`LQS4LDyaeTrs3K85ML3Zh5ESGkSobBbAtm`\n\nUSDT-`TAGRk59rbfV3H5teyZHA8rz7cii2GfFR8z`\n\nBTC-`13JhES1hA2syvJS8wXvhkjB5mJcg8bWp8b`\n\ndeal continues after the payment/network confirmation**")

@client.on(events.NewMessage(pattern=r'\.payid'))
async def handle_upi_command(event):
    # Edit the message to display "hello"
    await event.edit("**BINANCE PAYID- `799118109`**")

@client.on(events.NewMessage(pattern=r'\.price'))
async def handle_upi_command(event):
    # Edit the message to display "hello"
    await event.edit("**𝙋𝙧𝙞𝙘𝙚𝙨 -\n\n 50$ - 189 𝙞𝙣𝙧 / 2$\n\n100$ - 240 𝙞𝙣𝙧 / 2.6$\n\n𝘼𝙪𝙩𝙤𝙡𝙤𝙖𝙙 - 499 𝙞𝙣𝙧 / 6$**")

@client.on(events.NewMessage(pattern=r'\.rep'))
async def handle_upi_command(event):
    # Edit the message to display "hello"
    await event.edit("**𝙍𝙚𝙥𝙡𝙖𝙘𝙚𝙢𝙚𝙣𝙩 𝙧𝙪𝙡𝙚𝙨 -\n\n100$/50$ -\n𝙛𝙤𝙡𝙡𝙤𝙬 𝙖𝙡𝙡 𝙩𝙝𝙚 𝙧𝙪𝙡𝙚𝙨 𝙬𝙝𝙞𝙘𝙝 𝙘𝙤𝙢𝙚 𝙬𝙞𝙩𝙝 𝙩𝙝𝙚 𝙖𝙘𝙘𝙤𝙪𝙣𝙩,𝙧𝙚𝙥𝙡𝙖𝙘𝙚𝙢𝙚𝙣𝙩𝙨 𝙬𝙞𝙡𝙡 𝙗𝙚 𝙗𝙖𝙨𝙚𝙙 𝙤𝙣 𝙩𝙝𝙚 𝙖𝙢𝙤𝙪𝙣𝙩 𝙡𝙚𝙛𝙩 𝙞𝙣 𝙩𝙝𝙚 𝙖𝙘𝙘𝙤𝙪𝙣𝙩 𝙗𝙚𝙛𝙤𝙧𝙚 𝙖𝙣𝙮 𝙚𝙧𝙧𝙤𝙧.\n\n𝘼𝙪𝙩𝙤𝙡𝙤𝙖𝙙 -\n𝙄𝙛 𝙖𝙘𝙘𝙤𝙪𝙣𝙩 𝙙𝙤𝙚𝙨𝙣𝙩 𝙧𝙚𝙡𝙤𝙖𝙙 𝙩𝙝𝙚𝙣 𝙩𝙝𝙚 𝙨𝙥𝙚𝙣𝙙𝙞𝙣𝙜 𝙬𝙖𝙧𝙧𝙖𝙣𝙩𝙮 𝙤𝙛 𝙩𝙤𝙩𝙖𝙡 250$ 𝙞𝙣𝙨𝙩𝙚𝙖𝙙 𝙤𝙛 200$.**")


@client.on(events.NewMessage(pattern=r'\.qr'))
async def handle_qr_command(event):
    # Get the chat ID and message ID of the .qr command message
    chat_id = event.chat_id
    msg_id = event.id

    # Path to the image file you want to send (replace 'path_to_image' with the actual file path)
    image_path = r"C:\Users\shivang\Downloads\h.jpeg"
 # Replace this with your image file path

    # Send the image as a photo with a caption
    await client.send_file(chat_id, image_path, caption="**UPI - `shivanggupta.1509@oksbi`**", reply_to=msg_id)

    # Delete the original .qr message
    await event.delete()

approved_messages = set()  # Initialize an empty set to store approved messages

@client.on(events.MessageEdited(incoming=True))
async def forward_approved_messages(event):
    sender = await event.get_sender()

    if sender.username == 'onyxchecker_bot' and event.is_private:
        if 'Approved' in event.message.text:
            if event.id not in approved_messages:  # Check if the message has not been forwarded before
                print("Message contains 'approved'. Forwarding...")
                target_username = 'Psp8108'
                target_entity = await client.get_entity(target_username)
                await client.forward_messages(target_entity, event.message)
                approved_messages.add(event.id)  # Add the message ID to the set to mark it as forwarded
            else:
                print("Message already forwarded. Not forwarding again.")
        else:
            print("Message does not contain 'APPROVED'. Not forwarding.")


# Start the client and tasks
client.start()
client.loop.create_task(send_cards())
client.run_until_disconnected()
