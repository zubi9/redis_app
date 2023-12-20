import redis
import threading
import time

class RedisChat:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.StrictRedis(host=host, port=port, db=db)
        self.channel = 'chat_channel'
        self.exit_command = '/exit'

    def send_message(self, username, message):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"[{timestamp}] {username}: {message}"
        self.redis_client.publish(self.channel, formatted_message)

    def receive_messages(self):
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(self.channel)

        for message in pubsub.listen():
            if message['type'] == 'message':
                print(message['data'].decode('utf-8'))

    def notify_user(self, username, message):
        notification = f"{username} says: {message}"
        self.redis_client.publish(self.channel, notification)

def send_messages(chat_instance, username):
    while True:
        message = input(f"{username}, enter your message (type '/exit' to leave): ")
        if message.lower() == chat_instance.exit_command:
            print(f"Goodbye, {username}!")
            break
        chat_instance.send_message(username, message)

def main():
    # Change the port number if your Redis server is running on a different port
    redis_port = 6379
    
    # Create an instance of the RedisChat class
    chat = RedisChat(port=redis_port)
    
    # Get the username from the user
    username = input("Enter your username: ")
    
    # Notify others about the new user
    chat.notify_user(username, "has joined the chat.")
    
    # Create a thread to receive messages
    receive_thread = threading.Thread(target=chat.receive_messages, daemon=True)
    receive_thread.start()
    
    # Create a thread to send messages
    send_thread = threading.Thread(target=send_messages, args=(chat, username), daemon=True)
    send_thread.start()
    
    # Keep the main thread alive
    receive_thread.join()
    
    # Notify others about the user leaving
    chat.notify_user(username, "has left the chat.")

if __name__ == "__main__":
    main()
