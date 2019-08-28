import random, time, re, threading

FILE = "word_list_example.txt"
"""
Uses parsed text from the Tagaini Jisho program from www.tagaini.net 
when you click and copy an entry while using it.

So like... yeah... 

If there's anybody else using this, here's how you use it:
  You open up a notepad. You type (0,0,0) and then you copy and paste an entry from Taigani Jisho, which
  should look like this: 
  
(0,0,0)食べる, 喰べる (たべる): (1) to eat. (2) to live on (e.g. a salary), to live off, to subsist on.

And you make a newline and repeat for whatever words you want to add to it.

This program is made with the purpose of keeping track of your memorization progress of 
whatever words you pick out. It keeps track of your response time and how often you're right and
adjusts the chances of picking out random words you don't know.

Also here's a very important note: Use the handwriting IME pad and don't use romaji conversion, because that's cheating.

"""
TIME_SWITCH = False
TIME_TOTAL = float(0)

MS = 60
S = 60**2
M = 60**3
H = 60**4

def getSwitch(): return(globals().get("TIME_SWITCH"))
def flipSwitch():
    if getSwitch():
        globals().update({"TIME_SWITCH":False})
    else:
        globals().update({"TIME_SWITCH":True})
        
def resetTimer(): globals().update({"TIME_TOTAL":0})
def getTimer(): return(globals().get("TIME_TOTAL"))
def setTimer(x): return(globals().update({"TIME_TOTAL":x}))
def responseTimer():
    resetTimer()
    while True:
        if getSwitch():
            setTimer(getTimer()+1)
            time.sleep(0.01)
            if getTimer() > M*2:
                setTimer(M*2)

def formatTimer(t):
    a = t
    
    minutes = int(a/M)
    a -= int(a/M)*M

    seconds = int(a/S)
    a -= int(a/S)*S

    milliseconds = int(a/MS)
    a -= int(a/MS)*MS
    
    formattedTimer = "{:<2}:{:<2}:{:<2}".format(
        minutes, seconds, milliseconds)

    return(formattedTimer)
    

threadObj = threading.Thread(target=responseTimer)
threadObj.start()



WORD_FILE = open(FILE, "r+", encoding = "UTF-8")
WORDS = []
for line in WORD_FILE:
    if len(line) == 0 and line == "":
        continue
    else:
        WORDS.append(line)
WORD_FILE.close()

def getPercentage(x,y):
    x = float(x)
    y = float(y)
    percentage = float(0)
    try:
        percentage = (x*100)/y
    except ZeroDivisionError:
        percentage = 0
    return(percentage)

def getWordRoll():
    rng = random.randrange(0, len(WORDS))

    互reg = re.compile(r'\((\d*),(\d*),([-0-9.]*)\)(\D*)\((\D*)\): (.*)')
    cl = WORDS[rng].replace("\n", " ")

    cl = 互reg.findall(cl)[0]
    
    #print(cl)

    正   = int(cl[0])
    誤   = int(cl[1])
    時間  = float(cl[2])
    漢字  = cl[3].replace(" ", "").split(',')
    カナ  = cl[4]
    意味  = cl[5]


    total = 正 + 誤
    if total == 0:
        時間 = -1
    address = rng

    """
    正
    ----- =  ---
    Total    100
    """

    accuracy = getPercentage(正,total)
    inaccuracy = getPercentage(誤,total)
        
    print("正:{:<4}誤:{:<4}合計:{:<4}不正確:{:<6}".format(
        正,
        誤,
        total,
        round(inaccuracy, 2)))

    
    if inaccuracy <= 20:
        roll_limit = 20
    else:
        roll_limit = inaccuracy

    if total == 0:
        roll_limit = 100
    
    negative_range = int( -inaccuracy/10 )
    positive_range = int(    accuracy/10 )

    scaling_step = float(3/60)

    scaling = float(0.5 + scaling_step * total)
    
    rolls = int(total + 1)
    roll_sum = int(0)
    
    for x in range(1, rolls):
        roll_sum += random.randrange(negative_range, positive_range)

    roll_sum = roll_sum * scaling
    print("roll sum: ", roll_sum)
    
    if roll_sum >= roll_limit:
        print("Rerolled on 「%s」\n"%漢字)
        return(getWordRoll())
    
    return([カナ,漢字,正,誤,時間,意味, address])

def save_file():
    newSave = ""
    for line in WORDS:
        newSave += line
    newFile = open(FILE, "w", encoding = "UTF-8")
    newFile.write(newSave)
    newFile.close()
    
def run():
    msg =\
"""
Press ctrl+c to exit the program.
Using any other method to exit the program may
result in corrupted data.

"""
    print(msg)

    right_incrementor = 3
    wrong_incrementor = 1

    current_word = getWordRoll()
    flipSwitch()
    while True:
        try:
            カナ,漢字,正,誤,時間,意味,所 = current_word

            print("time to beat: %s"%formatTimer(時間))
            user_input = input("「%s」の漢字は何ですか？\n%s\n"%
                               (カナ,意味))
            
            if user_input in 漢字:
                new_time = int(getTimer())
                #flipSwitch()
                time.sleep(1)
                if(時間>new_time or 時間<0 or 時間==-1 or 正+誤==0):
                    print("%s\n%s(new record)"%(
                        formatTimer(時間),
                        formatTimer(new_time)))
                    時間 = new_time
                
                print("それは正しいです。")
                time.sleep(2)
                print('\n'*99)
                
                正 += right_incrementor
                old_stats = re.compile(r'\(\d*,\d*,[-0-9.]*\)')
                new_stats = "(%s,%s,%s)"%(正,誤,時間)
                WORDS[所] = re.sub(old_stats,new_stats,WORDS[所])
                
                wrong_incrementor = 1
                right_incrementor = 2

                new_word = getWordRoll()
                if new_word == current_word:
                    print("\n"*99)
                    print("Let's see if you can get it right again")
                    right_incrementor += 1
                current_word = new_word

                resetTimer()

            else:
                current_word = current_word
                print("漢字：　%s"%漢字)
                input("上に漢字の中から一つを選んで書いて下さい.\n")
                print("\n"*99)
                
                誤 += wrong_incrementor
                old_stats = re.compile(r'\(\d*,\d*,[-0-9.]*\)')
                new_stats = "(%s,%s,%s)"%(正,誤,時間)
                WORDS[所] = re.sub(old_stats,new_stats,WORDS[所])

                wrong_incrementor += 1
                right_incrementor -= 2
                if right_incrementor <= 1:
                    right_incrementor = 1
                    
        except KeyboardInterrupt:
            save_file()
            break
        
        except IndexError:
            print("A line wasn't properly formatted: ")
            print("\t",current_word)
            pass
run()
