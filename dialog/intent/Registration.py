# Registration intent

class Registration:
    def __init__(self):
        self.STATE_IDLE = 0
        self.ASK_NAME = 100
        self.ASK_ID = 200
        self.ASK_PHONE = 300
        self.ASK_PHOTO = 400
        self.DONE = 9999

        self.var_name = ''
        self.var_id = ''
        self.var_phone = ''
        self.var_photo = None

        self.current_state = self.STATE_IDLE

    def handle(self, message):
        if self.current_state == self.ASK_NAME:
            self.var_name = message
            self.current_state = self.ASK_ID
            return "Your citizen ID"
        elif self.current_state == self.ASK_ID:
            self.var_id = message
            self.current_state = self.ASK_PHONE
            return "Your phone"
        elif self.current_state == self.ASK_PHONE:
            self.var_phone = message
            self.current_state = self.ASK_PHOTO
            return "Your photo"
        elif self.current_state == self.ASK_PHOTO:
            self.var_photo = message
            self.current_state = self.DONE
            return "Welcome %s %s %s" % (self.var_name, self.var_id, self.var_phone)

        


        if message == 'bye':
            self.current_state = self.DONE
            return "Welcome %s %s %s" % (self.var_name, self.var_id, self.var_phone)
        elif message == 'register':
            self.current_state = self.ASK_NAME
            return "Please enter name"
    
    def endIntent(self):
        return self.current_state == self.DONE

    def getCurrentState(self):
        return self.current_state

    def getData(self):
        return {
            'name':self.var_name,
            'id':self.var_id,
            'phone':self.var_phone,
            'photo':self.var_photo
        }

if __name__ == "__main__":
    rego = Registration()

    while not rego.endIntent():
        s = input()
        o = rego.handle(s)
        print(o)
