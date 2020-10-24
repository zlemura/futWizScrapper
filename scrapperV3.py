import requests
from bs4 import BeautifulSoup
import multiprocessing
from multiprocessing import Pool
from functools import partial
from datetime import datetime
import json


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
        # print("Get squad links started at " + str(datetime.now()))
    URL = link
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    squadLinks = []
    squadLinkAs = soup.find_all("a", class_="squad_url")
    for squadLink in squadLinkAs:
        squadLinks.append(squadLink['href'])
    # print("Get squad links end at " + str(datetime.now()))
    return squadLinks


def find_squad_player_links(link):
    # print("Find squad player links started at " + str(datetime.now()))
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
        # print("Find squad player links ended at " + str(datetime.now()))
    return playerList


def add_players_to_list(squadPlayerList):
    # print("Add  players to link started at " + str(datetime.now()))
    temp_squad_player_list = {}
    for player in squadPlayerList:
        if player.futBinURL in temp_squad_player_list.keys():
            temp_squad_player_list[player.futBinURL] += 1
        else:
            temp_squad_player_list.update({player.futBinURL: 1})
    # print("Add  players to link ended at " + str(datetime.now()))
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


if __name__ == '__main__':

    print("Flow started at " + str(datetime.now()))

    squadLinks = get_squad_links(
        "https://www.futbin.com/squad-building-challenges/ALL/115/Top%20Form")

    if len(squadLinks) == 0:
        print("An error has occured")
        quit()

    print("Squad links found at " + str(datetime.now()))

    # print("Squad Links Found")

    player_list = {}
    scraped_player_list = []
    find_squad_player_links_processes = []
    player_link_list = []

    print("Pool started at " + str(datetime.now()))

    # Working Pool code
    pool = Pool(processes=len(squadLinks))
    data = pool.map(find_squad_player_links, squadLinks)
    pool.close()

    print("Pool ended at " + str(datetime.now()))

    print("Adding playerList to scraped started at " + str(datetime.now()))

    # Adding playerLists' to scraped_player_list (collated)
    for playerList in data:
        for player in playerList:
            scraped_player_list.append(player)

    print("Adding playerList to scraped ended at " + str(datetime.now()))

    # print("Player Scraping Complete")
    #
    # print("All Players Added to List")

    player_link_list = add_players_to_list(scraped_player_list)

    temp_player_link_list = []

    player_output_list = []

    print("Creating output list started at " + str(datetime.now()))

    for player in scraped_player_list:
        if player.futBinURL in temp_player_link_list:
            pass
        else:
            temp_player_link_list.append(player.futBinURL)
            playerCount = player_link_list[player.futBinURL]
            player.set_playerCount(playerCount)
            player_output_list.append(player)

    print("Creating output list ended at " + str(datetime.now()))

    # print("Player_List Size: " + str(len(player_list)))

    # sorted_player_list = dict(sorted(player_list.items(), key=lambda item: item[1], reverse=True))

    # print("Player List Sorted by Count")

    # for player in player_output_list:
    #     print(player.name + ", " + str(player.playerCount))

    sorted_list = sorted(player_output_list, reverse=True,
                         key=lambda x: x.playerCount)

    # print(json.dumps([ob.__dict__ for ob in player_output_list]))

    print(json.dumps([ob.__dict__ for ob in sorted_list]))

    # for player in sorted_player_list:
    #     print('Name: ' + player.name + '\n')
    #     print('Club: ' + player.club + '\n')
    #     print('League: ' + player.league + '\n')
    #     print('Nation: ' + player.nation + '\n')
    #     print('Revision: ' + player.revision + '\n')
    #     print('Level: ' + player.level + '\n')
    #     print('Position: ' + player.position + '\n')
    #     print('Link: ' + player.futBinURL + '\n')
