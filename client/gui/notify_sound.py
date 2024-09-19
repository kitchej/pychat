from just_playback import Playback

class NotificationSound(Playback):
    def __init__(self, path_to_file, name):
        Playback.__init__(self, path_to_file)
        self.filepath = path_to_file
        if name is None:
            self.name = 'None'
        else:
            self.name = name