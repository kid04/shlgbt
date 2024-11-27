class Sharing:
    """
    Объект, хранящий в себе важные для пересылки данные
    """
    def __init__(self):
        self.sender = ''
        self.to_send = False
        self.friends = []
        self.url = ''
        self.commentary = ''
        self.type = ''
        self.title = ''
        self.author = ''

class Mute_sharing:
    """
    Объект, хранящий в себе важные для тихой пересылки данные
    """
    def __init__(self, music):
        self.url = music.url
        self.commentary = music.commentary
        self.type = music.type
        self.title = music.title
        self.author = music.author


sharing_time = {}