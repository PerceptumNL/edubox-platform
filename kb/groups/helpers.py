import random

def generate_password(sep=''):
	adjective_list = [
        "rode", "gele", "paarse", "groene", "roze", "boze", "blije", "slimme",
        "flauwe", "coole", "zachte", "snelle", "brave", "stoere", "moderne",
        "maffe", "norse", "luie", "heuse", "dikke", "dunne", "keurige"
	]
	noun_list = [
        "draak", "kat", "hond", "haas", "aap", "kip", "pauw", "bij", "kikker",
        "slang", "leeuw", "tijger", "mier", "zebra", "beer", "koala", "pad",
        "leeuw", "wolf", "vosjes"
	]
	adjective = random.choice(adjective_list)
	adjective2 = random.choice(adjective_list)
	noun = random.choice(noun_list)
	noun2 = random.choice(noun_list)
	passwords = [
	    sep.join([noun,noun2]),
	    sep.join([adjective,noun]),
	    sep.join([adjective,noun,noun2]),
	    sep.join([adjective,noun,adjective2,noun2])
	]
	return random.choice(passwords)
