import base64

def extract_recipient(packet):
    to_index = packet.find("To: ") + len("To: ")
    newline_index = packet.find("\n", to_index)
    recipient = packet[to_index:newline_index].strip()
    return recipient

def extract_message(packet):
    to_index = packet.find("To: ") + len("To: ")
    newline_index = packet.find("\n", to_index)
    recipient = packet[newline_index:].strip()
    return recipient

def base64_decode_bytes(encoded_bytes):
    decoded_bytes = base64.b64decode(encoded_bytes)
    decoded_str = decoded_bytes.decode('UTF-8')
    return decoded_str

def clean_data(packet, mimetype):
    recipient = extract_recipient(packet)
    message = extract_message(packet) # returns a string
    if mimetype == 'application/octet-stream':
        print("base64 mimetype identified")
        message = message.encode('UTF-8')
        message = base64_decode_bytes(message)
    print("[MailServer] Message: ", message)
    if "Confidential" in message:
        message = "Hello, World!"
    message += "\nJust testing from a fake email address [perhaps test@example.com] or amessage selected from spam that some spam filter recently caught."
    return recipient, message
