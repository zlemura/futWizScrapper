import requests
from bs4 import BeautifulSoup


class Player:

    def set_playerCount(self, newPlayerCount):
        self.playerCount = newPlayerCount

    def __init__(self, name, club, league, nation, revision, level, position, playerCount, futBinURL):
        self.name = name
        self.club = club
        self.league = league
        self.nation = nation
        self.revision = revision
        self.level = level
        self.position = position
        self.playerCount = playerCount
        self.futBinURL = futBinURL


def get_squad_links(link):
    URL = link
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    squadLinks = []
    squadLinkAs = soup.find_all("a", class_="squad_url")
    for squadLink in squadLinkAs:
        squadLinks.append(squadLink['href'])
    return squadLinks


def find_squad_player_links(link):
    URL = 'https://www.futbin.com/' + link
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    playerList = []
    for i in range(1, 12):
        # Fetch Card Link
        playerClassName = "cardlid" + str(i)
        playerDiv = soup.find('div', id=playerClassName)
        playerDivCardDetails = playerDiv.find('div', class_="cardetails")
        playerDivCardDetails_a = playerDivCardDetails.find('a')

        # Fetch Card Details
        playerDivOtherDetails = playerDivCardDetails.find('div')
        # name, club, league, nation, revision, level, position, futBinURL
        # Fetch Name
        playerName = playerDivOtherDetails['data-player-commom']
        # Fetch Club
        playerClubDiv = playerDivOtherDetails.find(
            'div', class_="pcdisplay-club-name hide")
        playerClub = playerClubDiv.text.replace('Club: ', '')
        # print(playerClub)
        # Fetch League
        playerLeagueDiv = playerDivOtherDetails.find(
            'div', class_="pcdisplay-league-name hide")
        playerLeague = playerLeagueDiv.text.replace('League: ', '')
        # Fetch Nation
        playerNationDiv = playerDivOtherDetails.find(
            'div', class_="pcdisplay-nation-name hide")
        playerNation = playerNationDiv.text.replace('Country: ', '')
        # Fetch Revision & Level
        playerClass = playerDivOtherDetails['class']
        playerRevision = determine_player_revision_level(playerClass)[0]
        playerLevel = determine_player_revision_level(playerClass)[1]
        # Fetch Position
        playerPositionDiv = playerDivOtherDetails.find(
            'div', class_="pcdisplay-pos")
        playerPosition = playerPositionDiv.text
        # Fetch URL
        try:
            playerLink = playerDivCardDetails_a['href']
        except:
            pass
        # Add to playerList
        playerCount = 0
        playerList.append(Player(playerName, playerClub, playerLeague, playerNation,
                                 playerRevision, playerLevel, playerPosition, 0, playerLink))
    return playerList


def add_players_to_list(squadPlayerList):
    temp_squad_player_list = {}
    for player in squadPlayerList:
        if player.futBinURL in temp_squad_player_list.keys():
            temp_squad_player_list[player.futBinURL] += 1
        else:
            temp_squad_player_list.update({player.futBinURL: 1})
    return temp_squad_player_list


def determine_player_revision_level(playerClass):
    playerLevel = ''
    playerRevision = ''

    # Determine Special Revision
    if 'if' in playerClass:
        playerRevision = 'Inform'
    elif 'otw' in playerClass:
        playerRevision = 'Ones to Watch'
    elif 'sudamericana' in playerClass:
        playerRevision = 'Sudamericana'
    elif 'libertadores_b' in playerClass:
        playerRevision = 'Libertadores'
    elif 'icon' in playerClass:
        playerRevision = 'Icon'

    # Determine Regular Revision
    if playerRevision == '':
        if 'non-rare' in playerClass:
            playerRevision = 'Non-Rare'
        elif 'rare' in playerClass:
            playerRevision = 'Rare'
        else:
            pass

    # Determine Level
    if 'bronze' in playerClass:
        playerLevel = 'Bronze'
    elif 'silver' in playerClass:
        playerLevel = 'Silver'
    elif 'gold' in playerClass:
        playerLevel = 'Gold'
    else:
        pass

    return playerRevision, playerLevel
