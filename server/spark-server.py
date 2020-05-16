import tweepy
import socket
import selectors
import errno
import time

ACCESS_TOKEN = '1238072015237656579-PLb6iVt15Spbpwj8BG3QRL7OBKl2bJ'
ACCESS_SECRET = 'HKyiJgH2PZzaHy06tCibakPylvln1ZsXA5VlFQE1V6VFL'
CONSUMER_KEY = '6IcfzycgK624cSZcyo4ZpTkF1'
CONSUMER_SECRET = 'd3omrd0t3lPwHFe4fm5ObqBxoCCuTTVfBW0pIujoKfKV46x32m'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

#  I/O multiplexing
selector = selectors.DefaultSelector()


# Get tweets of specific user and send to ready clients
def send_tweets(conn, mask):
    try:
        tweets = tweepy.Cursor(api.user_timeline, screen_name="potus", exclude_replies=True).items(10000)
        for tweet in tweets:
            tweet_text = tweet.text.strip()
            # tweet_json = {"text": tweet_text, "timestamp": str(tweet.created_at), "user": tweet.user.screen_name}
            try:
                conn.send(bytes(tweet_text, 'utf-8'))
            except socket.error as e:
                if e.errno == errno.EPIPE:
                    print("Client disconnected...")
                    print('Closing connection {}...\n'.format(conn))
                    selector.unregister(conn)
                    conn.close()
                    return
                else:
                    print("Socket exception...")
    except tweepy.TweepError:
        time.sleep(10)


# Accept incoming socket connection
def accept(sock, mask):
    conn, addr = sock.accept()
    print('New connection {} from {}...\n'.format(conn, addr))
    conn.setblocking(False)
    selector.register(conn, selectors.EVENT_WRITE, send_tweets)


def main():
    # create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # allows a socket to forcibly bind to a port in use by another socket
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # connect socket to the local address 9000 port
    server_address = ("localhost", 9000)
    sock.bind(server_address)

    # 5 connections are kept waiting if the server is busy
    # and if a 6th socket tries to connect then the connection is refused
    sock.listen(5)
    print("Listening at {}...\n".format(server_address))

    sock.setblocking(False)
    selector.register(sock, selectors.EVENT_READ, accept)

    while True:
        events = selector.select()
        # loop through all events occurred
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Server stopped')
        try:
            # close all
            exit(-1)
        except SystemExit:
            exit(0)
