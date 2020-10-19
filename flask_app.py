
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request, render_template
from multiprocessing import Pool

import json

from core import create_app

from processing import get_squad_links
from processing import find_squad_player_links
from processing import add_players_to_list

if __name__ == '__main__':
    app.run()


class Config:
    DEBUG = True

app = create_app(Config)

@app.route("/", methods=["GET", "POST"])
def adder_page():
    if request.method == "POST":

        squadLinks = get_squad_links(request.form["squadLink"])

        scraped_player_list = []
        player_link_list = []
        player_link_list={}

        pool = Pool(processes = len(squadLinks))
        data = pool.map(find_squad_player_links, squadLinks)
        pool.close()

        #Adding playerLists' to scraped_player_list (collated)
        for playerList in data:
            for player in playerList:
                scraped_player_list.append(player)

        player_link_list = add_players_to_list(scraped_player_list)

        temp_player_link_list = []

        player_output_list=[]

        for player in scraped_player_list:
            if player.futBinURL in temp_player_link_list:
                pass
            else:
                temp_player_link_list.append(player.futBinURL)
                playerCount = player_link_list[player.futBinURL]
                player.set_playerCount(playerCount)
                player_output_list.append(player)

        sorted_list = sorted(player_output_list, reverse = True ,key=lambda x: x.playerCount)

        result = json.dumps([ob.__dict__ for ob in sorted_list])
        result = json.loads(result)
        return render_template("/result.html", results = result, squadLink = request.form["squadLink"])
        return '''
        <html>
                    <body>
                        <div>
                        {result}
                        </div>
                    </body>
        </html>
            '''.format(result=result)
#     return '''
#         <html>
#             <body>
#                 <p>Enter your FUTBIN SBC link:</p>
#                 <form method="post" action=".">
#                     <p><input type = "text" name="squadLink" /></p>
#                     <p><input type="submit" value="Fetch Players" /></p>
#                 </form>
#             </body>
#         </html>
# '''
    
    return render_template("index.html")
