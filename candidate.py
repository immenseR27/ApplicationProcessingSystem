import datetime

class Candidate():

    def __init__(self):
        self.id = 0
        self.position_id = 0
        self.surname = ''
        self.name = ''
        self.patronymic = ''
        self.date_of_birthday = datetime.date.today()
        self.experience = 0
        self.mail = ''
        self.phone = ''
        self.photo = ''
        self.extraversion = 0.0
        self.neuroticism = 0.0
        self.agreeableness = 0.0
        self.conscientiousness = 0.0
        self.openness = 0.0

    def set_position_id(self, id):
        self.position_id = id

    def set_surname(self, surname):
        self.surname = surname

    def set_name(self, name):
        self.name = name

    def set_patronymic(self, patronymic):
        self.patronymic = patronymic

    def set_date_of_birthday(self, date_of_birthday):
        self.date_of_birthday = date_of_birthday

    def set_experience(self, experience):
        self.experience = experience

    def set_mail(self, mail):
        self.mail = mail

    def set_phone(self, phone):
        self.phone = phone

    def set_extraversion(self, extraversion):
        self.extraversion = extraversion

    def set_neuroticism(self, neuroticism):
        self.neuroticism = neuroticism

    def set_agreeableness(self, agreeableness):
        self.agreeableness = agreeableness

    def set_conscientiousness(self, conscientiousness):
        self.conscientiousness = conscientiousness

    def set_openness(self, openness):
        self.openness = openness

    def get_position_id(self):
        return self.position_id

    def get_surname(self):
        return self.surname

    def get_patronymic(self):
        return self.patronymic

    def get_date_of_birthday(self, date_of_birthday):
        self.patronymic = date_of_birthday

    def get_experience(self):
        return self.experience

    def get_mail(self):
        return self.mail

    def get_phone(self):
        return self.phone

    def get_extraversion(self):
        return self.extraversion

    def get_neuroticism(self):
        return self.neuroticism

    def get_agreeableness(self):
        return self.agreeableness

    def get_conscientiousness(self):
        return self.conscientiousness

    def get_openness(self):
        return self.openness
