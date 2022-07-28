import json
import os
import subprocess
from tkinter import filedialog
DEFAULT_ACCOUNTS = ["HighUnderLords1"]

class Account:
	def __init__(self):
		self.username = ""
		self.token = ""

	def setUsername(self, username):
		self.username = username

	def getUsername(self):
		return self.username

	def getToken(self):
		return self.token

account = Account()

def loadUrl(url:str, token=False, useUsername=False):
	if not token:
		username = account.getUsername()
		if not username or not useUsername:
			data = json.loads(subprocess.check_output(f"curl {url}", shell=False, universal_newlines=True))
		else:
			data = json.loads(subprocess.check_output(f"curl -u {username} {url}", shell=False, universal_newlines=True))
	else:
		data = json.loads(subprocess.check_output(f"curl -H \"Authorization: token {account.getToken()}\" {url}"))
	clear()
	return data

def checkDefault(username:str):
	if username.lower()[0] == 'd' and len(username) == 2:
		try:
			username = DEFAULT_ACCOUNTS[int(username[1])-1]
		except:
			print("That index is not in the default accounts list", end="")
			input()
			username = ""
	return username

def checkAccount(username:str):
	data = loadUrl(f"https://api.github.com/users/{username}", token=False)
	if not data.get("message", 0):
		return username
	else:
		return ""

def clear():
	os.system("cls")

def viewList(data:list, url):
	for i, repo in enumerate(data):
		print(f"({i+1}) name : {repo['name']}")
		print(f"   Primary Language : {repo['language']}")
	whichRepo = int(input("Enter Repo Number: "))
	clear()
	try:
		repo = data[whichRepo-1]
		print(f"Viewing {repo['name']}")
		viewDict(repo, url)
	except:
		return

def viewDict(data:dict, url):
	if type(data) == list:
		viewList(data, url)
	else:
		print(f"You are at {url}")
		userKey = input("What do you wish to view? (Nothing to stop): ")
		while userKey:
			clear()
			if userKey in ["a", "all"]:
				for key, value in data.items():
					print(key + " : " + str(value))
			else:
				value = data.get(userKey, "Key not in data")
				print(userKey + " : " + str(value))
				try:
					if value[:4] == "http" and not userKey == "url" and not value[-4:]==".git":
						toUrl = input("Do you wish to look at url?: ")
						if toUrl.lower()[0] == 'y':
							loadData = loadUrl(value, token=False)
							if loadData and type(loadData) == list:
								viewList(loadData, value)
								clear()
							elif loadData and type(loadData) == dict:
								viewDict(loadData, value)
								clear()
							else:
								print("There is nothing at the url")
					elif value[-4:] == ".git":
						toClone = input("Do you want to clone this Repository?: ")
						if toClone.lower()[0] == 'y':
							cloneRepo(value)
				except:
					pass
			print(f"You are at {url}")
			userKey = input("What do you wish to view? (Nothing to stop): ")

def lookAtUser():
	username = ""
	while not username:
		username = input("Who do you want to look for?: ")
		username = checkDefault(username)
		username = checkAccount(username)
		if not username:
			print("That is not a user", end="")
			input()
			return
	url = f"https://api.github.com/users/{username}"
	data = loadUrl(url, token=False)
	viewDict(data, url)

def lookAtRepo():
	username = ""
	while not username:
		username = input("Enter the owner's username: ")
		username = checkDefault(username)
		username = checkAccount(username)
		if not username:
			print("That is not a valid account")
	data = {"message": "This is to intiate the loop"}
	while data.get("message", 0):
		repo_name = input("Enter the Repository name: ")
		url = f"https://api.github.com/repos/{username}/{repo_name}"
		data = loadUrl(url, token=False)
		if data.get("message", 0):
			print("That is not a valid Repository name")
		else:
			viewDict(data, url)
			return data["clone_url"]

