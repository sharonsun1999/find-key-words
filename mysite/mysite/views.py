from django.http import HttpResponse
from django.shortcuts import render,render_to_response
from django.views.decorators.csrf import csrf_exempt

def is_letter(char):
    if (ord(char) >= 65) and (ord(char) <= 90):
        return True
    elif (ord(char) >= 97) and (ord(char) <= 122):
        return True
    else:
        return False

def article_to_words(article):
    l = len(article)
    words = []
    word = ""
    has_appended = False
    for i in range(l):
        if is_letter(article[i]):
            if (i == 0) or (not is_letter(article[i - 1])):
                word = article[i]
                has_appended = False
            else:
                word = word + article[i]
        else:
            if not has_appended:
                words.append(word)
                has_appended = True
    if not has_appended:
        words.append(word)

    return words

def check_frequency(words):
    tree = {}
    tree[""] = {}
    num = {}
    num[""] = 0
    length = len(words)
    for i in range(length):
        word = words[i]
        l = len(word)
        pos = ""
        new_word = False
        for j in range(l):
            letter = word[j]
            if not tree[pos].has_key(pos + letter):
                new_word = True
                tree[pos][pos + letter] = letter
                tree[pos + letter] = {}
                num[pos + letter] = 0
            pos = pos + letter
        if new_word:
            num[word] = 1
        else:
            num[word] += 1
    return num

# Some of the following data is from https://en.wikipedia.org/wiki/Most_common_words_in_English
avoid_words = []

avoid_words += ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]

avoid_words += ["eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]

avoid_words += ["twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

avoid_words += ["hundred", "thousand", "million", "billion"]

avoid_words += ["be", "am", "is", "are", "have", "do", "say", "get", "make", "go", "know", "take", "see", "come", "think", "look", "want", "give", "use", "find", "tell", "ask", "work", "seem", "feel", "try", "leave", "call"]

avoid_words += ["has", "does", "says", "gets", "makes", "goes", "knows", "takes", "sees", "comes", "thinks", "looks", "wants", "gives", "uses", "finds", "tells", "asks", "works", "seems", "feels", "tries", "leaves", "calls"]

avoid_words += ["being", "having", "doing", "saying", "getting", "making", "going", "knowing", "taking", "seeing", "coming", "thinking", "looking", "wanting", "giving", "using", "finding", "telling", "asking", "working", "seeming", "feeling", "trying", "leaving", "calling"]

avoid_words += ["was", "were", "had", "did", "said", "got", "made", "went", "knew", "took", "saw", "came", "thought", "looked", "wanted", "gave", "used", "found", "told", "asked", "worked", "seemed", "felt", "tried", "left", "called"]

avoid_words += ["been", "done", "gotten", "gone", "known", "taken", "seen", "given"]

avoid_words += ["to", "of", "in", "for", "on", "with", "at", "by", "from", "up", "about", "into", "over", "after", "before"]

avoid_words += ["the", "and", "a", "that", "i", "me", "it", "not", "he", "as", "you", "this", "but", "his", "they", "her", "she", "or", "an", "will", "my", "one", "all", "would", "there", "their", "even", "very", "we", "our", "its", "these", "those"]

avoid_words += ["what", "which", "how", "when", "who", "where", "whom"]

avoid_words += ["can", "could", "shall", "should", "must", "may", "might", "not"]

avoid_words += ["however", "nevertheless", "nonetheless"]

avoid_words += ["don", "didn", "wouldn", "couldn", "shouldn", "mustn"]

avoid_words += ["s", "t"]

extra_words = []
for word in avoid_words:
    extra_words.append(chr(ord(word[0]) - 32) + word[1:])
avoid_words += extra_words

def should_avoid(word):
    for word2 in avoid_words:
        if word == word2:
            return True
    return False

def is_connected(word1, word2, words):
    count = 0
    connect_level = 2
    l = len(words)
    index = 0
    for word in words:
        if (word == word1) and (index != l - 1) and (words[index + 1] == word2):
            count += 1
        if count >= connect_level:
            return True
        index += 1
    return False

def check_plural(word1, word2):
    l = len(word1)
    
    if word1 + "s" == word2:
        return True
    
    if word1 + "es" == word2:
        return True
    
    if (word1[l - 1] == "y") and (word1[0:(l - 1)] + "ies" == word2):
        return True
    
    return False

def check_upcase(word1, word2):
    if (ord(word1[0]) - 32 == ord(word2[0])) and (word1[1:] == word2[1:]):
        return True
    else:
        return False

def find_max_frequency_words(n, article):
    words = article_to_words(article)
    num = check_frequency(words)
    ans = []

    if n <= 15:
        n1 = n
    else:
        n1 = 15

    while n1 > 0:
        key = []
        key = num.keys()
        if len(key) == 0:
            break
        max_frequency = 0
        max_frequency_word = ""
        for word in key:
            if max_frequency < num[word]:
                max_frequency = num[word]
                max_frequency_word = word
        if max_frequency == 1:
            break
        elif not should_avoid(max_frequency_word):
            ans.append(max_frequency_word)
            n1 -= 1
        num.pop(max_frequency_word)
    
    ans1 = list(ans)
    
    remove = set([])
    for word1 in ans1:
        for word2 in ans1:
            if is_connected(word1, word2, words):
                ans.append(word1 + " " + word2)
                remove.add(word1)
                remove.add(word2)
    for word in remove:
        ans.remove(word)

    for word1 in ans1:
        for word2 in ans1:
            if check_plural(word1, word2):
                ans.remove(word2)
            elif check_upcase(word1, word2):
                ans.remove(word2)
    
    ans1 = list(ans)
    ans = []
    for word in ans1:
        if (ord(word[0]) >= 65) and (ord(word[0]) <= 90):
            ans.append(word)
    for word in ans1:
        if (ord(word[0]) >= 97) and (ord(word[0]) <= 122):
            ans.append(word)
    
    keywords=''
    for oneword in ans:
        if keywords=='':
            keywords=str(oneword)
        else:
            keywords=keywords+', '+str(oneword)    
    return keywords

def index(request):
	return render(request, 'index.html')

@csrf_exempt
def textpost(request):
	if request.method == "GET":
		arti=request.GET['article']
		arti=find_max_frequency_words(10,arti)
		change={'count':arti}
		return render(request, 'index.html',change)
