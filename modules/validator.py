from validate_email_address import validate_email


class Validator():
    @staticmethod
    def email(email):
        if validate_email(email):
            return True
        else:
            return False

    @staticmethod
    def is_empty(item):
        if item:
            return True
        else:
            return False

    @staticmethod
    def remove_empty(list):
        cleand_list = []
        for item in list:
            if item:
                cleand_list.append(item)
        return cleand_list