def cloneRepo(cloneUrl:str):
	textUrl = input("Do you want to type the directory?: ")
	if textUrl.lower()[0] == 'y':
		place = input("Enter location you wish to clone Repo: ")
	else:
		place = filedialog.askdirectory()
	os.chdir(place)
	os.system(f"git clone {cloneUrl}")
	clear()


def main(username = ""):
	username = checkAccount(username)
	account.setUsername(username)
	numberChoice = 1
	while 0 < numberChoice <= 4:
		clear()
		print("What do you want to do")
		print("(1) Sign in")
		print("(2) Sign out")
		print("(3) Accounts")
		print("(4) Repositories")
		numberChoice = input(">>> ")
		if numberChoice in ["exit", "exit()", ""]:
			break
		else:
			numberChoice = int(numberChoice)

		if numberChoice == 1:
			username = ""
			while not username:
				clear()
				username = input("Enter your username: ")
				username = checkDefault(username)
				username = checkAccount(username)
				if not username:
					print("That is not a username!", end="")
					input()
			account.setUsername(username)
			print(f"You are signed in as {username}.")
			print("You will need to know the password for every query", end="")
			input()

		if numberChoice == 2:
			if not account.getUsername():
				print("You are not signed in", end="")
				input()
			else:
				account.setUsername("")
				print("Signed out", end="")
				input()

		if numberChoice == 3:
			clear()
			print("What do you want to do")
			print("(1) Look at account")
			print("(2) Look at default accounts")
			print("(3) Add default account")
			print("(4) Remove default account")
			choice = input('>>> ')
			if choice in ["exit", "exit()", ""]:
				continue
			else:
				choice = int(choice)

			if choice == 1:
				lookAtUser()
			if choice == 2:
				print("Default Accounts:\n")
				for i, username in enumerate(DEFAULT_ACCOUNTS):
					print("Username:", username, f"| Call: d{i+1}")
				input()
			if choice == 3:
				username = input("Enter your username: ")
				data = loadUrl(f"https://api.github.com/users/{username}", token=False)
				try:
					data["message"]
					print("That is not a valid account", end="")
					input()
				except:
					DEFAULT_ACCOUNTS.append(username)
					print("Username added to default accounts\nType 'd[index+1]' to use index", end="")
					input()
			if choice == 4:
				username = input("Enter username: ")
				if username in DEFAULT_ACCOUNTS:
					DEFAULT_ACCOUNTS.remove(username)
					print(f"Removed {username} from default accounts", end="")
					input()
				else:
					print(f"{username} not in account", end="")
					input()


		elif numberChoice == 4:
			clear()
			print("What do you want to do")
			print("(1) Clone Repository")
			print("(2) Look at Repository")
			choice = input(">>> ")
			if choice in ["exit", "exit()", ""]:
				continue
			else:
				choice = int(choice)

			if choice == 1:
				haveUrl = input("Do you have an url for the Repository?: ")
				if haveUrl.lower()[0] == 'y':
					repoUrl = input("Enter Repository Clone-Url: ")
				else:
					username = ""
					while not username:
						username = input("Enter the owner's username: ")
						username = checkDefault(username)
						username = checkAccount(username)
						if not username:
							print("That is an invalid account")
					data = {"message": "This is to intiate the loop"}
					while data.get("message", 0):
						repo_name = input("Enter the Repository name: ")
						url = f"https://api.github.com/repos/{username}/{repo_name}"
						data = loadUrl(url, token=False)
						if data.get("message", 0):
							print("That is not a valid Repository name")
					repoUrl = data["clone_url"]
				while repoUrl[-3:] != "git":
					clear()
					repoUrl = input("Enter Repository Clone-Url: ")
				cloneRepo(repoUrl)
			if choice == 2:
				lookAtRepo()

running = True
while running:
	username = account.getUsername()
	try:
		main(username)
		running = False
	except KeyboardInterrupt:
		pass