from PIL import Image, ImageDraw, ImageFont
import urllib2
from bs4 import BeautifulSoup
from bs4 import BeautifulStoneSoup
import random, re
import twitter

attempts = 0

raw_films = open("films.txt", "r").readlines()
films = []
for film in raw_films:
    if "(" in film:
        films.append(film[:film.index('(')-1].lower())
    else:
        films.append(film.lower())

# raw_songs = open("songs", "r").readlines()
# songs = []
# for song in raw_songs:
#     # print song
#     song = song[song.index(".")+1:song.index(" - ")].lower().strip()
#     songs.append(song)

def checkwidth(font, lines, lim):
    for line in lines:
        if(font.getsize(line)[0] >= lim):
            return False
    return True

def generate():
    raw_idioms = open("idioms.txt", "r").readlines()
    idioms = []
    for idiom in raw_idioms:
        # print song
        idioms.append(idiom.strip())

    data = idioms + films# + songs

    ingredients = ["tomato", "bacon", "pepper", "pea", "peas", "chevre", "fig", "radish", "leek", "olive", "curry", "shallot", "onion", "kale", "fennel", "poutine", "lentil", "egg", "carrot", "cheddar", "thyme",
                    "feta", "tuna", "corn", "honey", "blue", "chorizo", "rye", "sour", "swiss", "palm", "beet", "bean", "slaw", "cumin", "mint", "brie", "polenta",
                    "chilli", "yam", "bun", "barley", ]
    ingredient = random.choice(ingredients)

    ingredients_dict = {
        "bacon" : ["streaky bacon", "bacon rashers", "bacon"],
        "peas" : ["steamed peas", "peas", "snap peas", "snow peas"],
        "pea" : ["steamed peas", "peas", "snap peas", "snow peas"],
        "pepper" : ["red pepper", "sliced pepper", "peppers"],
        "chevre" : ["chevre cheese", "goat's cheese"],
        "fig" : ["a side of figs", "roasted fig"],
        "radish" : ["sliced radish", "radishes"],
        "leek" : ["braised leek", "steamed leeks"],
        "olive" : ["stuffed olives", "spanish olives", "olives"],
        "curry" : ["curry sauce"],
        "shallot" : ["shallots", "steamed shallots"],
        "onion" : ["red onion", "onion rings", "fried onions"],
        "kale" : ["kale", "crispy kale", "kale chips"],
        "fennel" : ["fennel"],
        "poutine" : ["a side of poutine"],
        "lentil" : ["green lentils"],
        "egg" : ["fried egg", "poached egg", "scrambled egg"],
        "carrot" : ["shredded carrot", "grated carrot"],
        "cheddar" : ["aged cheddar", "melted cheddar", "slices of cheddar"],
        "thyme" : ["thyme"],
        "feta" : ["feta cheese"],
        "tuna" : ["tuna steak"],
        "corn" : ["corn salsa"],
        "honey" : ["honey mustard", "a honey glaze"],
        "blue" : ["blue cheese"],
        "chorizo" : ["chorizo"],
        "rye" : ["a rye bun"],
        "sour" : ["a sourdough bun", "sour cream"],
        "swiss" : ["swiss cheese"],
        "palm" : ["hearts of palm"],
        "beet" : ["beets"],
        "bean" : ["beans", "refried beans", "pinto beans"],
        "slaw" : ["coleslaw"],
        "cumin" : ["cumin"],
        "mint" : ["mint relish"],
        "brie" : ["brie"],
        "polenta" : ["polenta"],
        "chilli" : ["chilli relish", "chillies"],
        "yam" : ["yams"],
        "bun" : ["a fancy bun"],
        "barley" : ["a barley roll"],
        "tomato" : ["cherry tomatoes", "a grilled tomato"],

    }

    #let's get a rhyme set

    hdr = { 'User-Agent' : 'grauniadconlums' }
    req = urllib2.Request("http://www.rhymezone.com/r/rhyme.cgi?Word="+ingredient+"&typeofrhyme=perfect&org1=syl&org2=l&org3=y", headers=hdr)

    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError:
        exit()

    html = response.read()

    FromRaw = lambda r: r if isinstance(r, unicode) else r.decode('utf-8', 'ignore')
    html = FromRaw(html)

    rhymeset = []

    #banlist but also words that have iffy rhymes that we want to avoid
    bannedwords = ["our", "hamp", "rom"]

    doc = BeautifulSoup(html, features="xml")
    for lnk in doc.findAll("a"):
        if lnk.parent.name == "b" and ">" in lnk.text:
            # print lnk.text
            # print lnk.text[lnk.text.index(">")+1:]
            if (len(lnk.text[lnk.text.index(">")+1:].lower()) > 2) and (not lnk.text[lnk.text.index(">")+1:].lower() in bannedwords):
                rhymeset.append(lnk.text[lnk.text.index(">")+1:].lower())

    poss = []
    meaning = []
    # print rhymeset

    for film in data:
        for rhyme in rhymeset:
            if rhyme == film:
                continue
            # if rhyme in film and len(film.replace(rhyme, ingredient)) < 60:
            #     poss.append(film.replace(rhyme, ingredient))
            #     meaning.append(film)
            if re.search(r"\b" + re.escape(rhyme) + r"\b", film): # + r"\b"
                poss.append(film.replace(rhyme, ingredient))
                meaning.append(film)
            if re.search(r"\b" + re.escape(rhyme) + r"[a-zA-Z]", film): # + r"\b"
                poss.append(film.replace(rhyme, ingredient+"-"))
                meaning.append(film)
            if re.search(r"[a-zA-Z]" + re.escape(rhyme) + r"\b", film):
                poss.append(film.replace(rhyme, "-"+ingredient))
                meaning.append(film)

    # print meaning
    # print poss

    if len(poss) == 0:
        print "failed to find for "+ingredient
        generate()
        return

    W, H = (1100,704)

    commentimg = Image.open("bobs_base.png")

    s1 = [random.choice(poss)+" burger"]
    s1[0] = s1[0].lower()
    s2 = "("+random.choice(["comes", "served"])+" with "+random.choice(ingredients_dict[ingredient])+")"

    #Let's check if we've generated this before
    existing = open("existing.txt", "ab+")
    already_done = existing.readlines()
    if s1[0] in already_done:
        existing.close()
        attempts += 1
        if(attempts > 200):
            #We need a bigger corpus
            print "Help! I might be exhausting my corpus."
            exit()
        generate()
        return
    else:
        existing.write(s1[0]+"\n")
        existing.close()

    import textwrap
    if(len(s1[0]) > 35):
        s1 = textwrap.wrap(s1[0], width=len(s1[0])/3 + 5)
    else:
        s1 = textwrap.wrap(s1[0], width=len(s1[0])/2 + 5)
    # if len(s1[0]) > 40:
    #     print "40+"
    #     s1 = textwrap.wrap(s1[0], width=len(s1[0])/3 + 5)
    # elif len(s1[0]) > 20:
    #     print "20+"
    #     s1 = textwrap.wrap(s1[0], width=20)


    fontsize = 16
    fnt1 = ImageFont.truetype("chalk.ttf", fontsize)
    while checkwidth(fnt1, s1, 360):
        # iterate until the text size is just larger than the criteria
        fontsize += 1
        fnt1 = ImageFont.truetype("chalk.ttf", fontsize)

    fontsize = 16
    fnt2 = ImageFont.truetype("chalk.ttf", fontsize)
    while fnt2.getsize(s2)[0] < 360:
        # iterate until the text size is just larger than the criteria
        fontsize += 1
        fnt2 = ImageFont.truetype("chalk.ttf", fontsize)

    d = ImageDraw.Draw(commentimg)

    chalk_color = (213, 220, 223, 255)

    line = 0
    for s in s1:
        delta = (400-fnt1.getsize(s)[0])/2
        d.text((360+delta,260+(fnt1.getsize(s)[1]*line)), s, font=fnt1, fill=chalk_color)
        line = line+1
    delta = (400-fnt2.getsize(s2)[0])/2
    d.text((360+delta, 470), s2, font=fnt2, fill=chalk_color)

    #sometimes add an extra image in
    print random.randint(0,3)
    if(random.randint(0, 2) == 1):
        imgs = [('char1.png', (25,200)), ('char2.png',(20,320)), ('char3.png',(15,360)), ('char4.png',(10,250)), ('char5.png', (10, 400)), ('char6.png', (10, 300)), ('char7.png', (-180, 405))]
        sel = random.choice(imgs)

        img = Image.open(sel[0], 'r')
        if(sel[0] == 'char7.png'):
            commentimg.paste(img, sel[1], img)
        elif(sel[0] == 'char6.png' or random.randint(0,1) == 0):
            commentimg.paste(img, (750-sel[1][0], sel[1][1]), img)
        else:
            commentimg.paste(img, sel[1], img)

    commentimg.show()

    commentimg.save("out.png");
    return

    api = twitter.Api(
    consumer_key='KPWQ0szhb0JYQht1J9dn8ahZ1',
    consumer_secret='3SVO0I2Ji7LlZrvqhHuMxxYvlwnCej5VbFmouXzxbg4DlJYcGR',
    access_token_key='719663414767960064-xtffbRMnDDq0iySsDsxK78TDbBNo4dy',
    access_token_secret='9IQyu8q7T016Y3Qkhn1PEQ4hBVLE6gH4MNhdIiSbomff2');

    api.PostMedia("","out.png")

generate()


