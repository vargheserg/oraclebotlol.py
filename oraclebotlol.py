# OracleBot by Varghese George
# This is a project to have interactions between discord chat bots and APIs
# This will be with a API from a MOBA called League of Legends
import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import urllib.request
import json

bot = commands.Bot(command_prefix='#')
# Default NA Servers
urlRef = 'https://na1.api.riotgames.com'
lolAPI = 'RGAPI-YourAPIKey'


# This indicates that the bot has successfully loaded and is online
@bot.event
async def on_ready():
    print('I have waited over a THOUSAND YEARS for this.')
    print('I am running on ' + bot.user.name)
    print('With the id ' + bot.user.id)

# Just to see if it is working
@bot.command(pass_context=True)
async def ping(ctx):
    await bot.say(':ping_pong: pong ')

# List of commands and how to use them
@bot.command(pass_context=True)
async def helpo(ctx):
    await bot.say("Alright, here is what you'll need.")
    embed = discord.Embed(title="Help", description="Function and Parameters", color=0x8888ff)
    embed.add_field(name="Change Region", value="#region [Regional Code] \nList of Regional Codes: \nNA EUNE EUW BR KR LAN LAS OCE TR RU PBE", inline=True)
    embed.add_field(name="Summoner Profile", value="#profile [Summoner Name]", inline=True)
    embed.add_field(name="Summoner Champion Mastery", value="#mastery [Summoner Name] [Champion Name]", inline=True)
    embed.add_field(name="Live Match Information", value="#livegame [Summoner Name]", inline=True)
    embed.add_field(name="Potential Errors", value="Do not uses spaces in Summoner Name\nCapitalize Champion Name\nLive Match Info requires user to be in a match 0_0", inline=True)
    embed.set_thumbnail(url="https://img00.deviantart.net/6758/i/2012/273/9/b/commission__ryze_by_medli20-d5gd9a5.png")
    await bot.say(embed=embed)


# Different Regions for different servers and users in them (Top 200 in North America, Top 200 in Europe West, etc)
@bot.command(pass_context=True)
async def region(ctx,region):
    global urlRef
    flag = True;
    if region == "NA":
        urlRef = 'https://na1.api.riotgames.com'
    elif region == "EUNE":
        urlRef = 'https://eun1.api.riotgames.com'
    elif region == "BR":
        urlRef = 'https://br1.api.riotgames.com'
    elif region == "JP":
        urlRef = 'https://jp1.api.riotgames.com'
    elif region == "KR":
        urlRef = 'https://kr1.api.riotgames.com'
    elif region == "LAN":
        urlRef = 'https://la1.api.riotgames.com'
    elif region == "LAS":
        urlRef = 'https://la2.api.riotgames.com'
    elif region == "OCE":
        urlRef = 'https://oc2.api.riotgames.com'
    elif region == "TR":
        urlRef = 'https://tr2.api.riotgames.com'
    elif region == "RU":
        urlRef = 'https://ru.api.riotgames.com'
    elif region == "PBE":
        urlRef = 'https://PBE.api.riotgames.com'
    elif region == "EUW":
        urlRef = 'https://euw1.api.riotgames.com'
    else:
        await bot.say("You did not use a listed region, or did not use capitals. Please refer to help command")
        flag = False
    if flag:
        await bot.say("Region Successfully changed to: " + region)


# Looks up profile image, ranked information, and top three champion masteries
@bot.command(pass_context=True)
async def profile(ctx,summonername):
    info = summonernametoid(summonername)
    summonerid = str(info[0])
    profileicon = str(info[1])
    embed = discord.Embed(title=summonername, description="Summoner Level [" + str(info[2]) + "]", color=0x00ff00)
    embed.set_thumbnail(url="http://ddragon.leagueoflegends.com/cdn/8.14.1/img/profileicon/" + profileicon + ".png")
    value = getrankinfo(summonerid)
    embed.add_field(name="Rank:", value=value, inline=True)
    url = urlgenerate("/lol/champion-mastery/v3/champion-masteries/by-summoner/", summonerid)
    parsemastery = json.loads(urllib.request.urlopen(url).read())
    value = ""
    for l in range(0,5):
        championid = str(parsemastery[l]["championId"])
        championname = json.loads(urllib.request.urlopen(urlgenerate("/lol/static-data/v3/champions/" + championid, "")).read())["name"]
        value += championname + ": [" + str(parsemastery[l]["championLevel"]) + "] " + str(parsemastery[l]["championPoints"]) + "\n"

    embed.add_field(name="Champion Mastery", value=value,inline=True)
    await bot.say(embed=embed)


# So to get the game information, one needs to get the summonerID
@bot.command(pass_context=True)
async def livegame(ctx, summonername):
    summonerid = str(summonernametoid(summonername)[0])
    url = urlgenerate('/lol/spectator/v3/active-games/by-summoner/', summonerid)
    matchinfo = urllib.request.urlopen(url)
    parsematchinfo = json.loads(matchinfo.read())
    # For some weird reason I can not set the thumbnail in the method so I am doing it outside
    embed = printteam(0, 5, 0x42C0FB, parsematchinfo, "Blue Team")
    embed.set_thumbnail(url="https://am-a.akamaihd.net/image?f=https://news-a.akamaihd.net/public/images/articles/2017/november/projectlearnmore/PROJECT-Ashe-First-Strike-Icon.jpg")
    await bot.say(embed=embed)
    embed = printteam(5, 10, 0xCC1100, parsematchinfo, "Red Team")
    embed.set_thumbnail(url="https://vignette.wikia.nocookie.net/leagueoflegends/images/9/92/PROJECT_profileicon.png/revision/latest?cb=20170504221607")
    await bot.say(embed=embed)


# Given champion/summoner, give its specific stats
@bot.command(pass_context=True)
async def mastery(ctx,summonername, championname):
    suminfo = summonernametoid(summonername)
    summonerid = str(suminfo[0])
    url = urlgenerate("/lol/static-data/v3/champions", "")
    championid = str(json.loads(urllib.request.urlopen(url).read())["data"][championname]["id"])
    url = urlgenerate2('/lol/champion-mastery/v3/champion-masteries/by-summoner/', summonerid, '/by-champion/', championid)
    masterylist = json.loads(urllib.request.urlopen(url).read())
    embed = discord.Embed(title=summonername, description= "Champion Mastery: " + championname, color=0xb9f2ff)
    embed.add_field(name="Mastery Level", value = masterylist["championLevel"], inline=True)
    embed.add_field(name="Mastery Score", value=masterylist["championPoints"], inline=True)
    thumbnailurl = "http://ddragon.leagueoflegends.com/cdn/6.24.1/img/champion/" + championname.title() + ".png"
    embed.set_thumbnail(url=thumbnailurl)
    await bot.say(embed=embed)


# One can't find information directly from username, so this method converts username to id for other searches
def summonernametoid(summonername):
    summonername = removespaces(summonername)
    url = urlgenerate('/lol/summoner/v3/summoners/by-name/', summonername)
    summonerinfo = urllib.request.urlopen(url)
    parsesummonerid = json.loads(summonerinfo.read())
    listinfo = [parsesummonerid['id'], parsesummonerid['profileIconId'], parsesummonerid['summonerLevel']]
    return listinfo


# These methods below take the information and make the url needed to make the API call
def urlgenerate(apiurl, secondinput):
    return urlRef + apiurl + secondinput + '?api_key=' + lolAPI


def urlgenerate2(apiurl1, secondinput1, apiurl2, secondinput2):
    return urlRef + apiurl1 + secondinput1 + apiurl2 + secondinput2 + '?api_key=' + lolAPI


def removespaces(string):
    string.replace(' ', '')
    return string


def getrankinfo(sumid):
    url = urlgenerate('/lol/league/v3/positions/by-summoner/', sumid)
    summonerrankinfo = json.loads(urllib.request.urlopen(url).read())
    if not summonerrankinfo:
        value = "UNRANKED"
    else:
        value = summonerrankinfo[0]['tier'] + " " + summonerrankinfo[0]['rank']
    return value


def printteam(range1, range2, color, parsematchinfo, title):
    embed = discord.Embed(title=title, description="", color=color)
    for k in range(range1, range2):
        title = parsematchinfo['participants'][k]['summonerName']
        sumid = str(parsematchinfo['participants'][k]['summonerId'])
        value = getrankinfo(sumid)
        embed.add_field(name=title, value=value, inline=True)
    return embed


bot.run('Your bot token')